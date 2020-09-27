# -*- coding: utf-8 -*-
import time
from typing import Callable, ContextManager, Optional, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass
class TimeContext:
    start_time: float = field(default_factory=time.time)
    start_clock: float = field(default_factory=time.process_time)
    end_time: Optional[float] = None
    end_clock: Optional[float] = None

    @property
    def time_delta(self):
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time

    @property
    def clock_delta(self):
        if self.end_clock is None:
            return time.process_time() - self.start_clock
        return self.end_clock - self.start_clock

    def close(self):
        self.end_time = time.time()
        self.end_clock = time.process_time()


def __catch_time__() -> Iterator[TimeContext]:
    context = TimeContext()
    try:
        yield context
    finally:
        context.close()


catch_time: Callable[..., ContextManager[TimeContext]] = contextmanager(__catch_time__)
