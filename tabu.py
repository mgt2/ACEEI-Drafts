import numpy as np
from generate import *
from node import *

def random_start_point(m) :
    start_prices = np.random.rand(m)
    return Node.create(start_prices)

def tabu (m, bound, t) :
    q = np.array([])
    curnode = random_start_point(m)
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
    return