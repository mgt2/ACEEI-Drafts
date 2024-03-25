import numpy as np
import gurobipy as gp
from gurobipy import GRB
from node import *
gp.setParam("TokenFile", "gurobi.lic")

def find_max_exclude (node, w, j) :
    m = node.data["m"]
    data = node.data
    prices = node.prices
    model = gp.Model("max_without_w")
    x = model.addVars(m, lb=0, ub=1, vtype=GRB.CONTINUOUS, name="x")

    # Sets objective
    model.setObjective(gp.quicksum(x[i] * data['valuations'][j][i] for i in range(m)) +
                   gp.quicksum(x[i] * x[k] * data['etas'][j][k][i] for i in range(m) for k in range(i)),
                   sense=GRB.MAXIMIZE)
    # Courses cannot exceed budget of agent
    model.addConstr(gp.quicksum(x[i] * prices[i] for i in range(m)) <= data['budgets'][j])

    # Type constraints must be satisfied
    for k in range(len(data['c_types'][0])):
        model.addConstr(gp.quicksum(x[i] * data['c_types'][j][i][k] for i in range(m)) <= data['maxes'][j][k])

    # Time constraints
    for k in range(len(data['c_times'][0])) :
        for l in range(len(data['c_times'][0][k])) :
            model.addConstr(gp.quicksum(x[i] * data['c_times'][i][k][l] for i in range(m)) <= 1)

     # Time constraints
    #model.addConstr(gp.quicksum(x[i] * data['c_times'][i][k][l] for k in range(len(data['c_times'][0])) for l in range(len(data['c_times'][0][k])) for i in range(m)) <= 1)

    # Cannot be course w
    model.addConstr(x[w] == 0, name=f"force_x_{w}_to_0")

    # Student is enrolled in enough courses
    # model.addConstr(gp.quicksum(x[i] for i in range(m)) >= data['min_courses'])

    # Don't print solver
    model.setParam('OutputFlag', 0)
    
    # Optimize the model
    model.optimize()

    if model.status == GRB.OPTIMAL :
        opt = model.objVal
        model.dispose()
        return opt
    print(f"Optimization status: {model.status}")
    model.dispose()
    return RuntimeError

def find_min_include(node, j, i, opt_without) :
    m = node.data["m"]
    data = node.data
    prices = node.prices
    model = gp.Model("max_without_w")
    x = model.addVars(m, lb=0, ub=1, vtype=GRB.CONTINUOUS, name="x")

    # Objective: minimum cost
    model.setObjective(gp.quicksum(x[k] * prices[k] for k in range(m)), sense=GRB.MINIMIZE)

    # Constraint: must have greater preference than maximum without course j
    model.addConstr(gp.quicksum(x[k] * data['valuations'][i][k] for k in range(m)) + gp.quicksum((l < k) * x[l] * x[k] * data['etas'][i][l][k] for l in range(m) for k in range(m)) >= float(opt_without) + 1e-10)
    
    # Constraint: Courses must satisfy time and type constraints
    # Type constraints must be satisfied
    for k in range(len(data['c_types'][0])):
        model.addConstr(gp.quicksum(x[l] * data['c_types'][l][k] for l in range(m)) <= data['maxes'][k])

    # Time constraints
    for k in range(len(data['c_times'][0])) :
        for l in range(len(data['c_times'][0][k])) :
            model.addConstr(gp.quicksum(x[a] * data['c_times'][a][k][l] for a in range(m)) <= 1)
    

    # Time constraints
    #model.addConstr(gp.quicksum(x[i] * data['c_times'][i][k][l] for k in range(len(data['c_times'][0])) for l in range(len(data['c_times'][0][k])) for i in range(m)) <= 1)

    # Constraint: Course j must be chosen
    model.addConstr(x[j] == 1)

    # Student is enrolled in enough courses
    # model.addConstr(gp.quicksum(x[k] for k in range(m)) >= data['min_courses'])

    # Don't print solver
    model.setParam('OutputFlag', 0)

    # Optimize
    model.optimize()

    if model.status == GRB.OPTIMAL :
        opt = model.objVal
        model.dispose()
        return opt
    print(f"Optimization status: {model.status}")
    model.dispose()
    return RuntimeError



