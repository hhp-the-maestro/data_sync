import json


def print_out(color, string):
    # print with colors
    colors = {
        "reset": '\033[0m',
        "red": "\033[91m",
        "cyan": "\033[96m", 
        "green": "\033[92m", 
        "yellow": "\033[93m", 
        "pink": "\033[94m", 
        "purple": "\033[95m", 
    }
    print(colors[color], string, colors[color], end="")
    print(colors["reset"], "", colors["reset"])


def load_map(filename="map_config.json"):
    # loads the mapping btw src and dest data
    file = open(filename)
    map = json.load(file)
    return map


def insertion_map(data, parent=''):
    # generates the mapping data to insert a new dest record from src
    mapper = load_map()
    dest_data = {}
    
    for key in data:
        if not data.get(key):
            continue
        parent_key = parent+key

        if mapper.get(parent_key):
            dest_key = mapper[parent_key]

            if "." in dest_key:
                dest_key = dest_key.split(".")[-1]

            if isinstance(data[key], list):
                dest_data[dest_key] = [insertion_map(dat, parent=key+".") for dat in data[key]]
            if isinstance(data[key], dict):
                dest_data[dest_key] = insertion_map(data[key])

            dest_data[dest_key] = data[key]
        else:
            if isinstance(data[key], list):
                dest_data.update(insertion_map(data[key][0], parent=key+"."))

    return dest_data




