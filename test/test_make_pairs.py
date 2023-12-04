import unittest

from make_pairs import make_pairs


class TestMakeParis(unittest.TestCase):

    def test_null(self):
        items = []
        partition = {}
        pairs = make_pairs(items, partition)
        self.assertEqual(len(pairs), 0)

    def test_simple(self):
        """
        Test a simple 2-node case

        Should be equivalent to (item1) --> (item2) --> (item1)

        :return:
        """
        items = ["item1", "item2"]
        partition = {"item1": "A", "item2": "B"}
        pairs = make_pairs(items, partition)
        item1_pair = [p for p in pairs if p[0] == "item1"][0]
        item2_pair = [p for p in pairs if p[0] == "item2"][0]
        self.assertEqual(item1_pair[1], "item2")
        self.assertEqual(item2_pair[1], "item1")
