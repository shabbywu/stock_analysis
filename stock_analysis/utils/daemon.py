# -*- coding: utf-8 -*-
import datetime
import signal
import time
from typing import List, Callable

from stock_analysis.utils.timeit import catch_time

HANDLED_SIGNALS = (
    signal.SIGINT,  # Unix signal 2. Sent by Ctrl+C.
    signal.SIGTERM,  # Unix signal 15. Sent by `kill <pid>`.
)


class SignalHandler:
    def __init__(self):
        self.callbacks = []

    def __call__(self, *args, **kwargs):
        for callback in self.callbacks:
            callback(*args, **kwargs)

    def register(self, callback):
        self.callbacks.append(callback)


class Daemon:
    trading_times = [
        (datetime.time(hour=8, minute=45), datetime.time(hour=11, minute=31)),
        (datetime.time(hour=12, minute=59), datetime.time(hour=15, minute=1)),
    ]

    def __init__(self, plugins: List[Callable]):
        self.plugins = plugins
        self.should_exit = False
        signal_handler.register(self.signal_handler)

    def in_trading(self, now: datetime.time = None):
        now = now or datetime.datetime.now().time()
        for trading_time in self.trading_times:
            if trading_time[0] <= now <= trading_time[1]:
                return True
        return False

    def loop(self):
        delta = 3
        while not self.should_exit:
            print("Start A Loop")
            if not self.in_trading():
                continue
            with catch_time() as ctx:
                for plugin in self.plugins:
                    plugin()
                if ctx.time_delta < delta:
                    time.sleep(delta - ctx.time_delta)
        print("exit.")

    def signal_handler(self, sig, frame):
        self.should_exit = True


signal_handler = SignalHandler()
for sig in HANDLED_SIGNALS:
    signal.signal(sig, signal_handler)
