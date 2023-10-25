import numpy as np
from generate import *
import gurobipy

gurobipy.setParam("TokenFile", "gurobi.lic")

class Node :

    score = 2 ** 64
    courses = np.array([])
    demand = 0
    prices = np.array([])
    
    def create(self, prices, potential_courses) :
        self.courses = potential_courses
        self.prices = prices
        return
    
    def calculate_demand(self) :
        return self.demand
    
    def score(self) :
        return
