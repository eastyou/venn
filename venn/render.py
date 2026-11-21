"""韦恩图 SVG 与练习纸渲染。"""

from __future__ import annotations

import html
from typing import List, Sequence

from .model import UNIVERSE, Venn, WorksheetItem

STYLE = """
@page { size: A4 portrait; margin: 14mm 13mm; }
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  color: #1f2937;
  font-size: 11pt;
  line-height: 1.65;
}
h1 { font-size: 21pt; margin: 0 0 1.5mm; }
.sub { color: #6b7280; font-size: 9.5pt; margin: 0 0 5mm; }
ol.items { margin: 0; padding-left: 7mm; }
li.item { margin-bottom: 7mm; page-break-inside: avoid; }
.prompt { margin: 0 0 1mm; }
.prompt .num { color: #b45309; font-weight: 600; margin-right: 1.5mm; }
.venn { height: 46mm; display: block; margin: 0 auto; }
.universe { color: #6b7280; font-size: 9pt; text-align: center; margin: 0 0 2mm; }
.answer-line { color: #475569; font-size: 10pt; }
.blank { display: inline-block; min-width: 100mm; border-bottom: 0.7pt solid #94a3b8; height: 1.1em; }
.answers { page-break-before: always; }
.answers h2 { font-size: 15pt; margin: 0 0 4mm; }
.answers ol { margin: 0; padding-left: 7mm; }
.answers li { margin-bottom: 3.5mm; }
.answers .ans { color: #0f4c81; }
.answers .count { color: #6b7280; font-size: 9.5pt; margin-left: 2mm; }
"""


def _escape(text: str) -> str:
    return html.escape(str(text), quote=True)


def render_venn_svg(venn: Venn) -> str:
    """画 2 圆或 3 圆韦恩图，圆外标注集合名称。"""
    if venn.size == 2:
        width, height = 200, 140
        centers = [(80.0, 70.0), (120.0, 70.0)]
        radius = 46.0
        labels = [(52.0, 133.0), (148.0, 133.0)]
    else:
        width, height = 200, 160
        centers = [(100.0, 48.0), (68.0, 88.0), (132.0, 88.0)]
        radius = 38.0
        labels = [(100.0, 14.0), (40.0, 154.0), (160.0, 154.0)]
    colors = ("#60a5fa", "#f87171", "#fbbf24")
    parts: List[str] = [
        '<svg class="venn" viewBox="0 0 %d %d" role="img" aria-label="%d 集合韦恩图">'
        % (width, height, venn.size)
    ]
    for index, (cx, cy) in enumerate(centers):
        parts.append(
            '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" fill-opacity="0.42" '
            'stroke="%s" stroke-width="0.8"></circle>'
            % (cx, cy, radius, colors[index], colors[index])
        )
    for index, (x, y) in enumerate(labels):
        parts.append(
            '<text x="%.1f" y="%.1f" font-size="6.2" text-anchor="middle" '
            'fill="#334155">%s %s</text>'
            % (x, y, _escape(venn.letters[index]), _escape(venn.rules[index].label))
        )
    parts.append("</svg>")
    return "".join(parts)


def render_worksheet(
    items: Sequence[WorksheetItem],
    title: str = "韦恩图练习",
    include_answers: bool = False,
) -> str:
    """生成 A4 集合练习纸。"""
    if not items:
        raise ValueError("至少需要一道题目")
    universe_text = "全集：%d 到 %d" % (UNIVERSE[0], UNIVERSE[-1])
    rows: List[str] = []
    for index, item in enumerate(items, start=1):
        rows.append(
            '<li class="item"><p class="prompt"><span class="num">%d.</span>%s</p>'
            '<p class="universe">%s</p>%s'
            '<p class="answer-line">答案：<span class="blank"></span></p></li>'
            % (
                index,
                _escape(item.prompt),
                _escape(universe_text),
                render_venn_svg(item.venn),
            )
        )
    body = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % _escape(title),
        "<style>%s</style>" % STYLE,
        "</head>",
        "<body>",
        "<h1>%s</h1>" % _escape(title),
        '<p class="sub">姓名：__________　班级：__________　日期：__________</p>',
        '<ol class="items">',
        "\n".join(rows),
        "</ol>",
    ]
    if include_answers:
        body.extend(_answer_section(items))
    body.extend(["</body>", "</html>"])
    return "\n".join(body)


def _answer_section(items: Sequence[WorksheetItem]) -> List[str]:
    rows: List[str] = []
    for index, item in enumerate(items, start=1):
        numbers = item.answer_numbers
        rows.append(
            '<li><span class="num">%d.</span> <span class="ans">%s</span>'
            '<span class="count">（%d 个）</span></li>'
            % (index, _escape(item.answer_text), len(numbers))
        )
    return [
        '<section class="answers">',
        "<h2>参考答案</h2>",
        "<ol>",
        "\n".join(rows),
        "</ol>",
        "</section>",
    ]
