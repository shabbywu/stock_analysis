# -*- coding: utf-8 -*-
from influxdb import InfluxDBClient, DataFrameClient

from stock_analysis import settings

client = InfluxDBClient(**settings.INFLUXDB_CONF)

df_client = DataFrameClient(**settings.INFLUXDB_CONF)
