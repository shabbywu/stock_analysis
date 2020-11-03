# -*- coding: utf-8 -*-
import datetime
import logging
from typing import Tuple

import backtrader as bt
from stock_analysis import settings
from stock_analysis.backtest.feeds import InfluxDB
from stock_analysis.utils.timeit import catch_time


class AOStrategy(bt.SignalStrategy):
    def __init__(self):
        self.AO = bt.ind.AO()
        self.order = None
        self.buy_date = None

    def log(self, txt):
        dt = self.data.datetime.datetime()
        logging.info("%s, %s" % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f"BUY EXECUTED, PRICE: {order.executed.price:0.2f} SIZE: {order.executed.size}"
                )
                self.buy_date = self.data.datetime.date()
            elif order.issell():
                self.log(
                    f"SELL EXECUTED, PRICE: {order.executed.price:0.2f} SIZE: {order.executed.size}"
                )

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")

        # Write down: no pending order
        self.order = None

    def next(self):
        if self.order:
            return

        if self.should_buy():
            if not self.position:
                self.order = self.buy()
            else:
                cost = self.position.size * self.position.price
                delta = (self.data.close[0] * self.position.size - cost) / cost
                if (
                    -0.02 < delta < 0.2
                    and self.broker.cash / self.broker.getvalue() > 0.5
                ):
                    self.order = self.buy()
        else:
            if self.position:
                should_sell, action = self.should_sell()
                if should_sell:
                    self.order = action()

    def should_buy(self) -> bool:
        today = self.data.datetime.date()
        if self.buy_date == today:
            return False
        if len(self.AO) < 2:
            return False
        if self.AO[-1] < 0 < self.AO[0]:
            return True
        if (
            len(self.AO) >= 3
            and 0 < self.AO[-1] < self.AO[0]
            and self.AO[-2] > self.AO[-1]
        ):
            return True
        return False

    def should_sell(self) -> Tuple[bool, callable]:
        today = self.data.datetime.date()
        cost = self.position.size * self.position.price
        delta = (self.data.close[0] * self.position.size - cost) / cost
        if self.buy_date == today:
            return False, None
        # 止损
        if delta < -0.05 and (today - self.buy_date) > datetime.timedelta(days=5):
            self.log(f"止损, 亏损: {delta}")
            return True, self.close
        if delta < -0.1:
            self.log(f"止损, 亏损: {delta}")
            return True, self.close
        # 止盈
        if delta > 0.5 and (today - self.buy_date) > datetime.timedelta(days=5):
            self.log(f"止盈, 减仓, 当前收益: {delta}")
            return True, self.sell
        if (
            delta > 0.10
            and self.broker.cash / self.broker.getvalue() < 0.75
            and (today - self.buy_date) < datetime.timedelta(days=3)
        ):
            self.log(f"套利, 减仓, 当前收益: {delta}")
            return True, self.sell
        if len(self.AO) < 2:
            return False, None
        if self.AO[-1] > 0 > self.AO[0]:
            self.log(f"下穿0线, 清仓离场: 收益{delta}")
            return True, self.close
        if (
            len(self.AO) >= 3
            and 0 > self.AO[-1] > self.AO[0]
            and self.AO[-2] < self.AO[-1]
        ):
            self.log(f"茶托卖点, 清仓离场: 收益{delta}")
            return True, self.close
        return False, None


def main():
    with catch_time() as ctx:
        cerebro = bt.Cerebro(runonce=False)
        cerebro.addstrategy(AOStrategy)
        data = InfluxDB(
            **settings.INFLUXDB_CONF,
            dataname="stock_history",
            stock_code="SZ.300274",
            from_date="2020-01-01",
            to_date="2020-10-01",
        )
        cerebro.replaydata(data, timeframe=bt.TimeFrame.Days, compression=True)
        # cerebro.adddata(data)
        cerebro.broker.setcash(100000.0)
        cerebro.broker.set_coc(True)
        cerebro.broker.set_coo(False)
        cerebro.addsizer(bt.sizers.PercentSizerInt, percents=20)
        cerebro.run()
        print(cerebro.broker.get_value())
    print("time cost: ", ctx.time_delta)


if __name__ == "__main__":
    with catch_time() as ctx:
        main()
    print("time cost: ", ctx.time_delta)
