# -*- coding: utf-8 -*-
import logging
from dataclasses import dataclass
from typing import List, Tuple, Dict

from futu.common import constant
from futu.common.constant import FinancialQuarter, Market, SortDir, StockField
from futu.quote.open_quote_context import FinancialFilter, SimpleFilter
from stock_analysis.datasources.futuapi.context import get_quote_ctx
from stock_analysis.datasources.futuapi.schemas import (
    StockBaseInfo as FUTUStockBaseInfo,
)
from stock_analysis.datasources.utils import detect_stock_market
from stock_analysis.schemas import StockBaseInfo
from stock_analysis.datasources.base import BaseRealTimeClient
from stock_analysis.schemas import StockTick

logger = logging.getLogger(__name__)


@dataclass
class StockInfoFetcher:
    """股票基础信息获取(股票代码、股票名称、财报)"""

    market: object = Market.SZ

    @property
    def fields(self):
        other_stocks = []
        # SimpleFilter
        for field in [
            StockField.MARKET_VAL,
            StockField.PE_ANNUAL,
            StockField.PE_TTM,
            StockField.PB_RATE,
        ]:
            stock = SimpleFilter()
            stock.is_no_filter = True
            stock.stock_field = field
            other_stocks.append(stock)
        # FinancialFilter
        for quarter in [
            FinancialQuarter.ANNUAL,
            FinancialQuarter.FIRST_QUARTER,
            FinancialQuarter.INTERIM,
            FinancialQuarter.THIRD_QUARTER,
        ]:
            for field in [
                # 财务数据
                StockField.NET_PROFIT,
                StockField.NET_PROFIX_GROWTH,
                StockField.SUM_OF_BUSINESS,
                StockField.SUM_OF_BUSINESS_GROWTH,
                StockField.NET_PROFIT_RATE,
                StockField.GROSS_PROFIT_RATE,
                StockField.DEBT_ASSET_RATE,
                StockField.RETURN_ON_EQUITY_RATE,
            ]:
                stock = FinancialFilter()
                stock.is_no_filter = True
                stock.stock_field = field
                stock.quarter = quarter
                other_stocks.append(stock)
        return [self.ordering_field, *other_stocks]

    @property
    def ordering_field(self):
        ordering_field = SimpleFilter()
        ordering_field.filter_min = 0
        ordering_field.filter_max = 100
        ordering_field.stock_field = StockField.CUR_PRICE
        ordering_field.is_no_filter = False
        ordering_field.sort = SortDir.ASCEND
        return ordering_field

    def batch_fetch(
        self, limit=200, offset=0
    ) -> Tuple[bool, int, List[FUTUStockBaseInfo]]:
        """从 富途 API 批量获取股票基本信息"""
        ctx = get_quote_ctx()
        ret, ls = ctx.get_stock_filter(Market.SZ, self.fields, begin=offset, num=limit)
        result = (bool(ls[0]), ls[1], [])
        for obj in ls[2]:
            financial = {
                key: {}
                for key in ["annual", "first_quarter", "interim", "third_quarter"]
            }
            # 处理财报
            for key in obj.__dict__.keys():
                if isinstance(key, tuple) and key[1] in [
                    "annual",
                    "first_quarter",
                    "interim",
                    "third_quarter",
                ]:
                    financial[key[1]][key[0]] = obj.__dict__[key]
            # update result
            result[2].append(
                FUTUStockBaseInfo(
                    name=obj.stock_name,
                    code=obj.stock_code,
                    pe_annual=obj.pe_annual,
                    pe_ttm=obj.pe_ttm,
                    pb_rate=obj.pb_rate,
                    **financial
                )
            )
        return result


@dataclass
class KLineFetcher:
    """股票k线获取"""

    def fetch(
        self,
        stock_code: str,
        limit=1000,
        ktype: object = constant.KLType.K_DAY,
        autype: object = constant.AuType.NONE,
    ):
        # TODO: 获取实时 k 线
        ctx = get_quote_ctx()
        ret, ls = ctx.get_cur_kline(stock_code, num=limit, ktype=ktype, autype=autype)


class FUTURealTimeClient(BaseRealTimeClient):
    stock_info_maps: Dict[str, StockBaseInfo] = {}

    def get_tick_batch(self, code_list: List[str]) -> List[StockTick]:
        return [self.get_tick(code) for code in code_list]

    def get_tick(self, code: str) -> StockTick:
        ctx = get_quote_ctx()
        ret, data = ctx.get_market_snapshot([code])
        stock_info = self.get_stock_info(code)
        return StockTick(
            # TODO: 获取名称
            name=stock_info.name,
            code=stock_info.code,
            time=data["update_time"][0],
            current=data["last_price"][0],
            volume=data["volume"][0],
            turnover=data["turnover"][0],
        )

    @classmethod
    def get_stock_info(cls, code: str) -> StockBaseInfo:
        """获取股票的基本信息"""
        if code not in cls.stock_info_maps:
            ctx = get_quote_ctx()
            ret, data = ctx.get_stock_basicinfo(
                detect_stock_market(code), code_list=[code]
            )
            info = StockBaseInfo(code=data["code"][0], name=data["name"][0])
            cls.stock_info_maps[code] = info
        return cls.stock_info_maps[code]
