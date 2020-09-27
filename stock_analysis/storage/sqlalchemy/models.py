# -*- coding: utf-8 -*-
from sqlalchemy import (
    DECIMAL,
    JSON,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
)
from stock_analysis.constants import StockFinancialType, AlertOperator
from stock_analysis.storage.sqlalchemy.databases import Base


class StockBaseInfo(Base):
    __tablename__ = "stock_base_info"

    stock_code = Column(String(16), primary_key=True)
    stock_name = Column(String(8))
    pe_annual = Column(DECIMAL, comment="市盈率")
    pe_ttm = Column(DECIMAL, comment="市盈率TTM")
    pb_rate = Column(DECIMAL, comment="市净率")


class StockFinancial(Base):
    __tablename__ = "stock_financial"

    id = Column("id", Integer, primary_key=True)
    stock_code = Column(String(16), ForeignKey(StockBaseInfo.stock_code))
    financial_type = Column(Enum(StockFinancialType))
    values = Column(JSON, comment="财报值, 详见StockFinancial")


class InfluxdbAlertStrategy(Base):
    __tablename__ = "influxdb_alert_strategy"

    id = Column(Integer, primary_key=True)
    stock_code = Column(
        String(16), ForeignKey(StockBaseInfo.stock_code), comment="股票代码"
    )
    enabled = Column(Boolean, default=False, comment="是否启用")
    sql = Column(Text, comment="告警sql")
    threshold = Column(DECIMAL, comment="阈值")
    operator = Column(Enum(AlertOperator), comment="阈值对比操作")
