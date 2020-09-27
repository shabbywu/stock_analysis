# -*- coding: utf-8 -*-
from typing import Dict, List

from pydantic import BaseModel
from stock_analysis.constants import StockFinancialType
from stock_analysis.schemas import StockBaseInfo as _StockBaseInfo


class StockFinancial(BaseModel):
    # 净利润
    net_profit: float
    # 净利润增长率（该字段为百分比字段，默认不展示%，如20实际对应20%。）
    net_profix_growth: float
    # 营业收入
    sum_of_business: float
    # 营业同比增长率
    sum_of_business_growth: float
    # 净利率
    net_profit_rate: float
    # 毛利率
    gross_profit_rate: float
    # 资产负债率
    debt_asset_rate: float
    # 净资产收益率
    return_on_equity_rate: float


class StockBaseInfo(_StockBaseInfo):
    # 财报
    annual: StockFinancial
    first_quarter: StockFinancial
    interim: StockFinancial
    third_quarter: StockFinancial

    def as_tags(self):
        return dict(stock_name=self.name, stock_code=self.code)

    def list_financial(self) -> List[Dict]:
        result = []
        for quarter in StockFinancialType:
            result.append(
                dict(
                    stock_code=self.code,
                    financial_type=quarter.value,
                    values=getattr(self, quarter.value).dict(),
                )
            )
        return result
