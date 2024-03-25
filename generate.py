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


# Helps with eta generation
def generate_pairs(m):
    pairs = [(i, j) for i in range(m) for j in range(m) if i != j]
    return pairs
# Helps with eta generation
def pick_distinct_pairs(m, num_pairs):
    pairs = generate_pairs(m)
    random.shuffle(pairs)
    selected_pairs = []
    for pair in pairs:
        if len(selected_pairs) >= num_pairs:
            break
        if pair not in selected_pairs and (pair[1], pair[0]) not in selected_pairs:
            selected_pairs.append(pair)
    return selected_pairs

# Generates n student etas
def generate_etas (n, m) :
    student_eta = np.zeros((n, m, m))
    # Create a random matrix
    for i in range(n) :
        pairs = pick_distinct_pairs(m, 10)
        for pair in pairs:
            (smaller, larger) = pair
            if pair[0] > pair[1] :
                smaller = pair[1]
                larger = pair[0]
            student_eta[i][smaller][larger] = np.random.uniform(-100/(2 * m), 100/(2 * m))

    return student_eta

# Represents constraints in array format conducive for Gurobi
def generate_constraints_list(n, m, t, times, days, types, class_days, class_times) :
    c_times = np.zeros((m, len(class_times), len(class_days)))
    
    for i in range(len(times)) :
        (start, end) = times[i]
        for j in range(len(class_times)):
            if class_times[j] <= end and class_times[j] >= start :
                c_times[i][j][days[i]==1] = 1
            elif class_times[j] > end:
                break
    
    # Each student chooses t types and sets each course to fit one of those types
    c_types = np.zeros((n, m, t))
    for i in range(n) :
        for j in range(m) :
            c_types[i][j][types[i][j]] = 1

    return c_times, c_types

# Generates constraints for each course: picks what type of course
# it is, what time it occurs, and how many of each type is allowed (picked between 2 and l)
# minl : lower limit of courses of type i that a student can take
# l : upper limit of courses of type i that a student can take
# t : number of types of courses
def generate_constraints(n, m, class_days, class_times, minl, l, t, all=False) :
    times = np.random.randint(0, len(class_times), size=(1, m))[0]
    class_length = np.random.choice([0.833, 1.333, 2.833], size = m, p=[0.5, 0.45, 0.05])

    indices = np.random.choice(len(class_days), size = (m,), p = [0.4, 0.4, 0.1, 0.07, 0.03])
    days = class_days[indices]
    tuples = []
    for i in range(len(times)) :
        tuples.append((class_times[times[i]], class_times[times[i]] + class_length[i]))
    
    tuples = np.array(tuples)
    types = np.array(np.random.randint(0, t, size=(n, m)))
    maxes = np.random.randint(minl, l, size= (n, t))

 
    
    if all :
        return tuples, days, np.array(types), maxes
    
    c_times, c_types = generate_constraints_list(m, t, tuples, days, types, class_days, class_times)
    return c_times, c_types, maxes

# Sample input
# class_days = np.array([[1, 0, 1, 0, 0], [0,1,0,1,0], [0,0,0,0,1], [1,1,1,1,0], [1,1,1,1,1]])
# times = np.array([8.5, 9, 9.5, 10, 11, 12.5, 13.5, 14.5, 15, 16.5, 19.5])
# print(generate_constraints(20, class_days, times, 2, 5, 4))

# Generates m courses
def generate_courses(n, m, class_days, class_times, minl, l, t) :
    times, days, types, maxes = generate_constraints(n, m, class_days, class_times, minl, l, t, all=True)
    # courses = []
    # for i in range(len(times)) :
    #     course = { # This dictionary is unused, but keeping for now just in case
    #         'time' : times[i],
    #         'days' : days[i],
    #         'type' : types[i],
    #         'price' : 0,
    #         'max_type' : maxes[types[i]] 
    #     }
    #     courses.append(course)
    
    c_times, c_types = generate_constraints_list(n, m, t, times, days, types, class_days, class_times)
    return c_times, c_types, maxes 

# Gathers all data into a struct, for easier use in the A-CEEI mechanism
def get_data_struct (data):
    budgets = generate_budgets(data['n'], data['k'])
    valuations = generate_valuations(data['n'], data['m'], budgets)
    etas = generate_etas(data['n'], data['m'])
    c_times, c_types, maxes = generate_courses(data['n'], data['m'], data['class_days'], data['class_times'], data['minl'], data['l'], data['t'])

    data_struct = {
        'n' : data['n'],
        'm' : data['m'],
        'k' : data['k'],
        't' : data['t'],
        'seats' : data['seats'],
        'valuations': valuations,
        'budgets':budgets,
        'etas': etas,
        'maxes':maxes,
        'c_times': c_times,
        'c_types':c_types,
        'min_courses': data['l']
    }
    return data_struct



# GENERATE DATA
n = 250
m = 50
l = 5
k = 5
seats = np.full(m, 27) # as done in Othman paper


# valuations = generate_valuations(n, m, l)
# budgets = generate_budgets(n, l)
# etas = generate_etas(n, m)

class_days = np.array([[1, 0, 1, 0, 0], [0,1,0,1,0], [0,0,0,0,1], [1,1,1,1,0], [1,1,1,1,1]])
class_times = [8.5, 9, 9.5, 10, 11, 12.5, 13.5, 14.5, 15, 16.5, 19.5]
# c_times, c_types, maxes = generate_constraints(m, class_days, class_times, minl=1, l=l, t=5)

data = {
    'n': n,
    'm': m,
    'k': k,
    'l': l,
    'minl':1,
    'seats' : np.full(m, 27),
    't' : 5,
    'class_days' : class_days,
    'class_times':class_times,
}



#indices = np.random.choice(len(class_days), size=m, p=np.array([0.1, 0.2, 0.3, 0.2, 0.2]))

data_struct = get_data_struct(data)

print(data_struct['c_types'])