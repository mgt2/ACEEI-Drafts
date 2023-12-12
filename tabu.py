import numpy as np
from generate import *
from node import *
from price_adjustment import *
import gurobipy
from tqdm import tqdm

gurobipy.setParam("TokenFile", "gurobi.lic")

def random_start_point(m, maxbudg) :
    start_prices = np.random.rand(m) * maxbudg
    return start_prices

def contains(node, nodelist) :
    for n in nodelist :
        if n.isEqual(node) :
            return True
    return False

def neighbors(curnode, seats, data):
    demand = curnode.calculate_demand()
    
    # Calculating gradient
    gradient = np.where(curnode.prices > 0, demand - seats, np.maximum(0, demand - seats))
    max_change_vals = np.array([10, 5, 1, 0.5, 0.1])
    gradient_neighbors = adjust_gradient_prices(curnode, gradient, max_change_vals, seats)
    
    #Calculating individual adjustment
    individual_adj_neighbors = adjust_prices(curnode, demand, seats, 1e-5)
    # individual_adj_neighbors = np.array([])
    neighbors = np.append(gradient_neighbors, individual_adj_neighbors)

    # Extract scores from nodes and create an array
    scores = np.array([node.score() for node in neighbors])

    # Get indices that would sort the scores
    sorted_indices = np.argsort(scores)

    # Sort neighbors based on the sorted indices
    sorted_neighbors = neighbors[sorted_indices]
    sorted_scores = scores[sorted_indices]

    return sorted_neighbors, sorted_scores

 

def tabu (data, bound, seats, max_runs=100, max_iters=100, q_size=100) :
    m = data['m']
    k = data['k']
    q = np.array([])
    # qscore = np.array([])
    # start_prices = random_start_point(m, np.max(data['budgets']))
    # curnode = Node()
    # curnode.create(start_prices, seats, data)
    # bestnode = curnode
    # best_score = curnode.score()
    # curscore = best_score

    with open('draft_output.txt', 'w') as file:
        file.write("Entering loop! ")
        print("Entering loop!")
        print("Q-size:", q_size)
        # while (best_score > bound or max_runs > 0) and max_iters > 0:
        #     q = np.append(q, curnode)
        #     qscore = np.append(qscore, curscore)
        #     if (len(q) >= q_size) :
        #         q = q[1:]
        #         qscore = qscore[1:]
        #         print("Evicting...")
        #     file.write("Finding neighbors! ")
        #     print("Finding neighbors")

        #     n, scores = neighbors(curnode, seats)

        #     print(scores)

        #     file.write(f"Neighbors found! ")
        #     print("Neighbors found!")

        #     best_neighbor_score = scores[0]
        #     print(n)
        #     print(q)
        #     curnode = n[0]
        #     # while contains(n[0], q) :
        #     while np.isin(scores[0], qscore) :
        #         print("HERE")
        #         if (len(n) > 1) :
        #             curnode = n[1]
        #             best_neighbor_score = scores[1]
        #             n = n[1:]
        #             scores = scores[1:]
        #         else :
        #             n = []
        #             break
        #     curscore = best_neighbor_score
        #     print("Best node: ", best_score)
        #     print("Best neighbor score: ", best_neighbor_score)
        #     print("Bound to beat: ", bound)
        #     if best_neighbor_score < best_score :
        #         bestnode = curnode
        #         best_score = best_neighbor_score

        #         file.write("Score improved! " + str(best_score))
        #         print("New score: ", best_score)
        #     elif best_score < bound :
        #         max_runs -= 1
        #         file.write("Max runs remaining: " + str(max_runs))
        #         print("Max runs remaining: ", max_runs)
        #     max_iters -=1
        #     file.write("Max iters remaining: " + str(max_iters) + "\n\n")
        #     print("Max iters remaining: ", max_iters)
        # print("Q-size:", q_size)
        # file.write("\nScore: " + str(best_score))
        # file.write("\nQ-size: " + str(q_size))
        best_score = 2 ** 64 - 1
        opt_prices = np.zeros(m)
        for _ in tqdm(range(max_iters), desc="Processing", unit="iteration"):
            prices = random_start_point(m, np.max(data['budgets']))
            curnode = Node()
            curnode.create(prices, seats, data)
            searcherror = curnode.score()
            q = []
            c = 0
            while c < 5 :
                n, scores = neighbors(curnode, seats, data) 
                foundnextstep = False
                while not foundnextstep and len(n) > 0 :
                    nprice = n[0].get_prices()
                    nscore = scores[0] # Paper uses demands instead of error: is this a problem?
                    if not np.isin(scores[0], q) :
                        foundnextstep = True
                    n = n[1:]
                    scores = scores[1:]
                if len(n) == 0 :
                    c = 5
                else :
                    prices = nprice
                    q.append(nscore)
                    if nscore < searcherror :
                        searcherror = nscore
                        c = 0
                    else :
                        c += 1
                    if nscore < best_score :
                        best_score = nscore
                        opt_prices = prices
        file.write("Prices: \n")
        for price in opt_prices :
            file.write(str(price) + "\n")
    return opt_prices