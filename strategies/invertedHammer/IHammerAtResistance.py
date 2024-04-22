# ================================================ Strategy: Inverted Hammer At Resistance ==============================================#
# Hypothesis: If market creates an inverted hammer at resistance then on breaking low it will move down in the multiples of candle size
# Strategy type: Intraday
# Signal: On breaking the low of inverted hammer at day High
# Entry: Buy put after the move
# SL: high of the inverted hammer candle
# Target: Nx of inverted hammer candle body
# Strategy implementation time: 10:00 AM to 03:15 PM
# Comments: 

import os, sys
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import datetime
load_dotenv()

# Add the root directory to the sys.path temporarily to import from any root label module like scripts
root_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root_dir))

from scripts.kite_trade import *

enctoken = os.environ.get("ENC_TOKEN")
kite = KiteApp(enctoken=enctoken)


def IHammerAtResistance(dp, n=2):
    positions = []
    inTrade = False

    currentDate = dp["date"][0].date()
    print(currentDate)
    dayHigh=0

    for i in range(len(dp)):
        upper_wick =  dp['high'][i] - max(dp['close'][i], dp['open'][i])
        lower_wick =  min(dp['close'][i], dp['open'][i]) - dp['low'][i]
        body_of_candle =  abs(dp['open'][i] - dp['close'][i])
        span_of_candle = abs(dp['low'][i] - dp['high'][i])

        if currentDate != dp["date"][i].date():
            if inTrade:
                #terminate trade forcefully
                print(currentDate, dp["date"][i].date(), currentDate != dp["date"][i].date())
                print("terminate trade forcefully")
                positions.append(dp.iloc[i-1].to_list() + [entry, sl, target, entry - dp["close"][i-1]])
                inTrade = False
                dayHigh = 0
            currentDate = dp["date"][i].date()
            dayHigh=0;

        if not inTrade:
            # simple conditions 
            if (upper_wick > 5*body_of_candle and upper_wick > 2*lower_wick) and (dp["high"][i] > dayHigh):
                entry = dp["low"][i]
                sl = dp["high"][i]
                target = entry - n*span_of_candle
                inTrade = True
                print (dayHigh, dp['high'][i])
                print("=============got entry for ", dp["date"][i], " =================")
        else:
            if dp["low"][i] <= target:
                # we found the target
                print(dp["date"][i], dp["low"][i] , target, dp["low"][i] <= target)
                print("we found the target")
                positions.append(dp.iloc[i].to_list() + [entry, sl, target, entry - target])
                inTrade = False
            elif dp["high"][i] >= sl:
                # we hit the SL
                print(dp["date"][i], dp["high"][i], sl, dp["high"][i] >= sl)
                print("we hit the SL")
                positions.append(dp.iloc[i].to_list() + [entry, sl, target, entry - sl])
                inTrade = False
        currentDate = dp["date"][i].date()
        dayHigh = max(dayHigh, dp["high"][i])
    return positions

def main():
    print (os.getcwd())
    # try:
    #     dp = pd.read_csv( os.getcwd()+"/market-analysis/assets/Nifty50_28Mar2024.csv")
    # except:
    #     dp = pd.read_csv( os.getcwd()+"\\assets\\Nifty50_28Mar2024.csv")


    nifty50_instrument = kite.ltp('NSE:NIFTY 50')
    print("Instrument token for Nifty 50:", nifty50_instrument['NSE:NIFTY 50']['instrument_token'])
    cDays = 30
    instrument_token = nifty50_instrument['NSE:NIFTY 50']['instrument_token']
    from_datetime = datetime.datetime(2024, 3, 1)
    to_datetime = from_datetime + datetime.timedelta(days=cDays)  
    interval = "5minute"
    dp = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)

    dp = pd.DataFrame(dp)
    dp.to_csv("Nifty50_01Mar2024.csv")
    # print(dp.head())


    result = IHammerAtResistance(dp)
    # print(result)
    columns = ["date","open","High","low","close", "volume", "Entry", "SL", "Target", "Final"]
    df = pd.DataFrame(result, columns=columns)
    
    df.to_csv("IHammerNifty50.csv")

main()
