import unittest
from registry import Registry


class TestRegistry(unittest.TestCase):
    def test_add_get_remove(self):
        registry = Registry()
        obj = object()
        registry.add("A", obj)
        self.assertIs(registry.get("A"), obj)
        self.assertEqual(len(registry), 1)
        self.assertIs(registry.remove("A"), obj)
        self.assertIsNone(registry.get("A"))
        self.assertEqual(len(registry), 0)


if __name__ == "__main__":
    unittest.main()
