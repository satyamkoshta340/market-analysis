# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 13:34:08 2022

@author: kosht
"""

import pandas as pd
import datetime as dt

def getAnalysisReport( result ):
    #  expected type of Input
    # result = {
    #     "Date": [],
    #     "Trade": [],    # call | put
    #     "Strategy": [], # 9:20 | reverse
    #     "Gain": []
    #     }
    n = len(result)
    i = 0
    total_trades = 0
    profitable_trades = 0
    loss_making_trades = 0
    no_trade_days = 0
    max_winning_streak = []
    curr_winning_streak = []
    max_losing_streak = []
    curr_losing_streak = []
    draw_down = 0
    dd = 0
    
    while i < n:
        if result["Trade"][i] != "None":
            total_trades += 1
        else:
            no_trade_days +=1
        if result["Gain"][i] > 0:
            profitable_trades += 1
            curr_winning_streak.append(result["Date"][i])
            curr_losing_streak = []
            max_winning_streak = curr_winning_streak if len(curr_winning_streak) > len(max_winning_streak) else max_winning_streak
        elif result["Gain"][i] < 0:
            loss_making_trades += 1
            curr_winning_streak  = []
            curr_losing_streak.append(result["Date"][i])
            max_losing_streak = curr_losing_streak if len( curr_losing_streak) > len(max_losing_streak) else max_losing_streak
            
        dd += result["Gain"][i]
        draw_down = min( draw_down, dd )
        i+=1
    print("Year:", result["Date"][1][6:10])
    print( "total number of trades: ",  total_trades)
    print( "no trade days", no_trade_days)
    print( "total profitable trades: ", profitable_trades, " [{:f}%]".format(100*profitable_trades/total_trades))
    print( "total loss-making trades: ", loss_making_trades, " [{:f}%]".format(100*loss_making_trades/total_trades))
    print( "max winning streak is ", len(max_winning_streak), " from ", max_winning_streak[0], " to ", max_winning_streak[-1])
    print( "max losing streak: ", len(max_losing_streak), " from ", max_losing_streak[0], " to ", max_losing_streak[-1])
    print( "Draw Down: ", draw_down)
    print( "total profit: ", dd)