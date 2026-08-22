"""
Experiment 4: adjacency list vs adjacency matrix memory usage.

X-axis: number of locations
Y-axis: memory used (KB)

Goal:
Show that an adjacency list is more memory-efficient for a sparse
road network, while an adjacency matrix requires O(V^2) space.

Run from the project root:

    python experiments/bench_graph_memory.py

Output:
    - raw memory measurements
    - labeled plot saved to experiments/plots/bench_graph_memory.png
"""

import os
import sys

import matplotlib.pyplot as plt


# ---------------------------------------------------------
# Make project-root modules importable.
# ---------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from graph import LocationGraph


SIZES = [10, 50, 100, 500]


def deep_size(obj, seen=None) -> int:
    """
    Recursively estimate the memory used by an object and
    its nested containers.

    This gives a more useful comparison than calling
    sys.getsizeof() only on the outer dictionary/list.
    """

    if seen is None:
        seen = set()

    object_id = id(obj)

    if object_id in seen:
        return 0

    seen.add(object_id)

    size = sys.getsizeof(obj)

    if isinstance(obj, dict):
        for key, value in obj.items():
            size += deep_size(key, seen)
            size += deep_size(value, seen)

    elif isinstance(obj, (list, tuple, set, frozenset)):
        for item in obj:
            size += deep_size(item, seen)

    return size


def build_sparse_graph(n: int) -> LocationGraph:
    """
    Build a deterministic sparse graph with n locations.

    Each location is connected to only a small number of nearby
    locations, representing a sparse road network.

    The same graph structure is used for both measurements.
    """

    graph = LocationGraph()

    locations = [
        f"L{i}"
        for i in range(n)
    ]

    # Add all locations.
    for location in locations:
        graph.add_location(location)

    # Connect each location to the next few locations.
    #
    # This keeps the graph sparse:
    # each vertex has only a small number of edges instead of
    # being connected to every other vertex.
    for i in range(n):

        if i + 1 < n:
            graph.add_road(
                locations[i],
                locations[i + 1],
                weight=1.0,
            )

        if i + 3 < n:
            graph.add_road(
                locations[i],
                locations[i + 3],
                weight=2.0,
            )

        if i + 7 < n:
            graph.add_road(
                locations[i],
                locations[i + 7],
                weight=3.0,
            )

    return graph


def measure_adjacency_list_memory(n: int) -> float:
    """
    Build a sparse LocationGraph and measure the memory footprint
    of its adjacency-list representation.

    Returns memory usage in KB.
    """

    graph = build_sparse_graph(n)

    memory_bytes = deep_size(graph._adj)

    return memory_bytes / 1024


def measure_adjacency_matrix_memory(n: int) -> float:
    """
    Build the same sparse LocationGraph and convert it to an
    adjacency matrix.

    Returns matrix memory usage in KB.
    """

    graph = build_sparse_graph(n)

    _, matrix = graph.to_adjacency_matrix()

    memory_bytes = deep_size(matrix)

    return memory_bytes / 1024


def main():
    """Run the memory experiment and generate the plot."""

    list_mem = []
    matrix_mem = []

    print("=" * 75)
    print("EXPERIMENT 4: ADJACENCY LIST vs ADJACENCY MATRIX MEMORY")
    print("=" * 75)

    print(
        f"{'Locations':>12} | "
        f"{'Adjacency List (KB)':>22} | "
        f"{'Adjacency Matrix (KB)':>24}"
    )

    print("-" * 75)

    for n in SIZES:

        list_memory = measure_adjacency_list_memory(n)
        matrix_memory = measure_adjacency_matrix_memory(n)

        list_mem.append(list_memory)
        matrix_mem.append(matrix_memory)

        print(
            f"{n:>12} | "
            f"{list_memory:>22.2f} | "
            f"{matrix_memory:>24.2f}"
        )

    # ---------------------------------------------------------
    # Create output directory.
    # ---------------------------------------------------------

    plot_directory = os.path.join(
        PROJECT_ROOT,
        "experiments",
        "plots",
    )

    os.makedirs(
        plot_directory,
        exist_ok=True,
    )

    output_path = os.path.join(
        plot_directory,
        "bench_graph_memory.png",
    )

    # ---------------------------------------------------------
    # Create plot.
    # ---------------------------------------------------------

    plt.figure()

    plt.plot(
        SIZES,
        list_mem,
        marker="o",
        label="Adjacency list",
    )

    plt.plot(
        SIZES,
        matrix_mem,
        marker="o",
        label="Adjacency matrix",
    )

    plt.xlabel("Number of locations")
    plt.ylabel("Memory used (KB)")
    plt.title("Graph Representation Memory: List vs Matrix")

    plt.legend()

    plt.tight_layout()

    plt.savefig(output_path)

    plt.close()

    print("-" * 75)
    print(f"Saved plot to {output_path}")


if __name__ == "__main__":
    main()