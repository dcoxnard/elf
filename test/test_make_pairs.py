import unittest
import inspect
import operator

from make_pairs import make_pairs


class TestMakeParis(unittest.TestCase):

    cases = {
        "null_case": {"items": [], "partition": {}, "not_allowed_map": {}},
        "2_item_case": {
            "items": ["item1", "item2"],
            "partition": {"item1": "A", "item2": "B"},
            "not_allowed_map": {}
        },
        "3_item_case": {
            "items": ["item1", "item2", "item3"],
            "partition": {"item1": "A", "item2": "B", "item3": "C"},
            "not_allowed_map": {}
        },
        "15_item_case": {
            "items": [f"item{i}" for i in range(1, 16)],
            "partition": {f"item{i}": chr(64 + i) for i in range(1, 16)},
            "not_allowed_map": {}
        },
        "realistic_case": {
            "items": ["AA", "AB", "AC", "AD", "BA", "CA", "CB", "CC", "CD", "DA"],
            "partition": {
                "AA": "A",
                "AB": "A",
                "AC": "A",
                "AD": "A",
                "BA": "B",
                "CA": "A",
                "CB": "C",
                "CC": "C",
                "CD": "C",
                "DA": "D"
            },
            "not_allowed_map": {}
        },
        "realistic_case_with_excl": {
            "items": ["AA", "AB", "AC", "AD", "BA", "CA", "CB", "CC", "CD", "DA"],
            "partition": {
                "AA": "A",
                "AB": "A",
                "AC": "A",
                "AD": "A",
                "BA": "B",
                "CA": "A",
                "CB": "C",
                "CC": "C",
                "CD": "C",
                "DA": "D"
            },
            "not_allowed_map": {
                "AA": "AB",
                "AB": "AC",
                "AC": "AD",
                "AD": "CA",
                "BA": "DA",
                "CA": "CB",
                "CB": "CC",
                "CC": "CD",
                "CD": "AA",
                "DA": "BA"
            }
        },
        # AC and BC are new
        "new_joiners": {
            "items": ["AA", "AB", "AC", "BA", "BB", "BC"],
            "partition": {
                "AA": "A",
                "AB": "A",
                "AC": "A",
                "BA": "B",
                "BB": "B",
                "BC": "B",
            },
            "not_allowed_map": {
                "AA": "BA",
                "AB": "BB",
                "AC": None,
                "BA": "AB",
                "BB": "AA",
                "BC": None
            }
        },
        # AC and BC have left
        "leavers": {
            "items": ["AA", "AB", "BA", "BB"],
            "partition": {
                "AA": "A",
                "AB": "A",
                "BA": "B",
                "BB": "B",
            },
            "not_allowed_map": {
                "AA": "BC",
                "AB": "BB",
                "BA": "AC",
                "BB": "AB",
            }
        }
    }

    def get_case(self, case_name):
        case = self.cases[case_name]
        args = operator.itemgetter("items", "partition", "not_allowed_map")(case)
        return args

    def test_cases_are_good(self):
        function_signature = inspect.signature(make_pairs)
        required = sorted(list(function_signature.parameters.keys()))
        for case_name, argset in self.cases.items():
            argnames = sorted(list(argset.keys()))
            with self.subTest(case=case_name):
                self.assertEqual(argnames, required)

    def test_null(self):
        items, partition, not_allowed_map = self.get_case("null_case")
        pairs = make_pairs(items, partition, not_allowed_map)
        self.assertEqual(len(pairs), 0)

    def test_simple(self):
        """
        Explicitly test a simple 2-node case

        Should be equivalent to (item1) --> (item2) --> (item1)
        """
        items, partition, not_allowed_map = self.get_case("2_item_case")
        pairs = make_pairs(items, partition, not_allowed_map)
        item1_pair = [p for p in pairs if p[0] == "item1"][0]
        item2_pair = [p for p in pairs if p[0] == "item2"][0]
        self.assertEqual(item1_pair[1], "item2")
        self.assertEqual(item2_pair[1], "item1")

    def test_does_not_map_self(self):
        """
        Test that no item gets paired with itself
        """
        for case_name, args in self.cases.items():
            with self.subTest(case=case_name):
                pairs = make_pairs(**args)
                map_other = [left != right for left, right in pairs]
                self.assertTrue(all(map_other))

    def test_does_not_map_same_partition(self):
        """
        Test that no item gets matched to another item in the same partition
        """
        for case_name, args in self.cases.items():
            with self.subTest(case=case_name):
                p = args["partition"]
                pairs = make_pairs(**args)
                mapped_partitions = [[p[lft], p[rt]] for lft, rt in pairs]
                different_partition = [p1 != p2 for p1, p2 in mapped_partitions]
                self.assertTrue(all(different_partition))

    def test_each_only_paired_once_left(self):
        """
        Test that every item appears once on the left side
        """
        for case_name, args in self.cases.items():
            with self.subTest(case=case_name):
                pairs = make_pairs(**args)
                lefts = sorted([pair[0] for pair in pairs])
                self.assertEqual(lefts, sorted(args["items"]))

    def test_each_only_paired_once_right(self):
        """
        Test that every item appears once on the right side
        """
        for case_name, args in self.cases.items():
            with self.subTest(case=case_name):
                pairs = make_pairs(**args)
                rights = sorted([pair[1] for pair in pairs])
                self.assertEqual(rights, sorted(args["items"]))

    def test_doesnt_map_excls(self):
        """
        Test that the pairing doesn't allow non-allowed items to pair up
        :return:
        """
        for case_name, args in self.cases.items():
            with self.subTest(case=case_name):
                not_allowed_map = args["not_allowed_map"]
                pairs = make_pairs(**args)
                not_excl = [not_allowed_map.get(pair[0]) != pairs[1] for pair in pairs]
        self.assertTrue(all(not_excl))
