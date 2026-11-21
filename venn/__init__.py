"""韦恩图：集合规则、区域计算与可打印练习纸。"""

from .model import (
    KINDS,
    LETTERS,
    RULES,
    SIZES,
    UNIVERSE,
    SetRule,
    Venn,
    VennError,
    WorksheetItem,
    build_worksheet,
    check_answer,
    parse_numbers,
)

__version__ = "0.1.0"

__all__ = [
    "KINDS",
    "LETTERS",
    "RULES",
    "SIZES",
    "UNIVERSE",
    "SetRule",
    "Venn",
    "VennError",
    "WorksheetItem",
    "build_worksheet",
    "check_answer",
    "parse_numbers",
]
