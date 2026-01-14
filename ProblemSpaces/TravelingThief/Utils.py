import re
import os
import csv


def read_file(file_path):

    with open(file_path, "r") as file:
        lines = file.readlines()

    params = {}
    for line in lines:
        if line.startswith("DIMENSION"):
            params["dimension"] = int(line.split(":")[1].strip())
        elif line.startswith("NUMBER OF ITEMS"):
            params["num_items"] = int(line.split(":")[1].strip())
        elif line.startswith("CAPACITY OF KNAPSACK"):
            params["knapsack_capacity"] = int(line.split(":")[1].strip())
        elif line.startswith("MIN SPEED"):
            params["min_speed"] = float(line.split(":")[1].strip())
        elif line.startswith("MAX SPEED"):
            params["max_speed"] = float(line.split(":")[1].strip())
        elif line.startswith("RENTING RATIO"):
            params["renting_ratio"] = float(line.split(":")[1].strip())
        elif line.startswith("MIN DISTANCE"):
            params["min_distance"] = int(line.split(":")[1].strip())
        elif line.startswith("MAX DISTANCE"):
            params["max_distance"] = int(line.split(":")[1].strip())
        elif line.startswith("MAX PROFIT"):
            params["max_profit"] = int(line.split(":")[1].strip())
     

    node_section_pattern = re.compile(r"NODE_COORD_SECTION\s+\(INDEX,\s+X,\s+Y\):")
    items_section_pattern = re.compile(
        r"ITEMS SECTION\s+\(INDEX,\s+PROFIT,\s+WEIGHT,\s+ASSIGNED NODE NUMBER\):"
    )

    node_section_index = next(
        (i for i, line in enumerate(lines) if node_section_pattern.search(line)), None
    )
    items_section_index = next(
        (i for i, line in enumerate(lines) if items_section_pattern.search(line)), None
    )

    if node_section_index is None or items_section_index is None:
        raise ValueError("Sections not found in the file")

    nodes = []
    node_lines = lines[node_section_index + 1 : items_section_index]
    city_list = [] 
    for line in node_lines:
        parts = line.split()
        nodes.append((int(parts[0]), float(parts[1]), float(parts[2])))
        city_list.append(int(parts[0]))

    params["cities"] = city_list 
    items = []
    for line in lines[items_section_index + 1 :]:
        parts = line.split()
        items.append((int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])))

    return params, nodes, items


def calculate_distance(node1, node2):
    dx = node1[1] - node2[1]
    dy = node1[2] - node2[2]
    return (dx**2 + dy**2) ** 0.5

def fitness(params, nodes, items, solution):
    #print(solution[1])
    max_speed = params["max_speed"]
    min_speed = params["min_speed"]
    knapsack_capacity = params["knapsack_capacity"]
    total_distance = 0
    total_profit = 0
    total_weight = 0
    total_traveling_time = 0

    results = {} 

    for i in range(len(solution[0])):
        curr_node_index = solution[0][i] - 1
        next_node_index = solution[0][(i + 1) % len(solution[0])] - 1

    

        curr_node = nodes[curr_node_index]
        next_node = nodes[next_node_index]
        distance = calculate_distance(curr_node, next_node)

        for item in items:
            if item[3] == curr_node_index + 1:
                if solution[1][item[0] - 1] == 1: # if item is included 
                    total_profit += item[1]
                    total_weight += item[2]

        current_speed = (
            max_speed - total_weight * (max_speed - min_speed) / knapsack_capacity
        )

        total_distance += distance
        traveling_time = distance / current_speed
        total_traveling_time += traveling_time
    fitness = total_profit - total_traveling_time
  

    results["total_profit"] = total_profit
    results["valid_profit"] = total_profit if total_weight <= params["knapsack_capacity"] else -total_weight
    results["total_weight"] = total_weight
    results["total_traveling_time"] = total_traveling_time
    results["total_distance"] = total_distance 
    results["fitness"] = fitness 
    return results