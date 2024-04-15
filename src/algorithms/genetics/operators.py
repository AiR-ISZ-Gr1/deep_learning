import random
import copy
from typing import Dict
from algorithms.interface import RobotRoute, AlgorithmOutput, Order
from objects.robot import Robot
from algorithms.genetics.other import fill_routes, cut_zeros, add_zeros

def crossover(parent1: AlgorithmOutput, parent2: AlgorithmOutput, order_items: Order, weights: Dict[int, int], warehouse)\
        -> AlgorithmOutput:
    """
    Function that takes half of solutions' routes from parent1 and half from parent2

    :param order_items:
    :param parent1:
    :param parent2:
    :return: new solutions based on two other
    """
    cut_zeros(parent2)
    cut_zeros(parent1)

    robots_indices = list(range(len(parent1.result)))
    first_parent_robots_indices = random.sample(robots_indices, len(robots_indices) // 2)

    robots = list(parent1.result.keys())
    second_parent_robots = []
    for k in parent2.result.keys():
        if robots.index(k) not in first_parent_robots_indices:
            second_parent_robots.append(k)

    new_solution = AlgorithmOutput({})
    items_left = copy.deepcopy(order_items.items)
    for i in first_parent_robots_indices:
        new_solution.result[robots[i]] = copy.deepcopy(parent1.result[robots[i]])
        for node, quantity in parent1.result[robots[i]].items.items():
            if items_left[node] == quantity:
                items_left.pop(node)
            else:
                items_left[node] = items_left[node] - quantity

    for robot in second_parent_robots:
        temp_robot_route = RobotRoute([], {})
        for node, quantity in parent2.result[robot].items.items():
            if node in items_left.keys():
                if items_left[node] > 0:  # could be skipped
                    temp_robot_route.route.append(node)
                    if items_left[node] <= quantity:
                        temp_robot_route.items[node] = items_left[node]
                        items_left.pop(node)
                    elif items_left[node] > quantity:
                        temp_robot_route.items[node] = quantity
                        items_left[node] = items_left[node] - quantity
        new_solution.result[robot] = temp_robot_route
    fill_routes(new_solution, Order(items_left), weights, warehouse)
    add_zeros(new_solution)
    add_zeros(parent1)
    add_zeros(parent2)
    return new_solution

def two_point_crossover(parent1: AlgorithmOutput, parent2: AlgorithmOutput, order_items: Order, weights: Dict[int, int], warehouse) -> AlgorithmOutput:
    """
    Function that swaps segments of solutions' routes between parent1 and parent2 using two-point crossover

    :param order_items:
    :param parent1:
    :param parent2:
    :return: new solution based on two other
    """
    cut_zeros(parent1)
    cut_zeros(parent2)

    robots = list(parent1.result.keys())
    num_robots = len(robots)

    if num_robots > 1:
        points = sorted(random.sample(range(num_robots), 2))
    else:
        points = [0, 0]  

    new_solution = AlgorithmOutput({})

    for i in range(num_robots):
        if points[0] <= i < points[1]:
            new_solution.result[robots[i]] = copy.deepcopy(parent2.result[robots[i]])
        else:
            new_solution.result[robots[i]] = copy.deepcopy(parent1.result[robots[i]])

    fill_routes(new_solution, Order(copy.deepcopy(order_items.items)), weights, warehouse)
    add_zeros(new_solution)
    add_zeros(parent1)
    add_zeros(parent2)
    return new_solution

def shuffle_mutate(solution: AlgorithmOutput, robots_count: int):
    """
    Shuffle node order in robots_count randomly chosen robots

    :param solution:
    :param robots_count:
    """
    cut_zeros(solution)
    robots_indices = list(range(len(solution.result)))
    chosen_robot_indices = random.sample(robots_indices, robots_count)
    robots = list(solution.result.keys())
    for robot_i in chosen_robot_indices:
        random.shuffle(solution.result[robots[robot_i]].route)
    add_zeros(solution)

def mutate_by_add_random_node(solution: AlgorithmOutput, nodes_no: int) -> None:
    """
    Mutate the solution by adding a random node to a random route of a random robot.

    :param solution: The solution to mutate.
    """
    robots = list(solution.result.keys())
    chosen_robot = random.choice(robots)
    route = solution.result[chosen_robot].route
    random_node = random.randint(1, len(route) - 1)
    route.insert(random_node, random.randint(1, nodes_no - 1))
    add_zeros(solution)

def value_change_mutation(solution: AlgorithmOutput, mutation_rate: float, nodes_no:int, max_change: int):
    """
    Perform value change mutation on a randomly selected gene in each robot's route in the solution.

    :param solution: The current solution to be mutated
    :param mutation_rate: The probability of mutation for each robot's route
    :param max_change: The maximum value by which the gene can be changed
    """
    for robot, route in solution.result.items():
        if random.random() < mutation_rate:
            index = random.randint(0, len(route.route) - 1)
            
            # random change to the selected gene
            change = random.randint(-max_change, max_change)
            route.route[index] += change

            route.route[index] = max(route.route[index], 0)
            route.route[index] = min(route.route[index], nodes_no - 1) # valid graph node

            solution.result[robot] = route

def swap_mutate(solution: AlgorithmOutput, mutation_rate: float) -> None:
    """
    Perform swap mutation on a randomly selected gene pair in each robot's route in the solution.

    :param solution: The current solution to be mutated
    :param mutation_rate: The probability of mutation for each robot's route
    """
    for robot, route in solution.result.items():
        if random.random() < mutation_rate:
            index1, index2 = random.sample(range(len(route.route)), 2)
            route.route[index1], route.route[index2] = route.route[index2], route.route[index1]
            solution.result[robot] = route
