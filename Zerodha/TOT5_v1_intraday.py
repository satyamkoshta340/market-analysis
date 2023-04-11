# Run this file on every market trading day at 10:30:02 
# This code should be run every 15/30/45/60/75 minutes depending on 
#wicks found so far

# Test of 5 Times
from kite_trade import *
import pandas as pd
import time
import os
from dotenv import load_dotenv
import datetime
load_dotenv()

enctoken = os.environ.get("ENC_TOKEN")
kite = KiteApp(enctoken=enctoken)

# instrument_token = 256265    # NIFTY 50
instrument_token = 260105    # NIFTY BANK

tm = 0
while tm < 20:
    tm+=1
    to_datetime = datetime.datetime(2023, 4, 10, 18, 00, 00, 000000)
    from_datetime = to_datetime - datetime.timedelta(days=1)     # From last & days
    
    interval = "15minute"
    nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
    dt = pd.DataFrame(nd)
    
    # Looking for buying opportunity
    dtb = dt.nlargest(5,"high")
    dtb["candle"] = dtb["close"] - dtb["open"]
    dtb = dtb.reset_index()
    #pfuw - price to be choosen for upper wick -> for green candle choose close
    dtb["pfuw"] = [dtb["open"][i] if dtb["candle"][i]<0 else dtb["close"][i] for i in range(len(dtb)) ]
    buy_entry_price = int(max(dtb["pfuw"]) + 1)
    dtb["uwp"] =  dtb["high"]- buy_entry_price   #to get #wicks penetrated
    upper_wicks = max([i+1 if dtb["uwp"][i]>1 else i for i in range(len(dtb))])   
    
    if min(dtb["uwp"]) >= 0 :
        print ("5 wicks penetrated succcessfully by a single hz line at", dts["date"].iloc[-1])
        print ("Buy Bank Nifty", "when get a closing above", buy_entry_price)
    
    # Looking for selling opportunity
    dts = dt.nsmallest(5,"low")
    dts = dts.nsmallest(5,"date")
    dts["candle"] = dts["close"] - dts["open"]
    dts = dts.reset_index()
    #pflw - price to be choosen for lower wick
    dts["pflw"] = [dts["close"][i] if dts["candle"][i]<0 else dts["open"][i] for i in range(len(dts)) ]
    sell_entry_price = int(min(dts["pflw"]) - 1)
    dts["lwp"] =  sell_entry_price - dts["low"]   #to get #wicks penetrated
    lower_wicks = max([i+1 if dts["lwp"][i]>1 else i for i in range(len(dts))])   
     
    if min(dts["lwp"]) >= 0 :
        print ("5 wicks penetrated succcessfully by a single hz line at\n", dts["date"].iloc[-1])
        print ("Sell Bank Nifty", "when get a closing below", sell_entry_price)

    remaining_wicks = 5 - max(upper_wicks,lower_wicks) + 1
    print ("Resting for",remaining_wicks*15, "minutes")
    time.sleep(remaining_wicks*15*60)

