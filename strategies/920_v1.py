# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 13:34:08 2022

@author: kosht

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

def analysisOf920(dp):
    signal_time = "09:15"
    max_market_time = "11:00"
    reverse_trade_max_entry_time = "10:00"
    n = len(dp)
    i = 0
    result = {
        "Date": [],
        "Trade": [],    # call | put
        "Strategy": [], # 9:20 | reverse
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
        trade = "None"
        while(i < n and td == dp["Date"][i]):
            if( not in_trade and dp["Close"][i] > five_minute_high ):
                # found a call trade
                entry = five_minute_high
                sl = five_minute_high - 70
                target = five_minute_high + 100
                in_trade = "call"
                trade = "call"
                # print("Started a CALL trade at ", dp["Time"][i], " on ", dp["Time"][i])
            elif not in_trade and dp["Close"][i] < five_minute_low :
                # found a put
                entry = five_minute_low
                sl = five_minute_low + 70
                target = five_minute_low - 100
                in_trade = "put"
                trade = "put"
                # print("Started a PUT trade at ", dp["Time"][i], " on ", dp["Time"][i])
            elif in_trade:
                while( i< n and td == dp["Date"][i] ):
                    if( in_trade in ["put", "call"] and  dp["Time"][i] > max_market_time ):
                        # terminate the trade
                        g += dp["Open"][i] - entry
                        in_trade = "terminated"
                                
                    elif( in_trade == "call" ):
                        if( dp["High"][i] >= target ):
                            # profit booked
                            g += 100
                            in_trade = "terminated"
    
                        elif( dp["Low"][i] <= sl):
                            # loss booked in call
                            g += -70
                            in_trade = "terminated"
                            if( can_reverse and dp["Time"][i] < reverse_trade_max_entry_time ):
                                in_trade = "reverse_call"
                                can_reverse = False
                            
                    elif( in_trade == "put" ):
                        if( dp["Low"][i] <= target ):
                            g += 100
                            in_trade = "terminated"
                            
                        elif dp["High"][i] >= sl:
                            g += -70
                            in_trade = "terminated"
                            if( can_reverse and dp["Time"][i] < reverse_trade_max_entry_time ):
                                in_trade = "reverse_put"
                                can_reverse = False
                                
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
        result["Strategy"].append(strategy)
        result["Trade"].append(trade)
        result["Gain"].append(g)
    return result