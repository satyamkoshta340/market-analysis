# Strategy - 15 min intraday inside candle formation
# Details 
# 1. 3 candles formed inside 9:15 to 9:30 candle
# 2. Candle that breaks the high or low of the first candle triggers entry
# 3. P/L ratio is 1.5/1

# Run this file on every market trading day at 10:45:10 to get the orders placed

# importing important library
from kite_trade import *
import pandas as pd
import time
import os
import datetime

# Added ENC token in dotenv file 
from dotenv import load_dotenv
load_dotenv()

# Reading token to use the already logged in session
enctoken = os.environ.get("ENC_TOKEN")
kite = KiteApp(enctoken=enctoken)
sleepTime = 12
print("Starting", kite.margins(), "loggid in")
print ("Logged in... sleeping for {} mins...".format(sleepTime), datetime.datetime.now())
# time.sleep(sleepTime*60)

doM = 19  		# Day of month 
mon = 2 		# Month
yr  = 2024		# Year 

# number of candles to look inside the first candle 
numOfCandles = 5 # number of inside candles to be checked

# Fibonacci retracement value for filtering proper stocks
febRet = .62

patternFound = 0   # pattern found in #stocks

# Capital to be deployed per stock
iniCap = 2000   # placing order for 5 stocks
tgPct = .01     # profit targeted in a trade


# getting the order object
ods_v1 = pd.DataFrame(kite.orders()) 	
print ("Order placed so far", ods_v1, len(ods_v1))
# pos_v1 = pd.DataFrame(kite.positions()) # getting the position object from Kite

# Get Historical Data
dir_path = os.path.dirname(os.path.realpath(__file__))
stk = pd.read_csv( dir_path+ "/itkn.csv")

# Creating a list of stocks that satisfies the pattern criterion
scanned = []

# Stocks to buy
filtered_scan1 = []; 

# Stocks to sell
filtered_scan2 = []

# Lopping through the list of FNO stocks (having high volumes)
for k in range(0,len(stk)):
	# if stk["itkn"][k] != 225537: continue

	# getting historical data
	instrument_token = stk["itkn"][k]    # DRREDDY 225537
	from_datetime = datetime.datetime(yr, mon, doM, 9, 00, 00, 000000)
	to_datetime = datetime.datetime(yr, mon, doM, 11, 00, 00, 000000)
	interval = "15minute"

	try:
		nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
		# print(kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False))
		dt = pd.DataFrame(nd)
	except:
		print ("Data not available for", stk["EQ"][k])
		continue

	if len(dt) < numOfCandles:
		print ("Error fetching data for", stk["EQ"][k], len(dt), 'candles available')
		continue


	# Finding the inside candle pattern in today's stocks
	for i in range(0,len(dt["date"])):
		start_time_hh = str(dt["date"][i]).split()[1][:2]
		start_time_mm = str(dt["date"][i]).split()[1][3:5]

		if start_time_hh == '09' and start_time_mm == '15':
			# Filtering stocks within speicific price band
			if dt["high"][i] <50 or dt["high"][i] > 7999:
				continue
			else:
				first_15m_high = dt["high"][i]
				first_15m_low = dt["low"][i]
				first_15m_close = dt["close"][i]
				sec_15m_high = max(dt["high"][i+1:len(dt)])
				sec_15m_low = min(dt["low"][i+1:len(dt)])

				first_candle_size = first_15m_high - first_15m_low
				pct_candle = round(100*first_candle_size/first_15m_high,2)
				rsfr = first_candle_size*febRet
		        # print ("Scanning", stk["EQ"][k],dt["date"][i] )
				if first_15m_high > max(dt["high"][i+1:i+numOfCandles]) and first_15m_low < min(dt["low"][i+1:i+numOfCandles]):
					patternFound += 1
					# print (stk["EQ"][k], "formed pattern with candle size of", first_candle_size, "percentage.")
					# print (dt.loc[i:i+numOfCandles])
					scanned.append((pct_candle, stk["EQ"][k]))
					# print (first_15m_high,rsfr, first_15m_low, min(dt["low"][i+1:i+numOfCandles]), first_15m_high- rsfr )
					buyfib = round((first_15m_high - min(dt["low"][i+1:i+numOfCandles])) / first_candle_size,2)
					sellfib = round((max(dt["high"][i+1:i+numOfCandles]) - first_15m_low) / first_candle_size,2)
					if min(dt["low"][i+1:i+numOfCandles]) >= (first_15m_high - rsfr):
						# checking the close should also be within top 40% of the high price
						if first_15m_close > first_15m_low + 0.6*first_candle_size:
							# print ("Condition satisfied to place buy order", stk["EQ"][k], dt["close"][i+numOfCandles], buyfib)
							slBuy = round(max(sec_15m_low,first_15m_high-first_15m_high*.005),1)
							if pct_candle <= 3.5:
								print (stk["EQ"][k], "Entry at", first_15m_high, "SL", slBuy)
								tg = round(first_15m_high+first_15m_high*0.007,1)
								filtered_scan1.append((pct_candle, stk["EQ"][k], first_15m_high, slBuy,buyfib,tg,"Buy"))
					if max(dt["high"][i+1:i+numOfCandles]) <= (first_15m_low + rsfr):
						if first_15m_close < first_15m_high - 0.6*first_candle_size:	
							# print ("Condition satisfied to place sell order", stk["EQ"][k], dt["close"][i+numOfCandles], sellfib)
							slSell = round(min(sec_15m_high,first_15m_low+first_15m_low*.005),1)
							if pct_candle <= 3.5:
								tg = round(first_15m_low-first_15m_low*0.007,1)
								print (stk["EQ"][k], "Entry at", first_15m_low, "SL", slSell)
								filtered_scan2.append((pct_candle, stk["EQ"][k], first_15m_low, slSell, sellfib,tg, "Sell"))

