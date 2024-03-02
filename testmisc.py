import numpy as np
oversubscribed_indices = [2, 4]

courses = [[0, 1, 1, 1, 0], [1, 0, 1, 0, 1], [0, 0, 1, 0, 1], [0, 1, 1, 0, 1]]

oversubscribed_indices = np.array(oversubscribed_indices)

# Assuming courses is a numpy array
courses = np.array(courses)

# Get the demand for the oversubscribed course
students_interested = courses[:, 4]

# Now you have a boolean array where each element indicates whether the corresponding student is interested in the oversubscribed course or not
# You can get the indices of the interested students using numpy's where function
interested_students_indices = np.where(students_interested, True, False)
interested_students_indices = np.where(interested_students_indices)[0]
print(interested_students_indices)

demand = np.array([1, 2, 4, 1, 3])
seats = np.array([2, 2, 2, 2, 2])
oversubscribed = np.where(demand - seats > 0, True, False)
oversubscribed_indices = np.where(oversubscribed)[0]
print(oversubscribed_indices)