from pathlib import Path
import numpy as np
import networkx as nx
import json
import matplotlib.pyplot as plt
from algorithms.interface import Order
from objects.robot import Robot
from objects.warehouse import Warehouse
from algorithms.genetics.genetic import GeneticAlgorithm
from algorithms.swarm import AntAlgorithm
import argparse
from tabulate import tabulate
from pathlib import Path

# Path to directory with input data for algorithms
APP_DIR = Path(__file__).resolve().parent
INPUT_DATA_DIR = APP_DIR.parent / 'input_data'

def test_genetic(selection_method: str, mutation_method: str, iterations_number: int, population: int):
    """
    Run a genetic algorithm with specified parameters and display results.

    :param selection_method: The method for selecting individuals in the genetic algorithm.
    :param mutation_method: The method for mutating individuals in the genetic algorithm.
    :param iterations_number: The maximum number of iterations for the genetic algorithm.
    :param population: The initial population size for the genetic algorithm.
    """
    # Load necessary data about available robots and current order
    with open(INPUT_DATA_DIR / 'robots/robotsg2.json', 'r') as f:
        sizes = json.load(f)

    with open(INPUT_DATA_DIR / 'orders/order2.json', 'r') as f:
        order = json.load(f)

    # Create graph from adjlist
    graph = nx.read_adjlist(INPUT_DATA_DIR / 'graphs/10_10.adjlist')
    # Create robot list from loaded file
    robots = [
        Robot(f'{i+1}', size)
        for i, size in enumerate(sizes)
    ]
    # Create object which represents warehouse
    warehouse = Warehouse(graph, robots)
    warehouse.graph = nx.relabel_nodes(warehouse.graph, {n: int(n) for n in warehouse.graph})
    order = {int(k): v for k, v in order.items()}
    # Create object which represents genetic algorithm
    GeneticAlg = GeneticAlgorithm(order=Order(order), warehouse=warehouse, selection_method=selection_method, mutation_method=mutation_method)
    # Run the algorithm with specified arguments 
    GeneticAlg.run(max_iter=iterations_number, population_count=population)

    # Print in terminal information about the algorithm and all required dependencies
    sizes_count = {
        'small': 0,
        'medium': 0,
        'large': 0,
    }
    for size in sizes:
        sizes_count[size] += 1

    sizes_count = {key: value for key, value in sizes_count.items() if value != 0}
    order_data = [(node, quantity) for node, quantity in order.items()]
    size_data = [(robot, quantity) for robot, quantity in sizes_count.items()]

    print("==================================")
    print(tabulate(size_data, headers=['Robot type', 'Quantity']))
    print("==================================")
    print(tabulate(order_data, headers=['Node', 'Item quantity']))
    print("==================================")
    print(f"Genetic algorithm info:\nnumber of max iterations: {iterations_number}\ninitial population: {population}\nselection method: {selection_method}\nmutation method: {mutation_method}")
    print("==================================")

    # Plot the chart of cost function
    x_vec = np.linspace(1, len(GeneticAlg.best_list), len(GeneticAlg.best_list))

    plt.step(x_vec, GeneticAlg.best_list, color='b', linestyle='-')
    plt.title('Step Plot of Change of Cost Function', fontsize=14)
    plt.xlabel('Iteration', fontsize=12)
    plt.ylabel('Value of Cost Function', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.legend(['Cost Function'], loc='best', fontsize=10)
    plt.tight_layout() 
    plt.show()


def test_case_1():
    with open(INPUT_DATA_DIR / 'robots\\robots1.json', 'r') as f:
        sizes = json.load(f)

    with open(INPUT_DATA_DIR / 'orders\\order1.json', 'r') as f:
        order = json.load(f)

    graph = nx.read_adjlist(INPUT_DATA_DIR / 'graphs\\10_10.adjlist')

    robots = [
        Robot(f'{i+1}', size)
        for i, size in enumerate(sizes)
    ]
    warehouse = Warehouse(graph, robots)
    order = {int(k): v for k, v in order.items()}

    alg = AntAlgorithm.from_input_data(order, warehouse)
    alg.solve(
        iter=1000,
        alpha=0.1,
        beta=0.1,
        decay_rate=0.01
    )

    # here will be generating plots script etc.

    return alg


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Enter flags for various algorithms fields:")
    parser.add_argument('-s', '--selection', choices=['rank', 'tournament', 'roulette', 'proportional'], default='rank', help='Selection method')
    parser.add_argument('-i', '--iterations', default=100, type=int, help='Iteratiions number of genetic algorithm')
    parser.add_argument('-p', '--population', default=10, type=int, help='Initial population size')
    parser.add_argument('-m', '--mutation', choices=['shuffle', 'add', 'change', 'swap'], default='shuffle', help='mutation method')
    args = parser.parse_args()
    test_genetic(args.selection, args.mutation, args.iterations, args.population)
