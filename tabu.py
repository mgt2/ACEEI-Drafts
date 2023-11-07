import numpy as np
from generate import *
from node import *
from price_adjustment import *
import gurobipy

gurobipy.setParam("TokenFile", "gurobi.lic")

def random_start_point(m, k) :
    start_prices = np.random.rand(m) * 100 / k
    return start_prices

def neighbors(curnode, seats, gradientw_prob, data):
    demand = curnode.calculate_demand()
    
    # Calculating gradient
    gradient = np.where(curnode.prices > 0, demand - seats, max(0, demand - seats))

    gradient_neighbors = Node()
    new_prices = curnode.prices - gradient * curnode.prices
    gradient_neighbors.create(new_prices, seats, data)
    
    # Calculating individual adjustment
    individual_adj_neighbors = adjust_prices(curnode, demand, seats, 1e-5)

    return 

 

def tabu (data, bound, seats, max_runs) :
    m = data['m']
    k = data['k']
    t = data['t']
    q = np.array([])
    start_prices = random_start_point(m, k)
    curnode = Node()
    curnode.create(start_prices, seats, data)
    bestnode = curnode

    max_iters = max_runs

    while bestnode.score() > bound and max_iters > 0:
        q = np.append(q, curnode)
        if (len(q) == t) :
            q = q[1:]
        n = neighbors(curnode, seats, 0.5, data)
        while np.isin(n[0], q) :
            if (len(n) > 1) :
                n = n[1:]
                curnode = n[0]
            else :
                n = []
                break
        if curnode.score() < bestnode.score() :
            bestnode = curnode
        else :
            max_iters -= 1
    return bestnode