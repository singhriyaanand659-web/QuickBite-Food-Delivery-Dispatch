"""
Experiment 1: list scan (O(n)) vs hash map lookup (O(1) average).

X-axis: number of orders (n)
Y-axis: lookup time (ms)

Run from the project root:

    python experiments/bench_lookup.py

Output:
    - raw timing results in the terminal
    - labeled plot saved to experiments/plots/bench_lookup.png
"""

import os
import sys
import time

import matplotlib.pyplot as plt


# ---------------------------------------------------------
# Allow imports from the project root.
# ---------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from models import Order, Customer, Restaurant
from registry import Registry


SIZES = [10, 100, 1_000, 10_000, 100_000]


def create_fake_orders(n: int) -> list[Order]:
    """Create n simple Order objects for the experiment."""

    customer = Customer(
        id="C001",
        name="Test Customer",
        location="Location-A",
    )

    restaurant = Restaurant(
        id="R001",
        name="Test Restaurant",
        location="Location-B",
    )

    orders = []

    for i in range(n):
        orders.append(
            Order(
                id=f"O{i:06d}",
                customer=customer,
                restaurant=restaurant,
            )
        )

    return orders


def time_linear_scan(n: int) -> float:
    """
    Build a list of n orders and find the last order
    using a linear scan.

    Complexity: O(n)
    """

    orders = create_fake_orders(n)
    target_id = orders[-1].id

    start = time.perf_counter()

    for order in orders:
        if order.id == target_id:
            break

    end = time.perf_counter()

    return (end - start) * 1000


def time_hash_lookup(n: int) -> float:
    """
    Build a Registry containing n orders and find the
    last order using hash-map lookup.

    Average complexity: O(1)
    """

    orders = create_fake_orders(n)

    registry = Registry()

    for order in orders:
        registry.add(order.id, order)

    target_id = orders[-1].id

    start = time.perf_counter()

    registry.get(target_id)

    end = time.perf_counter()

    return (end - start) * 1000


def main():
    """Run the benchmark and generate the plot."""

    list_times = []
    dict_times = []

    print("=" * 65)
    print("EXPERIMENT 1: LIST SCAN vs HASH MAP")
    print("=" * 65)

    print(
        f"{'Orders':>12} | "
        f"{'Linear Scan (ms)':>20} | "
        f"{'Hash Map (ms)':>18}"
    )

    print("-" * 65)

    for n in SIZES:

        linear_time = time_linear_scan(n)
        hash_time = time_hash_lookup(n)

        list_times.append(linear_time)
        dict_times.append(hash_time)

        print(
            f"{n:>12} | "
            f"{linear_time:>20.6f} | "
            f"{hash_time:>18.6f}"
        )

    # ---------------------------------------------------------
    # Create output directory.
    # ---------------------------------------------------------

    output_directory = os.path.join(
        PROJECT_ROOT,
        "experiments",
        "plots",
    )

    os.makedirs(
        output_directory,
        exist_ok=True,
    )

    output_path = os.path.join(
        output_directory,
        "bench_lookup.png",
    )

    # ---------------------------------------------------------
    # Create plot.
    # ---------------------------------------------------------

    plt.figure()

    plt.plot(
        SIZES,
        list_times,
        marker="o",
        label="Linear scan (list)",
    )

    plt.plot(
        SIZES,
        dict_times,
        marker="o",
        label="Hash map (dict)",
    )

    plt.xlabel("Number of orders (n)")
    plt.ylabel("Lookup time (ms)")
    plt.title("Order Lookup: Linear Scan vs Hash Map")

    plt.xscale("log")

    plt.legend()

    plt.tight_layout()

    plt.savefig(output_path)

    plt.close()

    print("-" * 65)
    print(f"Saved plot to {output_path}")


if __name__ == "__main__":
    main()