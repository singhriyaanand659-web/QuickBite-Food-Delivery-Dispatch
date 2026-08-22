import unittest
from graph import LocationGraph
from models import Rider, RiderStatus
from dispatch import select_best_rider_linear_scan, select_best_rider_heap


class TestDispatch(unittest.TestCase):
    def setUp(self):
        self.g = LocationGraph()
        for n in "ABCD":
            self.g.add_location(n)
        self.g.add_road("A", "B", 5)
        self.g.add_road("B", "C", 2)
        self.g.add_road("A", "D", 1)
        self.g.add_road("D", "C", 1)
        self.riders = [
            Rider("R1", "One", "A"),
            Rider("R2", "Two", "B"),
            Rider("R3", "Three", "C", RiderStatus.OFFLINE),
        ]

    def test_both_methods_agree(self):
        linear = select_best_rider_linear_scan(self.riders, "C", self.g)
        heap = select_best_rider_heap(self.riders, "C", self.g)
        self.assertIsNotNone(linear)
        self.assertIsNotNone(heap)
        self.assertEqual(linear.id, heap.id)


if __name__ == "__main__":
    unittest.main()
