"""
Experiment 3: linear scan vs heap for selecting the best rider.

X-axis: number of idle riders
Y-axis: selection time (ms)

Both methods use the SAME graph and the SAME Dijkstra-based distance
calculation. The only difference is how the best rider is selected:

    Linear scan:
        Check every rider and keep the smallest distance.

    Heap:
        Insert ranked riders into a min-heap and pop the best one.

Important:
The complete operation includes Dijkstra distance calculations for
each rider, so the entire function should NOT be described simply as
O(log n).

Run from the project root:

    python experiments/bench_dispatch.py

Output:
    - raw timing results
    - labeled plot saved to experiments/plots/bench_dispatch.png
"""

import os
import sys
import time

import matplotlib.pyplot as plt


# ---------------------------------------------------------
# Make project-root modules importable when this file is
# executed as:
#
#     python experiments/bench_dispatch.py
# ---------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from models import Rider, RiderStatus
from graph import LocationGraph
from dispatch import (
    select_best_rider_heap,
    select_best_rider_linear_scan,
)


# Keep the sizes reasonable because every rider requires
# a Dijkstra calculation.
SIZES = [10, 100, 1_000, 5_000]


def build_benchmark_graph() -> LocationGraph:
    """
    Build a small connected graph that all benchmark riders
    can use.

    Edge weights represent travel time in minutes.
    """

    graph = LocationGraph()

    locations = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
    ]

    for location in locations:
        graph.add_location(location)

    roads = [
        ("A", "B", 5),
        ("A", "C", 8),
        ("B", "D", 6),
        ("C", "D", 4),
        ("C", "E", 7),
        ("D", "F", 5),
        ("E", "F", 3),
        ("E", "G", 6),
        ("F", "H", 4),
        ("G", "H", 5),
        ("H", "I", 6),
        ("I", "J", 4),
        ("B", "E", 9),
        ("D", "G", 8),
    ]

    for a, b, weight in roads:
        graph.add_road(a, b, weight)

    return graph


def create_riders(n: int) -> list[Rider]:
    """
    Generate n idle riders distributed across the benchmark
    graph locations.

    Riders are given unique IDs but their locations repeat.
    This allows us to test large rider pools without needing
    thousands of graph vertices.
    """

    locations = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
    ]

    riders = []

    for i in range(n):
        riders.append(
            Rider(
                id=f"R{i:06d}",
                name=f"Rider {i}",
                current_location=locations[i % len(locations)],
                status=RiderStatus.IDLE,
            )
        )

    return riders


def time_linear_selection(
    n: int,
    graph: LocationGraph,
    riders: list[Rider],
) -> float:
    """
    Measure linear-scan rider selection time.

    Returns elapsed time in milliseconds.
    """

    start = time.perf_counter()

    select_best_rider_linear_scan(
        riders,
        "J",
        graph,
    )

    end = time.perf_counter()

    return (end - start) * 1000


def time_heap_selection(
    n: int,
    graph: LocationGraph,
    riders: list[Rider],
) -> float:
    """
    Measure heap-based rider selection time.

    Returns elapsed time in milliseconds.
    """

    start = time.perf_counter()

    select_best_rider_heap(
        riders,
        "J",
        graph,
    )

    end = time.perf_counter()

    return (end - start) * 1000


def main():
    """Run the rider-selection benchmark and generate a plot."""

    graph = build_benchmark_graph()

    linear_times = []
    heap_times = []

    print("=" * 70)
    print("EXPERIMENT 3: RIDER SELECTION")
    print("=" * 70)

    print(
        f"{'Riders':>12} | "
        f"{'Linear Scan (ms)':>20} | "
        f"{'Heap (ms)':>15}"
    )

    print("-" * 70)

    for n in SIZES:

        riders = create_riders(n)

        linear_time = time_linear_selection(
            n,
            graph,
            riders,
        )

        heap_time = time_heap_selection(
            n,
            graph,
            riders,
        )

        linear_times.append(linear_time)
        heap_times.append(heap_time)

        print(
            f"{n:>12} | "
            f"{linear_time:>20.6f} | "
            f"{heap_time:>15.6f}"
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
        "bench_dispatch.png",
    )

    # ---------------------------------------------------------
    # Create plot.
    # ---------------------------------------------------------

    plt.figure()

    plt.plot(
        SIZES,
        linear_times,
        marker="o",
        label="Linear scan",
    )

    plt.plot(
        SIZES,
        heap_times,
        marker="o",
        label="Heap (priority queue)",
    )

    plt.xlabel("Number of idle riders")
    plt.ylabel("Selection time (ms)")
    plt.title("Rider Selection: Linear Scan vs Heap")

    plt.xscale("log")

    plt.legend()

    plt.tight_layout()

    plt.savefig(output_path)

    plt.close()

    print("-" * 70)
    print(f"Saved plot to {output_path}")


if __name__ == "__main__":
    main()