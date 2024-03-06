import numpy as np
from generate import *
from node import *
from price_adjustment import *
import gurobipy
from tqdm import tqdm
import multiprocessing

gurobipy.setParam("TokenFile", "gurobi.lic")

if __name__ == '__main__':
    gurobipy.setParam("TokenFile", "gurobi.lic")
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

        gradient_data = [(curnode, gradient, max_change_val, seats) for max_change_val in max_change_vals]
        num_cores = min(multiprocessing.cpu_count(), 5)
        pool = multiprocessing.Pool(processes=num_cores)

        gradient_neighbors = pool.map(adjust_gradient_prices, gradient_data)

        pool.close()
        pool.join()
        neighbors = np.array(gradient_neighbors)
        
        # Finding individual neighbors
        def get_individual_neighbors() :
            minprice = 1000 # Larger than any price should be
            oversubscribed = np.where(demand - seats > 0, True, False)
            oversubscribed_indices = np.where(oversubscribed)[0]

            # If there are more than 50 oversubscribed courses, randomly choose 50 of them
            if len(oversubscribed_indices) > 50 :
                selected_indices = np.random.choice(len(oversubscribed_indices), size=50, replace=False)
                oversubscribed_indices = oversubscribed_indices[selected_indices]

            neighbors = np.array([])

            for j in oversubscribed_indices :
                minprice = 1000
                new_node = Node()
                new_node.create(curnode.prices.copy(), seats, curnode.data)
        
                budget_indices = np.where(curnode.courses[:, j], True, False)
                budget_indices = np.where(budget_indices)[0]

                individual_data = [(curnode, 1e-5, j, student_index) for student_index in budget_indices]

                num_cores = multiprocessing.cpu_count()
                pool = multiprocessing.Pool(processes=num_cores)

                individual_prices = pool.map(remove_student, individual_data)

                pool.close()
                pool.join()

                minprice = np.min(np.array(individual_prices))
                new_node.prices[j] += minprice
                new_node.setDemandCalc(False)
                neighbors = np.append(neighbors, new_node)
            return neighbors

        individual_neighbors = adjust_prices(curnode, demand, seats, 1e-5)
        #individual_neighbors = get_individual_neighbors()
        neighbors = np.append(individual_neighbors, gradient_neighbors)
        # neighbors = gradient_neighbors
        # Extract scores from nodes and create an array
        scores = np.array([node.score() for node in neighbors])
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
            file.write("\nQ-size: " + str(q_size))
            best_score = 2 ** 64 - 1
            opt_prices = np.zeros(m)
            for _ in tqdm(range(max_iters), desc="Tabu Processing", unit="iteration"):
                prices = random_start_point(m, np.max(data['budgets']))
                prices = adjust_prices_half(prices, np.max(data['budgets']), 0.1, seats, data)
                curnode = Node()
                curnode.create(prices, seats, data)
                searcherror = curnode.score()
                q = np.array([])
                c = 0
                while c < 5 :
                    n, scores = neighbors(curnode, seats) 
                    foundnextstep = False
                    while not foundnextstep and len(n) > 0 :
                        nprice = n[0].get_prices()
                        nscore = scores[0] # Paper uses demands instead of error: is this a problem?
                        ndemand = np.array(n[0].get_demand())
                        #if not np.isin(nscore, q) :
                        if not any(np.array_equal(row, ndemand) for row in q) :
                            foundnextstep = True
                        n = n[1:]
                        scores = scores[1:]
                    if len(n) == 0 :
                        c = 5
                        print("Breaking...")
                        break
                    else :
                        curnode = n[0]
                        prices = nprice
                        q = np.append(q, ndemand)
                        if nscore <= searcherror :
                            searcherror = nscore
                            c = 0
                            file.write("Score is now " + str(nscore) + "\n")
                            file.flush()
                        else :
                            c += 1
                            file.write("Score is now " + str(nscore) + "\n")
                            file.flush()
                        if nscore < best_score :
                            best_score = nscore
                            opt_prices = prices
                            file.write("Best score updated! Score is now " + str(best_score) + "\n")
                            file.flush()
            file.write("Prices: \n")
            for price in opt_prices :
                file.write(str(price) + "\n")
            file.write("Score: " + str(best_score))
        return opt_prices
    # GENERATE DATA
    n = 250
    m = 50
    l = 5
    k = 5
    seats = np.full(m, 27) # as done in Othman paper


    # valuations = generate_valuations(n, m, l)
    # budgets = generate_budgets(n, l)
    # etas = generate_etas(n, m)

    class_days = np.array([[1, 0, 1, 0, 0], [0,1,0,1,0], [0,0,0,0,1], [1,1,1,1,0], [1,1,1,1,1]])
    class_times = [8.5, 9, 9.5, 10, 11, 12.5, 13.5, 14.5, 15, 16.5, 19.5]
    # c_times, c_types, maxes = generate_constraints(m, class_days, class_times, minl=1, l=l, t=5)

    data = {
        'n': n,
        'm': m,
        'k': k,
        'l': l,
        'minl':0,
        't' : 5,
        'class_days' : class_days,
        'class_times':class_times,
    }



    #indices = np.random.choice(len(class_days), size=m, p=np.array([0.1, 0.2, 0.3, 0.2, 0.2]))

    data_struct = get_data_struct(data)

    bound = (k * m / 2)**(1/2)

    opt_prices = tabu(data_struct, bound, seats, 3, 11, q_size=5)

    bestnode = Node()
    bestnode.create(opt_prices, seats, data_struct)
    print("Final prices: ", opt_prices)
    print("Score: ", bestnode.score())

    new_prices = adjust_prices_half(opt_prices, np.max(data_struct['budgets']), 0.1, seats, data_struct)
    bestnode.prices = new_prices
    bestnode.setDemandCalc(False)
    courses = reduce_undersubscription(bestnode, seats)
    print("Adjusted prices: [")
    for price in bestnode.prices :
        print(price)
    print("]")
    print("Adjusted Score: ", bestnode.score())
    print("Final Allocations : \n")
    for student in courses:
        print(student)

