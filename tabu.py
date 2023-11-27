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

 

def tabu (data, bound, seats, max_runs=100, max_iters=1000) :
    m = data['m']
    k = data['k']
    t = data['t']
    q = np.array([])
    start_prices = random_start_point(m, k)
    curnode = Node()
    curnode.create(start_prices, seats, data)
    bestnode = curnode
    best_score = curnode.score()

    with open('draft_output.txt', 'w') as file:
        file.write("Entering loop! ")
        print("Entering loop!")
        while (best_score > bound or max_runs > 0) and max_iters > 0:
            q = np.append(q, curnode)
            if (len(q) == t) :
                q = q[1:]
            file.write("Finding neighbors! ")
            print("Finding neighbors")

            n, scores = neighbors(curnode, seats)

            file.write(f"Neighbors found! ")
            print("Neighbors found!")

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

                file.write("Score improved! {best_score}\n")
                print("New score: ", best_score)
            elif best_score < bound :
                max_runs -= 1
                file.write("Max runs remaining: {max_runs}")
                print("Max runs remaining: ", max_runs)
            max_iters -=1
            file.write("Max iters remaining: {max_iters}\n\n")
            print("Max iters remaining: ", max_iters)
        
    return bestnode