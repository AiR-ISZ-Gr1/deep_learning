import random
from math import ceil
from algorithms.genetics.operators import crossover, shuffle_mutate, mutate_by_add_random_node, value_change_mutation, swap_mutate
from algorithms.genetics.other import generate_population, calculate_all, rank_selection,\
    calculate_one, parents_to_population_rate, get_weights, tournament_selection, roulette_selection, modified_proportional_selection
from algorithms.genetics.transform_graph import change_graph

class GeneticAlgorithm:
    def __init__(self, order, warehouse, selection_method, mutation_method, population=None) -> None:
        self.order = order
        self.warehouse = warehouse
        self.population = population  # [(AlgorithmOutput, cost)]
        self.weights = get_weights(self.order.items)  # {item: weight}
        self.best_solution = ()  # (solution, cost)
        self.best_list = []
        self.selection = selection_method
        self.mutation = mutation_method

    def run(self, max_iter, population_count, mutation_rate=0.2):
        self.warehouse.graph = change_graph(self.warehouse.graph, self.order)

        if self.population is None:
            self.population = []
            population = generate_population(population_count, self.order.items, self.warehouse)
            costs = calculate_all(population, self.warehouse)
            for i in range(len(population)):
                self.population.append((population[i], costs[i]))

        self.population.sort(key=lambda tup: tup[1])
        for _ in range(max_iter):
            self.single_iteration(mutation_rate)
            self.best_list.append(self.population[0][1])
            if self.best_solution == () or self.best_solution[1] > self.population[0][1]:
                self.best_solution = self.population[0]

        return self.best_solution

    def single_iteration(self, mutation_rate):
        temp_population = self.population[:int(ceil(len(self.population) * parents_to_population_rate))]
        if self.selection == 'rank':
            to_crossover = rank_selection(self.population)
        elif self.selection == 'tournament':
            to_crossover = tournament_selection(self.population, tournament_size=2)
        elif self.selection == 'roulette':
            to_crossover = roulette_selection(self.population)
        elif self.selection == 'proportional':
            to_crossover = modified_proportional_selection(self.population)
        for _ in range(len(self.population)-len(temp_population)):
            # if len(to_crossover) < 2:
            #     break
            parents = random.sample(to_crossover, 2)
            to_crossover.remove(parents[0])
            to_crossover.remove(parents[1])
            # crossover
            child = crossover(parents[0], parents[1], self.order, self.weights, self.warehouse)

            # mutation
            if self.mutation == 'shuffle':
                if random.randrange(0, 1) < mutation_rate:
                    shuffle_mutate(child, len(child.result) // 2 + 1)  # can be changed
            elif self.mutation == 'add':
                if random.randrange(0, 1) < mutation_rate:
                    mutate_by_add_random_node(child)
            elif self.mutation == 'change':
                value_change_mutation(child, mutation_rate, max_change=1)
            elif self.mutation == 'swap':
                swap_mutate(child, mutation_rate)

            cost = calculate_one(child, self.warehouse)
            temp_population.append((child, cost))
            temp_population.sort(key=lambda tup: tup[1])
            self.population = temp_population

# import networkx as nx
#
#
# START_NODE = '0'
# graph = nx.read_adjlist('../../../generated_graphs/graph_4_4.adjlist')
# G = nx.path_graph(graph)  # or DiGraph, MultiGraph, MultiDiGraph, etc
# points = [{n: list(nbrdict.keys())} for n, nbrdict in G.adjacency()]
#
# shortest_paths = nx.shortest_path(graph)
#
# orders = {
#     7: 1,
#     11: 1,
#     9: 3,
#     8: 1,
#     6: 12,
#     1: 4,
#     2: 2,
# }
# nodes = list(orders.keys())
# nodes = [START_NODE] + [str(node) for node in nodes]
# complete_graph = nx.Graph()
#
# for src in nodes:
#     for dst in nodes:
#         if src == dst:
#             continue
#         path = shortest_paths[src][dst]
#         complete_graph.add_edge(src, dst, weight=len(path)-1, path=path, sum_load=0, feromone=0)
#
# print()


# nx.set_node_attributes(complete_graph, {
#     node: {"weight": orders.get(int(node), np.inf)}
#     for node in nodes
# })
# list(complete_graph.nodes())