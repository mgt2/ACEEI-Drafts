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
    for k in range(len(data['c_types'][j][0])):
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
    model.Params.NonConvex = 2
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
    for k in range(len(data['c_types'][j][0])):
        model.addConstr(gp.quicksum(x[l] * data['c_types'][j][l][k] for l in range(m)) <= data['maxes'][j][k])

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

def isValidTime(schedule, c_time) :
    return np.sum(np.bitwise_and(schedule, c_time)) == 0

def isValidType(count_types, c_type, maxes) :
    course_type = np.argmax(c_type)
    if count_types[course_type] + 1 > maxes[course_type] :
        return False
    return True

def isValidBundle(schedule, c_times, count_types, c_types, maxes, bundle) :
    if not isValidTime(schedule, c_times[bundle[0]]) or not isValidTime(schedule, c_times[bundle[1]]) :
        return False
    if not isValidType(count_types, c_types[bundle[0]], maxes) or not isValidType(count_types, c_types[bundle[1]], maxes) :
        return False
    if np.sum(np.bitwise_and(bundle[0], bundle[1])) > 0 :
        return False
    if np.argmax(c_types[bundle[0]]) == np.argmax([bundle[1]]) and count_types[np.argmax(c_types[bundle[0]])] + 2 > maxes[np.argmax(c_types[bundle[0]])] :
        return False
    return True

