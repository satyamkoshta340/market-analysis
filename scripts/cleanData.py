# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 13:34:08 2022

@author: kosht
"""

import pandas as pd
import datetime as dt

def cleanData(df, k):
    data = {
        "Date": [],
        "Time": [],
        "Open": [],
        "High": [],
        "Low": [],
        "Close": []
        }
    n = len(df)
    i = 0
    flag = True
    # fault_days = set()
    while( flag and i < n ):
        date = df["Date"][i]
        real_date =date
        date = str(date)
        date = date[6:8] + "-" + date[4:6] + "-" + date[0:4]
        time = df["Time"][i] if( df["Time"][i] != "09:08" ) else "09:15"
        o = df["Open"][i]
        h = df["High"][i]
        l = df["Low"][i]
        t = dt.datetime.strptime( time,'%H:%M' )
        for j in range(i+1, i+k):
            if( j == n):
                i = n
                flag = False
                break
            t = t + dt.timedelta(minutes = 1)
            if( "{:02d}:{:02d}".format(t.hour, t.minute) != df["Time"][j] ):
                flag = False
                break
            h = max(h, df["High"][j])
            l = min(l, df["Low"][j])
            
        if(not flag):
            flag = True
            # print("-------------------------------------------")
            while( i< n and df["Date"][i] == real_date ):
                _date = df["Date"][i]
                _date = str(_date)
                _date = _date[6:8] + "-" + _date[4:6] + "-" + _date[0:4]
                # print("skipiing ", _date, " ", df["Time"][i]) 
                i = i + 1
            continue
        i = i+k
        c = df["Close"][i-1]
        data["Date"].append(date)
        data["Time"].append(time)
        data["Open"].append(o)
        data["High"].append(h)
        data["Low"].append(l)
        data["Close"].append(c)
    return pd.DataFrame(data);