import gurobipy
import numpy as np
from generate import *
from demand import *
from node import *
from price_adjustment import *
from tabu import *

# gurobipy.setParam("TokenFile", "gurobi.lic")
# model = gurobipy.model()

# model.dispose()

# GENERATE DATA
n = 250
m = 50
l = 5
k = 5
seats = np.full(m, 27) # as done in Othman paper

# valuations = generate_valuations(n, m, l)
# budgets = generate_budgets(n, l)
# etas = generate_etas(n, m)

class_days = np.array([[1, 0, 1, 0, 0], [0,1,0,1,0], [0,0,0,0,1], [1,1,1,1,0], [1,1,1,1,1]])
class_times = [8.5, 9, 9.5, 10, 11, 12.5, 13.5, 14.5, 15, 16.5, 19.5]
# c_times, c_types, maxes = generate_constraints(m, class_days, class_times, minl=1, l=l, t=5)

data = {
    'n': n,
    'm': m,
    'k': k,
    'l': l,
    'minl':1,
    't' : 5,
    'class_days' : class_days,
    'class_times':class_times,
}



indices = np.random.choice(len(class_days), size=m, p=np.array([0.1, 0.2, 0.3, 0.2, 0.2]))

data_struct = get_data_struct(data)

bound = (k * m / 2)**(1/2)

bestnode = tabu(data_struct, bound, seats, 100)

print(bestnode.prices)
