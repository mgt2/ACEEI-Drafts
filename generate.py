import random
import numpy as np

# Generates n student valuations of m courses
def generate_valuations(n, m, k) :
    return np.random.rand(n, m) / k

# Generates budgets (MAY CHANGE)
def generate_budgets(n, k) :
    return np.random.uniform(1, 1 + min(1/n, 1/(k-1)), size = n)


# Generates n student etas
def generate_etas (n, m) :
    student_eta = np.zeros((n, m, m))
    # Create a random matrix
    for i in range(n) :
        eta_values = np.random.uniform(-1, 1, size=(m, m))
        np.fill_diagonal(eta_values, 0)
        student_eta[i] = np.triu(eta_values)

    return student_eta

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

# Generates m courses
def generate_courses(m, class_days, class_times, minl, l, t) :
    times, days, types, _ = generate_constraints(m, class_days, class_times, minl, l, t)
    courses = []
    for i in range(len(times)) :
        course = {
            'time' : times[i],
            'days' : days[i],
            'type' : types[i],
            'price' : 0
        }
        courses.append(course)
    
    return np.array(courses)

