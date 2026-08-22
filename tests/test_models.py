import unittest
from models import Customer, Restaurant, Rider, Order, OrderStatus, RiderStatus


class TestModels(unittest.TestCase):
    def test_default_statuses(self):
        c = Customer("C1", "A", "A")
        r = Restaurant("R1", "Cafe", "B")
        rider = Rider("D1", "Rider", "A")
        order = Order("O1", c, r)
        self.assertEqual(order.status, OrderStatus.PLACED)
        self.assertEqual(rider.status, RiderStatus.IDLE)


if __name__ == "__main__":
    unittest.main()
