import numpy as np
def ema_Vol(DF,day):
        """function to calculate MACD
           typical values a = 12; b =26, c =9"""
        df = DF.copy()
        df["EMA_volume"]=df["volume"].ewm(span=day,min_periods=day).mean()
        df["EMA21_volume"]=df["volume"].ewm(span=21,min_periods=21).mean()
        # df.dropna(inplace=True)
        return df

def get_ATR(DF,day):
    df = DF.copy()
    temp = df["high"]-df["low"]
    df["Range"] = [abs(i) for i in temp]
    df["ATR"] = df["Range"].ewm(span=day,min_periods=day).mean()    
    # df.dropna(inplace=True)
    return df

def candle_color(df):
    x = df["open"]-df["close"]
    z=[]
    for y in x:
        if y<0:
            z.append("Green")
        else:
            z.append("Red")
    df["Candle"] = z
    return df


def MACD(DF,a,b,c):
        """function to calculate MACD
           typical values a = 12; b =26, c =9"""
        df = DF.copy()
        df["MA_Fast"]=df["Prev close"].ewm(span=a,min_periods=a).mean()
        df["MA_Slow"]=df["Prev close"].ewm(span=b,min_periods=b).mean()
        df["MACD"]=df["MA_Fast"]-df["MA_Slow"]
        df["Signal"]=df["MACD"].ewm(span=c,min_periods=c).mean()
        df["Histo"] = df["MACD"] - df["Signal"]
        df.dropna(inplace=True)
        return df

def RSI(DF,n):
    "function to calculate RSI"
    df = DF.copy()
    df['delta']=df['close'] - df['close'].shift(1)
    df['gain']=np.where(df['delta']>=0,df['delta'],0)
    df['loss']=np.where(df['delta']<0,abs(df['delta']),0)
    avg_gain = []
    avg_loss = []
    gain = df['gain'].tolist()
    loss = df['loss'].tolist()
    for i in range(len(df)):
        if i < n:
            avg_gain.append(np.NaN)
            avg_loss.append(np.NaN)
        elif i == n:
            avg_gain.append(df['gain'].rolling(n).mean().tolist()[n])
            avg_loss.append(df['loss'].rolling(n).mean().tolist()[n])
        elif i > n:
            avg_gain.append(((n-1)*avg_gain[i-1] + gain[i])/n)
            avg_loss.append(((n-1)*avg_loss[i-1] + loss[i])/n)
    df['avg_gain']=np.array(avg_gain)
    df['avg_loss']=np.array(avg_loss)
    df['RS'] = df['avg_gain']/df['avg_loss']
    df['RSI'] = 100 - (100/(1+df['RS']))
    return df['RSI']

def ATR(DF,n):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L']=abs(df['high']-df['low'])
    df['H-PC']=abs(df['high']-df['close'].shift(1))
    df['L-PC']=abs(df['low']-df['close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    #df['ATR'] = df['TR'].ewm(span=n,adjust=False,min_periods=n).mean()
    df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
    return df2


def ADX(DF,n):
    "function to calculate ADX"
    df2 = DF.copy()
    df2['TR'] = ATR(df2,n)['TR'] #the period parameter of ATR function does not matter because period does not influence TR calculation
    df2['DMplus']=np.where((df2['high']-df2['high'].shift(1))>(df2['low'].shift(1)-df2['low']),df2['high']-df2['high'].shift(1),0)
    df2['DMplus']=np.where(df2['DMplus']<0,0,df2['DMplus'])
    df2['DMminus']=np.where((df2['low'].shift(1)-df2['low'])>(df2['high']-df2['high'].shift(1)),df2['low'].shift(1)-df2['low'],0)
    df2['DMminus']=np.where(df2['DMminus']<0,0,df2['DMminus'])
    TRn = []
    DMplusN = []
    DMminusN = []
    TR = df2['TR'].tolist()
    DMplus = df2['DMplus'].tolist()
    DMminus = df2['DMminus'].tolist()
    for i in range(len(df2)):
        if i < n:
            TRn.append(np.NaN)
            DMplusN.append(np.NaN)
            DMminusN.append(np.NaN)
        elif i == n:
            TRn.append(df2['TR'].rolling(n).sum().tolist()[n])
            DMplusN.append(df2['DMplus'].rolling(n).sum().tolist()[n])
            DMminusN.append(df2['DMminus'].rolling(n).sum().tolist()[n])
        elif i > n:
            TRn.append(TRn[i-1] - (TRn[i-1]/n) + TR[i])
            DMplusN.append(DMplusN[i-1] - (DMplusN[i-1]/n) + DMplus[i])
            DMminusN.append(DMminusN[i-1] - (DMminusN[i-1]/n) + DMminus[i])
    df2['TRn'] = np.array(TRn)
    df2['DMplusN'] = np.array(DMplusN)
    df2['DMminusN'] = np.array(DMminusN)
    df2['DIplusN']=100*(df2['DMplusN']/df2['TRn'])
    df2['DIminusN']=100*(df2['DMminusN']/df2['TRn'])
    df2['DIdiff']=abs(df2['DIplusN']-df2['DIminusN'])

    # DIdiff_act is the difference between plusDI (green line)
    # and minusDI (red line). 
    # DIdiff_act if positive tells that green is above red
    # and if negative tells green is below red
    df2['DIdiff_act']=df2['DIplusN']-df2['DIminusN']

    df2['DIsum']=df2['DIplusN']+df2['DIminusN']
    df2['DX']=100*(df2['DIdiff']/df2['DIsum'])
    ADX = []
    DX = df2['DX'].tolist()
    for j in range(len(df2)):
        if j < 2*n-1:
            ADX.append(np.NaN)
        elif j == 2*n-1:
            ADX.append(df2['DX'][j-n+1:j+1].mean())
        elif j > 2*n-1:
            ADX.append(((n-1)*ADX[j-1] + DX[j])/n)
    df2['ADX']=np.array(ADX)
    df2.drop(['TRn','DMplusN','DMminusN','DIdiff','DIsum','DX'],axis=1)
    return (df2)



def DMA(DF,n):
    "function to calculate Daily moving average"
    df = DF.copy()
    sma = []
    for i in range(len(df)):
        if i < n:
            sma.append(np.NaN)
        elif i >= n:
            sma.append(df['close'].rolling(n).mean().tolist()[n])
    df['DMA']=np.array(sma)
    return df
