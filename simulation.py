"""
Wires everything together and runs a sample end-to-end scenario.

Order flow:

  Order created
    -> registered in hash map
    -> enqueued at its restaurant's FIFO queue
    -> kitchen dequeues when ready
    -> dispatch selects best idle rider via min-heap
    -> graph computes route
    -> rider marked busy
    -> order status updated
    -> simulated delivery completed
    -> rider becomes idle again
    -> order marked delivered

Run with:

    python simulation.py
"""

from models import (
    Customer,
    Restaurant,
    Rider,
    Order,
    OrderStatus,
    RiderStatus,
)

from registry import (
    OrderRegistry,
    RiderRegistry,
    RestaurantRegistry,
)

from order_queue import (
    RestaurantOrderQueue,
    UrgentOrderQueue,
)

from graph import LocationGraph

from dispatch import (
    select_best_rider_heap,
    assign_rider_to_order,
    complete_delivery,
)


def build_sample_graph() -> LocationGraph:
    """
    Build a sample road network.

    Edge weights represent estimated travel time in minutes.

    The network intentionally contains an example where the route with
    fewer hops is not necessarily the route with the lowest travel time.
    """

    graph = LocationGraph()

    locations = [
        "Andheri",
        "Bandra",
        "Khar",
        "Santacruz",
        "Vile Parle",
        "Jogeshwari",
        "Goregaon",
        "Malad",
        "Dadar",
        "Matunga",
        "Kurla",
        "Ghatkopar",
        "Powai",
        "Sion",
        "Worli",
        "Lower Parel",
        "BKC",
        "Chembur",
        "Mulund",
        "Thane",
    ]

    for location in locations:
        graph.add_location(location)

    roads = [
        ("Andheri", "Bandra", 12),
        ("Andheri", "Vile Parle", 8),
        ("Andheri", "Jogeshwari", 7),

        ("Bandra", "Khar", 5),
        ("Bandra", "Santacruz", 6),
        ("Bandra", "BKC", 7),

        ("Khar", "Santacruz", 4),
        ("Santacruz", "Vile Parle", 5),

        ("Vile Parle", "Jogeshwari", 6),
        ("Jogeshwari", "Goregaon", 5),
        ("Goregaon", "Malad", 6),

        ("Bandra", "Dadar", 15),
        ("Dadar", "Matunga", 6),
        ("Dadar", "Sion", 8),

        ("Matunga", "Kurla", 7),
        ("Kurla", "Ghatkopar", 8),
        ("Kurla", "BKC", 6),

        ("Ghatkopar", "Powai", 9),
        ("Powai", "Mulund", 14),

        ("Sion", "Chembur", 9),
        ("Chembur", "Kurla", 7),

        ("Dadar", "Worli", 10),
        ("Worli", "Lower Parel", 7),
        ("Lower Parel", "BKC", 12),

        ("BKC", "Kurla", 6),
        ("Mulund", "Thane", 10),
    ]

    for a, b, travel_time in roads:
        graph.add_road(a, b, travel_time)

    return graph


def build_sample_riders() -> list[Rider]:
    """Create riders at different locations in the network."""

    return [
        Rider(
            id="R001",
            name="Aarav",
            current_location="Andheri",
        ),
        Rider(
            id="R002",
            name="Riya",
            current_location="Bandra",
        ),
        Rider(
            id="R003",
            name="Kabir",
            current_location="Dadar",
        ),
        Rider(
            id="R004",
            name="Neha",
            current_location="Kurla",
        ),
        Rider(
            id="R005",
            name="Arjun",
            current_location="Ghatkopar",
        ),
        Rider(
            id="R006",
            name="Meera",
            current_location="Goregaon",
        ),
    ]


def build_sample_orders(
    restaurants: list[Restaurant],
    customers: list[Customer],
) -> list[Order]:
    """Create a small set of normal and urgent orders."""

    return [
        Order(
            id="O001",
            customer=customers[0],
            restaurant=restaurants[0],
            is_urgent=False,
        ),
        Order(
            id="O002",
            customer=customers[1],
            restaurant=restaurants[1],
            is_urgent=True,
        ),
        Order(
            id="O003",
            customer=customers[2],
            restaurant=restaurants[2],
            is_urgent=False,
        ),
        Order(
            id="O004",
            customer=customers[3],
            restaurant=restaurants[0],
            is_urgent=False,
        ),
    ]


def _print_route(route: list[str]) -> str:
    """Convert a route list into readable text."""
    return " -> ".join(route)


