import numpy as np
from generate import *
from node import *
from price_adjustment import *
import gurobipy

gurobipy.setParam("TokenFile", "gurobi.lic")

def random_start_point(m, k) :
    start_prices = np.random.rand(m) * 100 / k
    return start_prices

def neighbors(curnode, seats):
    demand = curnode.calculate_demand()
    
    # Calculating gradient
    gradient = np.where(curnode.prices > 0, demand - seats, np.maximum(0, demand - seats))
    max_change_vals = np.array([10, 5, 1, 0.5, 0.1])
    gradient_neighbors = adjust_gradient_prices(curnode, gradient, max_change_vals, seats)
    
    # Calculating individual adjustment
    individual_adj_neighbors = adjust_prices(curnode, demand, seats, 1e-5)

    neighbors = np.append(gradient_neighbors, individual_adj_neighbors)

    # Extract scores from nodes and create an array
    scores = np.array([node.score() for node in neighbors])

    # Get indices that would sort the scores
    sorted_indices = np.argsort(scores)

    # Sort neighbors based on the sorted indices
    sorted_neighbors = neighbors[sorted_indices]
    sorted_scores = scores[sorted_indices]

    return sorted_neighbors, sorted_scores

 

def tabu (data, bound, seats, max_runs) :
    m = data['m']
    k = data['k']
    t = data['t']
    q = np.array([])
    start_prices = random_start_point(m, k)
    curnode = Node()
    curnode.create(start_prices, seats, data)
    bestnode = curnode
    best_score = curnode.score()

    max_iters = max_runs

    while best_score > bound and max_iters > 0:
        q = np.append(q, curnode)
        if (len(q) == t) :
            q = q[1:]
        print()
        print()
        print()
        print()
        print()
        print("FINDING NEIGHBORS")
        print()
        print()
        print()
        print()
        print()

        n, scores = neighbors(curnode, seats)

        print()
        print()
        print()
        print()
        print()
        print("NEIGHBORS FOUND")
        print()
        print()
        print()
        print()
        print()
        best_neighbor_score = scores[0]
        while np.isin(n[0], q) :
            if (len(n) > 1) :
                n = n[1:]
                scores = scores[1:]
                curnode = n[0]
                best_neighbor_score = scores[0]
            else :
                n = []
                break
        if best_neighbor_score < best_score :
            bestnode = curnode
            best_score = best_neighbor_score
            print()
            print()
            print()
            print()
            print()
            print("SCORE IMPROVED")
            print()
            print()
            print()
            print()
            print()
        else :
            max_iters -= 1
    return bestnode