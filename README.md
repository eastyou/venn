# venn

[![CI](https://github.com/eastyou/venn/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/venn/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

韦恩图：2 / 3 集合的交集、并集、差集题目，自动生成 SVG 图与可打印练习纸。

## 特性

- 全集 1–30，内置 8 条集合规则：倍数、大小比较、个位数字
- 支持 2 圆与 3 圆韦恩图，圆外标注集合名称
- 四种题型：只在集合中、交集、并集、差集
- 每题自动避开空答案，答案按集合比较，顺序无关
- A4 练习纸，可选参考答案与元素个数
- 纯标准库，零依赖，跨平台

## 安装

```bash
python -m pip install -e .
```

## 用法

```bash
venn rules
venn sheet --count 12 --size 3 --seed 3 --answers -o sheet.html
venn sheet --count 10 --size 2 --kinds union,difference -o two-sets.html
```

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `--count` | 题目数量 | 12 |
| `--size` | 集合数量，2 或 3 | 3 |
| `--kinds` | 题型，逗号分隔 | 四种都出 |
| `--seed` | 随机种子 | 无 |
| `--answers` | 追加参考答案 | 关闭 |

## 题型

- `only`：只属于某个集合，且不属于其他集合
- `intersection`：同时属于指定集合
- `union`：属于指定集合中的任意一个
- `difference`：属于第一个集合但不属于第二个

## 示例

- [examples/venn.html](examples/venn.html)：12 道三集合题，带答案
- [examples/venn-two-sets.html](examples/venn-two-sets.html)：10 道两集合题，带答案

## 测试

```bash
python -m unittest discover -s tests -v
```

## 说明

集合规则按整数判断，答案中的数字属于全集 1–30。交集题包含同时属于其他集合的元素，与教材中“公共部分”的通常含义一致。

## 协议

MIT © 2026 eastyou
