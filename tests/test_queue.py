import unittest
from models import Customer, Restaurant, Order
from order_queue import RestaurantOrderQueue


class TestQueue(unittest.TestCase):
    def test_fifo(self):
        c = Customer("C1", "A", "A")
        r = Restaurant("R1", "Cafe", "B")
        q = RestaurantOrderQueue()
        a = Order("O1", c, r)
        b = Order("O2", c, r)
        q.enqueue(a)
        q.enqueue(b)
        self.assertIs(q.dequeue(), a)
        self.assertIs(q.dequeue(), b)
        self.assertIsNone(q.dequeue())


if __name__ == "__main__":
    unittest.main()
