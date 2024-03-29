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

