# -*- coding: utf-8 -*-
from typing import Generator, List

import arrow
import easyquotation
from stock_analysis.datasources.base import BaseRealTimeClient
from stock_analysis.schemas import StockBaseInfo, StockTick


def format_code(code: str) -> str:
    if code.startswith("sh"):
        return code.replace("sh", "SH.")
    elif code.startswith("sz"):
        return code.replace("sz", "SZ.")
    return code


class TencentStockInfoFetcher:
    def __init__(self):
        self.quotation = easyquotation.use("tencent")

    def iter(self) -> Generator[StockBaseInfo, None, None]:
        for code, value in self.quotation.market_snapshot(prefix=True).items():
            try:
                yield StockBaseInfo(
                    code=format_code(code),
                    name=value["name"],
                    pe_annual=value.get("市盈(静)", 0),
                    pe_ttm=value.get("市盈(动)", 0),
                    pb_rate=value.get("PB", 0),
                )
            except ValueError as e:
                print(f"ValueError When iter from {code}<{value['name']}>")


class SinaRealTimeClient(BaseRealTimeClient):
    def __init__(self):
        self.quotation = easyquotation.use("sina")

    def get_tick(self, code: str) -> StockTick:
        _, item = self.quotation.real(code).popitem()
        return self.parse_stock(code, item)

    def get_tick_batch(self, code_list: List[str]) -> List[StockTick]:
        return [
            self.parse_stock(code, item)
            for code, item in self.quotation.real(code_list, prefix=True).items()
        ]

    def get_money_flow(self, code: str):
        pass

    @staticmethod
    def parse_stock(code, item) -> StockTick:
        bids = [
            dict(value=item[f"{bid}"], volume=item[f"{bid}_volume"])
            for bid in ["bid1", "bid2", "bid3", "bid4", "bid5"]
        ]
        asks = [
            dict(value=item[f"{ask}"], volume=item[f"{ask}_volume"])
            for ask in ["ask1", "ask2", "ask3", "ask4", "ask5"]
        ]
        return StockTick(
            name=item["name"],
            code=format_code(code),
            time=arrow.get(f"{item['date']}T{item['time']}").datetime,
            current=item["now"],
            volume=item["volume"],
            turnover=item["turnover"],
            bids=bids,
            asks=asks,
        )
