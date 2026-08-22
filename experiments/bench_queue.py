"""
Experiment 2: list.pop(0) queue vs collections.deque.

X-axis: number of enqueue/dequeue operations
Y-axis: total time (ms)

Goal:
Show that list.pop(0) is O(n) per dequeue operation, while
deque.popleft() is O(1) per dequeue operation.

Run from the project root:

    python experiments/bench_queue.py

Output:
    - raw timing results in the terminal
    - labeled plot saved to experiments/plots/bench_queue.png
"""

import os
import time
from collections import deque

import matplotlib.pyplot as plt


SIZES = [100, 1_000, 5_000, 20_000]


# ---------------------------------------------------------
# Find project root and create plot directory.
# ---------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PLOT_DIRECTORY = os.path.join(
    PROJECT_ROOT,
    "experiments",
    "plots",
)

os.makedirs(
    PLOT_DIRECTORY,
    exist_ok=True,
)


def time_list_queue(n: int) -> float:
    """
    Enqueue n items using list.append(), then dequeue all
    items using list.pop(0).

    Complexity:
        append()  -> O(1) amortized
        pop(0)    -> O(n)

    Total dequeue work grows approximately quadratically:
        O(n^2)
    """

    queue = []

    start = time.perf_counter()

    # Enqueue n items.
    for i in range(n):
        queue.append(i)

    # Dequeue all items.
    while queue:
        queue.pop(0)

    end = time.perf_counter()

    return (end - start) * 1000


def time_deque_queue(n: int) -> float:
    """
    Enqueue n items using deque.append(), then dequeue all
    items using deque.popleft().

    Complexity:
        append()   -> O(1)
        popleft()  -> O(1)

    Total:
        O(n)
    """

    queue = deque()

    start = time.perf_counter()

    # Enqueue n items.
    for i in range(n):
        queue.append(i)

    # Dequeue all items.
    while queue:
        queue.popleft()

    end = time.perf_counter()

    return (end - start) * 1000


def main():
    """Run the queue benchmark and generate the plot."""

    list_times = []
    deque_times = []

    print("=" * 65)
    print("EXPERIMENT 2: LIST QUEUE vs DEQUE")
    print("=" * 65)

    print(
        f"{'Operations':>12} | "
        f"{'list.pop(0) (ms)':>20} | "
        f"{'deque (ms)':>15}"
    )

    print("-" * 65)

    for n in SIZES:

        list_time = time_list_queue(n)
        deque_time = time_deque_queue(n)

        list_times.append(list_time)
        deque_times.append(deque_time)

        print(
            f"{n:>12} | "
            f"{list_time:>20.6f} | "
            f"{deque_time:>15.6f}"
        )

    # ---------------------------------------------------------
    # Create plot.
    # ---------------------------------------------------------

    output_path = os.path.join(
        PLOT_DIRECTORY,
        "bench_queue.png",
    )

    plt.figure()

    plt.plot(
        SIZES,
        list_times,
        marker="o",
        label="list.pop(0)",
    )

    plt.plot(
        SIZES,
        deque_times,
        marker="o",
        label="deque",
    )

    plt.xlabel("Number of enqueue/dequeue operations")
    plt.ylabel("Total time (ms)")
    plt.title("Queue Operations: list vs deque")

    plt.legend()

    plt.tight_layout()

    plt.savefig(output_path)

    plt.close()

    print("-" * 65)
    print(f"Saved plot to {output_path}")


if __name__ == "__main__":
    main()