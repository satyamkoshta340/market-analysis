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
dy= 1200
tradingSessions = 0
buySignals = 0
sellSignals = 0
buyPositions  = 0
sellPositions  = 0
pBuy, lBuy = 0,0
pSell, lSell = 0,0

while dy > 1:
    dy = dy-1
    from_datetime = datetime.datetime(2023, 4, 14, 9, 00, 00, 000000) - datetime.timedelta(days=dy)     # From last & days
    to_datetime = datetime.datetime(2023, 4, 14, 9, 00, 00, 000000) - datetime.timedelta(days=dy-1) 

    interval = "15minute"
    try:
        nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
        dt = pd.DataFrame(nd)
    except:
        continue

    if len(dt)>22:
        tradingSessions = tradingSessions + 1 

    no_of_wicks = 5
    # Looking for buying opportunity
    di = 0
    while di<len(dt)-5:
        di+=1
        dtn = dt[:5+di]
        dtb = dtn.nlargest(no_of_wicks,"high")
        dtb["candle"] = dtb["close"] - dtb["open"]
        dtb = dtb.reset_index()
        #pfuw - price to be choosen for upper wick -> for green candle choose close
        dtb["pfuw"] = [dtb["open"][i] if dtb["candle"][i]<0 else dtb["close"][i] for i in range(len(dtb)) ]
        buy_entry_price = int(max(dtb["pfuw"]) + 1)
        dtb["uwp"] =  dtb["high"]- buy_entry_price   #to get #wicks penetrated
        upper_wicks = max([i+1 if dtb["uwp"][i]>1 else i for i in range(len(dtb))])   

        # print(dtb)
        if min(dtb["uwp"]) >= 0 :
            # print (no_of_wicks,"wicks penetrated succcessfully by a single hz line at", dtb["date"].iloc[-1])
            print (dtb["date"].iloc[-1], "Buy Bank Nifty", "when get a closing above", buy_entry_price)
            buySignals += 1
            ci=5+di
            for i in range(ci,len(dt)):
                if dt["high"][i] > buy_entry_price + 22:
                    print ("Got buying position")
                    buyPositions += 1
                    if dt["high"][i] > buy_entry_price + 100:
                        print ("Profitable buy")
                        pBuy+=1
                        break
                    else:
                        print ("Losing buy signal")
                        lBuy+=1
                        break
            di=23

        # Looking for selling opportunity
        dts = dtn.nsmallest(no_of_wicks,"low")
        dts = dts.nsmallest(no_of_wicks,"date")
        dts["candle"] = dts["close"] - dts["open"]
        dts = dts.reset_index()
        #pflw - price to be choosen for lower wick
        dts["pflw"] = [dts["close"][i] if dts["candle"][i]<0 else dts["open"][i] for i in range(len(dts)) ]
        sell_entry_price = int(min(dts["pflw"]) - 1)
        dts["lwp"] =  sell_entry_price - dts["low"]   #to get #wicks penetrated
        lower_wicks = max([i+1 if dts["lwp"][i]>1 else i for i in range(len(dts))])   
         
        if min(dts["lwp"]) >= 0 :
            # print (no_of_wicks,"wicks penetrated succcessfully by a single hz line at\n", dts["date"].iloc[-1])
            print (dts["date"].iloc[-1],"Sell Bank Nifty", "when get a closing below", sell_entry_price)
            sellSignals += 1
            ci=5+di
            for i in range(ci,len(dt)):
                if dt["low"][i] < buy_entry_price - 22:
                    print ("Got selling position")
                    sellPositions += 1
                    if dt["low"][i] < buy_entry_price - 100:
                        # print ("Profitable sell")
                        pSell+=1
                        break
                    else:
                        # print ("Losing sell signal")
                        lSell+=1
                        break
            di=23

        remaining_wicks = 5 - max(upper_wicks,lower_wicks) + 1
        # print (dts)
totalSignals = buySignals + sellSignals
totalTrades = buyPositions + sellPositions
profitableTrades = pBuy + pSell
losingTrades = lBuy + lSell
winRatio = round(profitableTrades/totalTrades*100,2)

print ("\nIn {} sessions, total {} signals found. Out of which {} were buy and {} were sell signals".format(tradingSessions,totalSignals,buySignals,sellSignals))
print ("Total {} buyPositions made and {} sellPositions made".format(buyPositions,sellPositions))
print ("{} profitable buy trades, out of {} total buy trades".format(pBuy,pBuy+lBuy))
print ("{} profitable sell trades, out of {} total sell trades".format(pSell,pSell+lSell))
print("{} profitable trades, out of total {} trades. \nWinning ratio {}\n".format(profitableTrades,totalTrades,winRatio))

# def entry_exit_stats(s,buy_price,sell_price, dt):
#     buy_flag, sell_flag = False, False
#     for k in range(s,len(dt)):
#         if dt["high"][k] >= buy_price:
#             entry_time = dt["date"][k]
#             print("Entry triggered to buy")
#             buy_flag = True 
#     return(entry_time)

