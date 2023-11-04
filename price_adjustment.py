import numpy as np
import gurobipy as gp
from gurobipy import GRB

def find_max_exclude (node, w, j) :
    m = node.data["m"]
    data = node.data
    prices = node.prices
    model = gp.Model("max_without_w")
    x = model.addVars(m, vtype=GRB.BINARY, name="x")

    # Sets objective
    model.setObjective(gp.quicksum(x[i] * data['valuations'][j][i] for i in range(m)) +
                   gp.quicksum((i < k) * x[i] * x[k] * data['etas'][j][i][k] for i in range(m) for k in range(m)),
                   sense=GRB.MAXIMIZE)
    # Courses cannot exceed budget of agent
    model.addConstr(gp.quicksum(x[i] * prices[i] for i in range(m)) <= data['budgets'][j])

    # Type constraints must be satisfied
    for k in range(len(data['c_types'][0])):
        model.addConstr(gp.quicksum(x[i] * data['c_types'][i][k] for i in range(m)) <= data['maxes'][k])

    # Time constraints
    for k in range(len(data['c_times'][0])) :
        for l in range(len(data['c_times'][0][k])) :
            model.addConstr(gp.quicksum(x[i] * data['c_times'][i][k][l] for i in range(m)) <= 1)


    # Cannot be course w
    model.addConstr(x[w] == 0, name=f"force_x_{w}_to_0")

    # Optimize the model
    model.optimize()

    if model.status == GRB.OPTIMAL :
        opt = model.objVal
        model.dispose()
        return opt

    model.dispose()
    return RuntimeError

def find_min_include(node, j, i, opt_without) :
    m = node.data["m"]
    data = node.data
    prices = node.prices
    model = gp.Model("max_without_w")
    x = model.addVars(m, vtype=GRB.BINARY, name="x")

    # Objective: minimum cost
    model.setObjective(gp.quicksum(x[k] * prices[k] for k in range(m)), sense=GRB.MINIMIZE)

    # Constraint: must have greater preference than maximum without course j
    model.addConstr(gp.quicksum(x[k] * data['valuations'][i][k] for k in range(m)) +
                   gp.quicksum((l < k) * x[l] * x[k] * data['etas'][i][l][k] for l in range(m) for k in range(m)) > opt_without)
    
    # Constraint: Courses must satisfy time and type constraints
    # Type constraints must be satisfied
    for k in range(len(data['c_types'][0])):
        model.addConstr(gp.quicksum(x[l] * data['c_types'][l][k] for l in range(m)) <= data['maxes'][k])

    # Time constraints
    for k in range(len(data['c_times'][0])) :
        for l in range(len(data['c_times'][0][k])) :
            model.addConstr(gp.quicksum(x[a] * data['c_times'][a][k][l] for a in range(m)) <= 1)

    # Constraint: Course j must be chosen
    model.addConstr(x[j] == 1)

    # Optimize
    model.optimize()

    if model.status == GRB.OPTIMAL :
        opt = model.objVal
        model.dispose()
        return opt

    model.dispose()
    return RuntimeError



# Adjusts prices of courses such that one student will remove that course
def adjust_prices(curnode, demand, seats, epsilon) :
    minprice = 1000 # Larger than any price should be
    oversubscribed = np.where(demand - seats > 0, True, False)
    budgets = curnode.data['budgets']
    for j in range(len(curnode.prices)) :
        minprice = 1000
        changed = False
        if oversubscribed[j] == True:
            for i in range(len(budgets)) :
                if curnode.courses[i][j] == 1:
                    max_without_j = find_max_exclude(curnode, j, i)
                    min_with_j = find_min_include(curnode, j, i, max_without_j)

                    price = curnode.prices[j] +  budgets[i] - min_with_j + epsilon
                    if price < minprice :
                        minprice = price
                        changed = True
        if changed : 
            demand = curnode.calculate_demand() # Recalculate optimal courses
            oversubscribed = np.where(demand - seats > 0, True, False)