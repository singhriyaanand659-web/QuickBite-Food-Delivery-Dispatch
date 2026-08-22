"""
Hash-map-based registries for O(1) average lookup of orders/riders/restaurants
by id.

This is the structure you benchmark against a plain list scan in
experiments/bench_lookup.py -- see the plan's Model section for why:
dict lookup is O(1) average vs O(n) for scanning a list.
"""

from models import Order, Rider, Restaurant, RiderStatus


class Registry:
    """Generic id -> object store. One instance per entity type."""

    def __init__(self):
        self._items: dict[str, object] = {}

    def add(self, item_id: str, item: object) -> None:
        """Insert or overwrite an item by id."""
        self._items[item_id] = item

    def get(self, item_id: str) -> object | None:
        """Look up an item by id. Return None if not found."""
        return self._items.get(item_id)

    def remove(self, item_id: str) -> object | None:
        """Remove and return an item by id if present."""
        return self._items.pop(item_id, None)

    def all(self) -> list[object]:
        """Return all stored items."""
        return list(self._items.values())

    def __len__(self) -> int:
        """Return the number of stored items."""
        return len(self._items)


class OrderRegistry(Registry):
    """order_id -> Order"""
    pass


class RiderRegistry(Registry):
    """rider_id -> Rider"""

    def idle_riders(self) -> list[Rider]:
        """Return all riders currently idle."""
        return [
            rider
            for rider in self.all()
            if rider.status == RiderStatus.IDLE
        ]


class RestaurantRegistry(Registry):
    """restaurant_id -> Restaurant"""
    pass


def linear_scan_lookup(items: list, item_id: str):
    """
    Naive O(n) lookup used for benchmarking against the hash map.

    Searches through the list one item at a time until the requested
    ID is found.
    """
    for item in items:
        if item.id == item_id:
            return item

    return None