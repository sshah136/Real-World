import random, time

start_id = 111
topic = 'COMP216'


def generate_data(data):
    global start_id

    # temperature sensors are placed around the world
    new_data = {
        'id': start_id,
        'time': time.asctime(),
        'temperature': round(data, 4),
        'geographical_location': {
            'long': round(random.uniform(-180, 180), 2),
            'lat': round(random.uniform(-90, 90), 2)
        }
    }

    start_id += 1

    return new_data


def print_data(data_dict, indent=0):
    for key, value in data_dict.items():
        if isinstance(value, dict):
            print(str(key) + ': ')
            print_data(value, indent + 1)
        else:
            print('\t' * indent + str(key) + ': ' + str(value))
    print()

# new_data = create_data()
# print_data(new_data)
