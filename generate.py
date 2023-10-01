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
def generate_constraints(m, class_days, class_times, minl, l, t) :
    times = np.random.randint(0, len(class_times), size=(1, m))[0]
    class_length = np.random.choice([0.833, 1.333, 2.833], size = m, p=[0.5, 0.45, 0.05])
    days = np.random.choice(class_days, size = m, p = [0.4, 0.4, 0.1, 0.07, 0.03])
    tuples = []
    for i in range(len(times)) :
        tuples.append((class_times[times[i]], class_times[times[i]] + class_length[i]))
    
    tuples = np.array(tuples)
    types = np.random.randint(0, t, size=(1, m))[0]
    maxes = np.random.randint(minl, l, size= (1, t))[0]

    return tuples, days, np.array(types), maxes

# Sample input
# class_days = [(1, 3), (2, 4), (5, 0), (1, 2, 3, 4), (1, 2, 3, 4, 5)]
# times = [8.5, 9, 9.5, 10, 11, 12.5, 1.5, 2.5, 3, 3.5, 7.5]
# print(generate_constraints(20, times, 2, 5, 4))
