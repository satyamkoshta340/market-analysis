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
cDays = 380
ATR_day = 10 # day before from current date
returnDays = 20
# Reading stock symobl codes from the file saved locally
stk = pd.read_csv( dir_path+ "/nse_stocks.csv")
# stk = pd.read_csv( dir_path+ "/All_stocks.csv")

# Defining list - To append stocks identified
hbull_ret = []
pv_up = []; 
erred = []; up_move = []

# Running loop to check algo match in every stock
# for k in range(0,100):
# day_of_month = 0
# while day_of_month < 31: 
# 	day_of_month += 1
# 	print ('Day of month', day_of_month)
# 	time.sleep(10)
lda = 90
while lda > 19:
	stock_for_tom = []
	lda-=1
	time.sleep(10)
	printOnetime = 1
	for k in range(0,len(stk)):
		# Getting the stock token from the local file here to get the historical data
		instrument_token = stk["itkn"][k]    # DRREDDY 225537
		# Define the time up to which data needs to be fetched (yyyy, MM, DD, HH, MM, SS)
		symb = stk["EQ"][k]
		# if symb != 'ASHAPURMIN':
			# continue
		from_datetime = datetime.datetime.now() - datetime.timedelta(days=cDays+lda)     # From last & days
		to_datetime = datetime.datetime.now()- datetime.timedelta(days=lda)

		# from_datetime = to_datetime - datetime.timedelta(days=cDays)     # From last & days
		# to_datetime = datetime.datetime(2023, 7, 5, 18, 00, 00, 000000)
		interval = "day"
		# interval = "week"
		nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
		dt = pd.DataFrame(nd)
		# print (stk["EQ"][k], dt.head(1))

		if len(dt) < 200:
			# print ("Error fetching data for", stk["EQ"][k])
			# erred.append(stk["EQ"][k])
			continue

		# defining latest candle to get the latest close, open, high etc.	
		# this day stock gave ATR breakout
		lst = len(dt) - ATR_day - returnDays # reduce it to get the latest stocks with the RRG pattern
		# print ("Taking ATR Break day as", dt['date'][lst].date())
		# Not expecting a stock of more than 1000 to move 40% within 15 days, filtering stock with very low price- fishy
		if dt['close'][lst] > 1000 or dt['close'][lst] < 10:
			continue

		if printOnetime == 1:
			print ("Data period",from_datetime.date(), "to",to_datetime.date())
			print ("Total trading sessions found", len(dt))
			printOnetime = 2

		# Creating additional parameters 	
		dt = ema_Vol(dt,14)
		dt = get_ATR(dt,14)
		dt = candle_color(dt)
		dt["EMA20"]=dt["close"].ewm(span=20,min_periods=20).mean()
		dt["EMA50"]=dt["close"].ewm(span=50,min_periods=50).mean()

		# Closing price of the stock should be above 20 and 50 moving average, if it's less skip that
		if dt['close'][lst] < dt["EMA20"][lst] or dt['close'][lst] < dt["EMA50"][lst]:
			continue

		dt["EMA200"]=dt["close"].ewm(span=200,min_periods=200).mean()


		# closing price should be 15% of the moving averages to ensure that much of the move still remains
		if dt['close'][lst] > dt['EMA200'][lst]*1.15 or dt['close'][lst] > dt['EMA50'][lst]*1.20 or dt['close'][lst] > dt['EMA20'][lst]*1.20 :
			continue

		# checking the slope of 200 moving average - I need this slope to be upward
		if dt['EMA200'][lst] - dt['EMA200'][lst-2] < 0:
			continue

		# First check the green candle with high vol
		if dt["close"][lst] > dt["close"][lst-1] + 1.5*dt["ATR"][lst-1]  and dt["volume"][lst] >= 2*dt["EMA21_volume"][lst]:
			ddmmyy = dt['date'][lst].date()
			high_ofATR = dt['high'][lst]
			up_move.append((symb,ddmmyy))
			last_30_day_range = round((max(dt['high'][lst-30:lst]) - min(dt['low'][lst-30:lst]))/min(dt['low'][lst-30:lst])*100,2)
			last_20_day_range = round((max(dt['high'][lst-20:lst]) - min(dt['low'][lst-20:lst]))/min(dt['low'][lst-20:lst])*100,2)
			last_10_day_range = round((max(dt['high'][lst-10:lst]) - min(dt['low'][lst-10:lst]))/min(dt['low'][lst-10:lst])*100,2)
			print ("Upward move detected with high vols",symb,dt['close'][lst], ddmmyy)
			# print (dt['EMA200'][lst], dt['date'][lst-2], dt['EMA200'][lst-2])

			# Appending candle sequence for next 10 trading days
			candleSeq = []
			for x in range(lst,len(dt)):
				candleSeq.append(dt['Candle'][x])
				e = ''
				for j in candleSeq:
					e=e+j
				if 'RedRedGreen' in e:
					# print (dt["date"][x].date(), symb)
					# print ("data available till", dt['date'][len(dt)-1], "candles available", len(dt[x:]))
					try:
						if high_ofATR < dt['high'][x]:
							return_in_a_day = round((dt["close"][x+1] - dt["close"][x])/dt["close"][x]*100,2)
							return_in_two_days = round((dt["close"][x+2] - dt["close"][x])/dt["close"][x]*100,2)
							print ("Entry date",dt['date'][x].date(), symb,dt["close"][x], 'Candle color sequence matched')
							print ('Return in a day:', return_in_a_day,'%', 'Return in two days:', return_in_two_days,'%')
							return_in_ten_days = round((dt["close"][x+10] - dt["close"][x])/dt["close"][x]*100,2)
							print ('Return in ten day:', return_in_ten_days,'%')
							stock_for_tom.append((symb,dt["close"][x],dt["volume"][x],dt["EMA21_volume"][x], dt['date'][x].date(),return_in_a_day,return_in_two_days,ddmmyy,last_30_day_range,last_20_day_range,last_10_day_range,return_in_ten_days))
							break
					except:
						print (symb, "made RRG pattern today", "Keep this on your watchlist", dt['date'][x].date())
					break

		# if symb =='ORCHPHARMA-BE':
		# 	time.sleep(5)
			# break


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
	dk["return_in_ten_days"] = [i[11] for i in stock_for_tom]
	dk["pctRange_30_days"] = [i[8] for i in stock_for_tom]
	dk["pctRange_20_days"] = [i[9] for i in stock_for_tom]
	dk["pctRange_10_days"] = [i[10] for i in stock_for_tom]
	pd.set_option('display.max_columns', None)
	print ("\nStock for tomorrow\n", dk)   
	dk.to_csv('FlagPattern.csv', mode='a', index=False)

