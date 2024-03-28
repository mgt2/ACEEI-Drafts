import numpy as np
from generate import *
from node import *
from price_adjustment import *
import gurobipy
from tqdm import tqdm

gurobipy.setParam("TokenFile", "gurobi.lic")


def addToStash(nodestash, q, n, scores) :
    nodes = np.array([])
    nscores = np.array([])
    stash_demands = np.array([])

    for node in nodestash :
        stash_demands = np.append(stash_demands, node.get_demand())
    for i in range(len(n)):
        ndemand = n[i].get_demand()
        if any(np.array_equal(row, ndemand) for row in q) or any(np.array_equal(row, ndemand) for row in stash_demands):
            continue
        else:
            nodes = np.append(nodes, n[i])
            nscores = np.append(nscores, scores[i])
    for i in range(len(nodestash)):
        if nscores[0] < nodestash[i].get_score() :
            nodestash = np.insert(nodestash, i, nodes[0])
            if len(nodes) == 1 :
                nodes = np.array([])
                nscores = np.array([])
                break
            else :
                nscores = nscores[1:]
                nodes = nodes[1:]
    nodestash = np.append(nodestash, n)
    return nodestash

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
    max_change_vals = np.array([100, 10, 5, 1, 0.5, 0.1])
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
    # qscore = np.array([])
    # start_prices = random_start_point(m, np.max(data['budgets']))
    # curnode = Node()
    # curnode.create(start_prices, seats, data)
    # bestnode = curnode
    # best_score = curnode.score()
    # curscore = best_score

    with open('draft_output.txt', 'w') as file:
        # file.write("Entering loop! ")
        # print("Entering loop!")
        # print("Q-size:", q_size)
        # for _ in tqdm(range(max_iters), desc="Tabu Processing", unit="iteration"):
        #     file.flush()
        #     while (best_score > bound or max_runs > 0) and max_iters > 0:
        #         if not np.isin(curscore, qscore) :
        #             q = np.append(q, curnode)
        #             qscore = np.append(qscore, curscore)
        #         if (len(q) >= q_size) :
        #             q = q[1:]
        #             qscore = qscore[1:]
        #             print("Evicting...")
        #         file.write("Finding neighbors! ")
        #         print("Finding neighbors")

        #         n, scores = neighbors(curnode, seats)

        #         print(scores)

        #         file.write(f"Neighbors found! ")
        #         print("Neighbors found!")

        #         best_neighbor_score = scores[0]
        #         print(n)
        #         print(q)
        #         curnode = n[0]
        #         # while contains(n[0], q) :
        #         while np.isin(scores[0], qscore) :
        #             if (len(n) > 1) :
        #                 curnode = n[1]
        #                 best_neighbor_score = scores[1]
        #                 n = n[1:]
        #                 scores = scores[1:]
        #             else :
        #                 n = []
        #                 start_prices = random_start_point(m, np.max(data['budgets']))
        #                 curnode = Node()
        #                 curnode.create(start_prices, seats, data)
        #                 curscore = curnode.score()
        #                 break
        #         curscore = best_neighbor_score
        #         print("Best node: ", best_score)
        #         print("Best neighbor score: ", best_neighbor_score)
        #         print("Bound to beat: ", bound)
        #         if best_neighbor_score < best_score :
        #             bestnode = curnode
        #             best_score = best_neighbor_score

        #             file.write("Score improved! " + str(best_score))
        #             print("New score: ", best_score)
        #         elif best_score < bound :
        #             max_runs -= 1
        #             file.write("Max runs remaining: " + str(max_runs))
        #             print("Max runs remaining: ", max_runs)
        #         if best_score <= 0 :
        #             file.write("\n Perfect score! \n")
        #             break
        #         max_iters -=1
        #         file.write("Max iters remaining: " + str(max_iters) + "\n\n")
        #         print("Max iters remaining: ", max_iters)
        # print("Q-size:", q_size)
        # file.write("\nScore: " + str(best_score) + "\n")
        # return bestnode.prices
        best_score = 2 ** 64 - 1
        opt_prices = np.zeros(m)
        file.write("Iteration\tSubiteration Number\tBest Neighbor Score\t\tBest Score\n")
        file.write("---------------------------------------------------------------------------------\n")
        for i in tqdm(range(max_iters), desc="Tabu Processing", unit="iteration"):
            prices = random_start_point(m, np.max(data['budgets']/k))
            # prices = adjust_prices_half(prices, np.max(data['budgets']), 0.1, seats, data)
            curnode = Node()
            curnode.create(prices, seats, data)
            searcherror = curnode.get_score()
            q = np.array([])
            # nodestash = np.array([])
            c = 0
            # prev_score = searcherror
            while c < 5 and best_score > 0.0:
                n, scores = neighbors(curnode, seats) 
                foundnextstep = False
                while not foundnextstep and len(n) > 0 :
                    nprice = n[0].get_prices()
                    nscore = scores[0] # Paper uses demands instead of error: is this a problem?
                    ndemand = np.array(n[0].get_demand())
                    #if not np.isin(nscore, q) :
                    n = n[1:]
                    scores = scores[1:]
                    if not any(np.array_equal(row, ndemand) for row in q) :
                        foundnextstep = True
                    #     if prev_score <= bound :
                    #         nodestash = addToStash(nodestash, q, n, scores)
                # prev_score = nscore
                if len(n) == 0 :
                    c = 5
                    # print("Breaking...")
                    # break
                else :
                    curnode = n[0]
                    prices = nprice
                    q = np.append(q, ndemand)
                    if nscore < searcherror :
                        searcherror = nscore
                        c = 0
                        # file.write("Score is now " + str(nscore) + "\n")
                        # file.flush()
                    else :
                        c += 1
                        # file.write("Score is now " + str(nscore) + "\n")
                        file.flush()
                    if nscore < best_score :
                        best_score = nscore
                        opt_prices = prices
                        # file.write("Best score updated! Score is now " + str(best_score) + "\n")
                        # file.flush()
                    file.write("\t" + str(i) + "\t\t\t\t" + str(c) + "\t\t\t" + str("{:.7f}".format(nscore)) + "\t\t\t\t" + str("{:.7f}".format(best_score)) + "\n")
                    file.flush()
                    if nscore == 0.0 :
                        file.write("\nPerfect score!")
                        file.flush()
                        c = 5
                # if c == 5 and len(nodestash) > 0:
                #     curnode = nodestash[0]
                #     c = 0
                #     if len(nodestash) >= 2:
                #         nodestash = nodestash[1:]
                #     else :
                #         nodestash = np.array([])

        file.write("\nPrices: \n")
        for price in opt_prices :
            file.write(str(price) + "\n")
        file.write("Score: " + str(best_score) + "\n\n")

        #prices = adjust_prices_half(opt_prices, np.max(data['budgets']), 0.1, seats, data)


    return opt_prices