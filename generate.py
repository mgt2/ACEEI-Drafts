import random
import numpy as np
import gurobipy

gurobipy.setParam("TokenFile", "gurobi.lic")

# Generates n student valuations of m courses
def generate_valuations(n, m, budgets) :
    valuations = np.zeros((n, m))
    for i in range(n):
        # Generate random valuations for each course
        raw_valuations = np.random.rand(m)
        
        # Scale the valuations to sum up to the corresponding budget
        scaling_factor = budgets[i] / raw_valuations.sum()
        valuations[i] = raw_valuations * scaling_factor
    return valuations

# def generate_valuations(n, m, budgets) :
#     # Set the standard deviation
#     std_deviation = 10

#     # Draw 5 independent random samples from a normal distribution with mean 0
#     epsilon = np.random.normal(loc=0, scale=std_deviation, size=(n, m))

#     valuations = np.arange(n).reshape((n, 1)) + epsilon

#     return valuations

# Generates budgets
def generate_budgets(n, k) :
    return np.random.uniform(1, 1 + min(1/n, 1/(k-1)), size = n) * 100


# Generates n student etas
def generate_etas (n, m) :
    student_eta = np.zeros((n, m, m))
    # Create a random matrix
    for i in range(n) :
        eta_values = np.random.uniform(-10, 10, size=(m, m))
        np.fill_diagonal(eta_values, 0)
        student_eta[i] = np.triu(eta_values)

    return student_eta

# Represents constraints in array format conducive for Gurobi
def generate_constraints_list(m, t, times, days, types, class_days, class_times) :
    c_times = np.zeros((m, len(class_times), len(class_days)))
    
    for i in range(len(times)) :
        (start, end) = times[i]
        for j in range(len(class_times)):
            if class_times[j] <= end and class_times[j] >= start :
                c_times[i][j][days[i]==1] = 1
            elif class_times[j] > end:
                break
    c_types = np.zeros((m, t))
    for i in range(m) :
        c_types[i][types[i]] = 1

    return c_times, c_types

# Generates constraints for each course: picks what type of course
# it is, what time it occurs, and how many of each type is allowed (picked between 2 and l)
# minl : lower limit of courses of type i that a student can take
# l : upper limit of courses of type i that a student can take
# t : number of types of courses
def generate_constraints(m, class_days, class_times, minl, l, t, all=False) :
    times = np.random.randint(0, len(class_times), size=(1, m))[0]
    class_length = np.random.choice([0.833, 1.333, 2.833], size = m, p=[0.5, 0.45, 0.05])

    indices = np.random.choice(len(class_days), size = (m,), p = [0.4, 0.4, 0.1, 0.07, 0.03])
    days = class_days[indices]
    tuples = []
    for i in range(len(times)) :
        tuples.append((class_times[times[i]], class_times[times[i]] + class_length[i]))
    
    tuples = np.array(tuples)
    types = np.array(np.random.randint(0, t, size=(1, m))[0])
    maxes = np.random.randint(minl, l, size= (1, t))[0]

 
    
    if all :
        return tuples, days, np.array(types), maxes
    
    c_times, c_types = generate_constraints_list(m, t, tuples, days, types, class_days, class_times)
    return c_times, c_types, maxes

# Sample input
# class_days = np.array([[1, 0, 1, 0, 0], [0,1,0,1,0], [0,0,0,0,1], [1,1,1,1,0], [1,1,1,1,1]])
# times = np.array([8.5, 9, 9.5, 10, 11, 12.5, 13.5, 14.5, 15, 16.5, 19.5])
# print(generate_constraints(20, class_days, times, 2, 5, 4))

# Generates m courses
def generate_courses(m, class_days, class_times, minl, l, t) :
    times, days, types, maxes = generate_constraints(m, class_days, class_times, minl, l, t, all=True)
    courses = []
    for i in range(len(times)) :
        course = {
            'time' : times[i],
            'days' : days[i],
            'type' : types[i],
            'price' : 0,
            'max_type' : maxes[types[i]]
        }
        courses.append(course)
    
    c_times, c_types = generate_constraints_list(m, t, times, days, types, class_days, class_times)
    return np.array(courses), c_times, c_types, maxes 

# Gathers all data into a struct, for easier use in the A-CEEI mechanism
def get_data_struct (data):
    budgets = generate_budgets(data['n'], data['k'])
    valuations = generate_valuations(data['n'], data['m'], budgets)
    etas = generate_etas(data['n'], data['m'])
    courses, c_times, c_types, maxes = generate_courses(data['m'], data['class_days'], data['class_times'], data['minl'], data['l'], data['t'])

    data_struct = {
        'n' : data['n'],
        'm' : data['m'],
        'k' : data['k'],
        't' : data['t'],
        'valuations': valuations,
        'budgets':budgets,
        'etas': etas,
        'courses':courses,
        'maxes':maxes,
        'c_times': c_times,
        'c_types':c_types,
        'min_courses': data['l']
    }
    return data_struct


