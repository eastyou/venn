"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import (
    KINDS,
    RULES,
    SIZES,
    VennError,
    build_worksheet,
)
from .render import render_worksheet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="venn",
        description="韦恩图：集合规则、交集并集差集与可打印练习纸",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("rules", help="列出可用的集合规则")

    sheet_parser = subparsers.add_parser("sheet", help="生成练习纸 HTML")
    sheet_parser.add_argument("--count", type=int, default=12, help="题目数量，默认 12")
    sheet_parser.add_argument(
        "--size", type=int, default=3, choices=SIZES, help="集合数量，默认 3"
    )
    sheet_parser.add_argument("--seed", type=int, default=None, help="随机种子")
    sheet_parser.add_argument(
        "--kinds",
        default=",".join(KINDS),
        help="题型，用逗号分隔：only、intersection、union、difference",
    )
    sheet_parser.add_argument("--title", default="韦恩图练习", help="练习纸标题")
    sheet_parser.add_argument("--answers", action="store_true", help="追加参考答案")
    sheet_parser.add_argument("-o", "--output", default=None, help="输出文件")
    return parser


def _write_output(text: str, output: Optional[str]) -> None:
    if not output:
        print(text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("已写入 %s" % path)


def _parse_kinds(text: str) -> List[str]:
    parts = [part.strip() for part in text.split(",") if part.strip()]
    if not parts:
        raise VennError("至少需要一种题型")
    return parts


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "rules":
            print("可用集合规则（全集 1–30）：")
            for index, rule in enumerate(RULES):
                print("%d. %s" % (index, rule.label))
            return 0
        kinds = _parse_kinds(args.kinds)
        items = build_worksheet(args.count, args.size, args.seed, kinds)
        _write_output(render_worksheet(items, args.title, args.answers), args.output)
        return 0
    except VennError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
