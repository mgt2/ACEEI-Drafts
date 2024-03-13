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
    isDemandComputed = False
    isScoreComputed = False

    def create(self, prices, seats, data) :
        self.prices = prices
        self.seats = seats
        self.data = data
        self.demand = self._calculate_demand()
        return

    def set_prices(self, new_prices) :
        self.prices = new_prices
        self.isDemandComputed = False
        self.isScoreComputed = False
        return
    
    def get_prices(self) :
        return self.prices
    
    def get_courses(self) :
        if not self.isDemandComputed :
            self.courses = np.empty((0, self.data['m']), dtype=int)
            for i in range(self.data['n']) :
                self.courses = np.vstack((self.courses, compute_demand(self.prices, self.data, i)))
        return self.courses
    
    def set_courses(self, courses) :
        self.courses = courses
        return
    
    def isEqual(self, node) :
        if not np.array_equal(self.prices, node.prices) :
            return False
        if not self.score == node.score :
            return False
        if not np.array_equal(self.demand, node.demand) :
            return False
        return True
    
    def _calculate_demand(self) :
        self.courses = np.empty((0, self.data['m']), dtype=int)
        for i in range(self.data['n']) :
            self.courses = np.vstack((self.courses, compute_demand(self.prices, self.data, i)))
        self.demand = np.sum(self.courses, axis=0)
        self.isDemandComputed = True
        return self.demand

    def get_demand(self) :
        if self.isDemandComputed :
            return self.demand
        return self._calculate_demand()
    
    def setDemandCalc(self, val) :
        self.isDemandComputed = val
        return
    
    def _score(self) :
        if not self.isDemandComputed :
            self.courses = np.empty((0, self.data['m']), dtype=int)
            for i in range(self.data['n']) :
                self.courses = np.vstack((self.courses, compute_demand(self.prices, self.data, i)))
        
            self.demand = np.sum(self.courses, axis=0)
        clearing_error = np.where(self.prices > 0, self.demand - self.seats, np.maximum(0, self.demand - self.seats))
        self.score = np.linalg.norm(clearing_error)
        return self.score
    
    def get_score(self) :
        if self.isScoreComputed :
            return self.score
        else :
            self.isScoreComputed = True
            return self._score()
        
    



