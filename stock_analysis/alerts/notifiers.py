# -*- coding: utf-8 -*-
import datetime
from textwrap import dedent

import requests
from jinja2 import Template
from stock_analysis import settings
from stock_analysis.schemas import StockTick


class WeComNotifier:
    """企业微信通知发送器"""

    url = settings.WECOM_NOTIFY_URL
    summary_template = dedent(
        """
        # 股票代码: {{ stock.code }}-{{ stock.name }}
        ## 目前: <font color="warning">{{ stock.current }}</font>
        ## 买卖盘: {{ stock.bid_vs_ask }}
    """
    )

    def __init__(self):
        self.msg_cache = []

    def add_summary(self, stock: StockTick):
        self.msg_cache.append(Template(self.summary_template).render(stock=stock))

    def report(self, chart_id: str = settings.WECOM_CHART_ID):
        data = dict(
            chatid=chart_id,
            msgtype="markdown",
            markdown=dict(
                content=f"{datetime.datetime.now()}" + "\n\n".join(self.msg_cache)
            ),
        )
        requests.post(self.url, json=data)
        self.msg_cache.clear()
