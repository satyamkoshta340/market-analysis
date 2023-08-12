# ================================================ Strategy: Leveraging rapid moves ==============================================#
# Hypothesis: If market moves 0.5% up within 10/15 minutes. Chances are it will give away all the gains
# Strategy type: Intraday
# Signal: Rapid move of more than 0.5% within 10/15 minutes
# Entry: Buy put after the rapid move
# SL: 0.25% above rapid move
# Target: rapid move pts from entry
# Strategy implementation time: 10:00 AM to 03:15 PM
# Comments: Mostly happens on an event day i.e. RBI policy 
# =============================== Stats to be produced ==============================================#
# Frequency of the signal (Out of x trading days y trading signals)
# Win to lose ratio
# Max win/lose streak
# Daily/Monthly reports, ex 5 signals on wednesday out of which 3 win 2 lose
# Cumulative profit in a year
# ===================================================================================================#


import os
import pandas as pd
# Reading the data file 
dp = pd.read_csv( os.getcwd()+"\\assets\\BANK_NIFTY_5_MIN_2020.csv")
# dp = pd.read_csv( os.getcwd()+"/strategies/assets/BANK_NIFTY_5_MIN_2015.csv")

# def rapidMove(dp):
signal_time = "10:15"
max_market_time = "15:10"
n = len(dp)
n = 2000
i = 0
result = {
"Date": [],
"Trade": [],    # call | put
"Strategy": [], # 9:20 | reverse
"Gain": []
}

# Looping through the yearly data
while( i < n ):
    td= dp["Date"][i]
    entry = 0
    sl = 0
    target = 0
    in_trade = False
    strategy = "RapidMove"
    g = 0
    trade = "None"
    candle = 0
# going through the same days' data    -- a day has 74 candles of 5 minute, terminating at 72nd candle
    while(i < n and td == dp["Date"][i] and candle <72):
        candle += 1
        rapidPts = dp["Close"][i]*0.0044            # If index moves more than half percent within 10/15 minutes
# Creating vars to check movement within 10/ 15 min
        tenMinMove = dp["High"][i+1] - dp["Low"][i]
        fifteenMinMove = dp["High"][i+2] - dp["Low"][i]
        rHigh = dp["High"][i+2]
        rLow = dp["Low"][i]
        rClose = dp["Close"][i+2]
# First creating a strategy to detect 15 mins rapid move
        if( not in_trade and (fifteenMinMove > rapidPts)):
        # if( not in_trade and (tenMinMove > rapidPts or fifteenMinMove > rapidPts)): this can be materialized later
            print ("Signal generated: Found a 10 min rapid move")
            print (dp["Date"][i],dp["Time"][i], rLow, rHigh)
            entry = rLow + rapidPts
            sl = rHigh + rapidPts/2
            target = rHigh - rapidPts
            in_trade = "put"
            trade = "put"
        i+=1
    i+=1
