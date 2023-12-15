import matplotlib
import matplotlib.pyplot as plt
import mplcyberpunk
import json
import numpy as np
from pathlib import Path


MAX_DATA_LENGTH = 50


def load_stats(stats_file_path):
    with open(stats_file_path, "r") as stats_file:
        data = json.load(stats_file)

    speeds = np.array([entry["speed"] for entry in data])
    accuracies = np.array([entry["accuracy"] for entry in data])
    return speeds[-MAX_DATA_LENGTH:], accuracies[-MAX_DATA_LENGTH:]


def draw_line_graph(data, subplot_index, title, color):
    plt.subplot(*subplot_index)
    plt.plot(data, marker="o", color=color)
    plt.xticks(fontname="monospace", fontsize=10)
    plt.yticks(fontname="monospace", fontsize=10)
    plt.locator_params(axis="both", integer=True)
    plt.title(title, fontdict={"family": "monospace", "size": 16})
    mplcyberpunk.add_glow_effects()

    avg = np.mean(data)
    std_dev = np.std(data)
    max_value = np.max(data)
    stats_text = f"Avg: {avg:.2f}\nStd Dev: {std_dev:.2f}\nMax: {max_value:.2f}"
    plt.text(
        1.01,
        0.5,
        stats_text,
        transform=plt.gca().transAxes,
        verticalalignment="center",
        fontname="monospace",
        fontsize=10,
    )


def graph_stats(speeds, accuracies):
    matplotlib.rcParams["font.family"] = "monospace"
    matplotlib.rcParams["font.sans-serif"] = ["Courier"]
    plt.style.use("cyberpunk")
    plt.figure(figsize=(8, 6))
    plt.subplots_adjust(left=0.1, right=0.8, hspace=0.4)

    draw_line_graph(speeds, (2, 1, 1), "Speed (WPM)", "C0")
    draw_line_graph(accuracies, (2, 1, 2), "Accuracy (%)", "C1")
    plt.show()


def main():
    stats_file_path = Path(__file__).parent / "stats.json"
    speeds, accuracies = load_stats(stats_file_path)
    graph_stats(speeds, accuracies)


if __name__ == "__main__":
    main()
