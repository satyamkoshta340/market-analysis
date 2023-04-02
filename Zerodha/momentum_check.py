from kite_trade import *
import pandas as pd
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

enctoken = os.environ.get("ENC_TOKEN")
kite = KiteApp(enctoken=enctoken)

# Get Historical Data
dir_path = os.path.dirname(os.path.realpath(__file__))
stk = pd.read_csv( dir_path+ "/itkn.csv")

# Lopping through the list of FNO stocks (having high volumes)
for k in range(0, len(stk)):
    # if stk["itkn"][k] != 225537: continue
    # getting historical data
    instrument_token = stk["itkn"][k]    # DRREDDY 225537
    from_datetime = datetime.datetime.now() - datetime.timedelta(days=1)     # From last & days
    to_datetime = datetime.datetime.now()
    interval = "5minute"
    nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
    # print(kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False))
    dt = pd.DataFrame(nd)

    if len(dt) < 7:
        print ("Error fetching data for", stk["EQ"][k])
        continue
    # else:
    # 	print ("Data fetched for", stk["EQ"][k], instrument_token, len(dt))

    last_candle_size = abs(dt["open"][0] - dt["close"][0])
    candles_count = 1
    last_candle_type = "red" if dt["open"][0] > dt["close"][0] else "green"

    for i in range(1, len(dt["date"])):
        candle_type = "red" if dt["open"][i] > dt["close"][i] else "green"
        candle_size = abs(dt["open"][i] - dt["close"][i])
        if candle_type == last_candle_type and candle_size > last_candle_size:
            last_candle_size = candle_size
            candles_count += 1
        else:
            last_candle_type = candle_type
            candles_count = 1
            last_candle_size = candle_size

        if candles_count == 3:
            if candle_type == "red":
                # momentum found in the bears
                print("momentum found in the BEARs for stock "+ stk["EQ"][k] + " at " + str(dt["date"][i]))
            else:
                # momentum found in bulls
                print("momentum found in the BULLs for stock "+ stk["EQ"][k] + " at " + str(dt["date"][i]))
            break
            
    