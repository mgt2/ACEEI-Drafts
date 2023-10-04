import numpy as np
from generate import *
import gurobipy

gurobipy.setParam("TokenFile", "gurobi.lic")

class Node :

    score = 2 ** 64
    courses = np.array([])
    def create(prices, potential_courses) :
        courses = potential_courses
        return
    
    def score() :
        return
