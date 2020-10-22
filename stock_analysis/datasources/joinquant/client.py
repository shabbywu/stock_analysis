# -*- coding: utf-8 -*-
import math
from typing import Dict, List

import jqdatasdk
from pandas import DataFrame
from stock_analysis import settings
from stock_analysis.datasources.base import BaseHistoryClient
from stock_analysis.schemas import DateTimeRange, StockBaseInfo, StockHistogramItem


class JQClient(BaseHistoryClient):
    def get_bars(self, code: str, dr: DateTimeRange) -> List[StockHistogramItem]:
        return self.get_price(code, dr)

    def get_price(self, code: str, dr: DateTimeRange) -> List[StockHistogramItem]:
        """调用 jqdatasdk.get_price 获取指定股票代码在指定时间范围内的行情"""

        stock_info = self.get_stock_info(code)
        normalize_code = self.normalize_codes([code])[0]
        prices: DataFrame = jqdatasdk.get_price(
            security=normalize_code,
            start_date=dr.start_dt,
            end_date=dr.end_dt,
            frequency=dr.interval,
            fields=["open", "close", "high", "low", "volume", "money", "paused", "avg"],
        )
        return [
            StockHistogramItem(
                name=stock_info.name,
                code=stock_info.code,
                interval=dr.interval,
                time=item[0].to_pydatetime(),
                turnover=item[1]["money"],
                current=item[1]["avg"],
                **item[1]
            )
            for item in prices.iterrows()
            if not math.isnan(item[1][0])
        ]

    normalized_code_maps: Dict[str, str] = {}
    stock_info_maps: Dict[str, StockBaseInfo] = {}

    @classmethod
    def normalize_codes(cls, code_list: List[str]) -> List[str]:
        """标准化股票代码"""

        unknown_codes = [
            code for code in code_list if code not in cls.normalized_code_maps
        ]
        normalized_codes = jqdatasdk.normalize_code(unknown_codes)
        for key, value in zip(unknown_codes, normalized_codes):
            cls.normalized_code_maps[key] = value
        return [cls.normalized_code_maps[code] for code in code_list]

    @classmethod
    def get_stock_info(cls, code: str) -> StockBaseInfo:
        """获取股票的基本信息"""

        if code in cls.stock_info_maps:
            return cls.stock_info_maps[code]
        normalize_code = cls.normalize_codes([code])[0]
        security = jqdatasdk.get_security_info(normalize_code)
        ret = StockBaseInfo(code=code, name=security.display_name)
        cls.stock_info_maps[code] = ret
        return ret

    def __init__(self):
        if not jqdatasdk.is_auth():
            jqdatasdk.auth(**settings.JOINQUANT_AUTH)
