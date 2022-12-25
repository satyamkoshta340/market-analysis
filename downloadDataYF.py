# -*- coding: utf-8 -*-
"""
Created on Thu Sep 15 19:56:19 2022

@author: kosht
"""

import pandas as pd
import yfinance as yf
import datetime

start = datetime.datetime(2022,8,22)
end = datetime.datetime(2022,9,22)

td = datetime.datetime.today()
st = datetime.datetime(td.year, td.month, td.day)


df = pd.DataFrame()
df = yf.download("^NSEBANK", start=st, end=td, interval= '5m')

df.to_csv("./assets/BANKNIFTY_5MIN.csv", mode='a', header=False)
