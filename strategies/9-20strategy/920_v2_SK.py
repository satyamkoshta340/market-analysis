# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 13:34:08 2022

@author: kosht
Backtesting 
Data points requirement : 5min candle
Looking for 9:15 candle high and low
checking for break of five_min_high and five_min_low
target points: 100
sl points: 70
reverse trade is enabled before 10:00
termiate the trade forcefully after 11:00
"""

import pandas as pd
import datetime as dt
import sys, os
from pathlib import Path

# Add the root directory to the sys.path temporarily
root_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root_dir))

from scripts.globalTest import *

# need to provide 5 min datasets as dp 


def analysisOf920(dp):
    signal_time = "09:15"
    max_market_time = "11:00"
    reverse_trade_max_entry_time = "10:00"
    n = len(dp)
    i = 0
    result = {
        "Date": [],
        "Month": [],
        "Year": [],
        "Day": [],
        "Trade": [],    # call | put
        "Strategy": [], # 9:20 | reverse
        "Entry Time": [],
        "Exit Time": [],
        "Entry Price": [],
        "Exit Price": [],
        "Gain": []
    }
    
    while( i < n ):
        td= dp["Date"][i]
        five_minute_high = dp["High"][i]
        five_minute_low = dp["Low"][i]
        entry = 0
        sl = 0
        target = 0
        in_trade = False
        can_reverse = True
        i +=  1
        strategy = "09:20"
        g = 0
        entryTime = None
        exitTime = None
        entryPrice = None
        exitPrice = None
        tradeGain = 0
        trade = "None"
        while(i < n and td == dp["Date"][i]):
            if( not in_trade and dp["Close"][i] > five_minute_high ):
                # found a call trade
                entry = five_minute_high
                sl = five_minute_high - 70
                target = five_minute_high + 100
                in_trade = "call"
                trade = "call"
                entryTime = dp["Date"][i] + "--" + dp["Time"][i]
                entryPrice = five_minute_high
                # print("Started a CALL trade at ", dp["Time"][i], " on ", dp["Time"][i])
            elif not in_trade and dp["Close"][i] < five_minute_low :
                # found a put
                entry = five_minute_low
                sl = five_minute_low + 70
                target = five_minute_low - 100
                in_trade = "put"
                trade = "put"
                entryTime = dp["Date"][i] + "--" + dp["Time"][i]
                entryPrice = five_minute_low
                # print("Started a PUT trade at ", dp["Time"][i], " on ", dp["Time"][i])
            elif in_trade:
                while( i< n and td == dp["Date"][i] ):
                    if( in_trade in ["put", "call"] and  dp["Time"][i] > max_market_time ):
                        # terminate the trade
                        g += dp["Open"][i] - entry
                        in_trade = "terminated"
                        exitTime = dp["Date"][i] + "--" + dp["Time"][i]
                        exitPrice = dp["Open"][i]
                        
                        tradeGain = exitPrice - entryPrice if in_trade == "call" else entryPrice - exitPrice
                                
                    elif( in_trade == "call" ):
                        if( dp["High"][i] >= target ):
                            # profit booked
                            g += 100
                            in_trade = "terminated"
                            exitTime = dp["Date"][i] + "--" + dp["Time"][i]
                            exitPrice = target
                            tradeGain = 100
    
                        elif( dp["Low"][i] <= sl):
                            # loss booked in call
                            g += -70
                            in_trade = "terminated"
                            exitTime = dp["Date"][i] + "--" + dp["Time"][i]
                            exitPrice = sl
                            tradeGain = -70
                            if( can_reverse and dp["Time"][i] < reverse_trade_max_entry_time ):
                                in_trade = "reverse_call"
                                can_reverse = False

                                result["Date"].append(td)
                                result["Month"].append(td[3:5])
                                result["Year"].append(td[6:])
                                result["Day"].append(dt.datetime.strptime(td, '%d-%m-%Y').strftime('%A'))
                                result["Strategy"].append(strategy)
                                result["Trade"].append(trade)
                                result["Entry Time"].append(entryTime)
                                result["Exit Time"].append(exitTime)
                                result["Entry Price"].append(entryPrice)
                                result["Exit Price"].append(exitPrice)
                                result["Gain"].append(tradeGain)

                                entryTime = dp["Date"][i] + "--" + dp["Time"][i]
                                entryPrice = dp["Low"][i]
                            
                    elif( in_trade == "put" ):
                        if( dp["Low"][i] <= target ):
                            g += 100
                            in_trade = "terminated"
                            exitTime = dp["Date"][i] + "--" + dp["Time"][i]
                            exitPrice =target
                            tradeGain = 100
                            
                        elif dp["High"][i] >= sl:
                            g += -70
                            in_trade = "terminated"

                            exitTime = dp["Date"][i] + "--" + dp["Time"][i]
                            exitPrice = sl
                            tradeGain = -70

                            if( can_reverse and dp["Time"][i] < reverse_trade_max_entry_time ):
                                in_trade = "reverse_put"
                                can_reverse = False

                                result["Date"].append(td)
                                result["Month"].append(td[3:5])
                                result["Year"].append(td[6:])
                                result["Day"].append(dt.datetime.strptime(td, '%d-%m-%Y').strftime('%A'))
                                result["Strategy"].append(strategy)
                                result["Trade"].append(trade)
                                result["Entry Time"].append(entryTime)
                                result["Exit Time"].append(exitTime)
                                result["Entry Price"].append(entryPrice)
                                result["Exit Price"].append(exitPrice)
                                result["Gain"].append(tradeGain)
                                
                                entryTime = dp["Date"][i] + "--" + dp["Time"][i]
                                entryPrice = dp["High"][i]
                                
                    elif in_trade == "reverse_call":
                        if dp["Low"][i] < five_minute_low:
                            strategy += in_trade
                            in_trade = "put"
                            trade += ", put"
                            entry = five_minute_low
                            target = five_minute_low - 100
                            sl = five_minute_low + 70
                    elif in_trade == "reverse_put":
                        if dp["High"][i] > five_minute_high:
                            strategy += in_trade
                            in_trade = "call"
                            trade += ", call"
                            entry = five_minute_high
                            target = five_minute_high + 100
                            sl = five_minute_high - 70
                    else:
                        pass
                    i+=1
                i -= 1
            i+=1
        result["Date"].append(td)
        result["Month"].append(td[3:5])
        result["Year"].append(td[6:])
        result["Day"].append(dt.datetime.strptime(td, '%d-%m-%Y').strftime('%A'))
        result["Strategy"].append(strategy)
        result["Trade"].append(trade)
        result["Entry Time"].append(entryTime)
        result["Exit Time"].append(exitTime)
        result["Entry Price"].append(entryPrice)
        result["Exit Price"].append(exitPrice)
        result["Gain"].append(tradeGain)
    return result

def main():
    print (os.getcwd())
    result = pd.DataFrame({
        "Date": [],
        "Month": [],
        "Year": [],
        "Day": [],
        "Trade": [],    
        "Strategy": [],
        "Entry Time": [],
        "Exit Time": [],
        "Entry Price": [],
        "Exit Price": [],
        "Gain": []
    })
    for i in range(2015, 2021):
        try:
            dp = pd.read_csv( os.getcwd()+"/market-analysis/assets/BANK_NIFTY_5_MIN_{year}.csv".format(year = i))
        except:
            dp = pd.read_csv( os.getcwd()+"\\market-analysis\\strategies\\assets\\BANK_NIFTY_5_MIN_{year}.csv".format(year = i))

        res = analysisOf920(dp)
        res = pd.DataFrame(res)
        print(res.head())
        result = pd.concat([result, res])
    result.to_csv("920_v2_logs.csv")
    print(result.head());
    getGlobalAnalysis(result)

main()

