
# importing important libraries
from kite_trade import *
import pandas as pd
import time
import os
from dotenv import load_dotenv
load_dotenv()

# Putting enc_token to use the existing session for login
enctoken = os.environ.get("ENC_TOKEN")
kite = KiteApp(enctoken=enctoken)
print("Logged in")


# Get Historical Data
import datetime
# Will test on only bank nifty index
instrument_token = 260105    # NIFTY BANK
# instrument_token = 256265 

# Defining lists to get the data stored for back testing results

test_duration = 10
while test_duration > 2:
	time.sleep(2)
	test_duration-=1

	# Specifying the data period
	from_datetime = datetime.datetime.now() - datetime.timedelta(days=test_duration)     # From last & days
	to_datetime = datetime.datetime.now()- datetime.timedelta(days=1)

	# from_datetime = datetime.datetime(2023, 7, 7, 9, 00, 00, 000000)
	# to_datetime = datetime.datetime(2023, 7, 7, 16, 00, 00, 000000)

	interval = "5minute"

	nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
	# print(kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False))
	dt = pd.DataFrame(nd)
	# print (dt)

	try:
		first_5min_high = dt['high'][0]
		first_5min_low = dt['low'][0]
	except:
		continue
	ptMove = 150
	maxptMove = 300
	printOne = 0
	trend = 0
	entry = 0
	exit = 0
	down_trend = 0; up_trend = 0
	d_entry = 0; d_exit = 0
	u_entry = 0; u_exit = 0

	if printOne == 0:
		print ("=====================Trading date", dt['date'][0].date(), '====================')
		printOne=1

	for i in range(3,len(dt)):
		# check first movement of at least 166 points in one direction
		day_low = min(dt['low'][2:i])
		day_high = max(dt['high'][:i])

		down_side_move = day_high - dt['low'][i]
		up_side_move = dt['high'][i] - day_low 

		if down_side_move > ptMove and down_side_move <maxptMove and trend==0:
			print ("Down side trend established", dt['date'][i])
			low_made = dt['low'][i]
			down_trend = 1; trend =1

		if up_side_move > ptMove and up_side_move<maxptMove and trend==0:
			print ("Up side trend established", dt['date'][i])
			high_made = dt['high'][i]
			up_trend = 1; trend =1

	# check for small retracement to enter the trade

		if down_trend == 1 and d_entry!=1:
			marked_low = min(low_made,dt['low'][i])
			entry = marked_low + 100
			if dt['high'][i+1] > entry:
				print ("Take bearish entry at", dt['date'][i], entry)
				d_entry = 1

		if up_trend == 1 and u_entry!=1:
			marked_high = max(high_made,dt['high'][i])
			entry = marked_high - 100
			if dt['low'][i+1] < entry:
				print ("Take bullish entry at", dt['date'][i], entry)
				u_entry = 1


	# Entry done now, it's time for SL/Target
		if d_entry == 1 and d_exit!=1:
			sl = entry + 40
			tg = entry - 120

			if dt['high'][i] > sl:
				print ("SL Hit", dt['date'][i])
				d_exit = 1
			if dt['low'][i] < tg:
				print ("Target Hit", dt['date'][i], tg)
				d_exit = 1; exit= 1

		if u_entry == 1 and u_exit!=1:
			sl = entry - 40
			tg = entry + 120
			if dt['low'][i] < sl:
				print ("SL Hit", dt['date'][i])
				u_exit = 1; exit = 1
			if dt['high'][i] > tg:
				print ("Target Hit", dt['date'][i], tg)
				u_exit = 1; exit= 1

		if exit==1:
			print ("Closing the day", dt['date'][i])
			break

