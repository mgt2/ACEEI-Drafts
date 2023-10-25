import numpy as np
from generate import *
import gurobipy
from demand import compute_demand

gurobipy.setParam("TokenFile", "gurobi.lic")

class Node :

    score = 2 ** 64
    courses = np.array([])
    demand = 0
    prices = np.array([])
    data = {}

    def create(self, prices, data) :
        self.prices = prices
        self.data = data
        return
    
    def calculate_demand(self) :
        for i in range(self.data.n) :
            self.courses = np.append(self.courses, compute_demand(self.prices, self.data, i))
        self.demand = np.sum(self.courses, axis=0)
        return self.demand
    
    def score(self) :
        return
