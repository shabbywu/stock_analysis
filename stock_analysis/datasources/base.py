# -*- coding: utf-8 -*-
import abc
from typing import List

from stock_analysis.schemas import (
    BaseModel,
    DateTimeRange,
    StockBaseInfo,
    StockHistogramItem,
    StockTick,
)
from stock_analysis.storage.sqlalchemy import databases, models


class BaseRealTimeClient(metaclass=abc.ABCMeta):
    """实时数据获取客户端"""

    @abc.abstractmethod
    def get_tick(self, code: str) -> StockTick:
        """获取指定股票的实时行情报价"""

    @abc.abstractmethod
    def get_tick_batch(self, code_list: List[str]) -> List[StockTick]:
        """批量获取指定股票列表的实时行情报价"""

    @abc.abstractmethod
    def get_money_flow(self, code: str):
        """获取指定股票的现金流信息"""


class BaseHistoryClient(metaclass=abc.ABCMeta):
    """历史数据获取客户端"""

    @abc.abstractmethod
    def get_bars(self, code: str, dr: DateTimeRange) -> List[StockHistogramItem]:
        """获取指定股票的交易行情"""


class BaseDBWriter(metaclass=abc.ABCMeta):
    """股票信息更新器"""

    @abc.abstractmethod
    def write_to_db(self, obj: BaseModel):
        """将 obj 写进数据库"""


class BaseSynchronizer(metaclass=abc.ABCMeta):
    """同步器协议"""

    @abc.abstractmethod
    def synchronize(self):
        """执行批量同步操作"""


class StockInfoUpdater(BaseDBWriter):
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
