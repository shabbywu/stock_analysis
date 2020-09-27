# -*- coding: utf-8 -*-
from operator import eq, gt, ge, lt, le, ne
from aenum import Enum, skip


class MarketType(str, Enum):
    HK = "HK"
    US = "US"
    SH = "SH"
    SZ = "SZ"
    HK_FUTURE = "HK_FUTURE"
    NONE = "N/A"


class StockFinancialType(Enum):
    annual = "annual"
    first_quarter = "first_quarter"
    interim = "interim"
    third_quarter = "third_quarter"


class IntervalType(str, Enum):
    """单位时间长度"""

    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    ONE_DAY = "1d"
    FIVE_DAY = "5d"


class AlertOperator(str, Enum):
    """阈值告警对比逻辑"""

    EQ = "=="
    NEQ = "!="
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="

    operator_maps = skip({EQ: eq, NEQ: ne, GT: gt, GTE: ge, LT: lt, LTE: le})

    def __call__(self, left, right):
        return self.operator_maps[self](left, right)
