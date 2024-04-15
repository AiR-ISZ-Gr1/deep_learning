import matplotlib.pyplot as plt


def plot_loss_fn(runtime_data, index):
    plt.figure(figsize=(10, 6))
    data = runtime_data['best_scores']
    data.append(
        (runtime_data['params']['iter'], runtime_data['best_scores'][-1][1]))

    x, y = zip(*data)
    plt.step(x, y, where='post')

    plt.title('Best solution score over time')
    plt.xlabel('Iterations')
    plt.ylabel('Score')

    # plt.savefig(f'/workspaces/deep_learning/src/outputs/loss_fn{index}.png')
    plt.show()
