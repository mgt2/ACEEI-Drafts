import gurobipy as gp
from gurobipy import GRB
import numpy as np
gp.setParam("TokenFile", "gurobi.lic")

# Computes the demand LP function
# Takes in as parameters a set of prices and the data_struct from generate.py, 
# as well as index j to indicate which agent we are calculating demand for
def compute_demand(prices, data, j) :
    m = data['m']

    model = gp.Model("demand_computation")

    x = model.addVars(m, lb=0, ub=1, vtype=GRB.CONTINUOUS, name="x")

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
    # model.addConstr(gp.quicksum(x[i] * data['c_times'][i][k][l] for k in range(len(data['c_times'][0])) for l in range(len(data['c_times'][0][k])) for i in range(m)) <= 1)
    
    # model.addConstr(0 <= np.max(np.sum([x[a] * data['c_times'][a] for a in range(m)], axis=0)) <= 1)
    # Compute the expression for the constraint
    # expr = np.sum([x[a] * data['c_times'][a] for a in range(m)], axis=0)

    # # Add constraint for the upper bound
    # upper_bound = model.addConstr(expr[i][k] <= 1 for i in range(len(data['c_times'][0])) for k in range(len(data['c_times'][0][i])))

    # Student is enrolled in enough courses
    # model.addConstr(gp.quicksum(x[i] for i in range(m)) >= data['min_courses'])

    # Don't print solver
    model.setParam('OutputFlag', 0)

    # Optimize the model
    model.optimize()


    # Get the optimal solution
    status = model.status
    if status == GRB.OPTIMAL:
        selected_courses = [int(x[i].x) for i in range(m)]
        model.dispose()
        return selected_courses
    else:
        print(f"Optimization status: {status}")
    model.dispose()
    return RuntimeError



# # Sample data (very basic)
# data = {
#     'valuations': [[1, 1, 3, 4, 0]],
#     'm' : 5,
#     'c_types' : [[0, 0, 1], [0, 1, 0], [1, 0, 0], [0,0,1],[0,0,1]],
#     'maxes' : [0, 1, 2],
#     'c_times':[[]],
#     'etas':[[[0.3, 0.5, -0.2, 0, 1], [0.2, 0.3, 0, 0, 1], [-1, 2, 1, 0, 2], [-2, 4, 2, 1, 1], [3, 1, 0.4, -0.5, 1]]],
#     'budgets' : [3],
#     'min_courses': 2,
# }
# prices = [1, 2, 3, 2, 1]
# j = 0

# print("Selected Courses: ", compute_demand(prices, data, j))

# # Number of iterations
# num_iterations = 5

# # Create an empty 2D array
# courses = np.empty((0, 5), dtype=int)

# # Iterate and stack arrays vertically
# for _ in range(num_iterations):
#     courses = np.vstack((courses, compute_demand(prices, data, j)))

# print("Courses:\n", courses)

def isValidTime(schedule, c_time) :
    return np.sum((schedule & c_time)) == 0

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
    if np.sum(bundle[0] & bundle[1]) > 0 :
        return False
    if np.argmax(c_types[bundle[0]]) == np.argmax([bundle[1]]) and count_types[np.argmax(c_types[bundle[0]])] + 2 > maxes[np.argmax(c_types[bundle[0]])] :
        return False
    return True

