import pandas as pd

df = pd.read_csv("../assets/NIFTY50_5MIN.csv")
n = len(df)

print(df.head)
executeTime = "14:20"
flag = True
target=0
SL =0
tradeType=""
idx = 0

while( idx < n ):
    if( flag and df['Datetime'][idx][11:16] == executeTime ):
        candleOpen = df['Open'][idx]
        candleClose = df['Close'][idx]
        flag = False
    elif(not flag):
        if(df['Open'][idx] > candleOpen):
            tradeType = "call"

# yet to complete