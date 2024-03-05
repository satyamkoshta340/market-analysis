import pandas as pd
import os
import datetime
from Hammer import findHammers
from kite_trade import *
from dotenv import load_dotenv
import time
load_dotenv()
# THis is the latest commit 2
enctoken = os.environ.get("ENC_TOKEN")
kite = KiteApp(enctoken=enctoken)
date_format = "%Y-%m-%d %H:%M:%S"
dir_path = os.path.dirname(os.path.realpath(__file__))

def getDailyData(
        instrument_token = 225537,    # DRREDDY 225537,
        cDays = 5, # number of Days Data
        from_datetime = datetime.datetime(2024, 1, 24, 18, 00, 00, 000000) # date from data required 
        ):

    to_datetime = from_datetime + datetime.timedelta(days=cDays)  
    interval = "day"
    dt = pd.DataFrame()
    try:
        nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
        # print(nd)
        dt = pd.DataFrame(nd)
    except:
        print("XXXXXXXXXXXXXXXXX DATA NOT FOUND XXXXXXXXXXXXXXXXXX")
        return dt
    return dt

def runTest(to_datetime = datetime.datetime(2024, 1, 24, 18, 00, 00, 000000)):
    print( "Running Test for: ", to_datetime)
    try:
        """ To Fetch Data """
        dp = findHammers(to_datetime)
        dp.to_csv(dir_path + "/HammersSignals" + to_datetime.strftime("%d-%m-%Y")  +".csv")

        """ To Use Fetched Data """
        dp = pd.read_csv(dir_path + "/HammersSignals" + to_datetime.strftime("%d-%m-%Y")  +".csv")

        if len(dp)== 0:
            print("XXXXXXXXXXXXXX NO SINGNAL FOUND XXXXXXXXXXXXXXXXX")
            return pd.DataFrame()
        
        if datetime.datetime.strptime(dp["date"][0][:-6], date_format).strftime("%Y-%m-%d") != to_datetime.strftime("%Y-%m-%d"):
            return pd.DataFrame()
    except:
        print("XXXXXXXXXXXXXX ERROR IN FETHING SINGNALS XXXXXXXXXXXXXXXXX")
        return
    
    result = {
        'EQ': [],
        'signal_date': [],
        'entry_date': [],
        'exit_date': [],
        'entry_price': [],
        'exit_price': [],
        'profit': []
    }
    for i in range(len(dp)):
        try:
            from_datetime = datetime.datetime.strptime(dp["date"][i][:-6], date_format) + datetime.timedelta(days=1)
        except:
            from_datetime = dp["date"][i] + datetime.timedelta(days= 1)

        df = getDailyData(dp["itkn"][i], 5, from_datetime)
        
        if len(df) == 0:
            continue

        # print("Got Data To Test for ", dp["EQ"][i])
        entry_lower_range = dp["close"][i] - dp["close"][i]*0.005
        entry_upper_range = dp["high"][i] + dp["close"][i]*0.005
        sl = dp["low"][i]
        target = dp["close"][i]  + (dp["close"][i] - dp["low"][i])*2
        if entry_lower_range <= df["open"][0] <= entry_upper_range:
            # print("Got Entry for ", dp["EQ"][i])
            result["EQ"].append(dp["EQ"][i])
            result["signal_date"].append(dp["date"][i])
            result["entry_date"].append(df["date"][0])
            result["entry_price"].append(df["open"][0])
            if df["low"][0] <= sl and df["high"][0] >= target:
                #Its Lose case
                # print("lost")
                result["exit_date"].append(df["date"][0])
                result["exit_price"].append(sl)
                result["profit"].append( result["exit_price"][-1] - result["entry_price"][-1])
            elif df["low"][0] <= sl:
                #SL hit
                # print("lost")
                result["exit_date"].append(df["date"][0])
                result["exit_price"].append(sl)
                result["profit"].append(result["exit_price"][-1] - result["entry_price"][-1])
            elif df["high"][0] >= target:
                #Taarget hit
                # print("won")
                result["exit_date"].append(df["date"][0])
                result["exit_price"].append(target)
                result["profit"].append(result["exit_price"][-1] - result["entry_price"][-1])
            elif df["low"][1] <= sl and df["high"][1] >= target:
                #Its Lose case
                # print("lost")
                result["exit_date"].append(df["date"][1])
                result["exit_price"].append(sl)
                result["profit"].append(result["exit_price"][-1] - result["entry_price"][-1])
            elif df["low"][1] <= sl:
                #SL hit
                # print("lost")
                result["exit_date"].append(df["date"][1])
                result["exit_price"].append(sl)
                result["profit"].append(result["exit_price"][-1] - result["entry_price"][-1])
            elif df["high"][1] >= target:
                #Taarget hit
                # print("won")
                result["exit_date"].append(df["date"][1])
                result["exit_price"].append(target)
                result["profit"].append(result["exit_price"][-1] - result["entry_price"][-1])
            else:
                #force exit
                # print("Force")
                result["exit_date"].append(df["date"][1])
                result["exit_price"].append(df["close"][1])
                result["profit"].append(result["exit_price"][-1] - result["entry_price"][-1])
        else:
            print("NO Entry for ", dp["EQ"][i])
    # print(result)
    dr = pd.DataFrame(result)
    # dr.to_csv(dir_path + "/HammersResult" + to_datetime.strftime("%d-%m-%Y")  +".csv")
    return dr


if __name__ == "__main__":
    to_datetime = datetime.datetime(2023, 1, 1, 18, 00, 00, 000000)
    days = 365
    fdr = pd.DataFrame()
    curr_month = to_datetime.month
    while( days > 0 ):
        dr = runTest(to_datetime = to_datetime)
        fdr = pd.concat([fdr, dr], ignore_index=True)
        to_datetime = to_datetime + datetime.timedelta(days=1)
        if to_datetime.month > curr_month:
            fdr.to_csv(dir_path + "/HammersResult_" + str(curr_month)  +".csv")
            fdr = pd.DataFrame()
            time.sleep(10)
            curr_month += 1
        days -= 1
    fdr.to_csv(dir_path + "/HammersResult" + to_datetime.strftime("%d-%m-%Y")  +".csv")