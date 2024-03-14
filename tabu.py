import numpy as np
from generate import *
from node import *
from price_adjustment import *
import gurobipy
from tqdm import tqdm

gurobipy.setParam("TokenFile", "gurobi.lic")


def addToStash(nodestash, q, n, scores) :
    # nodes = []
    # nscores = []
    # for i in range(len(n)):
    #     ndemand = n[i].get_demand()
    #     if not any(np.array_equal(row, ndemand) for row in q) :
    #         nodes.append(n[i])
    #         nscores.append(scores[i])
    # for i in range(len(nodestash)):
    #     ndemand = nodes[0].get_demand()
        
    # nodestash = np.append(nodestash, n)
    # return nodestash
    return []

def random_start_point(m, maxbudg) :
    start_prices = np.random.rand(m) * maxbudg
    return start_prices

def contains(node, nodelist) :
    for n in nodelist :
        if n.isEqual(node) :
            return True
    return False

def neighbors(curnode, seats):
    demand = curnode.get_demand()
    
    # Calculating gradient
    gradient = np.where(curnode.prices > 0, demand - seats, np.maximum(0, demand - seats))
    max_change_vals = np.array([10, 5, 1, 0.5, 0.1])
    gradient_neighbors = adjust_gradient_prices(curnode, gradient, max_change_vals, seats)
    
    #Calculating individual adjustment
    individual_adj_neighbors = adjust_prices(curnode, demand, seats, 1e-5)
    # print(individual_adj_neighbors)
    neighbors = np.append(gradient_neighbors, individual_adj_neighbors)
    # neighbors = gradient_neighbors
    # Extract scores from nodes and create an array
    scores = np.array([node.get_score() for node in neighbors])
    #print(scores)
    # Get indices that would sort the scores
    sorted_indices = np.argsort(scores)

    # Sort neighbors based on the sorted indices
    sorted_neighbors = neighbors[sorted_indices]
    sorted_scores = scores[sorted_indices]

    return sorted_neighbors, sorted_scores

 

def tabu (data, bound, seats, max_runs=100, max_iters=1000, q_size=100) :
    m = data['m']
    k = data['k']
    q = np.array([])
    start_prices = random_start_point(m, np.max(data['budgets'])/k)
    curnode = Node()
    curnode.create(start_prices, seats, data)
    bestnode = curnode
    best_score = curnode.get_score()

    with open('draft_output.txt', 'w') as file:
        file.write("Iteration\tMax Runs Remaining\tBest Neighbor Score\t\tBest Score\n")
        file.write("--------------------------------------------------------------------------------\n")
        for i in tqdm(range(max_iters), desc="Tabu Processing", unit="iteration"):
            if (best_score < bound and max_runs <= 0) :
                break

            file.flush()

            ndemand = curnode.get_demand()
            if not any(np.array_equal(row, ndemand) for row in q) :
                q = np.append(q, ndemand)

            if (len(q) >= q_size) :
                q = q[1:]
                # qscore = qscore[1:]

            n, scores = neighbors(curnode, seats)
            best_neighbor_score = scores[0]
            curnode = n[0]
            found = False

            while len(n) > 0 and not found :
                ndemand = n[0].get_demand()
                if not any(np.array_equal(row, ndemand) for row in q) :
                    found = True

                elif (len(n) > 1) :
                    curnode = n[1]
                    best_neighbor_score = scores[1]
                    n = n[1:]
                    scores = scores[1:]

                else :
                    n = []
                    start_prices = random_start_point(m, np.max(data['budgets'])/k)
                    curnode = Node()
                    curnode.create(start_prices, seats, data)
                    break

            if best_neighbor_score < best_score :
                bestnode = curnode
                best_score = curnode.get_score()

            if best_score < bound :
                max_runs -= 1

            file.write("\t" + str(i) + "\t\t\t\t" + str(max_runs) + "\t\t\t" + str(best_neighbor_score) + "\t\t" + str(best_score) + "\n")

            if best_score <= 0 :
                file.write("\n Perfect score! \n")
                break

        file.write("\nScore: " + str(best_score) + "\n")
        file.write("Prices: \n")
        for price in bestnode.get_prices() :
            file.write(str(price) + "\n")
        return bestnode.get_prices()
    #     file.write("\nQ-size: " + str(q_size))
    #     best_score = 2 ** 64 - 1
    #     opt_prices = np.zeros(m)
    #     for _ in tqdm(range(max_iters), desc="Tabu Processing", unit="iteration"):
    #         prices = random_start_point(m, np.min(data['budgets']/k))
    #         # prices = adjust_prices_half(prices, np.max(data['budgets']), 0.1, seats, data)
    #         curnode = Node()
    #         curnode.create(prices, seats, data)
    #         searcherror = curnode.get_score()
    #         q = np.array([])
    #         nodestash = np.array([])
    #         c = 0
    #         prev_score = searcherror
    #         while c < 5 and best_score > 0.0:
    #             n, scores = neighbors(curnode, seats) 
    #             foundnextstep = False
    #             while not foundnextstep and len(n) > 0 :
    #                 nprice = n[0].get_prices()
    #                 nscore = scores[0] # Paper uses demands instead of error: is this a problem?
    #                 ndemand = np.array(n[0].get_demand())
    #                 #if not np.isin(nscore, q) :
    #                 n = n[1:]
    #                 scores = scores[1:]
    #                 if not any(np.array_equal(row, ndemand) for row in q) :
    #                     foundnextstep = True
    #                     if prev_score <= bound :
    #                         nodestash = addToStash(nodestash, q, n, scores)
    #             prev_score = nscore
    #             if len(n) == 0 :
    #                 c = 5
    #                 print("Breaking...")
    #                 break
    #             else :
    #                 curnode = n[0]
    #                 prices = nprice
    #                 q = np.append(q, ndemand)
    #                 if nscore <= searcherror :
    #                     searcherror = nscore
    #                     c = 0
    #                     file.write("Score is now " + str(nscore) + "\n")
    #                     file.flush()
    #                 else :
    #                     c += 1
    #                     file.write("Score is now " + str(nscore) + "\n")
    #                     file.flush()
    #                 if nscore < best_score :
    #                     best_score = nscore
    #                     opt_prices = prices
    #                     file.write("Best score updated! Score is now " + str(best_score) + "\n")
    #                     file.flush()
    #                 if nscore == 0.0 :
    #                     file.write("Perfect score!")
    #                     file.flush()
    #                     c = 5
    #     file.write("Prices: \n")
    #     for price in opt_prices :
    #         file.write(str(price) + "\n")
    #     file.write("Score: " + str(best_score) + "\n\n")

    #     #prices = adjust_prices_half(opt_prices, np.max(data['budgets']), 0.1, seats, data)


    # return opt_prices