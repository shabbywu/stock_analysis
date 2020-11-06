# -*- coding: utf-8 -*-
import time
from typing import List

from stock_analysis.constants import MarketType
from stock_analysis.datasources.base import (
    BaseSynchronizer,
    BaseDBWriter,
    StockTickWriter,
)
from stock_analysis.datasources.futuapi.client import (
    StockInfoFetcher,
    FUTURealTimeClient,
)
from stock_analysis.datasources.futuapi.schemas import StockBaseInfo
from stock_analysis.storage.sqlalchemy import databases, models


class FUTUStockInfoUpdater(BaseDBWriter):
    session: databases.Session

    def write_to_db(self, obj: StockBaseInfo):
        stock_base_info, _ = databases.get_or_create(
            self.session,
            models.StockBaseInfo(
                stock_code=obj.code,
                stock_name=obj.name,
                pe_annual=obj.pe_annual,
                pe_ttm=obj.pe_ttm,
                pb_rate=obj.pb_rate,
            ),
        )
        for financial in obj.list_financial():
            databases.get_or_create(self.session, models.StockFinancial(**financial))


class FUTUStockInfoBatchSynchronizer(BaseSynchronizer, FUTUStockInfoUpdater):
    def __init__(self, market: MarketType):
        self.market = market
        self.session = databases.get_session()
        self.fetcher = StockInfoFetcher(market)

    def synchronize(self):
        offset = 0
        while True:
            # TODO: 优化 fetch_result 的建模
            fetch_result = self.fetcher.batch_fetch(offset=offset)
            offset += 200
            for stock in fetch_result[2]:
                self.write_to_db(stock)
            time.sleep(10)
            if fetch_result[0]:
                break


class FUTUTickSynchronizer(BaseSynchronizer, StockTickWriter):
    source_type = "futu"

    def __init__(self, code_list: List[str]):
        self.code_list = code_list
        self.client = FUTURealTimeClient()

    def synchronize(self):
        if self.code_list:
            self.write_to_db(self.client.get_tick_batch(code_list=self.code_list))
