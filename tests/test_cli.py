"""命令行测试。"""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from venn.cli import main


def run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class RulesCommandTest(unittest.TestCase):
    def test_lists_rules(self):
        code, out, _ = run_cli(["rules"])
        self.assertEqual(code, 0)
        self.assertIn("偶数", out)
        self.assertIn("3 的倍数", out)

    def test_all_rules(self):
        code, out, _ = run_cli(["rules"])
        self.assertEqual(code, 0)
        for label in ("5 的倍数", "7 的倍数", "大于 15", "小于 10", "个位是 0"):
            self.assertIn(label, out)


class SheetCommandTest(unittest.TestCase):
    def test_stdout(self):
        code, out, _ = run_cli(["sheet", "--count", "2", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)

    def test_item_count(self):
        code, out, _ = run_cli(["sheet", "--count", "6", "--seed", "2"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count('class="item"'), 6)

    def test_two_sets(self):
        code, out, _ = run_cli(["sheet", "--count", "3", "--size", "2", "--seed", "3"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count("<circle"), 6)

    def test_three_sets(self):
        code, out, _ = run_cli(["sheet", "--count", "3", "--size", "3", "--seed", "3"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count("<circle"), 9)

    def test_answers(self):
        code, out, _ = run_cli(["sheet", "--count", "3", "--seed", "4", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_writes_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "sheet.html")
            code, out, _ = run_cli(["sheet", "--count", "2", "--seed", "5", "-o", target])
            self.assertEqual(code, 0)
            self.assertIn("已写入", out)
            self.assertTrue(os.path.exists(target))

    def test_nested_output(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "a", "b", "sheet.html")
            code, _, _ = run_cli(["sheet", "--count", "1", "-o", target])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(target))

    def test_custom_title(self):
        code, out, _ = run_cli(["sheet", "--count", "1", "--title", "集合小测"])
        self.assertEqual(code, 0)
        self.assertIn("集合小测", out)

    def test_invalid_count(self):
        code, _, err = run_cli(["sheet", "--count", "0"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_invalid_kind(self):
        code, _, err = run_cli(["sheet", "--kinds", "guess"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_invalid_size(self):
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                main(["sheet", "--size", "4"])
        self.assertEqual(ctx.exception.code, 2)

    def test_seed_reproducible(self):
        _, first, _ = run_cli(["sheet", "--count", "4", "--seed", "9"])
        _, second, _ = run_cli(["sheet", "--count", "4", "--seed", "9"])
        self.assertEqual(first, second)


class HelpTest(unittest.TestCase):
    def test_help_exits_zero(self):
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                main(["--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
