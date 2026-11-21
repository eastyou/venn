"""集合规则、韦恩图区域与出题测试。"""

import unittest
from dataclasses import FrozenInstanceError

from venn.model import (
    KINDS,
    RULES,
    UNIVERSE,
    SetRule,
    Venn,
    VennError,
    WorksheetItem,
    build_worksheet,
    check_answer,
    parse_numbers,
)

EVEN = RULES[0]
THREE = RULES[1]
FIVE = RULES[2]
GREATER = RULES[4]
LESS = RULES[5]


class SetRuleTest(unittest.TestCase):
    def test_multiple(self):
        self.assertTrue(EVEN.contains(4))
        self.assertFalse(EVEN.contains(3))

    def test_greater(self):
        self.assertTrue(GREATER.contains(16))
        self.assertFalse(GREATER.contains(15))

    def test_less(self):
        self.assertTrue(LESS.contains(9))
        self.assertFalse(LESS.contains(10))

    def test_unit(self):
        unit_five = SetRule("个位是 5", "unit", 5)
        unit_zero = SetRule("个位是 0", "unit", 0)
        self.assertTrue(unit_five.contains(25))
        self.assertFalse(unit_five.contains(12))
        self.assertTrue(unit_zero.contains(20))
        self.assertFalse(unit_zero.contains(21))

    def test_invalid_label(self):
        with self.assertRaises(VennError):
            SetRule("", "multiple", 2)

    def test_invalid_kind(self):
        with self.assertRaises(VennError):
            SetRule("测试", "prime", 2)

    def test_invalid_param(self):
        with self.assertRaises(VennError):
            SetRule("测试", "multiple", "2")

    def test_frozen(self):
        with self.assertRaises(FrozenInstanceError):
            EVEN.label = "奇数"


class VennTest(unittest.TestCase):
    def setUp(self):
        self.venn = Venn((EVEN, THREE, FIVE))

    def test_size_and_letters(self):
        self.assertEqual(self.venn.size, 3)
        self.assertEqual(self.venn.letters, ("A", "B", "C"))

    def test_label(self):
        self.assertEqual(self.venn.label(0), "A（偶数）")
        self.assertEqual(self.venn.label(2), "C（5 的倍数）")

    def test_memberships(self):
        by_number = dict(self.venn.memberships())
        self.assertEqual(by_number[30], frozenset({0, 1, 2}))
        self.assertEqual(by_number[6], frozenset({0, 1}))
        self.assertEqual(by_number[10], frozenset({0, 2}))
        self.assertEqual(by_number[15], frozenset({1, 2}))
        self.assertEqual(by_number[7], frozenset())

    def test_region_outside(self):
        outside = self.venn.region(frozenset())
        self.assertEqual(outside, [1, 7, 11, 13, 17, 19, 23, 29])

    def test_region_only_a(self):
        self.assertEqual(self.venn.only(0), [2, 4, 8, 14, 16, 22, 26, 28])

    def test_region_ab_only(self):
        self.assertEqual(self.venn.region(frozenset({0, 1})), [6, 12, 18, 24])

    def test_region_triple(self):
        self.assertEqual(self.venn.region(frozenset({0, 1, 2})), [30])

    def test_intersection_includes_third(self):
        self.assertEqual(self.venn.intersection((0, 1)), [6, 12, 18, 24, 30])

    def test_intersection_triple(self):
        self.assertEqual(self.venn.intersection((0, 1, 2)), [30])

    def test_union(self):
        self.assertEqual(
            self.venn.union((1, 2)),
            [3, 5, 6, 9, 10, 12, 15, 18, 20, 21, 24, 25, 27, 30],
        )

    def test_difference(self):
        self.assertEqual(
            self.venn.difference(0, 1),
            [2, 4, 8, 10, 14, 16, 20, 22, 26, 28],
        )

    def test_counts_sum(self):
        self.assertEqual(sum(self.venn.counts().values()), len(UNIVERSE))

    def test_invalid_index(self):
        for bad in (-1, 3, True, "0"):
            with self.assertRaises(VennError):
                self.venn.only(bad)

    def test_invalid_size(self):
        with self.assertRaises(VennError):
            Venn((EVEN,))

    def test_invalid_rules_type(self):
        with self.assertRaises(VennError):
            Venn([EVEN, THREE])

    def test_empty_universe(self):
        with self.assertRaises(VennError):
            Venn((EVEN, THREE), ())

    def test_intersection_empty_input(self):
        with self.assertRaises(VennError):
            self.venn.intersection(())

    def test_difference_same(self):
        with self.assertRaises(VennError):
            self.venn.difference(1, 1)


class TwoSetTest(unittest.TestCase):
    def setUp(self):
        self.venn = Venn((EVEN, THREE))

    def test_only(self):
        self.assertEqual(self.venn.only(0), [2, 4, 8, 10, 14, 16, 20, 22, 26, 28])

    def test_intersection(self):
        self.assertEqual(self.venn.intersection((0, 1)), [6, 12, 18, 24, 30])

    def test_union(self):
        self.assertEqual(len(self.venn.union((0, 1))), 20)

    def test_difference(self):
        self.assertEqual(self.venn.difference(1, 0), [3, 9, 15, 21, 27])

    def test_letters(self):
        self.assertEqual(self.venn.letters, ("A", "B"))


