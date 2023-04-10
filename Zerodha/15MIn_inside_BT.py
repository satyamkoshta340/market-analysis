from dotenv import load_dotenv
import pandas as pd
from kite_trade import *
import datetime
import os

load_dotenv()

enctoken = os.environ.get("ENC_TOKEN")
kite = KiteApp(enctoken=enctoken)

def insideCandleBT(dt):
    scanned = []
    result = {
        "trade_type": [],
        "entry_time": [],
        "exit_time": [],
        "entry_price": [],
        "exit_price": [],
        "profit": [],
        "profitable": []
    }
    filtered_scan1 = []; filtered_scan2 = []
    if len(dt) < 7:
        print ("not enough data")
        return None
    # else:
    # 	print ("Data fetched for", stk["EQ"][k], instrument_token, len(dt))
    
    # Finding the inside candle pattern in today's stocks
    i = 0
    c = -1
    while i < len(dt["date"]) - 4:
        start_time_hh = str(dt["date"][i]).split()[1][:2]
        start_time_mm = str(dt["date"][i]).split()[1][3:5]
        if start_time_hh == '09' and start_time_mm == '15':
            if dt["high"][i] <150:
                print("Can't run algo for this stock price")
                return None
            else:
                first_15m_high = dt["high"][i]
                first_15m_low = dt["low"][i]
                first_candle_size = first_15m_high - first_15m_low
                pct_candle = round(100*first_candle_size/first_15m_high,2)
                rsfr = first_candle_size*.62
                # print ("Scanning", stk["EQ"][k],dt["date"][i] )
                if first_15m_high > max(dt["high"][i+1:i+5]) and first_15m_low < min(dt["low"][i+1:i+5]):
                    ptf += 1
                    # print (stk["EQ"][k], "formed pattern with candle size of", first_candle_size, "percentage.")
                    # print (dt.loc[i:i+5])
                    scanned.append((pct_candle))
                    # print (first_15m_high,rsfr, first_15m_low, min(dt["low"][i+1:i+5]), first_15m_high- rsfr )

                    if min(dt["low"][i+1:i+5]) >= (first_15m_high - rsfr):
                        # print ("Condition to place buy order")
                        if pct_candle <= 1.5:
                            filtered_scan1.append((pct_candle, first_15m_high))
                            result["trade_type"] = "BUY"
                            result["entry_price"] = dt["close"][i+4]
                            result["entry_time"] = dt["date"][i+4]
                            result["exit_price"] = None
                            i += 4
                            c += 1

                    if max(dt["high"][i+1:i+5]) <= (first_15m_low + rsfr):
                        # print ("Condition satisfied to place sell order")
                        if pct_candle <= 1.5:
                            filtered_scan2.append((pct_candle, first_15m_low))
                            result["trade_type"] = "SELL"
                            result["entry_price"] = dt["close"][i+4]
                            result["entry_time"] = dt["date"][i+4]
                            result["exit_price"] = None
                            i += 4
                            c += 1
        elif c != -1 and result["exit_price"] == None:
            if dt["close"][i] >= result["entry_price"][c]*1.01 :
                # print( " Target reached ")
                result["exit_price"] = dt["close"][i]
                result["exit_time"] = dt["date"][i]
                result["profitable"] = True
                result["profit"] = dt["close"][i] - result["entry_price"][c]
            elif dt["close"][i] <= result["entry_price"][c]*0.94 :
                # print( "SL triggered")
                result["exit_price"] = dt["close"][i]
                result["exit_time"] = dt["date"][i]
                result["profitable"] = False
                result["profit"] = result["entry_price"][c] - dt["close"][i]
        i+=1

    df = pd.DataFrame(result)
    print(df.head)
    df.to_csv("15min_BT_result.csv")
    return df

instrument_token = "DRREDDY"
from_datetime = datetime.datetime(2022, 3, 26, 8, 00, 00, 000000)
to_datetime = datetime.datetime(2023, 3, 27, 18, 00, 00, 000000)
interval = "15minute"
nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
dt = pd.DataFrame(nd)

insideCandleBT(dt)