# -*- coding: utf-8 -*-
import logging
import datetime
from typing import List

from stock_analysis.datasources.base import BaseSynchronizer, BaseDBWriter
from stock_analysis.schemas import StockHistogramItem, DateTimeRange
from stock_analysis.datasources.joinquant.client import JQClient
from stock_analysis.storage.influxdb.databases import client as db


logger = logging.getLogger(__name__)


def format_datetime(dt: datetime.datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


def format_code(code: str) -> str:
    if code.endswith("XSHE"):
        return "SZ." + code.replace(".XSHE", "")
    elif code.endswith(".XSHG"):
        return "SH." + code.replace(".XSHG", "")
    return code


class StockHistoryWriter(BaseDBWriter):
    table_name = "stock_history"

    def write_to_db(self, obj: List[StockHistogramItem]):
        data = [
            dict(
                measurement=self.table_name,
                tags=dict(code=format_code(item.code), interval=item.interval.value),
                time=format_datetime(item.time),
                fields=item.dict(
                    include={
                        "open",
                        "close",
                        "high",
                        "low",
                        "current",
                        "volume",
                        "turnover",
                        "paused",
                    }
                ),
            )
            for item in obj
        ]
        db.write_points(data)


class JQStockHistorySynchronizer(BaseSynchronizer, StockHistoryWriter):
    def __init__(self, code_list: List[str], dr: DateTimeRange):
        self.code_list = code_list
        self.dr = dr
        self.client = JQClient()

    def synchronize(self):
        for code in self.code_list:
            logger.info(
                "It's going to synchronize history bar for %s for range: %s",
                code,
                self.dr,
            )
            self.write_to_db(self.client.get_bars(code, self.dr))
