# /* Press ctrl + fn + Insert to cancel *///

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
# print("Positions", kite.positions())
# print("Starting", kite.margins(), "\nloggid in")

# Capital to be deployed per stock

# Getting path of the current directory, this helps when collaborating on git
dir_path = os.path.dirname(os.path.realpath(__file__))
print (dir_path)

# Code running time 
current_datetime = datetime.datetime.now()

print ("Code executed at:", current_datetime)

# By default use current day's data 
use_current_date = 'Yes'

if use_current_date == 'Yes':
	yr = current_datetime.year
	mon = current_datetime.month
	doM = current_datetime.day
	print ("Running for {}-{}-{} date\n".format(yr,mon,doM))
else:
	yr = 2024
	mon = 4
	doM = 16
	print ("Running for {}-{}-{} date\n".format(yr,mon,doM))

# This is the number for which historical data of a stock will be fetched
cDays = 140
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
print ("Starting loop")
while ATR_day > 1:
	ATR_day-=1
	printOnetime = 1
	for k in range(0,len(stk)):
	# for k in range(1217,1218):
		# Getting the stock token from the local file here to get the historical data
		instrument_token = stk["itkn"][k]    # DRREDDY 225537
		# Define the time up to which data needs to be fetched (yyyy, MM, DD, HH, MM, SS)
		symb = stk["EQ"][k]
		# if symb == 'IRB':
		# 	print ("Last closing price", )
		# 	continue
		# else:
		# 	print(k)

		to_datetime = datetime.datetime(yr, mon, doM, 20, 00, 00, 000000)
		from_datetime = to_datetime - datetime.timedelta(days=cDays)     # From last & days
		interval = "day"

		try:
			nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
			dt = pd.DataFrame(nd)
			# print (symb, len(dt), dt)
		except:
			# print (symb,"Not able to fetch data") 
			continue
		# print (stk["EQ"][k], dt.head(1))
		if symb == 'IRB':
			print ("Last closing price", dt['close'][len(dt)-1])

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
		# if dt['close'][lst] > dt['EMA50'][lst]*1.15 or dt['close'][lst] > dt['EMA50'][lst]*1.20 or dt['close'][lst] > dt['EMA20'][lst]*1.20 :
		# 	print ('Skipping! Closing price more than 15% from ltp')
		# 	continue

		# checking the slope of 200 moving average - I need this slope to be upward
		if dt['EMA50'][lst] - dt['EMA50'][lst-2] < 0:
			continue

		high_in_past_60D = max(dt['high'][lst-60:lst])
		pctAway_from_high = round((dt["close"][lst]- high_in_past_60D)/dt["close"][lst]*100,2)


		# print ('LTP', dt["close"][lst], 'Prev LTP', dt["close"][lst-1] /
		# 	'1.5 times ATR', 1.5*dt["ATR"][lst-1],  'Last volume', dt["volume"][lst], '2times EMA vol', 2*dt["EMA21_volume"][lst])

		# First check the green candle with high vol
		if dt["close"][lst] > dt["close"][lst-1] + 1.5*dt["ATR"][lst-1]  and dt["volume"][lst] >= 2*dt["EMA21_volume"][lst]:
			# print ("First condition met")
			ddmmyy = dt['date'][lst].date()
			up_move.append((symb,ddmmyy))
			last_30_day_range = round((max(dt['high'][lst-30:lst]) - min(dt['low'][lst-30:lst]))/min(dt['low'][lst-30:lst])*100,2)
			last_20_day_range = round((max(dt['high'][lst-20:lst]) - min(dt['low'][lst-20:lst]))/min(dt['low'][lst-20:lst])*100,2)
			last_10_day_range = round((max(dt['high'][lst-10:lst]) - min(dt['low'][lst-10:lst]))/min(dt['low'][lst-10:lst])*100,2)
			# print ("Upward move detected with high vols",symb,ddmmyy, dt["close"][lst])
			low_of_ATR_Break = dt["low"][lst]
			# print (dt['EMA200'][lst], dt['date'][lst-2], dt['EMA200'][lst-2])

			
			# Appending candle sequence for next 10 trading days
			candleSeq = []
			for x in range(lst,len(dt)):
				candleSeq.append(dt['Candle'][x])
				e = ''
				for j in candleSeq:
					e=e+j
				if 'RedRedGreen' in e:
					# if dt["date"][x].date() == '2023-07-04':
					# print (dt["date"][x].date(), symb)

					ltp = dt["close"][x]
					vol, ema21_vol = int(dt["volume"][x]), int(dt["EMA21_volume"][x])
					trade_date = dt['date'][x].date()
				# check if any of the red candle broke the low of ATR break out candle
					if dt["low"][x] < low_of_ATR_Break or dt["low"][x-1] < low_of_ATR_Break :
						pass
						# print ('AVOID ---',symb, "One of the red candle broke low of initial breakout Green! ")
					else:
						try:
							return_in_a_day = round((dt["close"][x+1] - dt["close"][x])/dt["close"][x]*100,2)
							return_in_two_days = round((dt["close"][x+2] - dt["close"][x])/dt["close"][x]*100,2)
							print (dt['date'][x].date(), symb,dt["close"][x], 'Candle color sequence matched')
							print ('Return in a day:', return_in_a_day,'%', 'Return in two days:', return_in_two_days,'%')
							stock_for_tom.append((symb,ltp, vol, ema21_vol, trade_date,return_in_a_day,return_in_two_days,ddmmyy,last_30_day_range,last_20_day_range,last_10_day_range))
							break
						except:
							check_these.append((symb,ltp, dt['date'][x].date()))
							print (symb, "===== made RRG pattern today", dt['date'][x].date(), ",pctAway_from_high", pctAway_from_high, ', -high in p60', high_in_past_60D)
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