filtered_scan1 = sorted(filtered_scan1)
filtered_scan2 = sorted(filtered_scan2)
print ("Total stocks found", len(scanned), sorted(scanned))
print ("\nStock for sell   candleSizePct, Stock, Entry, Stoploss, fibPct, target")
print ("\nStocks for Sell",len(filtered_scan2), filtered_scan2)
print ("\nStocks to Buy",len(filtered_scan1), filtered_scan1)

b = [s[1] for s in filtered_scan1[:3]]
s = [s[1] for s in filtered_scan2[:2]]
patternIn = b+s 

finalStocks = filtered_scan1[:2] + filtered_scan2[:3]
orderbook = pd.DataFrame()
today = datetime.datetime.now().date()
orderbook["date"] = [today for s in finalStocks]
orderbook["Order"] = [s[6] for s in finalStocks]
orderbook["Stock"] = [s[1] for s in finalStocks]
orderbook["pctCandle"] = [s[0] for s in finalStocks]
orderbook["fibRetr"] = [s[4] for s in finalStocks]
orderbook["entryPrice"] = [s[2] for s in finalStocks]
orderbook["SL"] = [s[3] for s in finalStocks]
orderbook["Target"] = [s[5] for s in finalStocks]
# orderbook.to_csv("orderbook_{}.csv".format(today))

print (patternIn)

def getEntryExit (symb):
	for stk in filtered_scan1:
		if stk[1] == symb:
			sl = stk[3]
			tg = stk[2] + stk[2]*0.007
	for stk in filtered_scan2:
		if stk[1] == symb:
			sl = stk[3]
			tg = stk[2] - stk[2]*0.007
	sl = round(sl,1)
	tg = round(tg,1)
	return (symb,sl,tg)

def entryBuyOrder (tsb, entry_price, sl, target):
	qty = int(5*iniCap/entry_price)
	exProfit = int((target-entry_price)*qty)
	exLoss = int((sl-entry_price)*qty)
	print ("\nExpected profit {}, loss {}".format(exProfit, exLoss))
	print ("Placing buying order for", tsb, "at", entry_price, "qty", qty, "SL",sl,"Target",target)
	time.sleep(1)
	order = kite.place_order(variety=kite.VARIETY_REGULAR,
			exchange=kite.EXCHANGE_NSE,
			tradingsymbol=tsb,
			transaction_type=kite.TRANSACTION_TYPE_BUY,
			quantity=qty,
			product=kite.PRODUCT_MIS,
			order_type=kite.ORDER_TYPE_SL,
			price=entry_price,
			validity=None,
			disclosed_quantity=None,
			trigger_price=entry_price,
			squareoff=None,
			stoploss=None,
			trailing_stoploss=None,
			tag="TradeViaPython")
	return order

