# -*- coding: utf-8 -*-
import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from stock_analysis.constants import IntervalType


class StockBaseInfo(BaseModel):
    code: str
    name: str
    pe_annual: float = Field(0, description="市盈率")
    pe_ttm: float = Field(0, description="市盈率TTM")
    pb_rate: float = Field(0, description="市净率")


class QuotedPrice(BaseModel):
    """买/卖 报价单"""

    value: float
    volume: int


class StockTick(BaseModel):
    """股票实时行情"""

    name: Optional[str] = Field(None, description="标的的名称")
    code: str = Field(..., description="标的的代码")
    time: datetime.datetime = Field(..., description="tick发生的时间")

    current: float = Field(..., description="最新价")
    volume: Optional[int] = Field(None, description="截至到当前时刻的成交量")
    turnover: Optional[int] = Field(None, description="截至到当前时刻的成交额")
    bids: List[QuotedPrice] = Field(default_factory=list, description="买手单")
    asks: List[QuotedPrice] = Field(default_factory=list, description="卖手单")

    @property
    def bid_vs_ask(self):
        """买卖盘趋势对比"""
        total_bid_volume = sum(bid.volume for bid in self.bids)
        total_ask_volume = sum(ask.volume for ask in self.asks)
        return f"{total_bid_volume} / {total_ask_volume}"


class StockHistogramItem(BaseModel):
    """股票 k 线"""

    name: Optional[str] = Field(None, description="标的的名称")
    code: str = Field(..., description="标的的代码")
    time: datetime.datetime = Field(..., description="tick发生的时间")
    interval: IntervalType = Field(..., description="单位时间长度")

    current: float = Field(..., description="最新价")
    open: float = Field(..., description="时间段开始时价格")
    close: float = Field(..., description="时间段结束时价格")
    high: float = Field(..., description="时间段中的最高价")
    low: float = Field(..., description="时间段中的最低价")
    volume: int = Field(..., description="时间段中的成交的股票数量")
    turnover: int = Field(..., description="时间段中的成交的金额")
    paused: bool = Field(..., description="是否停牌")


class DateTimeRange(BaseModel):
    """数据有效期间"""

    start_dt: datetime.datetime
    end_dt: datetime.datetime
    interval: IntervalType = IntervalType.ONE_MINUTE

    def __str__(self):
        return f"{self.start_dt}:{self.end_dt}:{self.interval.value}"
