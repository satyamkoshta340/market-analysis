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
cDays = 80
ATR_day = 7 # day before from current date
# Reading stock symobl codes from the file saved locally
stk = pd.read_csv( dir_path+ "/nse_stocks.csv")
# stk = pd.read_csv( dir_path+ "/All_stocks.csv")

# Defining list - To append stocks identified
check_these = []
pv_up = []; stock_for_tom = []
erred = []; up_move = []

# Running loop to check algo match in every stock
# for k in range(0,100):
# day_of_month = 0
# while day_of_month < 31: 
# 	day_of_month += 1
# 	print ('Day of month', day_of_month)
# 	time.sleep(10)
while ATR_day > 1:
	ATR_day-=1
	printOnetime = 1
	for k in range(0,len(stk)):
		# Getting the stock token from the local file here to get the historical data
		instrument_token = stk["itkn"][k]    # DRREDDY 225537
		# Define the time up to which data needs to be fetched (yyyy, MM, DD, HH, MM, SS)
		symb = stk["EQ"][k]
	# 	if symb != 'NAHARINDUS':
	# 		continue
		to_datetime = datetime.datetime(2023, 12, 14, 22, 00, 00, 000000)
		from_datetime = to_datetime - datetime.timedelta(days=cDays)     # From last & days
		interval = "day"
		# interval = "week"	
		try:
			nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
			dt = pd.DataFrame(nd)
		except:
			print (symb,"Not able to fetch data") 
			continue
		# print (stk["EQ"][k], dt.head(1))
		if len(dt) < 80:
			# print ("Error fetching data for", stk["EQ"][k])
			# erred.append(stk["EQ"][k])b
			continue

		# defining latest candle to get the latest close, open, high etc.	
		# this day stock gave ATR breakout
		lst = len(dt) - ATR_day # reduce it to get the latest stocks with the RRG pattern
		# print ("Taking ATR Break day as", dt['date'][lst].date())

		# Not expecting a stock of more than 1000 to move 40% within 15 days, filtering stock with very low price- fishy
		if dt['close'][lst] > 3000 or dt['close'][lst] < 10:
			continue

		# Creating additional parameters 	
		dt = ema_Vol(dt,14)
		dt = get_ATR(dt,14)
		dt = candle_color(dt)
		dt["EMA20"]=dt["close"].ewm(span=20,min_periods=20).mean()
		dt["EMA50"]=dt["close"].ewm(span=50,min_periods=50).mean()

		# Closing price of the stock should be above 20 and 50 moving average, if it's less skip that
		if dt['close'][lst] < dt["EMA20"][lst] or dt['close'][lst] < dt["EMA50"][lst]:
			continue

		# stock should not have a wick of more than 3%
		upper_wick =  dt['high'][lst] - dt['close'][lst]
		closePrice = dt['close'][lst]
		pct_uwck = upper_wick/closePrice*100

		if  pct_uwck > 3:
			# print("Skip", symb, "this stock has high upper wick")
			continue

		# dt["EMA200"]=dt["close"].ewm(span=200,min_periods=200).mean()


		# closing price should be 15% of the moving averages to ensure that much of the move still remains
		if dt['close'][lst] > dt['EMA50'][lst]*1.15 or dt['close'][lst] > dt['EMA50'][lst]*1.20 or dt['close'][lst] > dt['EMA20'][lst]*1.20 :
			continue

		# checking the slope of 200 moving average - I need this slope to be upward
		if dt['EMA50'][lst] - dt['EMA50'][lst-2] < 0:
			continue

		# First check the green candle with high vol
		if dt["close"][lst] > dt["close"][lst-1] + 1.5*dt["ATR"][lst-1]  and dt["volume"][lst] >= 2*dt["EMA21_volume"][lst]:
			ddmmyy = dt['date'][lst].date()
			up_move.append((symb,ddmmyy))
			last_30_day_range = round((max(dt['high'][lst-30:lst]) - min(dt['low'][lst-30:lst]))/min(dt['low'][lst-30:lst])*100,2)
			last_20_day_range = round((max(dt['high'][lst-20:lst]) - min(dt['low'][lst-20:lst]))/min(dt['low'][lst-20:lst])*100,2)
			last_10_day_range = round((max(dt['high'][lst-10:lst]) - min(dt['low'][lst-10:lst]))/min(dt['low'][lst-10:lst])*100,2)
			# print ("Upward move detected with high vols",symb,ddmmyy, dt["close"][lst])
			low_of_ATR_Break = dt["low"][lst]
			# print (dt['EMA50'][lst], dt['date'][lst-2], dt['EMA50'][lst-2])

			
			# Appending candle sequence for next 10 trading days
			candleSeq = []
			for x in range(lst,len(dt)):
				candleSeq.append(dt['Candle'][x])
				e = ''
				for j in candleSeq:
					e=e+j
				if 'RedRed' in e:
					# if dt["date"][x].date() == '2023-07-04':
					# print (dt["date"][x].date(), symb)
					try:
						return_in_a_day = round((dt["close"][x+1] - dt["close"][x])/dt["close"][x]*100,2)
						return_in_two_days = round((dt["close"][x+2] - dt["close"][x])/dt["close"][x]*100,2)
						print (dt['date'][x].date(), symb,dt["close"][x], 'Candle color sequence matched')
						print ('Return in a day:', return_in_a_day,'%', 'Return in two days:', return_in_two_days,'%')
						stock_for_tom.append((symb,dt["close"][x],dt["volume"][x],dt["EMA21_volume"][x], dt['date'][x].date(),return_in_a_day,return_in_two_days,ddmmyy,last_30_day_range,last_20_day_range,last_10_day_range))
						break
					except:
						check_these.append((symb,dt["close"][x],dt["volume"][x],dt["EMA21_volume"][x], dt['date'][x].date()))
						print (symb, "===== made RRG pattern today", "Keep this on your watchlist", dt['date'][x].date())
						# check if any of the red candle broke the low of ATR break out candle
						if dt["low"][x] < low_of_ATR_Break or dt["low"][x-1] < low_of_ATR_Break :
							print ('AVOID ---',symb, "One of the red candle broke low of initial breakout Green! ")
					break

		# if symb =='ORCHPHARMA-BE':
		# 	time.sleep(5)
		# 	break
print (check_these)

if len(stock_for_tom)==0:
	print ("\n Better luck next time!")
else:
	dk= pd.DataFrame()
	dk["ATR_Break_Date"] = [i[7] for i in stock_for_tom]
	dk["SignalDate"] = [i[4] for i in stock_for_tom]
	dk["Stock"] = [i[0] for i in stock_for_tom]
	dk["Closing Price"] = [i[1] for i in stock_for_tom]
	dk["volume"] = [i[2] for i in stock_for_tom]
	dk["21_EMA_Vol"] = [i[3] for i in stock_for_tom]
	dk["return_in_a_day"] = [i[5] for i in stock_for_tom]
	dk["return_in_two_days"] = [i[6] for i in stock_for_tom]
	dk["pctRange_30_days"] = [i[8] for i in stock_for_tom]
	dk["pctRange_20_days"] = [i[9] for i in stock_for_tom]
	dk["pctRange_10_days"] = [i[10] for i in stock_for_tom]
	pd.set_option('display.max_columns', None)
	print ("\nStock for tomorrow\n", dk)   
	dk.to_csv('FlagPattern.csv', mode='a', index=False)

