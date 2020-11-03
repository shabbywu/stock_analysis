# -*- coding: utf-8 -*-
import signal
from typing import Optional
from stock_analysis import settings

from futu.quote.open_quote_context import OpenQuoteContext, SysConfig

_quote_ctx: Optional[OpenQuoteContext] = None


HANDLED_SIGNALS = (
    signal.SIGINT,  # Unix signal 2. Sent by Ctrl+C.
    signal.SIGTERM,  # Unix signal 15. Sent by `kill <pid>`.
)


def close_quote_ctx(sig, frame):
    global _quote_ctx
    if _quote_ctx is not None:
        print("closing OpenQuoteContext")
        _quote_ctx.close()


def get_quote_ctx():
    global _quote_ctx
    if _quote_ctx is None:
        SysConfig.enable_proto_encrypt(True)
        SysConfig.set_init_rsa_file(settings.FUTU_OPEND_PRI_KEY)  # rsa 私钥文件路径
        _quote_ctx = OpenQuoteContext(**settings.FUTU_OPEND_SERVER)
        for sig in HANDLED_SIGNALS:
            signal.signal(sig, close_quote_ctx)
    return _quote_ctx
