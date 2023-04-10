# Test of 5 Times
from kite_trade import *
import pandas as pd
import time
# Run this file on every market trading day at 10:45:10 to get the orders placed
import os
from dotenv import load_dotenv
import datetime
load_dotenv()

enctoken = os.environ.get("ENC_TOKEN")
kite = KiteApp(enctoken=enctoken)

test_duration = 90 #90 Days or 3 months
interval = "day"
instrument_token = "3019265" #SAKSOFT
from_datetime = datetime.datetime.now() - datetime.timedelta(days=test_duration)     # From last & days
to_datetime = datetime.datetime.now()- datetime.timedelta(days=1)

nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
dt = pd.DataFrame(nd)
# print(dt.head())

def find_TOT_in_bulls(dt, time_count = 5):
    five_high = dt.nlargest( time_count + 20, "high")

    i = time_count - 1
    while( i< time_count + 20 ):
        j = i
        target_value = five_high["high"][i]*0.99
        c = 0
        while( j >= 0 ):
            if target_value > five_high["open"][i] and target_value > five_high["close"][i]:
                c += 1
            j -= 1
        if c >= time_count:
            print("Test of {c} Times occured at ".format(c = c), dt["date"][len(dt)-1])
            break
        i+=1

find_TOT_in_bulls(dt)