def find_min_include(node, included_j, i, prev_min) :
    data = node.data
    m = data["m"]
    budget = data['budgets'][i]
    prices = node.get_prices()
    valuations = np.array(data['valuations'][i])
    etas = data['etas']
    budget = data['budgets'][i]
    c_types = data['c_types'][i]
    c_times = data['c_times']
    maxes = data['maxes'][i]

    min_price = prev_min

    count_types = np.zeros(data['t'])
    schedule = np.zeros(shape=(len(c_times[0]), len(c_times[0][0])))

    c_times = c_times.astype(int)
    schedule = schedule.astype(int)
    # Calculate the ratios
    ratios = valuations / np.array(prices)

    # Get the indices that would sort the ratios in descending order
    sorted_indices = np.argsort(ratios)[::-1]

    x = np.zeros(m)

    t = []
    t_utilities = np.array([])
    t_prices = np.array([])
    for j in range(m) :
        for k in range(j) :
            if etas[i][k][j] != 0 :
                # Add tuple (j, k) to t (for bundles)
                t.append((j, k))
                t_utilities = np.append(t_utilities, valuations[k] + valuations[j] + etas[i][k][j])
                t_prices = np.append(t_prices, prices[j] + prices[k])

    t_ratios = t_utilities / t_prices
    t_sorted_indices = np.argsort(t_ratios)[::-1]
    taken_course = np.zeros(m)
    courses_picked = 0
    lowest_ratio_taken = 2 ** 10 # Arbitrarily large number (in practice this will never be exceeded)

    while budget > 0 and courses_picked < data['k']:
        # If best singleton has been used in a taken bundle already, or if best bundle has been used in a taken singleton already
        best_singleton_index = sorted_indices[0] if len(sorted_indices) > 0 else -1

        best_bundle_index = t_sorted_indices[0] if len(t_sorted_indices) > 0 else -1
        (best_bundle_index_1, best_bundle_index_2) = t[best_bundle_index] if best_bundle_index != -1 else (-1, -1)

        if best_singleton_index == -1 :
            break

        # If best singleton is invalid or taken already in a bundle, we remove it from consideration
        while best_singleton_index == included_j or (taken_course[best_singleton_index] == 1 or not isValidTime(schedule, c_times[best_singleton_index]) or not isValidType(count_types, c_types[best_singleton_index], maxes)) :
            sorted_indices = np.delete(sorted_indices, 0)
            if len(sorted_indices) == 0 :
                break
            best_singleton_index = sorted_indices[0]
        
        # If somehow we have chosen all courses, we break
        if len(sorted_indices) == 0 :
            break

        first_bundle_with_j = -1
        first_bundle_with_j_seen = False
            
        # If one or more courses in a bundle is invalid or taken already, we remove the bundle from consideration
        # print(best_bundle_index, best_bundle_index_1, best_bundle_index_2)
        while best_bundle_index != -1 and (best_bundle_index_1 == included_j or best_bundle_index_2 == included_j or taken_course[best_bundle_index_1] == 1 or taken_course[best_bundle_index_2] == 1 or not isValidBundle(schedule, c_times, count_types, c_types, maxes, t[best_bundle_index])) :
            if not first_bundle_with_j_seen and (best_bundle_index_1 == included_j or best_bundle_index_2 == included_j) :
                first_bundle_with_j = best_bundle_index
                first_bundle_with_j_seen = True
            t_sorted_indices = np.delete(t_sorted_indices, 0)
            best_bundle_index = t_sorted_indices[0] if len(t_sorted_indices) > 0 else -1
            (best_bundle_index_1, best_bundle_index_2) = t[best_bundle_index] if best_bundle_index != -1 else (-1, -1)

        # If the node we want to include is the best singleton, we increase its price so its ratio is equal to the next in line
        # if best_singleton_index == included_j and not (best_bundle_index_1 == included_j or best_bundle_index_2 == included_j) :
        #     # If the second-best (or the best) ratio belongs to the best bundle
        #     if len(t_sorted_indices) > 0 and len(sorted_indices) > 1 and t_ratios[t_sorted_indices[0]] > ratios[sorted_indices[1]]:
        #         # We increase the price of the singleton so its ratio is equal to the second best (ONLY IF IT WOULD OTHERWISE BE THE BEST)
        #         if ratios[sorted_indices[0]] > t_ratios[t_sorted_indices[0]] :
        #             min_price = valuations[included_j] / t_ratios[t_sorted_indices[0]]
        #             ratios[sorted_indices[0]] = valuations[included_j] / (min_price + 1e-5)

        #     # We stop considering our best singleton and add second best. We keep our best singleton and compare again later.
        #     elif len(sorted_indices) > 1 :
        #         min_price = valuations[included_j] / ratios[sorted_indices[1]]
        #         ratios[sorted_indices[0]] = valuations[included_j] / (min_price + 1e-5)
        #         singleton_index = 1

        # HANDLE BUNDLE ITEM EXCLUSION
        # elif best_bundle_index_1 == included_j or best_bundle_index_2 == included_j and sorted_indices[0] != included_j :
        #     # If the second-best (or the best) ratio belongs to the best singleton
        #     if len(t_sorted_indices) > 1 and ratios[sorted_indices[0]] > t_ratios[t_sorted_indices[1]] :
        #         # We increase the price of the bundle so its ratio is equal to the second best (ONLY IF IT WOULD OTHERWISE BE THE BEST)
        #         if t_ratios[t_sorted_indices[0]] > ratios[sorted_indices[0]] :
        #             min_price = (valuations[best_bundle_index_1] + valuations[best_bundle_index_2]) / ratios[sorted_indices[0]]
        #             t_ratios[t_sorted_indices[0]] = (valuations[best_bundle_index_1] + valuations[best_bundle_index_2]) / (min_price + 1e-5)

        #     # We stop considering our best bundle and add second best. We keep our best bundle and compare again later.
        #     elif len(t_sorted_indices) > 1 :
        #         (secondbest_bundle1, secondbest_bundle2) = t[t_sorted_indices[1]]
                
        #         min_price = (t_utilities[t_sorted_indices[0]]) / t_ratios[t_sorted_indices[1]]
        #         t_ratios[t_sorted_indices[0]] = t_utilities[t_sorted_indices[0]] / (min_price + 1e-5)
        #         bundle_index = 1

        #     # If this is the last bundle, we raise the price to match the utility/price ratio to the next singleton
        #     else :
        #         min_price = t_utilities[t_sorted_indices[0]] / ratios[sorted_indices[0]]
        #         t_ratios[t_sorted_indices[0]] = t_utilities[t_sorted_indices[0]] / (min_price + 1e-5)
        
        # HANDLE BOTH SINGLETON AND BUNDLE EXCLUSION

        # If the minimum price we increase by is greater than the previous minimum, we have not improved and give up.
        # if min_price > prev_min :
        #     return prev_min

        # If best bundle is preferred to best singleton
        if len(t_sorted_indices) > 0 and t_ratios[t_sorted_indices[0]] > ratios[sorted_indices[0]] :
            if t_prices[t_sorted_indices[0]] <= budget :
                j = int(t[t_sorted_indices[0]][0])
                k = int(t[t_sorted_indices[0]][1])
                x[j] = 1
                x[k] = 1
                budget -= t_prices[t_sorted_indices[0]]

                # Update lowest ratio taken
                lowest_ratio_taken = t_ratios[t_sorted_indices[0]]

                t_sorted_indices = np.delete(t_sorted_indices, 0)
                taken_course[j] = 1
                taken_course[k] = 1
                courses_picked += 2

                # Adding bundle to schedule
                schedule = schedule + c_times[j] + c_times[k]

                # Adding course types to count_types
                count_types[np.argmax(c_types[j])] += 1
                count_types[np.argmax(c_types[k])] += 1

            else :
                j = int(t[t_sorted_indices[0]][0])
                k = int(t[t_sorted_indices[0]][1])
                x[j] = budget / t_prices[t_sorted_indices[0]]
                x[k] = budget / t_prices[t_sorted_indices[0]]
                budget = 0
                # Update lowest ratio taken
                lowest_ratio_taken = t_ratios[t_sorted_indices[0]]

        # If best singleton is preferred to best bundle
        else :
            if prices[sorted_indices[0]] <= budget :
                x[sorted_indices[0]] = 1
                budget -= prices[sorted_indices[0]]
                taken_course[sorted_indices[0]] = 1

                # Adding singleton to schedule
                schedule = schedule + c_times[sorted_indices[0]]

                # Adding course type to count_types
                count_types[np.argmax(c_types[sorted_indices[0]])] += 1

                # Update lowest ratio taken
                lowest_ratio_taken = ratios[sorted_indices[0]]

                sorted_indices = np.delete(sorted_indices, 0)
                courses_picked += 1
            else :
                x[sorted_indices[0]] = budget / prices[sorted_indices[0]]
                budget = 0
                # Update lowest ratio taken
                lowest_ratio_taken = ratios[sorted_indices[0]]
    
    if first_bundle_with_j_seen :
        min_price = min(valuations[included_j] / lowest_ratio_taken, t_utilities[first_bundle_with_j] / lowest_ratio_taken)
    
    else :
        min_price = valuations[included_j] / lowest_ratio_taken

    return min_price


# Adjusts prices of courses such that one student will remove that course
def adjust_prices(curnode, demand, seats, epsilon) :
    minprice = 1000 # Larger than any price should be
    oversubscribed = np.where(demand - seats > 0, True, False)
    oversubscribed_indices = np.where(oversubscribed)[0]
    budgets = curnode.data['budgets']
    neighbors = np.array([])
    count = 0
    for j in oversubscribed_indices :
        # minprice = 1000
        changed = False

        new_node = Node()
        new_node.create(curnode.prices.copy(), seats, curnode.data)
        
        count += 1

        budget_indices = np.where(curnode.courses[:, j], True, False)
        budget_indices = np.where(budget_indices)[0]
        prev_min = 2 ** 10
        for i in budget_indices :
            # max_without_j = find_max_exclude(curnode, j, i)
            min_with_j = find_min_include(curnode, j, i, prev_min)

            if min_with_j < prev_min :
                prev_min = min_with_j
                changed = True

            # price = curnode.prices[j] +  budgets[i] - min_with_j + epsilon
            # if price < minprice :
            #     minprice = price
            #     changed = True
        if changed : 
            new_node.prices[j] = prev_min
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
