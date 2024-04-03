import random
from pathlib import Path
from typing import List

import networkx as nx

from algorithms.swarm import AntAlgorithm, transform_graph
from algorithms.swarm.ant import Ant
from objects import Robot, RobotSize, Warehouse


def order(num_items):
    # TODO zwrócić listę zamówień {id: licza sztuk, id2: liczba sztuk, ...}

    product_ids = [f'id{i+1}' for i in range(num_items)]

    quantities = [1, 2, 3, 4, 5]
    weights = [0.2, 0.3, 0.25, 0.15, 0.1]  # Adjust weights as needed

    orders = {product_id: random.choices(quantities, weights, k=1)[
        0] for product_id in product_ids}

    return orders


def generate_robots(size_of_robots: List[RobotSize] = [RobotSize.SMALL, RobotSize.SMALL]):
    tab = []
    for idx, size in enumerate(size_of_robots):
        tab.append(Robot(id=idx, size=size))

    return tab


def main():
    print("Hello World!")
    # TODO generacja magazynu i robotów
    # TODO: zparametryzować
    size_of_robots = [RobotSize.SMALL, RobotSize.SMALL]
    robots = generate_robots(size_of_robots)
    warehouse = Warehouse(
        txt_file='generated_graphs/graph_4_4.adjlist', robots=robots)
    # TODO wygenerowanie listy zamówień
    example_num_items = 10
    orders = order(example_num_items)

    # TODO run algorithm (rojowy lub genetyczny)
    # TODO zwrócić listę tras i kosztów
    result = AntAlgorithm(order=orders, warehouse=warehouse)
    # TODO wizualizacja wyników i porównanie z innymi algorytmami


def mock_main():
    graph = nx.read_adjlist('/home/lf/stdia/8/ML/deep_learning/generated_graphs/graph_4_4.adjlist')
    orders = {
        7: 1,
        11: 1,
        9: 3,
        8: 1,
        6: 12,
        1: 4,
        2: 2,
    }

    graph = transform_graph(graph, orders)
    ants = [
        Ant(graph, max_capacity=10, velocity_factor=1),
        Ant(graph, max_capacity=10, velocity_factor=1),
        # Ant(graph, max_capacity=10, velocity_factor=1),
        # Ant(graph, max_capacity=10, velocity_factor=1),
    ]

    alg = AntAlgorithm(graph, ants)
    solution = alg.solve(
        iter=100,
        alpha=0.1,
        beta=0.1,
        decay_rate=0.01
    )

    print("Best solution:", *[
            'Ant {id}: total distance {total_distance:2d}, path {path}'.format(**log)  # noqa
            for log in solution
        ],
        sep='\n'
    )


# if __name__ == '__main__':
#     mock_main()


def test_case_1():
    robots = [
        Robot('1', RobotSize.SMALL),
        Robot('2', RobotSize.SMALL),
        Robot('3', RobotSize.SMALL),
        Robot('4', RobotSize.LARGE),
    ]

    orders = {
        7: 1,
        11: 1,
        9: 3,
        8: 1,
        6: 12,
        1: 4,
        2: 2,
    }

    path = Path('/home/lf/stdia/8/ML/deep_learning/generated_graphs/graph_10_10.adjlist')
    warehouse = Warehouse(
        txt_file=path, robots=robots)

    alg = AntAlgorithm.from_orders_warehouse(orders, warehouse)
    solution = alg.solve(
        iter=1000,
        alpha=0.1,
        beta=0.1,
        decay_rate=0.01
    )

    return alg

def test_case_2():
    robots = [
        Robot('1', RobotSize.SMALL),
        Robot('2', RobotSize.MEDIUM),
        Robot('3', RobotSize.LARGE),
    ]

    orders = {
        7: 1,
        11: 1,
        9: 3,
        8: 1,
        6: 12,
        1: 4,
        2: 2,
    }

    orders = {k: v * 1 for k, v in orders.items()}

    path = Path('/home/lf/stdia/8/ML/deep_learning/generated_graphs/graph_10_10.adjlist')
    warehouse = Warehouse(
        txt_file=path, robots=robots)

    alg = AntAlgorithm.from_orders_warehouse(orders, warehouse)
    solution = alg.solve(
        iter=1000,
        alpha=0.1,
        beta=0.1,
        decay_rate=0.01
    )

    return alg
