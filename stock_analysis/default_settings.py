# -*- coding: utf-8 -*-
import logging.config
from pathlib import Path

INFLUXDB_CONF = dict(
    host="your-host",
    port="your-port",
    username="your-username",
    password="your-password",
    database="your-database",
)

# 数据库配置
SQLALCHEMY_DB_URL = "sqlite:///" + str(
    Path(__file__).parent.parent / "runtime/stock.db"
)

# JOIN QUANT 配置
JOINQUANT_AUTH = dict(username="your-username", password="your-password")

# FUTUOpenD
FUTU_OPEND_PRI_KEY = "abs-path-to-your-rsa-private-key"
FUTU_OPEND_SERVER = dict(host="your-host", port="your-port")

WECOM_NOTIFY_URL = None
WECOM_CHART_ID = None

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s [%(asctime)s] %(name)s(ln:%(lineno)d): %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}


logging.config.dictConfig(LOGGING)
