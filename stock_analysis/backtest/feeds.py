# -*- coding: utf-8 -*-
from typing import Iterator
import backtrader as bt

import datetime as dt
from influxdb import InfluxDBClient as idbclient
from influxdb.exceptions import InfluxDBClientError


TIMEFRAMES = dict(
    (
        (bt.TimeFrame.Seconds, "s"),
        (bt.TimeFrame.Minutes, "m"),
        (bt.TimeFrame.Days, "d"),
        (bt.TimeFrame.Weeks, "w"),
        (bt.TimeFrame.Months, "m"),
        (bt.TimeFrame.Years, "y"),
    )
)


class InfluxDB(bt.feeds.DataBase):
    ndb: idbclient
    biter: Iterator

    params = (
        ("host", "127.0.0.1"),
        ("port", "8086"),
        ("username", None),
        ("password", None),
        ("database", None),
        ("timeframe", bt.TimeFrame.Minutes),
        ("startdate", None),
        ("high", "high"),
        ("low", "low"),
        ("open", "open"),
        ("close", "close"),
        ("volume", "volume"),
        ("stock_code", None),
    )

    def start(self):
        super(InfluxDB, self).start()
        try:
            self.ndb = idbclient(
                self.p.host,
                self.p.port,
                self.p.username,
                self.p.password,
                self.p.database,
            )
        except InfluxDBClientError as err:
            raise Exception("Failed to establish connection to InfluxDB: %s" % err)

        tf = "{multiple}{timeframe}".format(
            multiple=(self.p.compression if self.p.compression else 1),
            timeframe=TIMEFRAMES.get(self.p.timeframe, "d"),
        )

        if not self.p.startdate:
            st = "<= now()"
        else:
            st = ">= '%s'" % self.p.startdate

        # The query could already consider parameters like fromdate and todate
        # to have the database skip them and not the internal code
        qstr = (
            'SELECT mean("{open_f}") AS "open", mean("{high_f}") AS "high", '
            'mean("{low_f}") AS "low", mean("{close_f}") AS "close", '
            'mean("{vol_f}") AS "volume" '
            'FROM "{dataname}" '
            "WHERE time {begin} AND code='{stock_code}' "
            "GROUP BY time({timeframe}) fill(none)"
        ).format(
            open_f=self.p.open,
            high_f=self.p.high,
            low_f=self.p.low,
            close_f=self.p.close,
            vol_f=self.p.volume,
            stock_code=self.p.stock_code,
            timeframe=tf,
            begin=st,
            dataname=self.p.dataname,
        )

        try:
            dbars = list(self.ndb.query(qstr).get_points())
        except InfluxDBClientError as err:
            raise Exception("InfluxDB query failed: %s" % err)

        self.biter = iter(dbars)

    def _load(self):
        try:
            bar = next(self.biter)
        except StopIteration:
            return False

        self.l.datetime[0] = bt.utils.date2num(
            dt.datetime.strptime(bar["time"], "%Y-%m-%dT%H:%M:%SZ")
        )

        self.l.open[0] = bar["open"]
        self.l.high[0] = bar["high"]
        self.l.low[0] = bar["low"]
        self.l.close[0] = bar["close"]
        self.l.volume[0] = bar["volume"]

        return True
