import json
from generate import *

def generate_data(n, m, k, seats, t, class_days, class_times, minl=1, l=5):
    data = {
        'n': n,
        'm': m,
        'k': k,
        'l': l,
        'minl':minl,
        't' : t,
        'class_days' : class_days,
        'class_times':class_times,
        'seats' : seats,
    } 
    return get_data_struct(data)

def write_to_json(data, filename="data.json") :
    # Serialize the data to JSON
    json_data = json.dumps(data, indent=4)  # indent for human-readable formatting

    # Write JSON data to a file
    file_path = filename
    with open(file_path, "w") as json_file:
        json_file.write(json_data)

    print("Data has been written to", file_path)
    return

# GENERATE DATA
n = 50
m = 10
l = 5
k = 5
seats = np.full(m, 27) # as done in Othman paper


class_days = np.array([[1, 0, 1, 0, 0], [0,1,0,1,0], [0,0,0,0,1], [1,1,1,1,0], [1,1,1,1,1]])
class_times = [8.5, 9, 9.5, 10, 11, 12.5, 13.5, 14.5, 15, 16.5, 19.5]

data_struct = generate_data(n, m, k, seats, 5, class_days, class_times)

data_struct['valuations'] = data_struct['valuations'].tolist()
data_struct['budgets'] = data_struct['budgets'].tolist()
data_struct['etas'] = data_struct['etas'].tolist()
data_struct['maxes'] = data_struct['maxes'].tolist()
data_struct['c_times'] = data_struct['c_times'].tolist()
data_struct['c_types'] = data_struct['c_types'].tolist()
data_struct['seats'] = data_struct['seats'].tolist()

write_to_json(data_struct, "small_5.json")



