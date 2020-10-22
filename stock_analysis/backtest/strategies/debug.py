# -*- coding: utf-8 -*-
import backtrader as bt
from numbers import Number
from typing import NamedTuple

from stock_analysis.backtest.feeds import OHLC

ohlc = NamedTuple("ohlc", open=Number, high=Number, low=Number, close=Number)


class MAStrategy(bt.SignalStrategy):
    def __init__(self):
        self.IND = bt.ind.AccelerationDecelerationOscillator(self.data, period=5)

    def next(self):
        print(f"{self.IND[0]}")


if __name__ == "__main__":
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MAStrategy)
    data = OHLC(
        _iter=iter(
            [
                ohlc(open=19, high=73, low=49, close=19),
                ohlc(open=99, high=63, low=17, close=99),
                ohlc(open=82, high=42, low=82, close=24),
                ohlc(open=93, high=90, low=34, close=32),
                ohlc(open=81, high=82, low=89, close=10),
                ohlc(open=93, high=21, low=67, close=88),
                ohlc(open=49, high=93, low=90, close=99),
                ohlc(open=1, high=51, low=9, close=20),
                ohlc(open=67, high=30, low=21, close=93),
                ohlc(open=80, high=33, low=4, close=61),
            ]
        )
    )
    # data = Data(_iter=iter([18, 72, 85, 91, 83, 45, 80]))
    cerebro.adddata(data)
    cerebro.run(runonce=False)
    # cerebro.plot(EchartPlotter())
