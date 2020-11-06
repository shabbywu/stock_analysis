# -*- coding: utf-8 -*-
from jinja2 import Template
from textwrap import dedent
from futu import PriceReminderHandlerBase, RET_OK, RET_ERROR

from stock_analysis.alerts.notifiers import WeComNotifier
from stock_analysis.datasources.futuapi.context import get_quote_ctx


class WeComPriceReminder(PriceReminderHandlerBase):
    def __init__(self):
        super().__init__()
        self.notifier = WeComNotifier()

    def on_recv_rsp(self, rsp_pb):
        ret_code, content = super().on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("WeComPriceReminder: error, msg: %s" % content)
            return RET_ERROR, content
        print("on_recv_rsp: ", content)
        self.notifier.msg_cache.append(
            Template(
                dedent(
                    """# {{ code }} {{ content }}
                    ## 目前: <font color="warning">{{ price }}</font>, 变化率: {{ change_rate }}
                    ## 告警阈值: {{ set_value }}"""
                )
            ).render(**content)
        )
        self.notifier.report()
        return RET_OK, content


def receive_futu_notify():
    ctx = get_quote_ctx()
    ctx.set_handler(WeComPriceReminder())