def entrySellOrder (tsb, entry_price, sl, target):
	qty = int(5*iniCap/entry_price)
	exProfit = int((entry_price - target)*qty)
	exLoss = int((entry_price-sl)*qty)
	print ("\nExpected profit {}, loss {}".format(exProfit, exLoss))
	print ("Placing selling order for", tsb, "at", entry_price, "qty", qty, "SL",sl,"Target",target)
	time.sleep(1)
	order = kite.place_order(variety=kite.VARIETY_REGULAR,
			exchange=kite.EXCHANGE_NSE,
			tradingsymbol=tsb,
			transaction_type=kite.TRANSACTION_TYPE_SELL,
			quantity=qty,
			product=kite.PRODUCT_MIS,
			order_type=kite.ORDER_TYPE_SL,
			price=entry_price,
			validity=None,
			disclosed_quantity=None,
			trigger_price=entry_price,
			squareoff=None,
			stoploss=None,
			trailing_stoploss=None,
			tag="TradeViaPython")
	return (order)

actualRun = "Yes"
maxBuy = 0
maxSell = 0
if actualRun == "Yes":
	hrOfDay = int(str(datetime.datetime.now().time())[:2])
	minOfDay = int(str(datetime.datetime.now().time())[3:5])
	# if hrOfDay > 12 :
	# 	break
	for stk_no in range(0,len(filtered_scan1)):
		tsb = filtered_scan1[stk_no][1]
		entry_price = round((filtered_scan1[stk_no][2] + filtered_scan1[stk_no][2]*0.0001),1)
		sl = round(filtered_scan1[stk_no][3] - filtered_scan1[stk_no][2]*0.0005,1)
		target = round((filtered_scan1[stk_no][2] + filtered_scan1[stk_no][2]*tgPct),1)
		ods_v1 = pd.DataFrame(kite.orders()) 	

		try:
			# No orders has been placed yet with below condition true
			if len(ods_v1) < 1: 
				print (tsb,'placing first buying order at', datetime.datetime.now().time())
				maxBuy+=1
				eb = entryBuyOrder (tsb, entry_price, sl, target)

			checkOrder = len(ods_v1[(ods_v1["tradingsymbol"]==tsb) & (ods_v1["price"]==entry_price) & (ods_v1["status"]=="TRIGGER PENDING") & (ods_v1["product"]=="MIS") & (ods_v1["transaction_type"]=="BUY")])
			if checkOrder > 0:
				print ("Buy order already placed for", tsb)
			else:
				print (tsb,'placing buying orders at', datetime.datetime.now().time())
				maxBuy+=1
				if maxBuy <4:
					eb = entryBuyOrder (tsb, entry_price, sl, target)
		except:
			print ("- - - - - - Error placing buy order for", tsb)

	# placing selling orders
	for stk_no in range(0,len(filtered_scan2)):
		ods_v1 = pd.DataFrame(kite.orders()) 	
		try:
			tsb = filtered_scan2[stk_no][1]
			entry_price = round((filtered_scan2[stk_no][2] - filtered_scan2[stk_no][2]*0.0001),1)
			sl = round(filtered_scan2[stk_no][3] + filtered_scan1[stk_no][2]*0.0005,1)
			target = round((filtered_scan2[stk_no][2] - filtered_scan2[stk_no][2]*tgPct),1)
			checkOrder = len(ods_v1[(ods_v1["tradingsymbol"]==tsb) & (ods_v1["price"]==entry_price) & (ods_v1["status"]=="TRIGGER PENDING") & (ods_v1["product"]=="MIS") & (ods_v1["transaction_type"]=="SELL")])
			print (tsb, entry_price, sl, target)
			if checkOrder > 0:
				print ("Sell order already placed for", tsb)
			else:
				maxSell+=1
				if maxSell <3:
					es = entrySellOrder(tsb, entry_price, sl, target)
		except:
			print("- - - - - Error placing sell order", tsb)
	# else:
	# 	print("Trading past 1... should not enter now...")			
else:
	print ("Not placing any orders!")