# Adjusts prices of courses such that one student will remove that course
def adjust_prices(curnode, demand, seats, epsilon) :
    minprice = 1000 # Larger than any price should be
    oversubscribed = np.where(demand - seats > 0, True, False)
    oversubscribed_indices = np.where(oversubscribed)[0]
    budgets = curnode.data['budgets']
    neighbors = np.array([])
    count = 0
    for j in oversubscribed_indices :
        minprice = 1000
        changed = False

        new_node = Node()
        new_node.create(curnode.prices.copy(), seats, curnode.data)
        
        count += 1

        budget_indices = np.where(curnode.courses[:, j], True, False)
        budget_indices = np.where(budget_indices)[0]
        for i in budget_indices :
            max_without_j = find_max_exclude(curnode, j, i)
            min_with_j = find_min_include(curnode, j, i, max_without_j)

            price = curnode.prices[j] +  budgets[i] - min_with_j + epsilon
            if price < minprice :
                minprice = price
                changed = True
        if changed : 
            new_node.prices[j] += minprice
            new_node.setDemandCalc(False)
        neighbors = np.append(neighbors, new_node)
        if count > 50 :
            break
    
    return neighbors


# Adjusts prices with gradient
def adjust_gradient_prices(node, gradient, max_change_vals, seats) :
    gradient_node = Node()
    neighbors = np.array([])
    for i in range(len(max_change_vals)) :
        gradient_node = Node()
        c = max_change_vals[i] / np.max(np.abs(gradient * node.prices))
        new_prices = node.prices + c * gradient * node.prices
        gradient_node.create(new_prices, seats, node.data)
        neighbors = np.append(neighbors, gradient_node)
    return neighbors


def adjust_prices_half(prices, max_budget, epsilon, seats, data) :
    adjust_node = Node()
    adjust_node.create(prices, seats, data)
    demand = adjust_node.get_demand()
    oversubscribed = np.array(demand - seats)
    j = np.argmax(oversubscribed)
    while np.max(oversubscribed) > 0 :
        d = int(0.5 * oversubscribed[j])
        low_p = prices[j]
        high_p = max_budget

        while high_p - low_p > epsilon :
            prices[j] = 0.5 * (high_p + low_p)
            demand = adjust_node.get_demand()
            oversubscribed = np.array(demand - seats)

            if oversubscribed[j] > d :
                low_p = prices[j]
            else :
                high_p = prices[j]
        prices[j] = high_p
        j = np.argmax(oversubscribed)
    return prices

def reduce_undersubscription(node, seats) :
    def reoptimize(i, undersubscribed, node, old_courses) :
        model = gp.Model("reoptimize")
        x = model.addVars(m, lb=0, ub=1, vtype=GRB.CONTINUOUS, name="x")
        model.setObjective(gp.quicksum(x[j] * node.data['valuations'][i][j] for j in range(node.data['m'])) +
                   gp.quicksum(x[j] * x[k] * node.data['etas'][i][k][j] for j in range(node.data['m']) for k in range(j)),
                   sense=GRB.MAXIMIZE)
        
        model.addConstr(gp.quicksum(x[j] * node.prices[j] for j in range(node.data['m'])) <= node.data['budgets'][i] * 1.1)
        for k in range(len(node.data['c_types'][i])):
            model.addConstr(gp.quicksum(x[j] * node.data['c_types'][i][j][k] for j in range(node.data['m'])) <= node.data['maxes'][i][k])

        # Time constraints
        for k in range(len(node.data['c_times'][0])) :
            for l in range(len(node.data['c_times'][0][k])) :
                model.addConstr(gp.quicksum(x[j] * node.data['c_times'][j][k][l] for j in range(node.data['m'])) <= 1)
        
        # Time constraints
        # model.addConstr(gp.quicksum(x[i] * node.data['c_times'][i][k][l] for k in range(len(node.data['c_times'][0])) for l in range(len(node.data['c_times'][0][k])) for i in range(node.data['m'])) <= 1)
        # Only undersubscribed courses can be changed
        for j in range(node.data['m']):
            if undersubscribed[j] < 0:
                model.addConstr(x[j] <= 1)
            else :
                model.addConstr(x[j] - old_courses[j] <= 0)

        # Don't print solver
        model.setParam('OutputFlag', 0)

        # Optimize the model
        model.optimize()


        # Get the optimal solution
        status = model.status
        if status == GRB.OPTIMAL:
            selected_courses = [int(x[i].x) for i in range(node.data['m'])]
            model.dispose()
            return selected_courses
        else:
            print(f"Optimization status: {status}")
        model.dispose()
        return RuntimeError

    def get_undersubscribed(courses) :
        undersubscribed = np.sum(courses, axis =0)
        return undersubscribed
    
    done = False
    demand = node.get_demand()
    undersubscribed = np.array(demand - seats)
    old_courses = node.get_courses()
    while not done :
        done = True
        for i in range(node.data['n']) :
            new_courses = reoptimize(i, undersubscribed, node, old_courses[i])
            if not np.array_equal(new_courses, old_courses[i]) :
                done = False
                old_courses[i] = new_courses
                break
        undersubscribed = get_undersubscribed(old_courses)
    return old_courses
