# -*- coding: utf-8 -*-
from typing import Optional
from stock_analysis import settings
from stock_analysis.utils.daemon import signal_handler

from futu.quote.open_quote_context import OpenQuoteContext, SysConfig

_quote_ctx: Optional[OpenQuoteContext] = None


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
        signal_handler.register(close_quote_ctx)
    return _quote_ctx
