# Test of 5 Times
from kite_trade import *
import pandas as pd
import time
# Run this file on every market trading day at 10:45:10 to get the orders placed
import os
from dotenv import load_dotenv
import datetime
load_dotenv()

enctoken = os.environ.get("ENC_TOKEN")
kite = KiteApp(enctoken=enctoken)

import datetime
dir_path = os.path.dirname(os.path.realpath(__file__))
stk = pd.read_csv( dir_path+ "/nse_stocks.csv")
scanned = []
filtered_scan1 = []; filtered_scan2 = []

# token   Index
# 256265	NIFTY 50
# 260105	NIFTY BANK

instrument_token = 260105    # DRREDDY 225537

to_datetime = datetime.datetime(2023, 4, 10, 18, 00, 00, 000000)
from_datetime = to_datetime - datetime.timedelta(days=1)     # From last & days

interval = "15minute"
nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
dt = pd.DataFrame(nd)

sol = dt.nlargest(5,"high")
sol = sol.nsmallest(5,"date")
sol["candle"] = sol["close"] - sol["open"]
sol = sol.reset_index()
#pfuw - price to be choosen for upper wick
sol["pfuw"] = [sol["open"][i] if sol["candle"][i]<0 else sol["close"][i] for i in range(len(sol)) ]
entry_price = round(max(sol["pfuw"]) + 0.1,2)
sol["wp"] =  sol["high"]- entry_price   #to get #wicks penetrated

if sol.iloc[-1]["date"].date() == to_datetime.date():
    if min(sol["wp"]) >= 0 :
        print ("5 wicks penetrated succcessfully by a single hz line")
        print ("Buy Bank Nifty", "when get a closing above", entry_price)



