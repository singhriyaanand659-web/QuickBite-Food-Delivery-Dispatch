import unittest
from graph import LocationGraph


class TestGraph(unittest.TestCase):
    def setUp(self):
        self.g = LocationGraph()
        for n in "ABCDE":
            self.g.add_location(n)
        self.g.add_road("A", "B", 10)
        self.g.add_road("B", "D", 10)
        self.g.add_road("A", "C", 2)
        self.g.add_road("C", "E", 2)
        self.g.add_road("E", "D", 2)

    def test_bfs_fewest_hops(self):
        self.assertEqual(self.g.bfs_shortest_hops("A", "D"), ["A", "B", "D"])

    def test_dijkstra_lowest_weight(self):
        result = self.g.dijkstra_shortest_weighted("A", "D")
        self.assertEqual(result, (["A", "C", "E", "D"], 6))


if __name__ == "__main__":
    unittest.main()
