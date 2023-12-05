from kite_trade import *
import pandas as pd
import time
# Run this file on every market trading day at 10:45:10 to get the orders placed
import os
from dotenv import load_dotenv
load_dotenv()


enctoken = os.environ.get("ENC_TOKEN")
kite = KiteApp(enctoken=enctoken)
print("Logged in")


# Get Historical Data
import datetime
noc = 3 # number of inside candles to be checked
instrument_token = 260105    # NIFTY BANK
instrument_token = 256265 
dy = 820 
signal_dates = []
tradingSessions = 0
while dy > 1:
	dy = dy-1
	from_datetime = datetime.datetime(2023, 4, 14, 9, 00, 00, 000000) - datetime.timedelta(days=dy)     # From last & days
	to_datetime = datetime.datetime(2023, 4, 14, 9, 00, 00, 000000) - datetime.timedelta(days=dy-1) 
	# to_datetime = datetime.datetime.now()
	# from_datetime = datetime.datetime(2023, 4, 13, 9, 00, 00, 000000)
	# to_datetime = datetime.datetime(2023, 4, 13, 15, 00, 00, 000000)
	interval = "hour"
	try:
# 		print ("Starting on", from_datetime)
		nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
		# print(kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False))
		dt = pd.DataFrame(nd)
		# print (dt)
		if len(dt)<6:
			continue
	except:
# 		print ("No data found", from_datetime)
		continue

	# Finding the inside candle pattern in today's stocks
	i=0
	tradingSessions = tradingSessions + 1
	start_time_hh = str(dt["date"][i]).split()[1][:2]
	start_time_mm = str(dt["date"][i]).split()[1][3:5]
	if start_time_hh == '09' and start_time_mm == '15':
		first_15m_high = dt["high"][i]
		first_15m_low = dt["low"][i]
		first_candle_size = first_15m_high - first_15m_low
		pct_candle = round(100*first_candle_size/first_15m_high,2)
		rsfr = first_candle_size*.62  			# Fibonacci retracement value for filtering proper stocks

		if first_15m_high > max(dt["high"][i+1:i+noc]) and first_15m_low < min(dt["low"][i+1:i+noc]):
			print ("Formed inside candle", dt["date"][i])
			signal_dates.append(dt["date"][i].date())

			if min(dt["low"][i+1:i+noc]) >= (first_15m_high - rsfr):
				print ("Condition satisfied to place buy order",  dt["close"][i+noc], dt["volume"][i+noc],dt["date"][i+noc])
				
			if max(dt["high"][i+1:i+noc]) <= (first_15m_low + rsfr):
				print ("Condition satisfied to place sell order",  dt["close"][i+noc], dt["volume"][i+noc],dt["date"][i+noc])
				
print (signal_dates)
print (len(signal_dates), "signals found in",tradingSessions,"trading sessions")

# Trade analysis

tad = pd.DataFrame()
tad["SignalDates"] = signal_dates
prevSig = [signal_dates[i]-signal_dates[i-1] for i in range(0,len(signal_dates))]
tad["PrevSignal"] = prevSig

print (tad)
