import numpy as np
import random
import decimal

courses = [] # courses[i] contains a tuple(starttime, endtime)
prices = [] # Cost of each course
preferences = [] # preferences[i][j] represents student i's jth choice.  Courses are labeled 1 through m.
highest_available = [] # highest_available[i] represents student i's j-th choice, which is their favorite remaining option.
q = [] # q[i] represents the number of seats in course i
psi = [] # psi[i] records student i's current schedule times, to ensure there will be no conflicts
x = [] # x[i][j] = True if course j assigned to student i, False otherwise
b = [] # b[i] is budget of student i
numcourses = [] # numcourses[i] represents the number of courses student i is enrolled in.

# Randomly assigns varying budgets to each student.
def assign_budgets (N, k, b) :
    beta = min(1/N, 1/(k-1))
    for i in range(len(b)) :
        b[i] = random.randint(100, int((1 + beta) * 100))/100
    return b

# Computes the prices for each course.
def compute_prices (prices) :
    # TODO
    return

# Checks if a course is valid to be drafted by a student
def isValidCourse(coursenum, courses, prices, q, psi, b, studentnum) :
    # SEAT CHECK
    if q[coursenum] == 0 :
        return False
    
    # PRICE CHECK
    elif b[studentnum] - prices[coursenum] < 0 :
        return False 
    
    # TIME CHECK
    (starttime, endtime) = courses[coursenum]
    for (start, end) in psi[studentnum] :
        if start <= starttime and end > starttime :
            return False
        elif start < endtime and end >= endtime :
            return False
    
    return True

# Executes a full round of allocations
def execute_round(courses, prices, preferences, highest_available, q, psi, x, b, k) :
    for i in range(len(b)) : # for each student
        while numcourses[i] < k and highest_available[i] < len(preferences[0]) :
            if isValidCourse(preferences[highest_available[i]], courses, prices, q, psi, b, i) :
                q[preferences[highest_available[i]]] -= 1
                b[i] -= prices[preferences[highest_available[i]]]
                x[i][preferences[highest_available[i]]] = True
                psi[i].append(courses[preferences[highest_available[i]]])
                highest_available[i] += 1
                numcourses[i] += 1
                break
            else :
                highest_available[i] += 1
    return

def draft():
    return