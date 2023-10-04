import numpy as np
from generate import *
from node import *
import gurobipy

gurobipy.setParam("TokenFile", "gurobi.lic")

def random_start_point(m, k) :
    start_prices = np.random.rand(m) / k
    return Node.create(start_prices)

def tabu (m, k, bound, t, model=None) :
    model = gurobipy.model()
    q = np.array([])
    curnode = random_start_point(m, k)
    bestnode = curnode

    while bestnode > bound :
        tabu = np.append(tabu, curnode)
        if (len(tabu) == t) :
            tabu = tabu[1:]
        n = neighbors(curnode)
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
    return