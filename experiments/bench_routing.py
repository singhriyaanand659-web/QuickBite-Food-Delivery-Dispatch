"""
Experiment 5: BFS (fewest hops) vs Dijkstra (shortest weighted) route quality.

This experiment demonstrates an important routing issue:

    BFS:
        Finds the route with the FEWEST number of road segments.

    Dijkstra:
        Finds the route with the LOWEST TOTAL TRAVEL TIME.

These are not necessarily the same route.

Example:

    A --2--> B --2--> D
    A --1--> C --1--> C2 --1--> D

BFS chooses:

    A -> B -> D

because it has 2 hops.

Dijkstra chooses:

    A -> C -> C2 -> D

because its total weight is only 3 minutes,
compared with 4 minutes for the BFS route.

Run from the project root:

    python experiments/bench_routing.py

Output:
    - BFS route and total travel time
    - Dijkstra route and total travel time
    - labeled bar chart saved to experiments/plots/bench_routing.png
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


def build_bug_demo_graph() -> LocationGraph:
    """
    Build a deliberately constructed graph where:

        fewest hops != lowest travel time.

    Route 1:

        A -> B -> D

    Hops:
        2

    Weight:
        2 + 2 = 4 minutes

    Route 2:

        A -> C -> C2 -> D

    Hops:
        3

    Weight:
        1 + 1 + 1 = 3 minutes

    Therefore:

        BFS      -> A -> B -> D
        Dijkstra -> A -> C -> C2 -> D
    """

    graph = LocationGraph()

    locations = [
        "A",
        "B",
        "C",
        "C2",
        "D",
    ]

    for location in locations:
        graph.add_location(location)

    # Fewest-hop route:
    #
    # A -> B -> D
    #
    # Total = 4 minutes

    graph.add_road(
        "A",
        "B",
        2,
    )

    graph.add_road(
        "B",
        "D",
        2,
    )

    # More-hop but faster route:
    #
    # A -> C -> C2 -> D
    #
    # Total = 3 minutes

    graph.add_road(
        "A",
        "C",
        1,
    )

    graph.add_road(
        "C",
        "C2",
        1,
    )

    graph.add_road(
        "C2",
        "D",
        1,
    )

    return graph


def calculate_path_weight(
    graph: LocationGraph,
    path: list[str],
) -> float:
    """
    Calculate the total weight of an already-selected path.

    BFS chooses the path without considering weights, so we calculate
    its actual travel time afterward for a fair comparison.
    """

    total_weight = 0.0

    for i in range(len(path) - 1):

        current = path[i]
        next_node = path[i + 1]

        for neighbor, weight in graph.neighbors(current):

            if neighbor == next_node:
                total_weight += weight
                break

    return total_weight


def main():
    """Run the BFS vs Dijkstra routing-quality experiment."""

    graph = build_bug_demo_graph()

    start = "A"
    end = "D"

    # ---------------------------------------------------------
    # BFS
    # ---------------------------------------------------------

    bfs_path = graph.bfs_shortest_hops(
        start,
        end,
    )

    if bfs_path is None:
        raise RuntimeError(
            "BFS could not find a route."
        )

    bfs_total_weight = calculate_path_weight(
        graph,
        bfs_path,
    )

    # ---------------------------------------------------------
    # Dijkstra
    # ---------------------------------------------------------

    dijkstra_result = graph.dijkstra_shortest_weighted(
        start,
        end,
    )

    if dijkstra_result is None:
        raise RuntimeError(
            "Dijkstra could not find a route."
        )

    dijkstra_path, dijkstra_total_weight = dijkstra_result

    # ---------------------------------------------------------
    # Print results
    # ---------------------------------------------------------

    print("=" * 70)
    print("EXPERIMENT 5: BFS vs DIJKSTRA ROUTE QUALITY")
    print("=" * 70)

    print(f"\nStart: {start}")
    print(f"Destination: {end}")

    print("\nBFS:")
    print(f"  Path:         {' -> '.join(bfs_path)}")
    print(f"  Number hops:  {len(bfs_path) - 1}")
    print(f"  Total time:   {bfs_total_weight:.2f} minutes")

    print("\nDijkstra:")
    print(f"  Path:         {' -> '.join(dijkstra_path)}")
    print(f"  Number hops:  {len(dijkstra_path) - 1}")
    print(f"  Total time:   {dijkstra_total_weight:.2f} minutes")

    # ---------------------------------------------------------
    # Calculate improvement.
    # ---------------------------------------------------------

    time_saved = (
        bfs_total_weight - dijkstra_total_weight
    )

    percentage_saved = (
        (time_saved / bfs_total_weight) * 100
        if bfs_total_weight > 0
        else 0
    )

    print("\nComparison:")
    print(
        f"  Dijkstra saves: "
        f"{time_saved:.2f} minutes"
    )

    print(
        f"  Improvement: "
        f"{percentage_saved:.2f}%"
    )

    # ---------------------------------------------------------
    # Create plot directory.
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
        "bench_routing.png",
    )

    # ---------------------------------------------------------
    # Create bar chart.
    # ---------------------------------------------------------

    plt.figure()

    plt.bar(
        [
            "BFS\n(fewest hops)",
            "Dijkstra\n(shortest weight)",
        ],
        [
            bfs_total_weight,
            dijkstra_total_weight,
        ],
    )

    plt.ylabel("Total route weight / time (minutes)")

    plt.title(
        f"Route Quality: BFS vs Dijkstra ({start} -> {end})"
    )

    plt.tight_layout()

    plt.savefig(output_path)

    plt.close()

    print("\n" + "-" * 70)
    print(f"Saved plot to {output_path}")


if __name__ == "__main__":
    main()