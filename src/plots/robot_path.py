import networkx as nx
import matplotlib.pyplot as plt


def plot_all_robot_paths(solution, graph, index):
    num_robots = len(solution)
    num_plots_per_row = 3
    num_rows = (num_robots - 1) // num_plots_per_row + 1

    plt.figure(figsize=(4 * num_plots_per_row, 4 * num_rows))

    for idx, robot in enumerate(solution):
        plt.subplot(num_rows, num_plots_per_row, idx % num_plots_per_row +
                    1 + (idx // num_plots_per_row) * num_plots_per_row)
        plot_robot_path(robot['path'], graph)
        plt.title(f"Robot {robot['id']}")

    plt.subplots_adjust(wspace=0.5, hspace=0.5)  # Adjust spacing
    plt.tight_layout()  # Adjust layout
    # plt.savefig(f'/workspaces/deep_learning/src/outputs/robot_paths{index}.png')
    plt.show()


def plot_robot_path(path, graph):
    colors = color_generator()

    routes = split_path(path)

    G = nx.DiGraph()
    G.add_nodes_from(graph.nodes)
    G.add_edges_from(graph.edges)

    pos = nx.spring_layout(G, seed=42)  # spring layout
    nx.draw(G, pos, with_labels=True, node_color='lightblue',
            node_size=1500, edge_color='lightgray', arrows=False)

    for route in routes:
        color = next(colors)
        route = [(src, dst) for src, dst in zip(route[:-1], route[1:])]
        nx.draw_networkx_edges(G, pos, edgelist=route,
                               edge_color=color, width=3, arrows=True)


def color_generator():
    cmap = plt.colormaps.get_cmap('tab10')
    i = 0
    while True:
        yield cmap(i)
        i = (i + 1) % 10


def split_path(path):
    subarrays = []
    subarray = []

    for element in path:
        if element == '0':
            if subarray:
                subarray = ['0', *subarray, '0']
                subarrays.append(subarray)
            subarray = []
        else:
            subarray.append(element)

    return subarrays
