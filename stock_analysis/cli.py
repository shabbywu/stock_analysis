# -*- coding: utf-8 -*-
import time
import datetime
from typing import List

import arrow
import click
from stock_analysis.alerts.watchdogs import InfluxdbWatchDog
from stock_analysis.constants import MarketType, IntervalType
from stock_analysis.datasources.easyquotation.persistence import (
    SinaTickSynchronizer,
    TencentStockInfoBatchSynchronizer,
)
from stock_analysis.datasources.futuapi.persistence import (
    FutuStockInfoBatchSynchronizer,
)
from stock_analysis.datasources.joinquant.persistence import JQStockHistorySynchronizer
from stock_analysis.schemas import DateTimeRange
from stock_analysis.utils.timeit import catch_time
from stock_analysis.storage.sqlalchemy import databases, models


@click.group()
def cli():
    """stock analysis helpers"""


@cli.command()
@click.argument("market", type=click.Choice([t.value for t in MarketType]))
def fetch_stock_base_info_by_futuapi(market: str):
    synchronizer = FutuStockInfoBatchSynchronizer(market)
    synchronizer.synchronize()


@cli.command()
def fetch_stock_base_info_by_tencentapi():
    synchronizer = TencentStockInfoBatchSynchronizer()
    synchronizer.synchronize()


@cli.command()
@click.option(
    "-i",
    "--interval",
    type=click.Choice([t.value for t in IntervalType]),
    default=IntervalType.ONE_MINUTE,
)
@click.option("--code", multiple=True, type=str, required=True)
@click.option("-s", "--start", type=str, default="2015-01-01")
@click.option("-e", "--end", type=str, default=None)
def fetch_stock_history_info_by_joinquant(code, interval, start, end):
    for start_dt, end_dt in arrow.Arrow.span_range(
        "years", arrow.get(start), arrow.get(end)
    ):
        dr = DateTimeRange(
            start_dt=start_dt.datetime, end_dt=end_dt.datetime, interval=interval
        )
        synchronizer = JQStockHistorySynchronizer(code_list=set(code), dr=dr)
        synchronizer.synchronize()


class Daemon:
    trading_times = [
        (datetime.time(hour=8, minute=45), datetime.time(hour=11, minute=31)),
        (datetime.time(hour=12, minute=59), datetime.time(hour=15, minute=1)),
    ]

    def __init__(self, code_list: List[str]):
        self.synchronizer = SinaTickSynchronizer(code_list)
        self.watch_dog = InfluxdbWatchDog()

    def in_trading(self, now: datetime.time = None):
        now = now or datetime.datetime.now().time()
        for trading_time in self.trading_times:
            if trading_time[0] <= now <= trading_time[1]:
                return True
        return False

    def loop(self):
        delta = 3
        while True:
            if not self.in_trading():
                continue
            with catch_time() as ctx:
                self.synchronizer.synchronize()
                self.watch_dog.watch()
                if ctx.time_delta < delta:
                    time.sleep(delta - ctx.time_delta)


@cli.command()
def daemon():
    session = databases.get_session()
    code_list = [
        item[0] for item in session.query(models.StockBaseInfo.stock_code).all()
    ]
    session.close()
    try:
        Daemon(code_list).loop()
    except KeyboardInterrupt:
        pass
