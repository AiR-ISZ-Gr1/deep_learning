import networkx as nx
import random
from objects.robot import Robot
from algorithms.interface import AlgorithmOutput, Order, RobotRoute
from typing import Dict, List, Tuple
from objects.warehouse import Warehouse
from math import ceil

from algorithms.genetics.transform_graph import change_graph

def fill_routes(solution: AlgorithmOutput, items_left: Order, weights: Dict[int, int], warehouse):
    for i, quantity in items_left.items.items():
        times = calculate_times(solution, warehouse)
        subtracted = 0
        for k in range(len(times)):
            temp_robot = min(times, key=times.get)
            times.pop(temp_robot)
            temp_cap = capacity_left(temp_robot, solution.result[temp_robot], weights)
            if temp_cap > 0:
                if temp_cap < weights[i] * (quantity-subtracted):
                    for j in range(quantity-subtracted):
                        if capacity_left(temp_robot, solution.result[temp_robot], weights) > weights[i]:
                            if i in solution.result[temp_robot].route:
                                solution.result[temp_robot].items[i] += 1
                            else:
                                solution.result[temp_robot].route.append(i)
                                solution.result[temp_robot].items[i] = 1
                            subtracted += 1
                else:
                    if i in solution.result[temp_robot].route:
                        solution.result[temp_robot].items[i] += quantity - subtracted
                    else:
                        solution.result[temp_robot].route.append(i)
                        solution.result[temp_robot].items[i] = quantity - subtracted
                    subtracted += quantity - subtracted

            if items_left.items[i] == subtracted:
                break


def get_weights(orders: Dict) -> Dict:
    weight_dict = {}
    weight_range = [0.2, 0.2, 0.3, 0.4, 0.5] #adjust as needed
    index = 0

    for item_id in orders.keys():
        weight_dict[item_id] = weight_range[index % len(weight_range)] #repetitive result weight depend on index of edge
        index += 1

    return weight_dict


def capacity_left(robot: Robot, route: RobotRoute, weights: Dict[int, int]) -> int:
    s = 0
    for i, quantity in route.items.items():
        s += weights[i] * quantity  # I need this weights dict that says which item weighs how much
    return robot.load_capacity - s

def truncation_selection(population: List[Tuple], parents_to_population_rate: float = 2/3) -> List[AlgorithmOutput]:
    """
    Select individuals from the population based on truncation selection.

    :param population: A list of tuples containing solutions and their fitness values.
    :param parents_to_population_rate: The ratio of parents to the population size.
    :return: A list of selected AlgorithmOutput solutions.
    """
    sorted_population = sorted(population, key=lambda x: x[1], reverse=True)
    solutions_to_take = int(ceil(len(population) * parents_to_population_rate))
    selected_individuals = [individual[0] for individual in sorted_population[:solutions_to_take]]

    return selected_individuals

def rank_selection(population: List[Tuple]) -> List[AlgorithmOutput]:
    """
    Select individuals from the population based on rank selection.

    :param population: A list of tuples containing solutions and their fitness values.
    :param parents_to_population_rate: The ratio of parents to the population size.
    :return: A list of selected AlgorithmOutput solutions.
    """
    solutions_to_take = int(ceil(len(population) * parents_to_population_rate))  # I want to take 2/3 of the solutions
    selected_individuals = [solution[0] for solution in population[:solutions_to_take]]

    return selected_individuals

def tournament_selection(population: List[Tuple], tournament_size: int, parents_to_population_rate: float = 2/3) -> List[AlgorithmOutput]:
    """
    Select individuals from the population based on tournament selection.

    :param population: A list of tuples containing solutions and their fitness values.
    :param tournament_size: The number of individuals participating in each tournament.
    :param parents_to_population_rate: The ratio of parents to the population size.
    :return: A list of selected AlgorithmOutput solutions.
    """
    solutions_to_take = int(ceil(len(population) * parents_to_population_rate))
    selected_individuals = []

    while len(selected_individuals) < solutions_to_take:
        tournament_indices = random.sample(range(len(population)), tournament_size)
        tournament_solutions = [population[i][0] for i in tournament_indices]

        # Choosing the best solution based on the length of the route - solution with shortest route 
        best_solution = min(tournament_solutions, key=lambda x: sum(sum(route.items.values()) for route in x.result.values()))

        selected_individuals.append(best_solution)
        
        if len(selected_individuals) >= solutions_to_take:
            break

    return selected_individuals

