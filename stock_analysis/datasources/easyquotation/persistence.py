# -*- coding: utf-8 -*-
from typing import List

from stock_analysis.datasources.base import (
    BaseSynchronizer,
    StockInfoUpdater,
    StockTickWriter,
)
from stock_analysis.datasources.easyquotation.client import (
    SinaRealTimeClient,
    TencentStockInfoFetcher,
)
from stock_analysis.storage.sqlalchemy import databases


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
