# Fetching important libraries
from kite_trade import *
import pandas as pd
import time
import os
from Bourses import *
import datetime
from dotenv import load_dotenv
load_dotenv()

# Providing enc_token to login to zerodha portal
enctoken = os.environ.get("ENC_TOKEN")
kite = KiteApp(enctoken=enctoken)
print("Starting", kite.positions())
# Capital to be deployed per stock

# Getting path of the current directory, this helps when collaborating on git
dir_path = os.path.dirname(os.path.realpath(__file__))
print (dir_path)

# This is the number for which historical data of a stock will be fetched
cDays = 330
# Reading stock symobl codes from the file saved locally
stk = pd.read_csv( dir_path+ "/nse_stocks.csv")
# stk = pd.read_csv( dir_path+ "/All_stocks.csv")

# Defining list - To append stocks identified
hbull_ret = []
pv_up = []; stock_for_tom = []
erred = []; up_move = []

# Running loop to check algo match in every stock
# for k in range(0,100):
for k in range(0,len(stk)):
	# Getting the stock token from the local file here to get the historical data
	instrument_token = stk["itkn"][k]    # DRREDDY 225537
	# Define the time up to which data needs to be fetched (yyyy, MM, DD, HH, MM, SS)
	to_datetime = datetime.datetime(2023, 6,20, 18, 00, 00, 000000)
	from_datetime = to_datetime - datetime.timedelta(days=cDays)     # From last & days
	interval = "day"
	# interval = "week"
	nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
	dt = pd.DataFrame(nd)
	symb = stk["EQ"][k]
	# print (stk["EQ"][k], dt.head(1))
	if len(dt) < 200:
		print ("Error fetching data for", stk["EQ"][k])
		erred.append(stk["EQ"][k])
		continue

	# defining latest candle to get the latest close, open, high etc.	
	lst = len(dt)-1

	# Creating additional parameters 	
	dt = ema_Vol(dt,14)
	dt = get_ATR(dt,14)
	dt = candle_color(dt)
	dt["EMA20"]=dt["close"].ewm(span=20,min_periods=20).mean()
	dt["EMA50"]=dt["close"].ewm(span=50,min_periods=50).mean()
	dt["EMA200"]=dt["close"].ewm(span=200,min_periods=200).mean()

	# Closing price of the stock should be above 20 and 50 moving average, if it's less skip that
	if dt['close'][lst] < dt["EMA20"][lst] or dt['close'][lst] < dt["EMA50"][lst]:
		continue

	# closing price should be 15% of the moving averages to ensure that much of the move still remains
	if dt['close'][lst] > dt['EMA200'][lst]*1.1 or dt['close'][lst] > dt['EMA50'][lst]*1.20 or dt['close'][lst] > dt['EMA20'][lst]*1.20 :
		continue

	# checking the slope of 200 moving average - I need this slope to be upward
	if dt['EMA200'][lst] - dt['EMA200'][lst-5] < 0:
		continue

	# Not expecting a stock of more than 1000 to move 40% within 15 days, filtering stock with very low price- fishy
	if dt['close'][lst] > 1000 or dt['close'][lst] < 10:
		continue

	#print (dt[len(dt)-5:])
	for i in range(len(dt)-5,len(dt)):
		ddmmyy2 = dt['date'][len(dt)-2]
	# First check the green candle with high vol
		if dt["close"][i-2] > dt["close"][i-3] + 1*dt["ATR"][i-3]  and dt["volume"][i-2] >= 3*dt["EMA21_volume"][i-3]:
			ddmmyy = dt['date'][len(dt)-3]
			up_move.append((symb,ddmmyy))
			print ("Upward move detected with high vols",symb,ddmmyy)
		# Check next day if the stock is going down with low volume
		# if dt["Candle"][i-1] == "Red" and dt["volume"][i-1] <= dt["volume"][i-2] and dt["close"][i-1] < dt["close"][i-2]:
			if dt["volume"][i-1] <= dt["volume"][i-2] and dt["close"][i-1] < dt["close"][i-2]:
				print ("First day", symb,dt["close"][i],dt["volume"][i],dt["EMA21_volume"][i])

			# if dt["close"][i+1] > dt["close"][i]-dt["Range"][i-1]*0.38:
			if dt["close"][i] > dt["close"][i-1]-dt["Range"][i-2]*0.38 and dt["volume"][i] <= dt["EMA21_volume"][i-1]:
			# if dt["ADX"][i] < dt["DIplusN"][i]:
				ddmmyy2 = dt['date'][len(dt)-2]
				if dt["EMA21_volume"][i]> 100000:
					print (symb,"stock moving with low volumes after upward move",ddmmyy2)
					pv_up.append((symb,ddmmyy2))
					td = dt['date'][len(dt)-2]
					if ddmmyy2==td:
						print ("=========================================")
						print ("Yohooo!, You have found it", symb)
						print ("=========================================")
				stock_for_tom.append((symb,dt["close"][i],dt["volume"][i],dt["EMA21_volume"][i], dt['EMA20']))
	if symb =='AIRAN':
		break


if len(stock_for_tom)==0:
	print ("\n Better luck next time!")
else:
	dk= pd.DataFrame()
	dk["Stock"] = [i[0] for i in stock_for_tom]
	dk["Closing Price"] = [i[1] for i in stock_for_tom]
	dk["volume"] = [i[2] for i in stock_for_tom]
	dk["21_EMA_Vol"] = [i[3] for i in stock_for_tom]
	print ("\nStock for tomorrow\n", dk)   