class WorksheetItemTest(unittest.TestCase):
    def setUp(self):
        self.venn = Venn((EVEN, THREE, FIVE))

    def test_only_prompt(self):
        item = WorksheetItem("only", self.venn, (0,))
        self.assertIn("只在A（偶数）中", item.prompt)

    def test_intersection_prompt(self):
        item = WorksheetItem("intersection", self.venn, (0, 1))
        self.assertIn("同时属于 A（偶数）和B（3 的倍数）", item.prompt)

    def test_triple_prompt(self):
        item = WorksheetItem("intersection", self.venn, (0, 1, 2))
        self.assertIn("A（偶数）、B（3 的倍数）和C（5 的倍数）", item.prompt)

    def test_union_prompt(self):
        item = WorksheetItem("union", self.venn, (0, 1))
        self.assertIn("属于 A（偶数）或B（3 的倍数）", item.prompt)

    def test_difference_prompt(self):
        item = WorksheetItem("difference", self.venn, (0, 1))
        self.assertIn("但不属于 B（3 的倍数）", item.prompt)

    def test_answer_text(self):
        item = WorksheetItem("intersection", self.venn, (0, 1))
        self.assertEqual(item.answer_text, "6、12、18、24、30")

    def test_empty_answer_text(self):
        venn = Venn((GREATER, LESS))
        item = WorksheetItem("intersection", venn, (0, 1))
        self.assertEqual(item.answer_text, "无")
        self.assertEqual(item.answer_numbers, [])

    def test_invalid_kind(self):
        with self.assertRaises(VennError):
            WorksheetItem("guess", self.venn, (0,))

    def test_only_needs_one(self):
        with self.assertRaises(VennError):
            WorksheetItem("only", self.venn, (0, 1))

    def test_difference_needs_two(self):
        with self.assertRaises(VennError):
            WorksheetItem("difference", self.venn, (0,))

    def test_difference_same(self):
        with self.assertRaises(VennError):
            WorksheetItem("difference", self.venn, (0, 0))

    def test_duplicate_indexes(self):
        with self.assertRaises(VennError):
            WorksheetItem("union", self.venn, (0, 0))

    def test_index_out_of_range(self):
        with self.assertRaises(VennError):
            WorksheetItem("only", self.venn, (3,))


class ParseAndCheckTest(unittest.TestCase):
    def test_parse_separators(self):
        self.assertEqual(parse_numbers("2、4、6"), [2, 4, 6])
        self.assertEqual(parse_numbers("2, 4 6"), [2, 4, 6])

    def test_parse_empty(self):
        self.assertEqual(parse_numbers("无"), [])
        self.assertEqual(parse_numbers(None), [])

    def test_check_order_insensitive(self):
        item = WorksheetItem("intersection", Venn((EVEN, THREE)), (0, 1))
        self.assertTrue(check_answer(item, "30、6、12、18、24"))

    def test_check_duplicates_allowed(self):
        item = WorksheetItem("intersection", Venn((EVEN, THREE)), (0, 1))
        self.assertTrue(check_answer(item, "6、6、12、18、24、30"))

    def test_check_wrong(self):
        item = WorksheetItem("intersection", Venn((EVEN, THREE)), (0, 1))
        self.assertFalse(check_answer(item, "6、12"))

    def test_check_none(self):
        item = WorksheetItem("intersection", Venn((GREATER, LESS)), (0, 1))
        self.assertTrue(check_answer(item, "无"))

    def test_check_empty(self):
        item = WorksheetItem("only", Venn((EVEN, THREE)), (0,))
        self.assertFalse(check_answer(item, " "))

    def test_check_non_item(self):
        self.assertFalse(check_answer(None, "1"))


class BuildWorksheetTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(build_worksheet(10, 3, seed=1)), 10)

    def test_two_sets(self):
        for item in build_worksheet(8, 2, seed=2):
            self.assertEqual(item.venn.size, 2)

    def test_three_sets(self):
        for item in build_worksheet(8, 3, seed=3):
            self.assertEqual(item.venn.size, 3)

    def test_all_answers_non_empty(self):
        for item in build_worksheet(20, 3, seed=4):
            self.assertTrue(item.answer_numbers)

    def test_unique(self):
        items = build_worksheet(12, 3, seed=5)
        keys = {
            (item.kind, item.venn.rules, item.indexes) for item in items
        }
        self.assertEqual(len(keys), 12)

    def test_kinds(self):
        for item in build_worksheet(12, 3, seed=6):
            self.assertIn(item.kind, KINDS)

    def test_custom_kinds(self):
        for item in build_worksheet(5, 2, seed=7, kinds=("union",)):
            self.assertEqual(item.kind, "union")

    def test_deterministic(self):
        first = build_worksheet(6, 3, seed=8)
        second = build_worksheet(6, 3, seed=8)
        self.assertEqual(
            [(item.kind, item.venn.rules, item.indexes) for item in first],
            [(item.kind, item.venn.rules, item.indexes) for item in second],
        )

    def test_invalid_count(self):
        for bad in (0, -1, True, "4"):
            with self.assertRaises(VennError):
                build_worksheet(bad)

    def test_invalid_size(self):
        with self.assertRaises(VennError):
            build_worksheet(3, 4)

    def test_invalid_kind(self):
        with self.assertRaises(VennError):
            build_worksheet(3, 3, kinds=("guess",))

    def test_empty_kinds(self):
        with self.assertRaises(VennError):
            build_worksheet(3, 3, kinds=())

    def test_too_many(self):
        with self.assertRaises(VennError):
            build_worksheet(5000, 3)


if __name__ == "__main__":
    unittest.main()
