# -*- coding: utf-8 -*-
from typing import Any

import arrow
from jinja2 import Template
from pandas import DataFrame
from stock_analysis.schemas import StockTick
from stock_analysis.storage.sqlalchemy.databases import get_session
from stock_analysis.storage.sqlalchemy.models import InfluxdbAlertStrategy
from stock_analysis.storage.influxdb.databases import df_client as influxdb
from stock_analysis.alerts.notifiers import WeComNotifier


class InfluxdbWatchDog:
    def __init__(self):
        self.notifier = WeComNotifier()

    def watch(self):
        session = get_session()
        for strategy in session.query(InfluxdbAlertStrategy).filter_by(enabled=True):
            if not self.detect(strategy):
                continue
            self.notifier.add_summary(
                self.recover_newest_stock_tick(stock_code=strategy.stock_code)
            )
        else:
            if self.notifier.msg_cache:
                self.notifier.report()
        session.close()

    @staticmethod
    def recover_newest_stock_tick(stock_code: str):
        _, result = influxdb.query(
            f"select * from stock_ticks where code = '{stock_code}' ORDER BY desc LIMIT 1"
        ).popitem()
        index = result.index[0]
        bids = [
            dict(
                value=result[f"{bid}_price"][index],
                volume=result[f"{bid}_volume"][index],
            )
            for bid in ["bid_1", "bid_2", "bid_3", "bid_4", "bid_5"]
        ]
        asks = [
            dict(
                value=result[f"{ask}_price"][index],
                volume=result[f"{ask}_volume"][index],
            )
            for ask in ["ask_1", "ask_2", "ask_3", "ask_4", "ask_5"]
        ]
        return StockTick(
            bids=bids,
            asks=asks,
            time=index.to_pydatetime(),
            **{
                v: result[v][index]
                for v in ["name", "code", "current", "volume", "turnover", "name"]
            },
        )

    @staticmethod
    def detect(strategy: InfluxdbAlertStrategy) -> bool:
        sql = Template(strategy.sql).render(
            stock_code=strategy.stock_code,
            five_minutes=arrow.now()
            .shift(minutes=-5)
            .replace(microsecond=0)
            .isoformat(),
        )
        _, result = influxdb.query(sql).popitem()  # type: Any, DataFrame
        # 从 DataFrame 降维到 Series 再降维 到 bool
        return strategy.operator(result, strategy.threshold).any().any()
