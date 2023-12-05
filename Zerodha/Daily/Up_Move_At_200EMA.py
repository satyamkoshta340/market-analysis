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
# print("Starting", kite.positions())
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
range_break = []
pv_up = []; stock_for_tom = []
erred = []; up_move = []

# Running loop to check algo match in every stock
# for k in range(0,100):
for k in range(0,len(stk)):
	# Getting the stock token from the local file here to get the historical data
	instrument_token = stk["itkn"][k]    # DRREDDY 225537
	# Define the time up to which data needs to be fetched (yyyy, MM, DD, HH, MM, SS)
	symb = stk["EQ"][k]
	# if symb != 'AIROLAM':
	# 	continue
	to_datetime = datetime.datetime(2023, 12, 2, 18, 00, 00, 000000)
	from_datetime = to_datetime - datetime.timedelta(days=cDays)     # From last & days
	interval = "day"
	# interval = "week"
	
	try:
		nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
		dt = pd.DataFrame(nd)
		# print (symb, len(dt))
	except:
		print (symb,"Not able to fetch data") 
		continue

	# print (stk["EQ"][k], dt.tail(5))
	if len(dt) < 200:
		# print ("Error fetching data for", stk["EQ"][k])
		# erred.append(stk["EQ"][k])
		continue
	# defining latest candle to get the latest close, open, high etc.	
	# toggle here if you to check the retrurns for a day
	lst = len(dt)-1
	s_lst = len(dt)-2

	# Not expecting a stock of more than 1000 to move 40% within 15 days, filtering stock with very low price- fishy
	if dt['close'][lst] > 5000 or dt['close'][lst] < 5:
		continue

	# Creating additional parameters 	
	dt = ema_Vol(dt,14)
	dt = get_ATR(dt,14)
	dt = candle_color(dt)
	dt["EMA20"]=dt["close"].ewm(span=20,min_periods=20).mean()
	dt["EMA50"]=dt["close"].ewm(span=50,min_periods=50).mean()

	# Closing price of the stock should be above 20 and 50 moving average, if it's less skip that
	if dt['close'][lst] < dt["EMA20"][lst] or dt['close'][lst] < dt["EMA50"][lst]:
		# print ("Price not above 20 and 50 EMA")
		continue

	# stock should not have a wick of more than 3%
	upper_wick =  dt['high'][lst] - dt['close'][lst]
	closePrice = dt['close'][lst]
	pct_uwck = upper_wick/closePrice*100

	if  pct_uwck > 3:
		# print("Skip", symb, "this stock has high upper wick")
		continue

	# Skipping stocks that are jumping up
	if (dt['open'][lst] - dt['close'][s_lst])/dt['close'][s_lst] > 0.04:
		continue

	dt["EMA200"]=dt["close"].ewm(span=200,min_periods=200).mean()

	# closing price should not be below 200 ma more than 10%
	if dt['close'][lst] < dt['EMA200'][lst] :
		Below_EMA_200_Flag=1
	else:
		Below_EMA_200_Flag=0

	high_in_past_60D = max(dt['high'][lst-60:lst])
	pctAway_from_high = round((dt["close"][lst]- high_in_past_60D)/dt["close"][lst]*100,2)
	last_22_day_range = round((max(dt['high'][lst-22:s_lst]) - min(dt['low'][lst-22:s_lst]))/min(dt['low'][lst-22:s_lst])*100,2)
	# First check the green candle with high vol
	# print ("Close",dt["close"][lst], "Prev close",dt["close"][lst-1], "ATR", dt["ATR"][lst-1],"Vol",dt["volume"][lst]/10000,"21 EMA Vol",int(dt["EMA_volume"][lst]/10000))
	if dt["close"][lst] > dt["close"][lst-1] + 1.5*dt["ATR"][lst-1]  and dt["volume"][lst] >= 2*dt["EMA_volume"][lst]:
		ddmmyy = dt['date'][lst]
		up_move.append((symb,ddmmyy))
		vol_ratio = round(dt["volume"][lst]/dt["EMA_volume"][lst],1)
		# print (dt['EMA200'][lst], dt['date'][lst-2], dt['EMA200'][lst-2])
		if last_22_day_range < 20:
			stock_for_tom.append((symb,dt["close"][lst],vol_ratio,last_22_day_range,pctAway_from_high,Below_EMA_200_Flag))
			print (last_22_day_range,"===== Range break with high vols {}".format(vol_ratio),symb,dt["close"][lst], ddmmyy.date(),"pctAway_from_high",pctAway_from_high)
		else:
			print ("Upward move detected with high vols {}".format(vol_ratio),symb,dt["close"][lst], ddmmyy.date(),"pctAway_from_high",pctAway_from_high)
			stock_for_tom.append((symb,dt["close"][lst],vol_ratio,last_22_day_range,pctAway_from_high,Below_EMA_200_Flag))

# pd.set_option('display.max_columns', None)
if len(stock_for_tom)==0:
	print ("/n Better luck next time!")
else:
	dk= pd.DataFrame()
	dk["Stock"] = [i[0] for i in stock_for_tom]
	dk["Volume_ratio"] = [i[2] for i in stock_for_tom]
	dk["Closing_Price"] = [i[1] for i in stock_for_tom]
	dk["Last_22_day_range"] = [i[3] for i in stock_for_tom]
	dk["pctAway_from_high"] = [i[4] for i in stock_for_tom]
	dk["Below_EMA_200_Flag"] = [i[5] for i in stock_for_tom]
	print ("/nStock for tomorrow/n", dk.sort_values(by=["Last_22_day_range"]))   
	dk.to_csv("E:/Abhishek_Koshta/Personal/Investment/Back Testing/market-analysis/Zerodha/Dont_Upload/{}_ATR_BREAK_STOCKS.csv".format(ddmmyy.date()))

