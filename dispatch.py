"""
Rider dispatch: given an order ready for pickup, select the best available
(idle) rider using a min-heap priority queue keyed by travel time from the
rider's current location to the restaurant.

This is what you benchmark in experiments/bench_dispatch.py:
heap-based selection vs. a naive linear scan over idle riders.
"""

import heapq
from dataclasses import dataclass, field

from graph import LocationGraph
from models import Rider, Order, RiderStatus, OrderStatus


@dataclass(order=True)
class _RankedRider:
    """Rider ranked by travel time to the restaurant."""

    distance: float
    rider: Rider = field(compare=False)


def _rider_distance(
    rider: Rider,
    restaurant_location: str,
    graph: LocationGraph
) -> float | None:
    """
    Calculate the rider's travel time to the restaurant using Dijkstra.

    Returns None if the restaurant is unreachable.
    """
    result = graph.dijkstra_shortest_weighted(
        rider.current_location,
        restaurant_location
    )

    if result is None:
        return None

    _, total_time = result
    return total_time


def select_best_rider_heap(
    idle_riders: list[Rider],
    restaurant_location: str,
    graph: LocationGraph
) -> Rider | None:
    """
    Select the idle rider with the smallest travel time to the restaurant.

    Uses a min-heap.

    Returns None if there are no reachable idle riders.
    """
    if not idle_riders:
        return None

    heap: list[_RankedRider] = []

    for rider in idle_riders:
        distance = _rider_distance(
            rider,
            restaurant_location,
            graph
        )

        if distance is None:
            continue

        heapq.heappush(
            heap,
            _RankedRider(distance, rider)
        )

    if not heap:
        return None

    return heapq.heappop(heap).rider


def select_best_rider_linear_scan(
    idle_riders: list[Rider],
    restaurant_location: str,
    graph: LocationGraph
) -> Rider | None:
    """
    Naive linear-scan version.

    Checks every idle rider, calculates travel time, and keeps
    the rider with the smallest reachable distance.

    Used as the baseline for the heap benchmark.
    """
    if not idle_riders:
        return None

    best_rider: Rider | None = None
    best_distance = float("inf")

    for rider in idle_riders:
        distance = _rider_distance(
            rider,
            restaurant_location,
            graph
        )

        if distance is None:
            continue

        if distance < best_distance:
            best_distance = distance
            best_rider = rider

    return best_rider


def assign_rider_to_order(
    order: Order,
    rider: Rider,
    graph: LocationGraph
) -> None:
    """
    Assign a rider to an order.

    Route:

        rider -> restaurant -> customer

    Updates the rider and order state.
    """

    rider_to_restaurant = graph.dijkstra_shortest_weighted(
        rider.current_location,
        order.restaurant.location
    )

    restaurant_to_customer = graph.dijkstra_shortest_weighted(
        order.restaurant.location,
        order.customer.location
    )

    if rider_to_restaurant is None:
        raise ValueError(
            f"No route from rider {rider.id} to "
            f"restaurant {order.restaurant.location}"
        )

    if restaurant_to_customer is None:
        raise ValueError(
            f"No route from restaurant {order.restaurant.location} "
            f"to customer {order.customer.location}"
        )

    first_path, first_time = rider_to_restaurant
    second_path, second_time = restaurant_to_customer

    # Join the paths without repeating the restaurant.
    full_route = first_path + second_path[1:]

    rider.status = RiderStatus.BUSY

    order.assigned_rider = rider
    order.route = full_route
    order.eta_minutes = first_time + second_time
    order.status = OrderStatus.OUT_FOR_DELIVERY


def complete_delivery(
    order: Order,
    rider: Rider
) -> None:
    """Mark the order delivered and make the rider idle again."""

    order.status = OrderStatus.DELIVERED

    rider.status = RiderStatus.IDLE

    # The rider finishes at the customer's location.
    rider.current_location = order.customer.location