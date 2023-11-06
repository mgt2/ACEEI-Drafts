import numpy as np
from generate import *
from node import *
from price_adjustment import *
import gurobipy

gurobipy.setParam("TokenFile", "gurobi.lic")

def random_start_point(m, k) :
    start_prices = np.random.rand(m) * 100 / k
    return start_prices

def neighbors(curnode, seats, gradientw_prob):
    demand = curnode.calculate_demand()
    
    # Calculating gradient
    if random.rand() < gradientw_prob :
        gradient = np.where(curnode.prices > 0, demand - seats, max(0, demand - seats))
        return gradient
    
    # Calculating individual adjustment
    individual_adj = adjust_prices(curnode, demand, seats, 1e-5)

    return individual_adj

 

def tabu (data, bound, seats, model=None) :
    model = gurobipy.model()
    m = data['m']
    k = data['k']
    t = data['t']
    q = np.array([])
    curnode = Node.create(random_start_point(m, k), data)
    bestnode = curnode

    while bestnode > bound :
        tabu = np.append(tabu, curnode)
        if (len(tabu) == t) :
            tabu = tabu[1:]
        n = neighbors(curnode, seats, 0.5)
        while np.isin(n[0], q) :
            if (len(n) > 1) :
                n = n[1:]
                curnode = n[0]
            else :
                n = []
                break
        if curnode.score() < bestnode.score() :
            bestnode = curnode
    model.dispose()
    return bestnode