# -*- coding: utf-8 -*-

import arrow
import click
from stock_analysis.alerts.watchdogs import InfluxdbWatchDog
from stock_analysis.constants import MarketType, IntervalType
from stock_analysis.datasources.easyquotation.persistence import (
    SinaTickSynchronizer,
    TencentStockInfoBatchSynchronizer,
)
from stock_analysis.datasources.futuapi.persistence import (
    FUTUStockInfoBatchSynchronizer,
    FUTUTickSynchronizer,
)
from stock_analysis.datasources.futuapi.handlers import receive_futu_notify
from stock_analysis.datasources.joinquant.persistence import JQStockHistorySynchronizer
from stock_analysis.schemas import DateTimeRange
from stock_analysis.utils.daemon import Daemon
from stock_analysis.utils.basic import detect_stock_market
from stock_analysis.storage.sqlalchemy import databases, models


@click.group()
def cli():
    """stock analysis helpers"""


@cli.command()
@click.argument("market", type=click.Choice([t.value for t in MarketType]))
def fetch_stock_base_info_by_futuapi(market: str):
    synchronizer = FUTUStockInfoBatchSynchronizer(market)
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


@cli.command()
@click.option("--fetch-data/--no-fetch-data", default=True)
@click.option("-n", "--notify", type=bool, default=False, is_flag=True)
@click.option("--listen-futu-callback", type=bool, default=False, is_flag=True)
def daemon(fetch_data, notify, listen_futu_callback):
    session = databases.get_session()
    code_list = [
        item[0] for item in session.query(models.StockBaseInfo.stock_code).all()
    ]
    session.close()
    plugins = []

    if fetch_data:
        plugins.append(
            SinaTickSynchronizer(
                [
                    code
                    for code in code_list
                    if detect_stock_market(code) in ["SZ", "SH"]
                ]
            ).synchronize
        )
        plugins.append(
            FUTUTickSynchronizer(
                [code for code in code_list if detect_stock_market(code) == "HK"]
            ).synchronize
        )

    if notify:
        plugins.append(InfluxdbWatchDog().watch)

    if listen_futu_callback:
        receive_futu_notify()

    try:
        Daemon(plugins).loop()
    except KeyboardInterrupt:
        raise