def compute_demand(prices, data, j) :

    m = data['m']
    valuations = np.array(data['valuations'][j])
    etas = data['etas']
    budget = data['budgets'][j]
    c_types = data['c_types'][j]
    c_times = data['c_times']
    maxes = data['maxes'][j]

    count_types = np.zeros(data['t'])
    schedule = np.zeros(shape=(len(c_times), len(c_times[0])))

    # Calculate the ratios
    ratios = valuations / np.array(prices)

    # Get the indices that would sort the ratios in descending order
    sorted_indices = np.argsort(ratios)[::-1]

    x = np.zeros(m)

    t = []
    t_utilities = np.array([])
    t_prices = np.array([])
    for i in range(m) :
        for k in range(i) :
            if etas[j][k][i] != 0 :
                # Add tuple (i, k) to t (for bundles)
                t.append((i, k))
                t_utilities = np.append(t_utilities, valuations[k] + valuations[i] + etas[j][k][i])
                t_prices = np.append(t_prices, prices[i] + prices[k])

    t_ratios = t_utilities / t_prices
    t_sorted_indices = np.argsort(t_ratios)[::-1]
    taken_course = np.zeros(m)

    while budget > 0 :

        # If best singleton has been used in a taken bundle already, or if best bundle has been used in a taken singleton already
        best_singleton_index = sorted_indices[0] if len(sorted_indices) > 0 else -1

        best_bundle_index = t_sorted_indices[0] if len(t_sorted_indices) > 0 else -1
        (best_bundle_index_1, best_bundle_index_2) = t[best_bundle_index] if best_bundle_index != -1 else (-1, -1)

        if best_singleton_index == -1 :
            break

        while (taken_course[best_singleton_index] == 1 or not isValidTime(schedule, c_times[best_singleton_index]) or not isValidType(count_types, c_types[best_singleton_index], maxes)) :
            sorted_indices = np.delete(sorted_indices, 0)
            if len(sorted_indices) == 0 :
                break
            best_singleton_index = sorted_indices[0]
        
        if len(sorted_indices) == 0 :
            break
            
        while best_bundle_index != -1 and (taken_course[best_bundle_index_1] == 1 or taken_course[best_bundle_index_2] == 1 or not isValidBundle(schedule, c_times, count_types, c_types, maxes, t[best_bundle_index])) :
            t_sorted_indices = np.delete(t_sorted_indices, 0)
            best_bundle_index = t_sorted_indices[0] if len(t_sorted_indices) > 0 else -1
            (best_bundle_index_1, best_bundle_index_2) = t[best_bundle_index] if best_bundle_index != -1 else (-1, -1)

        # If best bundle is preferred to best singleton
        if len(t_sorted_indices) > 0 and t_ratios[t_sorted_indices[0]] > ratios[sorted_indices[0]] :
            if t_prices[t_sorted_indices[0]] <= budget :
                i = int(t[t_sorted_indices[0]][0])
                k = int(t[t_sorted_indices[0]][1])
                x[i] = 1
                x[k] = 1
                budget -= t_prices[t_sorted_indices[0]]
                t_sorted_indices = np.delete(t_sorted_indices, 0)
                taken_course[i] = 1
                taken_course[k] = 1

                # Adding bundle to schedule
                schedule = schedule | c_times[i] | c_times[k]

                # Adding course types to count_types
                count_types[np.argmax(c_types[i])] += 1
                count_types[np.argmax(c_types[k])] += 1
            else :
                i = int(t[t_sorted_indices[0]][0])
                k = int(t[t_sorted_indices[0]][1])
                x[i] = budget / t_prices[t_sorted_indices[0]]
                x[k] = budget / t_prices[t_sorted_indices[0]]
                budget = 0

        # If best singleton is preferred to best bundle
        else :
            if prices[sorted_indices[0]] <= budget :
                x[sorted_indices[0]] = 1
                budget -= prices[sorted_indices[0]]
                taken_course[sorted_indices[0]] = 1
                sorted_indices = np.delete(sorted_indices, 0)

                # Adding singleton to schedule
                schedule = schedule | c_times[sorted_indices[0]]

                # Adding course type to count_types
                count_types[np.argmax(c_types[sorted_indices[0]])] += 1
            else :
                x[sorted_indices[0]] = budget / prices[sorted_indices[0]]
                budget = 0

    return x




# # Sample data (very basic)
# data = {
#     'valuations': [[1, 1, 3, 4, 0]],
#     'm' : 5,
#     'c_types' : [[0, 0, 1], [0, 1, 0], [1, 0, 0], [0,0,1],[0,0,1]],
#     'maxes' : [0, 1, 2],
#     'c_times':[[]],
#     'etas':[[[ 0.,          9.32499788,  0.08150192,  5.96131375, -0.37370232], 
#              [ 0.,          0.,         -0.22510998, -7.60114388,  9.47311775],
#             [ 0.,          0.,          0.,         -3.01725857,  4.14200983],
#             [ 0.,          0.,          0.,          0.,          5.40094205],
#             [ 0.,          0.,          0.,          0.,          0.        ]]],
#     'budgets' : [3],
#     'min_courses': 2,
# }
# prices = [1, 2, 3, 2, 1]
# j = 0

# print("Demand: ", compute_demand(prices, data, j))
# print("Budgets:", (data['budgets']))