import random
import numpy as np

# Generates n student valuations of m courses
def generate_valuations(n, m) :
    return np.random.rand(n, m)


# Generates n student etas
def generate_etas (n, m) :
    student_eta = np.random.randint(0, m, size=(n, 5))
    eta_values = np.random.rand(n)
    return student_eta, eta_values

# Generates constraints for each course: picks what type of course
# it is, what time it occurs, and how many of each type is allowed (picked between 2 and l)
# minl : lower limit of courses of type i that a student can take
# l : upper limit of courses of type i that a student can take
# t : number of types of courses
def generate_constraints(m, starttime, endtime, minl, l, t) :
    times = np.random.randint(starttime, endtime, size=(1, m))
    types = np.random.randint(0, t, size=(1, m))
    maxes = np.random.randint(minl, l, size= (1, t))

    return np.array([times[0], types[0]]), maxes[0]

# Sample input
# print(generate_constraints(20, 8, 16, 2, 5, 4))
