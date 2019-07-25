import pandas as pd
from collections import OrderedDict
import pytz
from zipline.api import order, record, symbol, set_benchmark, order_target_percent, get_open_orders
from zipline.utils.calendars.exchange_calendar_twentyfourhr import TwentyFourHR
import zipline
import matplotlib.pyplot as plt
from datetime import datetime


def initialize(context):
    set_benchmark(symbol("BTC"))


def handle_data(context, data):

    slowma = data.history(symbol("BTC"), fields='price', bar_count=50, frequency='1m').mean()
    fastma = data.history(symbol("BTC"), fields='price', bar_count=10, frequency='1m').mean()

    if fastma < slowma:
        if symbol("BTC") not in get_open_orders():
            order_target_percent(symbol("BTC"), 0.04)

    if fastma > slowma:
        if symbol("BTC") not in get_open_orders():
            order_target_percent(symbol("BTC"), 0.96)

    record(BTC=data.current(symbol('BTC'), fields='price'))


data = OrderedDict()
data['BTC'] = pd.read_csv("BTC-USD.csv")

data['BTC']['date'] = pd.to_datetime(data['BTC']['time'], unit='s', utc=True)
data['BTC'].set_index('date', inplace=True)
data['BTC'].drop('time', axis=1, inplace=True)
data['BTC'] = data['BTC'].resample("1min").mean()
data['BTC'].fillna(method="ffill", inplace=True)
data['BTC'] = data['BTC'][["low","high","open","close","volume"]]
print(data['BTC'].head())

panel = pd.Panel(data)
panel.minor_axis = ["low","high","open","close","volume"]
panel.major_axis = panel.major_axis.tz_localize(pytz.utc)
print(panel)


perf = zipline.run_algorithm(start=datetime(2018, 2, 7, 0, 0, 0, 0, pytz.utc),
                      end=datetime(2018, 3, 26, 0, 0, 0, 0, pytz.utc),
                      initialize=initialize,
                      trading_calendar=TwentyFourHR(),
                      capital_base=10000,
                      handle_data=handle_data,
                      data_frequency ='minute',
                      data=panel)