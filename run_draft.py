import gurobipy as gp
import numpy as np
from generate import *
from demand import *
from node import *
from price_adjustment import *
from tabu import *
import json

# gurobipy.setParam("TokenFile", "gurobi.lic")
# model = gurobipy.model()

# model.dispose()

# # GENERATE DATA
# n = 250
# m = 50
# l = 5
# k = 5
# seats = np.full(m, 27) # as done in Othman paper


# # valuations = generate_valuations(n, m, l)
# # budgets = generate_budgets(n, l)
# # etas = generate_etas(n, m)

# class_days = np.array([[1, 0, 1, 0, 0], [0,1,0,1,0], [0,0,0,0,1], [1,1,1,1,0], [1,1,1,1,1]])
# class_times = [8.5, 9, 9.5, 10, 11, 12.5, 13.5, 14.5, 15, 16.5, 19.5]
# # c_times, c_types, maxes = generate_constraints(m, class_days, class_times, minl=1, l=l, t=5)

# data = {
#     'n': n,
#     'm': m,
#     'k': k,
#     'l': l,
#     'minl':1,
#     't' : 5,
#     'class_days' : class_days,
#     'class_times':class_times,
# }



# #indices = np.random.choice(len(class_days), size=m, p=np.array([0.1, 0.2, 0.3, 0.2, 0.2]))

# data_struct = get_data_struct(data)
file_path = "input_data/small_random/small_1.json"
with open(file_path, "r") as json_file:
    loaded_data = json.load(json_file)
    data_struct = loaded_data

data_struct['valuations'] = np.array(data_struct['valuations'])
data_struct['budgets'] = np.array(data_struct['budgets'])
data_struct['etas'] = np.array(data_struct['etas'])
data_struct['maxes'] = np.array(data_struct['maxes'])
data_struct['c_times'] = np.array(data_struct['c_times'])
data_struct['c_types'] = np.array(data_struct['c_types'])
data_struct['seats'] = np.array(data_struct['seats'])

bound = (k * m / 2)**(1/2)

opt_prices = tabu(data_struct, bound, seats, 10, 10, q_size=5)

bestnode = Node()
bestnode.create(opt_prices, seats, data_struct)
print("Final prices: ", opt_prices)
print("Score: ", bestnode.get_score())

# new_prices = adjust_prices_half(opt_prices, np.max(data_struct['budgets']), 0.1, seats, data_struct)
# bestnode.set_prices(new_prices)
# courses = reduce_undersubscription(bestnode, seats)
# print("Adjusted prices: ", bestnode.prices)
# print("Adjusted Score: ", bestnode.get_score())
print("Final Allocations : \n", bestnode.get_courses())
print("\n\nStudent Valuations: \n", data_struct['valuations'])


# TESTING SCORE
# n = 10
# m = 10
# k = 2
# l = 1
# seats = np.full(m, 2)

# class_days = np.array([[1, 0, 1, 0, 0], [0,1,0,1,0], [0,0,0,0,1], [1,1,1,1,0], [1,1,1,1,1]])
# class_times = [8.5, 9, 9.5, 10, 11, 12.5, 13.5, 14.5, 15, 16.5, 19.5]

# data = {
#     'n': n,
#     'm': m,
#     'k': k,
#     'l': l,
#     'minl':0,
#     't' : 5,
#     'class_days' : class_days,
#     'class_times': class_times,
# }
# data_struct = get_data_struct(data)

# bound = (k * m / 2)**(1/2)
# opt_prices = tabu(data_struct, bound, seats, 10, 10, q_size=5)
# bestnode = Node()
# bestnode.create(opt_prices, seats, data_struct)
# print("Final prices: ", opt_prices)
# print("Score: ", bestnode.score())
# new_prices = adjust_prices_half(opt_prices, np.max(data_struct['budgets']), 0.1, seats, data_struct)
# bestnode.prices = new_prices
# bestnode.setDemandCalc(False)
# courses = reduce_undersubscription(bestnode, seats)
# print("Adjusted prices: ", bestnode.prices)
# print("Adjusted Score: ", bestnode.score())
# print("Final Allocations : \n", courses)




