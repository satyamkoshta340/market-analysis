from kite_trade import *
import pandas as pd
import datetime
import numpy as np

# enctoken = "JqoBMCif7iNreXyO3Jk4QeKfgzxfDJxahU4JzWEHeAu6F6+tovurUvTFn0nZ2yYDNAFEzglJtbOVRv8tpvUzP/VEb+t+qj6Ug+3iLSto6TYpIUEEIqDUyw=="
# kite = KiteApp(enctoken=enctoken)
# instrument_token = 256265    # NIFTY 50
# # instrument_token = 260105    # NIFTY BANK
# # time.sleep(78*60)
# cDays = 1365
# to_datetime = datetime.datetime.now() - datetime.timedelta(days=3) ;
# from_datetime = to_datetime - datetime.timedelta(days=cDays) 
# interval = "day"
# print(to_datetime, from_datetime)
# dt = pd.DataFrame(kite.historical_data(instrument_token, from_datetime, to_datetime, interval))
# dt.to_csv("nifty50_daily_data_3yr.csv")
# print( dt.head() )

dt = pd.read_csv("nifty50_daily_data_3yr.csv")

def calculate_rsi(df, param, period=14):
    """
    Calculate the Relative Strength Index (RSI) for a DataFrame of historical price data.

    :param df: Pandas DataFrame with a 'Close' column containing price data.
    :param period: The look-back period for RSI calculation (default is 14).
    :return: A DataFrame with an additional 'RSI' column containing RSI values.
    """
    if param not in df.columns:
        raise ValueError("DataFrame must have a 'Close' column for RSI calculation.")

    changes = df[param].diff()

    gains = changes.where(changes > 0, 0)
    losses = -changes.where(changes < 0, 0)

    avg_gain = gains.rolling(window=period, min_periods=1).mean()
    avg_loss = losses.rolling(window=period, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


period = 4
param = "close"
rsi_vals = calculate_rsi(dt, param, period)
dt["rsi"] = rsi_vals
dt["color"] = [ "green" if dt["open"][i] < dt["close"][i] else "red" for i in range(len(dt))]
print(dt.head())

trades = {  "date":[],
			"buy_price": [],
			"sell_price": [],
			"gain": [],
			"streak": [],
			"buy_open": [],
			"buy_low": [],
			"buy_high": [],
			"sell_open": [],
			"sell_low": [],
			"sell_high": []
		}
i = 1
flag = 0 # looking for signal
buy_price =0
sell_price = 0
gain = 0
gd_points = 100
while( i < len(dt)-1):
	if( flag == 0 and dt["rsi"][i] < 30 ):
		flag = 1
		days = 5
	elif( flag == 1 and days > 0 ):
		if( dt["color"][i] == "green" ):
			print("BUY Signal-----------------------", dt["date"][i])
			trades["date"].append(dt["date"][i])
			buy_price = dt["close"][i]
			trades["buy_price"].append(buy_price)
			trades["buy_low"].append(dt["low"][i])
			trades["buy_high"].append(dt["high"][i])
			trades["buy_open"].append(dt["open"][i])
			i += 1
			trades["sell_low"].append(dt["low"][i])
			trades["sell_high"].append(dt["high"][i])
			trades["sell_open"].append(dt["open"][i])

			
			if( buy_price - trades["sell_open"][-1] > gd_points ):
				sell_price = trades["sell_open"][-1]
			
			else:
				sell_price = dt["close"][i]

			
			trades["sell_price"].append(sell_price)
			gain = sell_price - buy_price

			if( len(trades["streak"]) == 0 ):
				trades["streak"].append(1)
			else:
				if( gain > 0 and trades["gain"][-1] > 0):
					trades["streak"].append(trades["streak"][-1] + 1)
				elif( gain < 0 and trades["gain"][-1] < 0):
					trades["streak"].append(trades["streak"][-1] + 1)
				else:
					trades["streak"].append(1)

			trades["gain"].append(gain)
			flag = 0
		else:
			days -= 1
	elif( flag == 1 and days <=0 ):
		flag = 0
	i+=1

df = pd.DataFrame(trades)
print(df.head())
df.to_csv("4P_RSI_nifty_result_3yr_new.csv")
# print(trades)

