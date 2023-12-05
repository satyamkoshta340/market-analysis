## =================================================================================================================== ##
# 									getting stocks with 30% return within 10 days
## =================================================================================================================== ##
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
print (dir_path)
# check movement within days
cDays = 10
stk = pd.read_csv( dir_path+ "/nse_stocks.csv")

# stk = pd.read_csv( dir_path+ "/All_stocks.csv")
scanned = []
filtered_scan1 = []; filtered_scan2 = []
# Lopping through the list of FNO stocks (having high volumes)
# for k in range(0,100):
for k in range(0,len(stk)):
	# getting historical data
	instrument_token = stk["itkn"][k]    # DRREDDY 225537

	to_datetime = datetime.datetime(2023, 11, 30, 18, 00, 00, 000000)
	from_datetime = to_datetime - datetime.timedelta(days=cDays)     # From last & days

	interval = "day"
	try:
		nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
		dt = pd.DataFrame(nd)
	except:
		continue

	if len(dt) <2:
		# print ("Error fetching data for", stk["EQ"][k])
		continue
	if dt["volume"][0] < 10000:
		continue
	if dt["close"][0] < 5:
		continue
	try:
		# lowestPrice = min(dt['close'][len(dt)-cDays:])
		lowestPrice = min(dt['close'])
		lastClose = dt['close'][len(dt)-1]
		pctChange = round((lastClose - lowestPrice)/lowestPrice*100,2)
		# print (lowestPrice,i,dt['close'][-1], pctChange)
		# if pctChange > .1 and pctChange < .2:

		if pctChange > 40:
			filtered_scan1.append((pctChange, stk["EQ"][k], lowestPrice, lastClose))
			print (stk["EQ"][k], "lastClose:", lastClose, "pctChange:", pctChange, dt['date'][len(dt)-1].date())
	except:
		continue
 
filtered_scan1 = sorted(filtered_scan1)
print ("\nStocks to Buy",len(filtered_scan1), filtered_scan1)

print ("Starting date", dt['date'][0], len(dt))
