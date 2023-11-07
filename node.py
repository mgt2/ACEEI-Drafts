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
    seats = np.array([])

    def create(self, prices, seats, data) :
        self.prices = prices
        self.seats = seats
        self.data = data
        self.courses = np.array([])
        for i in range(self.data['n']) :
            self.courses = np.append(self.courses, compute_demand(self.prices, self.data, i))
        return
    
    def calculate_demand(self) :
        self.courses = np.array([])
        for i in range(self.data['n']) :
            self.courses = np.append(self.courses, compute_demand(self.prices, self.data, i))
        self.demand = np.sum(self.courses, axis=0)
        return self.demand
    
    def score(self) :
        self.courses = np.array([])
        for i in range(self.data['n']) :
            self.courses = np.append(self.courses, compute_demand(self.prices, self.data, i))
        
        self.demand = np.sum(self.courses, axis=0)
        clearing_error = np.where(self.prices > 0, self.demand - self.seats, np.maximum(0, self.demand - self.seats))
        return np.linalg.norm(clearing_error)
