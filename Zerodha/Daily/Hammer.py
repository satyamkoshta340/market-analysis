## =================================================================================================================== ##
# 									getting stocks hammer pattern
## =================================================================================================================== ##
from kite_trade import *
import pandas as pd
import time
import os
from Bourses import *
from dotenv import load_dotenv
import datetime
load_dotenv()

def findHammers(
		to_datetime = datetime.datetime(2024, 1, 24, 18, 00, 00, 000000),
		cDays = 34 # check movement within days
		):
	enctoken = os.environ.get("ENC_TOKEN")
	kite = KiteApp(enctoken=enctoken)
	# print("Starting", kite.positions())
	# Capital to be deployed per stock

	# Get Historical Data
	
	dir_path = os.path.dirname(os.path.realpath(__file__))
	print (dir_path)
	# check movement within days
	# cDays = 34
	stk = pd.read_csv( dir_path+ "/nse_stocks.csv")  	# All NSE stocks
	# stk = pd.read_csv( dir_path+ "/itkn.csv")			# All FNO stocks
	# stk = pd.read_csv( dir_path+ "/All_stocks.csv")
	scanned = []; best_hammer = []; raw_data = []
	filtered_scan1 = []; filtered_scan2 = []
	# Looping through the list of FNO stocks (having high volumes)
	# for k in range(0,100):
	for k in range(0,len(stk)):
		# getting historical data
		instrument_token = stk["itkn"][k]    # DRREDDY 225537

		# to_datetime = datetime.datetime(2024, 1, 24, 18, 00, 00, 000000)
		from_datetime = to_datetime - datetime.timedelta(days=cDays)     # From last & days

		# if stk["EQ"][k] != 'FIBERWEB' :
		# 	continue

		interval = "day"
		try:
			nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
			dt = pd.DataFrame(nd)
		except:
			print ("Error in fetching API of data ", stk["EQ"][k])
			continue

		if len(dt) <20:
			print ("Error fetching data for", stk["EQ"][k])
			continue
		if dt["volume"][0] < 5000:
			continue
		if dt["close"][0] < 5:
			continue
		lst = len(dt)-1
		simple_hammer = 0
		print(dt.iloc[lst])
		high_in_past_20D = max(dt['high'][lst-60:lst])
		low_in_past_5D = min(dt['low'][lst-8:lst])
		pctAway_from_high_past20D = round((high_in_past_20D - dt["close"][lst])/dt["close"][lst]*100,2)

		# if stk["EQ"][k]=='INFY':
		# 	print (dt)

		try:
			lastClose =  dt['close'][lst]
			upper_wick =  dt['high'][lst] - dt['close'][lst]
			lower_wick =  dt['close'][lst] - dt['low'][lst]
			body_of_candle =  abs(dt['open'][lst] - dt['close'][lst]) +0.001
			body_times_lower_wick = int(lower_wick/body_of_candle)
			pct_away_from_high = round(100*(dt['high'][lst] - dt['close'][lst])/dt['close'][lst],2)

			move_during_day = round(100*(dt['high'][lst] - dt['low'][lst])/dt['low'][lst],2)
			times_lowerWk_grt_thn_upperWk = round(lower_wick/upper_wick,2)

			# simple conditions 
			if lower_wick > 3*body_of_candle and lower_wick > upper_wick:
			# Hammer appeared after at least 10% decay from high in previous 20 trading days
				if pctAway_from_high_past20D >= 10 and low_in_past_5D >=  dt['low'][lst]:
					print ("========================  Hammer after 10% decay from high  ====================")
					print ("%away from past 20 day high", pctAway_from_high_past20D, ', low in past 5 day', low_in_past_5D, ', todays low', dt['low'][lst])
					print ('***',stk["EQ"][k], "lastClose:", lastClose, ', body times wick',body_times_lower_wick,\
						', pct_away_from_high',pct_away_from_high,', move_during_day',move_during_day,\
						', times_lowerWk_grt_thn_upperWk', times_lowerWk_grt_thn_upperWk)
					time.sleep(3)
					best_hammer.append((stk["EQ"][k], dt['close'][lst],body_times_lower_wick, pct_away_from_high,move_during_day))
					raw = stk.iloc[k].tolist() + dt.iloc[lst].tolist()
					raw.append(body_times_lower_wick)
					print("->->->->->->->->->->", raw)
					raw_data.append(raw)
				else:
					simple_hammer+=1


		except:
			continue
	
	sorted_by_body_times_wick = sorted (best_hammer, key = lambda x:x[2])
	raw_data = sorted( raw_data, key = lambda x:x[-1])
	return pd.DataFrame(raw_data, columns=["itkn", "EQ", "date", "open", "high", "low", "close", "volume", "body_times_lower_wick"])


if __name__ == "__main__":
   findHammers()

# Back testing code to be written with following conditions 

# 1. Write back testing for one day first
# 2. Get all the stocks using the above code for entries
# 3. Entry (next day) will be between closing and high of the signal day 
# 4. SL will be low of the hammer candle (signal day)
# 5. Target will be two times of the SL. 
	# For example entry was made at 35 for a stock and hammer's low is 34.5 (SL) then target would be 36 (2x0.5)

# Stats needed 
# Check for SL/Target hit in next 2 days from entry
# 1. Total stocks found -> Number of profitable stocks/losing stocks/no SL/Target hit stocks - overall cumulative return
# 2. Exit after 2 day's at closing price if SL not hit - %profit from such exit strategy
# 3. Now do it for a month



