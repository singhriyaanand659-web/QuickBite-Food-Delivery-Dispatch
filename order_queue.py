"""
FIFO order queue per restaurant, plus an optional priority queue for urgent
orders.

FIFO: use collections.deque, NOT list.pop(0) -- that's the exact O(n) mistake
you benchmark against in experiments/bench_queue.py.

Priority queue: use heapq. Only build this out if you're actually using
"urgent" orders in your simulation.
"""

from collections import deque
from dataclasses import dataclass, field
import heapq

from models import Order


class RestaurantOrderQueue:
    """FIFO queue of orders waiting to be prepared at one restaurant."""

    def __init__(self):
        self._queue: deque[Order] = deque()

    def enqueue(self, order: Order) -> None:
        """Add a new order to the back of the queue."""
        self._queue.append(order)

    def dequeue(self) -> Order | None:
        """
        Remove and return the next order to prepare.

        Returns None if the queue is empty.
        """
        if not self._queue:
            return None

        return self._queue.popleft()

    def __len__(self) -> int:
        """Return the number of orders currently waiting."""
        return len(self._queue)


@dataclass(order=True)
class _PrioritizedOrder:
    """
    Wrapper so heapq can compare by priority without comparing
    Order objects directly.
    """

    priority: int
    order: Order = field(compare=False)


class UrgentOrderQueue:
    """
    Min-heap priority queue for urgent orders.

    Lower `priority` value = handled sooner.
    """

    def __init__(self):
        self._heap: list[_PrioritizedOrder] = []

    def push(self, order: Order, priority: int) -> None:
        """Add an order with a given priority."""
        heapq.heappush(
            self._heap,
            _PrioritizedOrder(priority, order)
        )

    def pop(self) -> Order | None:
        """
        Remove and return the highest-priority order.

        Lower priority value is handled first.
        Returns None if the queue is empty.
        """
        if not self._heap:
            return None

        prioritized_order = heapq.heappop(self._heap)
        return prioritized_order.order

    def __len__(self) -> int:
        """Return the number of urgent orders waiting."""
        return len(self._heap)