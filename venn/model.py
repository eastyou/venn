"""韦恩图：集合规则、区域计算与练习题。"""

from __future__ import annotations

import itertools
import random
import re
from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional, Sequence, Tuple

KINDS = ("only", "intersection", "union", "difference")
SIZES = (2, 3)
UNIVERSE: Tuple[int, ...] = tuple(range(1, 31))
LETTERS = ("A", "B", "C")


class VennError(ValueError):
    """韦恩图相关的输入错误。"""


@dataclass(frozen=True)
class SetRule:
    """一条集合规则，例如“偶数”或“3 的倍数”。"""

    label: str
    kind: str
    param: int

    def __post_init__(self) -> None:
        if not isinstance(self.label, str) or not self.label.strip():
            raise VennError("规则名称不能为空")
        if self.kind not in ("multiple", "greater", "less", "unit"):
            raise VennError("未知规则类型：%s" % self.kind)
        if isinstance(self.param, bool) or not isinstance(self.param, int):
            raise VennError("规则参数必须是整数")

    def contains(self, number: int) -> bool:
        if self.kind == "multiple":
            return number % self.param == 0
        if self.kind == "greater":
            return number > self.param
        if self.kind == "less":
            return number < self.param
        return number % 10 == self.param


RULES: Tuple[SetRule, ...] = (
    SetRule("偶数", "multiple", 2),
    SetRule("3 的倍数", "multiple", 3),
    SetRule("5 的倍数", "multiple", 5),
    SetRule("7 的倍数", "multiple", 7),
    SetRule("大于 15", "greater", 15),
    SetRule("小于 10", "less", 10),
    SetRule("个位是 5", "unit", 5),
    SetRule("个位是 0", "unit", 0),
)


def _check_index(index: int, size: int) -> int:
    if isinstance(index, bool) or not isinstance(index, int):
        raise VennError("集合序号必须是整数")
    if index < 0 or index >= size:
        raise VennError("集合序号越界：%d" % index)
    return index


@dataclass(frozen=True)
class Venn:
    """2 个或 3 个集合的韦恩图。"""

    rules: Tuple[SetRule, ...]
    universe: Tuple[int, ...] = UNIVERSE

    def __post_init__(self) -> None:
        if not isinstance(self.rules, tuple) or len(self.rules) not in SIZES:
            raise VennError("韦恩图需要 2 个或 3 个集合")
        for rule in self.rules:
            if not isinstance(rule, SetRule):
                raise VennError("集合必须是 SetRule")
        if not isinstance(self.universe, tuple) or not self.universe:
            raise VennError("全集不能为空")
        for number in self.universe:
            if isinstance(number, bool) or not isinstance(number, int):
                raise VennError("全集元素必须是整数")

    @property
    def size(self) -> int:
        return len(self.rules)

    @property
    def letters(self) -> Tuple[str, ...]:
        return LETTERS[: self.size]

    def label(self, index: int) -> str:
        _check_index(index, self.size)
        return "%s（%s）" % (self.letters[index], self.rules[index].label)

    def memberships(self) -> List[Tuple[int, FrozenSet[int]]]:
        """返回每个元素及其所属集合的序号集合。"""
        rows: List[Tuple[int, FrozenSet[int]]] = []
        for number in self.universe:
            keys = frozenset(
                index
                for index, rule in enumerate(self.rules)
                if rule.contains(number)
            )
            rows.append((number, keys))
        return rows

    def region(self, indexes: FrozenSet[int]) -> List[int]:
        """返回恰好属于这些集合、且不属于其余集合的元素。"""
        for index in indexes:
            _check_index(index, self.size)
        return [
            number
            for number, keys in self.memberships()
            if keys == indexes
        ]

    def only(self, index: int) -> List[int]:
        _check_index(index, self.size)
        return self.region(frozenset((index,)))

    def intersection(self, indexes: Sequence[int]) -> List[int]:
        if not indexes:
            raise VennError("至少需要一个集合")
        chosen = {_check_index(index, self.size) for index in indexes}
        return [
            number
            for number, keys in self.memberships()
            if chosen <= keys
        ]

    def union(self, indexes: Sequence[int]) -> List[int]:
        if not indexes:
            raise VennError("至少需要一个集合")
        chosen = {_check_index(index, self.size) for index in indexes}
        return [
            number
            for number, keys in self.memberships()
            if keys & chosen
        ]

    def difference(self, first: int, second: int) -> List[int]:
        _check_index(first, self.size)
        _check_index(second, self.size)
        if first == second:
            raise VennError("差集的两个集合不能相同")
        return [
            number
            for number, keys in self.memberships()
            if first in keys and second not in keys
        ]

    def counts(self) -> Dict[FrozenSet[int], int]:
        result: Dict[FrozenSet[int], int] = {}
        for _, keys in self.memberships():
            result[keys] = result.get(keys, 0) + 1
        return result


