"""韦恩图渲染测试。"""

import unittest

from venn.model import RULES, Venn, WorksheetItem
from venn.render import render_venn_svg, render_worksheet


class VennSvgTest(unittest.TestCase):
    def setUp(self):
        self.venn3 = Venn((RULES[0], RULES[1], RULES[2]))
        self.venn2 = Venn((RULES[0], RULES[1]))

    def test_three_circles(self):
        self.assertEqual(render_venn_svg(self.venn3).count("<circle"), 3)

    def test_two_circles(self):
        self.assertEqual(render_venn_svg(self.venn2).count("<circle"), 2)

    def test_aria_label(self):
        self.assertIn('aria-label="3 集合韦恩图"', render_venn_svg(self.venn3))
        self.assertIn('aria-label="2 集合韦恩图"', render_venn_svg(self.venn2))

    def test_labels(self):
        svg = render_venn_svg(self.venn3)
        self.assertIn("A 偶数", svg)
        self.assertIn("B 3 的倍数", svg)
        self.assertIn("C 5 的倍数", svg)

    def test_role(self):
        self.assertIn('role="img"', render_venn_svg(self.venn2))


class WorksheetTest(unittest.TestCase):
    def setUp(self):
        venn = Venn((RULES[0], RULES[1], RULES[2]))
        self.items = [
            WorksheetItem("only", venn, (0,)),
            WorksheetItem("intersection", venn, (0, 1)),
        ]

    def test_doctype(self):
        self.assertTrue(render_worksheet(self.items).startswith("<!DOCTYPE html>"))

    def test_item_count(self):
        self.assertEqual(render_worksheet(self.items).count('class="item"'), 2)

    def test_universe(self):
        self.assertIn("全集：1 到 30", render_worksheet(self.items))

    def test_svg_per_item(self):
        self.assertEqual(render_worksheet(self.items).count('class="venn"'), 2)

    def test_prompts(self):
        page = render_worksheet(self.items)
        self.assertIn("只在A（偶数）中", page)
        self.assertIn("同时属于", page)

    def test_no_answers_default(self):
        self.assertNotIn("参考答案", render_worksheet(self.items))

    def test_answers(self):
        page = render_worksheet(self.items, include_answers=True)
        self.assertIn("参考答案", page)
        self.assertIn("6、12、18、24、30", page)

    def test_answer_count(self):
        page = render_worksheet(self.items, include_answers=True)
        self.assertIn("（8 个）", page)
        self.assertIn("（5 个）", page)

    def test_empty(self):
        with self.assertRaises(ValueError):
            render_worksheet([])

    def test_custom_title(self):
        self.assertIn("集合小测", render_worksheet(self.items, title="集合小测"))

    def test_title_escaped(self):
        page = render_worksheet(self.items, title="<集合>")
        self.assertIn("&lt;集合&gt;", page)

    def test_two_set_svg(self):
        venn = Venn((RULES[0], RULES[1]))
        page = render_worksheet([WorksheetItem("union", venn, (0, 1))])
        self.assertEqual(page.count("<circle"), 2)


if __name__ == "__main__":
    unittest.main()
