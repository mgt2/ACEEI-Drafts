import numpy as np
import random
import decimal
import Integer
from scipy.optimize import minimize


courses = [] # courses[i] contains a tuple(starttime, endtime)
prices = [] # Cost of each course
preferences = [] # preferences[i][j] represents student i's jth choice.  Courses are labeled 1 through m.
highest_available = [] # highest_available[i] represents student i's j-th choice, which is their favorite remaining option.
q = [] # q[i] represents the number of seats in course i
psi = [] # psi[i] records student i's current schedule times, to ensure there will be no conflicts
x = [] # x[i][j] = True if course j assigned to student i, False otherwise
b = [] # b[i] is budget of student i
numcourses = [] # numcourses[i] represents the number of courses student i is enrolled in.
valuations = [] # valuations[i][j] is student i's valuation of course j.
course_combinations = []

# Computes size of array (distance formula)
def dist (list) :
    sum = 0
    for el in list :
        sum += el **2
    return np.sqrt(sum)

# Randomly assigns varying budgets to each student.
def assign_budgets (N, k, b) :
    beta = min(1/N, 1/(k-1))
    for i in range(len(b)) :
        b[i] = random.randint(100, int((1 + beta) * 100))/100
    return b

# Extracts list of courses which are stored in a tuple of variable length
def extract_courses (course_tuple) :
    result_array = []
    for item in course_tuple:
        result_array.append(item)
    
    return result_array

# Returns True if student can afford their schedule, False otherwise
def isValidSchedule(budget, prices, course_tuple) :
    courses = extract_courses(course_tuple)
    sum = 0
    for course in courses:
        sum += prices[course]
        if budget < sum :
            return False
    return True


# Returns would-be allocations if there were no capacities
def get_allocations(u, p, b) :
    a = np.zeros(len(b), len(p))
    for i in range(len(b)):
        preferred = np.argmax(u[i])
        while not isValidSchedule(b[i], prices, course_combinations[preferred]) or u[i][preferred] == Integer.MIN_INT: 
            u[i][preferred] = Integer.MIN_INT
            preferred = np.argmax(u[i])
        if u[i][preferred] < 0 : # In this case, there are no valid schedules which student i likes.  Will handle this case later.
            return RuntimeError
        else :
            courses = extract_courses(course_combinations[preferred])
            for course in courses :
                a[i][course] += 1
    return a

# Calculates excess demand
def excess_demand (utilities, seats, prices,  budgets) :
    z = []
    a = get_allocations(utilities, prices, budgets)
    for j in range(len(seats)) :
        sum = 0
        for i in range(len(budgets)) :
            sum += a[i][j]
        z.append(sum - seats[j])
    return z

# Calculates clipped excess demand
def clipped_excess_demand(u, c, p ,b) :
    z = excess_demand(u, c, p, b)
    z_tilde = []
    for j in range(len(z)) :
        if prices[j] == 0:
            z_tilde.append(max(0, z[j]))
        else :
            z_tilde.append(z[j])
    return z_tilde


# Computes the prices for each course.
# def compute_prices (prices) :
#     # TODO
#     return

# # Checks if a course is valid to be drafted by a student
# def isValidCourse(coursenum, courses, prices, q, psi, b, studentnum) :
#     # SEAT CHECK
#     if q[coursenum] == 0 :
#         return False
    
#     # PRICE CHECK
#     elif b[studentnum] - prices[coursenum] < 0 :
#         return False 
    
#     # TIME CHECK
#     (starttime, endtime) = courses[coursenum]
#     for (start, end) in psi[studentnum] :
#         if start <= starttime and end > starttime :
#             return False
#         elif start < endtime and end >= endtime :
#             return False
    
#     return True

# # Executes a full round of allocations
# def execute_round(courses, prices, preferences, highest_available, q, psi, x, b, k) :
#     for i in range(len(b)) : # for each student
#         while numcourses[i] < k and highest_available[i] < len(preferences[0]) :
#             if isValidCourse(preferences[highest_available[i]], courses, prices, q, psi, b, i) :
#                 q[preferences[highest_available[i]]] -= 1
#                 b[i] -= prices[preferences[highest_available[i]]]
#                 x[i][preferences[highest_available[i]]] = True
#                 psi[i].append(courses[preferences[highest_available[i]]])
#                 highest_available[i] += 1
#                 numcourses[i] += 1
#                 break
#             else :
#                 highest_available[i] += 1
#     return

def allocation_constraint_ef_tb(u, p, b) :
    return

def allocation_constraint_contested_ef_tb(u, p, b) :
    return

def find_budget_perturbation(u, c, b0, epsilon, t, p):
    # Use a numerical optimization library like SciPy to find budgets that minimize the error
    constraints = [
        {'type': 'ineq', 'fun': lambda b: np.linalg.norm(b - b0, np.inf) - epsilon},
    ]
    if t == 1:
        constraints.append({'type': 'eq', 'fun': lambda b: allocation_constraint_ef_tb(u, p, b)})
    elif t == 2:
        constraints.append({'type': 'eq', 'fun': lambda b: allocation_constraint_contested_ef_tb(u, p, b)})

    result = minimize(lambda b: clipped_excess_demand(u, c, p, b), b0, constraints=constraints)
    return result.x

def find_a_ceei(u, c, b0, delta, epsilon, t):
    p = np.zeros(len(c))
    while True:
        b = find_budget_perturbation(u, c, b0, epsilon, t, p)
        z = clipped_excess_demand(u, c, p, b)
        if np.linalg.norm(z, 2) == 0:
            return p, b
        else:
            p += delta * z

# Performs epsilon budget perturbation
def epsilon_budgets(m, N, u, c, b_0, delta, epsilon, t, prices, b) :
    z_tilde = clipped_excess_demand(u, c, prices, b)
    if dist(z_tilde) == 0:
        return prices, b
    
    # PICK BUDGETS
    # END BUDGET PICKING

    prices += delta * z_tilde
    return epsilon_budgets(m, N, u, c, b_0, delta, epsilon, t, prices, b)

# Runs the full A-CEEI Draft
def draft(m, N, u, c, b_0, delta, epsilon, t):
    prices = np.zeroes(m)

    return epsilon_budgets(m, N, u, c, b_0, delta, epsilon, t, prices, b_0)

# https://arxiv.org/pdf/2305.11406.pdf for better way of doing this