def _join_labels(labels: Sequence[str], connector: str) -> str:
    if len(labels) == 1:
        return labels[0]
    return "%s%s%s" % ("、".join(labels[:-1]), connector, labels[-1])


def _answer_for(venn: Venn, kind: str, indexes: Tuple[int, ...]) -> List[int]:
    if kind == "only":
        return venn.only(indexes[0])
    if kind == "intersection":
        return venn.intersection(indexes)
    if kind == "union":
        return venn.union(indexes)
    return venn.difference(indexes[0], indexes[1])


@dataclass(frozen=True)
class WorksheetItem:
    """一道集合题。"""

    kind: str
    venn: Venn
    indexes: Tuple[int, ...]

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise VennError("未知题型：%s" % self.kind)
        if not isinstance(self.venn, Venn):
            raise VennError("缺少韦恩图")
        if not isinstance(self.indexes, tuple) or not self.indexes:
            raise VennError("缺少集合序号")
        for index in self.indexes:
            _check_index(index, self.venn.size)
        if self.kind == "only" and len(self.indexes) != 1:
            raise VennError("only 题型只需要一个集合")
        if self.kind == "difference" and len(self.indexes) != 2:
            raise VennError("difference 题型需要两个集合")
        if self.kind == "difference" and self.indexes[0] == self.indexes[1]:
            raise VennError("差集的两个集合不能相同")
        if len(set(self.indexes)) != len(self.indexes):
            raise VennError("集合序号不能重复")

    @property
    def answer_numbers(self) -> List[int]:
        return _answer_for(self.venn, self.kind, self.indexes)

    @property
    def answer_text(self) -> str:
        numbers = self.answer_numbers
        if not numbers:
            return "无"
        return "、".join(str(number) for number in numbers)

    @property
    def prompt(self) -> str:
        labels = [self.venn.label(index) for index in self.indexes]
        if self.kind == "only":
            body = "只在%s中" % labels[0]
        elif self.kind == "intersection":
            body = "同时属于 %s" % _join_labels(labels, "和")
        elif self.kind == "union":
            body = "属于 %s" % _join_labels(labels, "或")
        else:
            body = "属于 %s 但不属于 %s" % (labels[0], labels[1])
        return "%s的数有哪些？" % body


def parse_numbers(text: str) -> List[int]:
    """从答案中提取整数，支持顿号、逗号与空格分隔。"""
    if not isinstance(text, str):
        return []
    return [int(value) for value in re.findall(r"\d+", text)]


def check_answer(item: WorksheetItem, text: str) -> bool:
    """按集合比较答案，顺序无关。"""
    if not isinstance(item, WorksheetItem) or not isinstance(text, str):
        return False
    cleaned = text.strip()
    if not cleaned:
        return False
    if not re.search(r"\d", cleaned):
        return cleaned in ("无", "没有", "空", "空集", "∅")
    return sorted(set(parse_numbers(cleaned))) == sorted(set(item.answer_numbers))


def _index_combos(size: int, kind: str) -> List[Tuple[int, ...]]:
    if kind == "only":
        return [(index,) for index in range(size)]
    if kind == "difference":
        return [
            (first, second)
            for first in range(size)
            for second in range(size)
            if first != second
        ]
    combos: List[Tuple[int, ...]] = []
    for length in range(2, size + 1):
        combos.extend(itertools.combinations(range(size), length))
    return combos


def _candidates(size: int, kinds: Sequence[str]) -> List[Tuple[str, Tuple[int, ...], Tuple[int, ...]]]:
    rows: List[Tuple[str, Tuple[int, ...], Tuple[int, ...]]] = []
    for rule_indexes in itertools.combinations(range(len(RULES)), size):
        venn = Venn(tuple(RULES[index] for index in rule_indexes))
        for kind in kinds:
            for indexes in _index_combos(size, kind):
                if _answer_for(venn, kind, indexes):
                    rows.append((kind, rule_indexes, indexes))
    return rows


def build_worksheet(
    count: int = 12,
    size: int = 3,
    seed: Optional[int] = None,
    kinds: Sequence[str] = KINDS,
) -> List[WorksheetItem]:
    """随机抽取集合题，每题都有非空答案。"""
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise VennError("题目数量必须是正整数")
    if isinstance(size, bool) or not isinstance(size, int) or size not in SIZES:
        raise VennError("集合数量只能是 2 或 3")
    if not kinds:
        raise VennError("至少需要一种题型")
    for kind in kinds:
        if kind not in KINDS:
            raise VennError("未知题型：%s" % kind)
    pool = _candidates(size, kinds)
    if count > len(pool):
        raise VennError("可用题目不足 %d 道" % count)
    rng = random.Random(seed)
    chosen = rng.sample(pool, count)
    return [
        WorksheetItem(kind=kind, venn=Venn(tuple(RULES[i] for i in rule_indexes)), indexes=indexes)
        for kind, rule_indexes, indexes in chosen
    ]
