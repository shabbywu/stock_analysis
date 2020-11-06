# -*- coding: utf-8 -*-
from futu.common.constant import Market


def detect_stock_market(code: str) -> str:
    """探测股票属于哪个市场"""
    code = code.upper()
    if code.startswith("HK."):
        return Market.HK
    if code.startswith("SZ.") or code.endswith(".XSHE"):
        return Market.SZ
    if code.startswith("SH.") or code.endswith("XSHG"):
        return Market.SH
