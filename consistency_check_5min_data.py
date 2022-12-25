# -*- coding: utf-8 -*-
"""
Created on Sat Sep 24 16:30:09 2022

@author: kosht
"""

import pandas as pd
df = pd.read_csv("../assets/BANKNIFTY_5MIN.csv")
n = len(df)

idx=0;
currDate= df['Datetime'][idx][0:10]
currTime= df['Datetime'][idx][11:16]
hours = ['09', '10', '11', '12', '13', '14', '15']
mins = ['00', '05', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55']

data={
    'Datetime':[],
    'Open':[],
    'High':[],
    'Low':[],
    'Close':[],
    'Volume':[]
}

while(currTime != '09:15'):
    idx+= 1
    currDate= df['Datetime'][idx][0:10]
    currTime= df['Datetime'][idx][11:16]

while(idx < n):
    print(idx)
    currDate= df['Datetime'][idx][0:10]
    for h in hours:
        st=0; end=12
        if(h== '09'):
            st=3
        elif(h== '15'):
            end= 6
        for i in range(st, end):
            
            while(idx < n and df['Datetime'][idx][11:16] > "15:25"):
                idx+=1
            if(idx == n): break
            if(df['Datetime'][idx][0:10] == currDate ) and (df['Datetime'][idx][11:16] == h+":"+mins[i]):
                data['Datetime'].append(df['Datetime'][idx])
                data['Open'].append(df['Open'][idx])
                data['Low'].append(df['Low'][idx])
                data['High'].append(df['High'][idx])
                data['Close'].append(df['Close'][idx])
                data['Volume'].append(df['Volume'][idx])
                idx+=1
            else:
                temp = currDate+ " " + h+":"+mins[i] +":00+05:30"
                data['Datetime'].append(temp)
                data['Open'].append(df['Open'][idx])
                data['Low'].append(df['Low'][idx])
                data['High'].append(df['High'][idx])
                data['Close'].append(df['Close'][idx])
                data['Volume'].append(df['Volume'][idx])
    
dk = pd.DataFrame(data)
print(dk.head())
print(len(dk))