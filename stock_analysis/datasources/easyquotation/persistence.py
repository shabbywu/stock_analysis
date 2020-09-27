# -*- coding: utf-8 -*-
import datetime
from typing import Dict, List

from stock_analysis.datasources.base import (
    BaseDBWriter,
    BaseSynchronizer,
    StockInfoUpdater,
)
from stock_analysis.datasources.easyquotation.client import (
    SinaRealTimeClient,
    TencentStockInfoFetcher,
)
from stock_analysis.schemas import QuotedPrice, StockTick
from stock_analysis.storage.influxdb.databases import client as db
from stock_analysis.storage.sqlalchemy import databases


def format_datetime(dt: datetime.datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


def format_quotations(prefix: str, prices: List[QuotedPrice]) -> Dict:
    ret = {}
    for idx, quotation in enumerate(prices):
        ret.update(
            {
                f"{prefix}_{idx + 1}_price": quotation.value,
                f"{prefix}_{idx + 1}_volume": quotation.volume,
            }
        )
    return ret


class StockTickWriter(BaseDBWriter):
    table_name = "stock_ticks"
    source_type: str

    def write_to_db(self, objs: List[StockTick]):
        data = [
            dict(
                measurement=self.table_name,
                tags=dict(code=obj.code, source_type=self.source_type),
                time=format_datetime(obj.time),
                fields=dict(
                    **format_quotations("ask", obj.asks),
                    **format_quotations("bid", obj.bids),
                    **obj.dict(include={"current", "volume", "turnover", "name"}),
                ),
            )
            for obj in objs
        ]
        db.write_points(data)


class SinaTickSynchronizer(BaseSynchronizer, StockTickWriter):
    source_type = "sina"

    def __init__(self, code_list: List[str]):
        self.code_list = code_list
        self.client = SinaRealTimeClient()

    def synchronize(self):
        self.write_to_db(self.client.get_tick_batch(code_list=self.code_list))


class TencentStockInfoBatchSynchronizer(BaseSynchronizer, StockInfoUpdater):
    def __init__(self):
        self.session = databases.get_session()
        self.fetcher = TencentStockInfoFetcher()

    def synchronize(self):
        for obj in self.fetcher.iter():
            self.write_to_db(obj)