def roulette_selection(population: List[Tuple]) -> List[AlgorithmOutput]:
    """
    Select individuals from the population based on roulette wheel selection.

    :param population: A list of tuples containing solutions and their fitness values.
    :return: A list of selected AlgorithmOutput solutions.
    """
    solutions_to_take = int(ceil(len(population) * parents_to_population_rate))
    total_fitness = sum(1 / fitness for _, fitness in population)
    selected_individuals = []

    while len(selected_individuals) < solutions_to_take:
        selected_fitness = random.uniform(0, total_fitness)
        current_sum = 0

        for solution, fitness in population:
            current_sum += 1 / fitness
            if current_sum > selected_fitness:
                selected_individuals.append(solution)
                break
    
    return selected_individuals

def modified_proportional_selection(population: List[Tuple]) -> List[AlgorithmOutput]:
    """
    Select individuals from the population based on modified proportional selection.

    :param population: A list of tuples containing solutions and their fitness values.
    :return: A list of selected AlgorithmOutput solutions.
    """
    solutions_to_take = int(ceil(len(population) * parents_to_population_rate))
    fitness_value = [fitness for _, fitness in population]
    total_fitness = sum(fitness_value)
    selected_individuals = []

    while len(selected_individuals) < solutions_to_take:
        selected_fitness = random.uniform(0, total_fitness)
        selected_range = random.uniform(0, total_fitness)
        cumulative_probability = 0

        for solution, fitness in population:
            cumulative_probability = fitness / total_fitness
            if cumulative_probability >= selected_fitness and cumulative_probability <= selected_range:
                selected_individuals.append(solution)
                break
    
    return selected_individuals


def calculate_times(robots: AlgorithmOutput, warehouse: Warehouse) -> Dict[Robot, float]:
    distance_dict = {}

    graph_transformed = warehouse.graph
    distance_dict_norm = nx.get_edge_attributes(graph_transformed, 'distance')

    distance_dict_norm = {tuple(int(key) for key in keys): value for keys, value in distance_dict_norm.items()}

    for robot, (route, _) in robots.result.items():

        total_distance = 0
        route = [0, *route, 0]
        for i in range(len(route) - 1):

            if route == [0, 0]:
                break
            u = route[i]
            v = route[i+1]

            # check if edge exists
            try:
                if u != v:
                    total_distance += distance_dict_norm[(u, v)]
            except KeyError:
                try:
                    if u != v:
                        total_distance += distance_dict_norm[(v, u)]
                except KeyError:
                    continue

        distance_dict[robot] = float("{:.2f}".format(total_distance))
    times_dict = {robot: float("{:.2f}".format(distance_dict[robot] / robot.calculate_velocity())) for robot in distance_dict.keys()}
    return times_dict


def calculate_one(solution: AlgorithmOutput, warehouse: Warehouse) -> float: #assumed that it's robot id?
    return max(calculate_times(solution, warehouse).values()) 
        


def calculate_all(population: List[AlgorithmOutput], warehouse: Warehouse) -> List[float]:  # albo float
    return [calculate_one(sol, warehouse) for sol in population]


def generate_random_solution(orders: Order, warehouse: Warehouse) -> AlgorithmOutput:
    solution = {}

    graph = warehouse.graph
    robot_list = warehouse.robots

    weight_dict = get_weights(orders)

    picked_items = {item_id: 0 for item_id in orders}

    for robot in robot_list:
        route = [0]  #starting point for each robot
        items = {}  #tracking gathered items
        curr_capacity = robot.load_capacity

        for _ in range(len(orders)):
            if curr_capacity <= 0:
                break

            #filter out items that have already been picked
            available_items = [item_id for item_id in orders.keys() if picked_items[item_id] < orders[item_id]]

            if not available_items:
                break

            item_id = random.choice(available_items)  #random item to pick up

            max_items_to_pick = curr_capacity // weight_dict[item_id]
            amount_to_pick = min(orders[item_id] - picked_items[item_id], max_items_to_pick)

            if amount_to_pick == 0:
                continue

            # shortest_paths = nx.shortest_path(graph, route[-1], item_id)
            route.append(item_id)

            items[item_id] = int(amount_to_pick)
            curr_capacity -= amount_to_pick * weight_dict[item_id]
            picked_items[item_id] += amount_to_pick #tracking already picked items

        # shortest_paths = nx.shortest_path(graph, route[-1], 0) #return to starting point
        route.append(0)

        solution[robot] = RobotRoute(route=route, items=items)

    return AlgorithmOutput(solution)


def generate_population(count: int, orders, warehouse) -> List[AlgorithmOutput]:
    return [generate_random_solution(orders, warehouse) for _ in range(count)]


def cut_zeros(solution: AlgorithmOutput):
    for route in solution.result.values():
        if len(route.route) > 1:
            route.route.pop(0)
            route.route.pop()


def add_zeros(solution: AlgorithmOutput):
    for route in solution.result.values():
        # if len(route.route) > 1:
        route.route.insert(0, 0)
        route.route.append(0)


parents_to_population_rate = 2 / 3
