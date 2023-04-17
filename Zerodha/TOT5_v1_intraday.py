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
import time 

enctoken = os.environ.get("ENC_TOKEN")
kite = KiteApp(enctoken=enctoken)

# instrument_token = 256265    # NIFTY 50
instrument_token = 260105    # NIFTY BANK
# time.sleep(78*60)

to_datetime = datetime.datetime(2023, 4, 17, 18, 00, 00, 000000)
from_datetime = to_datetime - datetime.timedelta(days=1)     # From last & days

interval = "15minute"
nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
dt = pd.DataFrame(nd)

no_of_wicks = 5
# Looking for buying opportunity
dtb = dt.nlargest(no_of_wicks,"high")
dtb["candle"] = dtb["close"] - dtb["open"]
dtb = dtb.reset_index()
#pfuw - price to be choosen for upper wick -> for green candle choose close
dtb["pfuw"] = [dtb["open"][i] if dtb["candle"][i]<0 else dtb["close"][i] for i in range(len(dtb)) ]
buy_entry_price = int(max(dtb["pfuw"]) + 1)
dtb["uwp"] =  dtb["high"]- buy_entry_price   #to get #wicks penetrated
wk=0
upper_wicks = max([wk+1 if dtb["uwp"][i]>0 else wk for i in range(len(dtb))])   

print(dtb)
if min(dtb["uwp"]) >= 0 :
    print (no_of_wicks,"wicks penetrated succcessfully by a single hz line at", dtb["date"].iloc[-1])
    print ("Buy Bank Nifty", "when get a closing above", buy_entry_price)
print ("{} upper_wicks have been formed till now".format(upper_wicks))


# Looking for selling opportunity
dts = dt.nsmallest(no_of_wicks,"low")
dts = dts.nsmallest(no_of_wicks,"date")
dts["candle"] = dts["close"] - dts["open"]
dts = dts.reset_index()
#pflw - price to be choosen for lower wick
dts["pflw"] = [dts["close"][i] if dts["candle"][i]<0 else dts["open"][i] for i in range(len(dts)) ]
sell_entry_price = int(min(dts["pflw"]) - 1)
dts["lwp"] =  sell_entry_price - dts["low"]   #to get #wicks penetrated
wk=0
lower_wicks = max([wk+1 if dts["lwp"][i]>0 else wk for i in range(len(dts))])   
 
if min(dts["lwp"]) >= 0 :
    print (no_of_wicks,"wicks penetrated succcessfully by a single hz line at\n", dts["date"].iloc[-1])
    print ("Sell Bank Nifty", "when get a closing below", sell_entry_price)

remaining_wicks = 5 - max(upper_wicks,lower_wicks) + 1
print (dts)
print ("{} lower_wicks have been formed till now".format(lower_wicks))