def run_simulation() -> None:
    """Run the complete food-delivery simulation."""

    print("=" * 70)
    print("FOOD DELIVERY ORDER & RIDER DISPATCH SIMULATION")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. Build road network
    # ---------------------------------------------------------

    graph = build_sample_graph()

    print(f"\nRoad network: {len(graph._adj)} locations")

    # ---------------------------------------------------------
    # 2. Create registries
    # ---------------------------------------------------------

    order_registry = OrderRegistry()
    rider_registry = RiderRegistry()
    restaurant_registry = RestaurantRegistry()

    # ---------------------------------------------------------
    # 3. Create restaurants
    # ---------------------------------------------------------

    restaurants = [
        Restaurant(
            id="REST001",
            name="Spice Kitchen",
            location="Bandra",
        ),
        Restaurant(
            id="REST002",
            name="Burger House",
            location="Andheri",
        ),
        Restaurant(
            id="REST003",
            name="Pizza Point",
            location="Kurla",
        ),
    ]

    for restaurant in restaurants:
        restaurant_registry.add(
            restaurant.id,
            restaurant,
        )

    # ---------------------------------------------------------
    # 4. Create customers
    # ---------------------------------------------------------

    customers = [
        Customer(
            id="C001",
            name="Devan",
            location="Dadar",
        ),
        Customer(
            id="C002",
            name="Rahul",
            location="Powai",
        ),
        Customer(
            id="C003",
            name="Sneha",
            location="Goregaon",
        ),
        Customer(
            id="C004",
            name="Aditya",
            location="Thane",
        ),
    ]

    # ---------------------------------------------------------
    # 5. Create riders
    # ---------------------------------------------------------

    riders = build_sample_riders()

    for rider in riders:
        rider_registry.add(
            rider.id,
            rider,
        )

    # ---------------------------------------------------------
    # 6. Create orders
    # ---------------------------------------------------------

    orders = build_sample_orders(
        restaurants,
        customers,
    )

    for order in orders:
        order_registry.add(
            order.id,
            order,
        )

    # ---------------------------------------------------------
    # 7. Create FIFO queues for each restaurant
    # ---------------------------------------------------------

    restaurant_queues: dict[str, RestaurantOrderQueue] = {}

    for restaurant in restaurants:
        restaurant_queues[restaurant.id] = RestaurantOrderQueue()

    urgent_queue = UrgentOrderQueue()

    # ---------------------------------------------------------
    # 8. Put orders into their restaurant queues
    # ---------------------------------------------------------

    for order in orders:
        order.status = OrderStatus.QUEUED

        if order.is_urgent:
            urgent_queue.push(order, priority=1)
        else:
            restaurant_queues[
                order.restaurant.id
            ].enqueue(order)

    # ---------------------------------------------------------
    # 9. Process urgent order first
    # ---------------------------------------------------------

    processing_order: list[Order] = []

    urgent_order = urgent_queue.pop()

    if urgent_order is not None:
        processing_order.append(urgent_order)

    # ---------------------------------------------------------
    # 10. Process normal restaurant queues
    # ---------------------------------------------------------

    for restaurant in restaurants:
        queue = restaurant_queues[restaurant.id]

        while len(queue) > 0:
            order = queue.dequeue()

            if order is not None:
                processing_order.append(order)

    # ---------------------------------------------------------
    # 11. Dispatch each order
    # ---------------------------------------------------------

    delivered_count = 0
    failed_count = 0
    total_eta = 0.0

    print("\n" + "-" * 70)
    print("ORDER PROCESSING")
    print("-" * 70)

    for order in processing_order:

        # Mark the order as being prepared.
        order.status = OrderStatus.PREPARING

        # Once the kitchen finishes, it waits for a rider.
        order.status = OrderStatus.AWAITING_RIDER

        # Find all currently idle riders.
        idle_riders = rider_registry.idle_riders()

        # Select the best rider using the heap-based dispatcher.
        rider = select_best_rider_heap(
            idle_riders,
            order.restaurant.location,
            graph,
        )

        if rider is None:
            order.status = OrderStatus.FAILED
            failed_count += 1

            print(
                f"\n{order.id}: FAILED - no reachable idle rider"
            )

            continue

        # Assign rider and calculate complete route.
        try:
            assign_rider_to_order(
                order,
                rider,
                graph,
            )
        except ValueError as error:
            order.status = OrderStatus.FAILED
            failed_count += 1

            print(f"\n{order.id}: FAILED - {error}")

            continue

        print(f"\nOrder: {order.id}")
        print(f"Customer: {order.customer.name}")
        print(f"Restaurant: {order.restaurant.name}")
        print(f"Assigned Rider: {rider.name} ({rider.id})")
        print(f"Urgent: {'Yes' if order.is_urgent else 'No'}")
        print(f"Route: {_print_route(order.route)}")
        print(f"ETA: {order.eta_minutes:.1f} minutes")
        print(f"Status: {order.status.value}")

        # Simulate delivery completion.
        complete_delivery(
            order,
            rider,
        )

        delivered_count += 1

        if order.eta_minutes is not None:
            total_eta += order.eta_minutes

        print(f"Final Status: {order.status.value}")

    # ---------------------------------------------------------
    # 12. Final summary
    # ---------------------------------------------------------

    average_eta = (
        total_eta / delivered_count
        if delivered_count > 0
        else 0.0
    )

    print("\n" + "=" * 70)
    print("END-OF-RUN SUMMARY")
    print("=" * 70)

    print(f"Total orders:       {len(orders)}")
    print(f"Delivered orders:   {delivered_count}")
    print(f"Failed orders:      {failed_count}")
    print(f"Average ETA:        {average_eta:.2f} minutes")

    print("\nFinal rider status:")

    for rider in rider_registry.all():
        print(
            f"  {rider.id} - {rider.name}: "
            f"{rider.status.value} "
            f"(location: {rider.current_location})"
        )

    print("\nFinal order status:")

    for order in order_registry.all():
        print(
            f"  {order.id}: {order.status.value}"
        )

    print("=" * 70)


if __name__ == "__main__":
    run_simulation()