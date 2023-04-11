from kite_trade import *
import pandas as pd
import time
import os
from Bourses import *
from dotenv import load_dotenv
load_dotenv()

enctoken = os.environ.get("ENC_TOKEN")
kite = KiteApp(enctoken=enctoken)
# print("Starting", kite.positions())
# Capital to be deployed per stock

# Get Historical Data
import datetime
dir_path = os.path.dirname(os.path.realpath(__file__))
stk = pd.read_csv( dir_path+ "/nse_stocks.csv")
scanned = []
filtered_scan1 = []; filtered_scan2 = []
erred = []
ptf = 0   # pattern found in #stocks

# Lopping through the list of FNO stocks (having high volumes)
# for k in range(0,100):
for k in range(0,len(stk)):
	# if stk["itkn"][k] != 225537: continue
	# getting historical data
	instrument_token = stk["itkn"][k]    # DRREDDY 225537
	# from_datetime = datetime.datetime.now() - datetime.timedelta(days=30)     # From last & days
	# to_datetime = datetime.datetime.now()

	to_datetime = datetime.datetime(2023, 4, 10, 18, 00, 00, 000000)
	from_datetime = to_datetime - datetime.timedelta(days=60)     # From last & days

	interval = "day"
	nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
	dt = pd.DataFrame(nd)
	# print (stk["EQ"][k], dt.head(1))
	if len(dt) <2:
		print ("Error fetching data for", stk["EQ"][k])
		erred.append(stk["EQ"][k])
		continue
	if dt["volume"][0] < 100000 or dt["close"][0] < 24:
		continue
	dt = DMA(dt,9)
	dt = ema_Vol(dt,14)
	# print (dt.tail())
	# Finding the inside candle pattern in today's stocks
	# for i in range(0,len(dt["date"])):
	i = len(dt)-2

	#Filtering stocks with low volume
	if dt["volume"][i] < dt["EMA_volume"][i]*1.25:
		continue
	try:
		first_15m_high = dt["high"][i]
		first_15m_low = dt["low"][i]
		first_candle_size = first_15m_high - first_15m_low
		pct_candle = round(100*first_candle_size/first_15m_high,2)
		rsfr = first_candle_size*.62  			# Fibonacci retracement value for filtering proper stocks
		if first_15m_high > max(dt["high"][i+1:i+2]) and first_15m_low < min(dt["low"][i+1:i+2]):
			scanned.append((pct_candle, stk["EQ"][k]))
			# print (first_15m_high,rsfr, first_15m_low, min(dt["low"][i+1:i+2]), first_15m_high- rsfr )

			if min(dt["low"][i+1:i+2]) >= (first_15m_high - rsfr):
				# print ("Scanning", stk["EQ"][k],dt["date"][i], first_15m_high, max(dt["high"][i+1:i+2]) ,first_15m_low,min(dt["low"][i+1:i+2]))
				# print(min(dt["low"][i+1:i+2]), first_15m_high - rsfr)
				# break
				if dt["close"][i] >= dt["DMA"][i]:
					print ("Condition satisfied to place buy order", stk["EQ"][k], dt["close"][i], dt["volume"][i], dt["date"][i+1])
					# if pct_candle <= 1.5:
					filtered_scan1.append((pct_candle, stk["EQ"][k], first_15m_high))
			if max(dt["high"][i+1:i+2]) <= (first_15m_low + rsfr):
				if dt["close"][i] <= dt["DMA"][i]:
					# print ("Scanning", stk["EQ"][k],dt["date"][i], first_15m_high, max(dt["high"][i+1:i+2]) ,first_15m_low,min(dt["low"][i+1:i+2]))
					# print(min(dt["low"][i+1:i+2]), first_15m_high - rsfr)
					# print ("Condition satisfied to place sell order", stk["EQ"][k], dt["close"][i], dt["volume"][i],dt["date"][i+1])
					# print (dt.tail(2))
					# if pct_candle <= 1.5:
					filtered_scan2.append((pct_candle, stk["EQ"][k], first_15m_low))
	except:
		continue
 
er = pd.DataFrame()
er["rstk"] = erred
er.to_csv("remove_stks.csv")
filtered_scan1 = sorted(filtered_scan1)
filtered_scan2 = sorted(filtered_scan2)

print ("Total stocks found", len(scanned), sorted(scanned))
print ("\nStocks for Sell",len(filtered_scan2), filtered_scan2)
print ("\nStocks to Buy",len(filtered_scan1), filtered_scan1)
print (dt["date"][i+1])

