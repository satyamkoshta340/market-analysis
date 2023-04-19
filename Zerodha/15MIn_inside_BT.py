from dotenv import load_dotenv
import pandas as pd
from kite_trade import *
import datetime
import os

load_dotenv()

enctoken = os.environ.get("ENC_TOKEN")
kite = KiteApp(enctoken=enctoken)

def insideCandleBT(dt, target_point = 100, sl_point = 80):
    scanned = []
    number_of_inside_candles = 5        #including the first candle
    result = {
        "trade_type": [],
        "entry_time": [],
        "exit_time": [],
        "entry_price": [],
        "exit_price": [],
        "profit": [],
        "profitable": [],
        "signal_time": []
    }
    filtered_scan1 = []; filtered_scan2 = []
    if len(dt) < 7:
        print ("not enough data")
        return pd.DataFrame(result)

    # Finding the inside candle pattern in today's stocks
    i = 0
    c = -1
    while i < len(dt) - number_of_inside_candles:
        start_time_hh = str(dt["date"][i]).split()[1][:2]
        start_time_mm = str(dt["date"][i]).split()[1][3:5]
        if start_time_hh == '09' and start_time_mm == '15':
            flag = True
        if flag and (c == -1 or result["exit_price"][c] not in [-1, -2] ):
            if dt["high"][i] <50:
                print("Can't run algo for this stock price")
                return pd.DataFrame(result)
            else:
                first_15m_high = dt["high"][i]
                first_15m_low = dt["low"][i]
                first_candle_size = first_15m_high - first_15m_low
                pct_candle = round(100*first_candle_size/first_15m_high,2)
                rsfr = first_candle_size*.62   # Fibonacci retracement value for filtering proper stocks

                if first_15m_high > max(dt["high"][i+1:i+number_of_inside_candles]) and first_15m_low < min(dt["low"][i+1:i+number_of_inside_candles]):
                    
                    scanned.append((pct_candle))
                    # Inside candel pattern occured

                    if min(dt["low"][i+1:i+number_of_inside_candles]) >= (first_15m_high - rsfr):
                        print ("Condition to place buy order at ", dt["date"][i])
                        if pct_candle <= 3.5:
                            filtered_scan1.append((pct_candle, first_15m_high))
                            result["signal_time"].append(dt["date"][i+number_of_inside_candles-1])
                            result["trade_type"].append("BUY")
                            result["entry_price"].append(round((first_15m_high + first_15m_high*0.0001),1))
                            result["entry_time"].append(-1)
                            result["exit_price"].append(-1)
                            result["profitable"].append(-1)
                            result["exit_time"].append(-1)
                            result["profit"].append(-1)
                            i += number_of_inside_candles - 1
                            c += 1
                    elif max(dt["high"][i+1:i+number_of_inside_candles]) <= (first_15m_low + rsfr):
                        print ("Condition satisfied to place sell order at", dt["date"][i])
                        if pct_candle <= 3.5:
                            filtered_scan2.append((pct_candle, first_15m_low))
                            result["signal_time"].append(dt["date"][i+number_of_inside_candles-1])
                            result["trade_type"].append("SELL")
                            result["entry_price"].append(round((first_15m_low - first_15m_low*0.0001),1))
                            result["entry_time"].append(-1)
                            result["exit_price"].append(-1)
                            result["profitable"].append(-1)
                            result["exit_time"].append(-1)
                            result["profit"].append(-1)
                            i += number_of_inside_candles -1
                            c += 1

        elif result["exit_price"][c] == -1:
            if start_time_hh == '15' and start_time_mm == '15':
                # force exit the trade
                if result["entry_time"][c] == -1:
                    result["exit_price"][c] = -2
                    continue
                else:
                    result["exit_time"][c] =dt["date"][i]
                    result["exit_price"][c] = dt["close"][i]
                    result["profitable"][c] = (True if (result["trade_type"][c] == "BUY" and result["exit_price"][c] > result["entry_price"][c]) 
                                                or (result["trade_type"][c] == "SELL" and result["exit_price"][c] < result["entry_price"][c])  else False)
                    result["profit"][c] =  result["exit_price"][c] - result["entry_price"][c] if result["trade_type"][c] == "BUY" else result["entry_price"][c] - result["exit_price"][c]

            elif result["entry_time"][c] == -1:
                if result["trade_type"][c] == "BUY" and dt["close"][i] >= result["entry_price"][c]:
                    result["entry_time"][c] = dt["date"][i]
                    flag = False

            elif result["trade_type"] == "BUY":
                if dt["close"][i] >= result["entry_price"][c] + target_point :
                    # print( " Target reached ")
                    result["exit_price"][c] = dt["close"][i]
                    result["exit_time"][c] = dt["date"][i]
                    result["profitable"][c] = True
                    result["profit"][c] = dt["close"][i] - result["entry_price"][c]
                elif dt["close"][i] <= result["entry_price"][c] - sl_point :
                    # print( "SL triggered")
                    result["exit_price"][c] = dt["close"][i]
                    result["exit_time"][c] = dt["date"][i]
                    result["profitable"][c] = False
                    result["profit"][c] = result["entry_price"][c] -  dt["close"][i]

            elif result["trade_type"][c] == "SELL":
                if dt["close"][i] <= result["entry_price"][c] - target_point :
                    result["exit_price"][c] = dt["close"][i]
                    result["exit_time"][c] = dt["date"][i]
                    result["profitable"][c] = True
                    result["profit"][c] =  dt["close"][i] - result["entry_price"][c] 
                elif dt["close"][i] >= result["entry_price"][c] + sl_point :
                    result["exit_price"][c] = dt["close"][i]
                    result["exit_time"][c] = dt["date"][i]
                    result["profitable"][c] = False
                    result["profit"][c] = result["entry_price"][c] - dt["close"][i]
        i+=1

    df = pd.DataFrame(result)
    # print(df.head())
    # df.to_csv("15min_BT_result.csv")
    return df


dir_path = os.path.dirname(os.path.realpath(__file__))
stk = pd.read_csv( dir_path+ "/itkn.csv")
results = pd.DataFrame({
        "trade_type": [],
        "entry_time": [],
        "exit_time": [],
        "entry_price": [],
        "exit_price": [],
        "profit": [],
        "profitable": [],
        "signal_time": [],
        "stock" : []
    })
for k in range(0,len(stk)):
    # if stk["itkn"][k] != 225537: continue
    # getting historical data
    instrument_token = stk["itkn"][k]
    from_datetime = datetime.datetime(2023, 4, 18, 9, 15, 00, 000000)
    to_datetime = datetime.datetime(2023, 4, 18, 18, 00, 00, 000000)
    interval = "15minute"
    nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
    dt = pd.DataFrame(nd)
    print(dt.head())
    try:
        df = insideCandleBT(dt)
        df["stock"] = [stk["EQ"][k]] * len(df)
        print(df.head())
        results = pd.concat([results, df])
    except:
        print("------------------------------------------")
        print("Error in ", stk["EQ"][k])

results.to_csv("15min_BT_result.csv")