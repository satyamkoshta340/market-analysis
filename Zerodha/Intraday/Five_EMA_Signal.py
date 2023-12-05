#importing important libraries
# https://www.youtube.com/watch?v=VytCe70yybI
from kite_trade import *
import pandas as pd
import time
# Run this file on every market trading day at 10:45:10 to get the orders placed
import os
import datetime
from dotenv import load_dotenv
load_dotenv()


enctoken = os.environ.get("ENC_TOKEN")
kite = KiteApp(enctoken=enctoken) 

ods_v1 = pd.DataFrame(kite.orders()) 	# getting the order object
# pos_v1 = pd.DataFrame(kite.positions()) # getting the position object from Kite
instrument_token = 260105    # this is for bank nifty
# stk["itkn"][k]    # DRREDDY 225537
c_mins = 18
while c_mins < 60:
	c_mins = c_mins + 1
	print ("Sleeping for 5 min",datetime.datetime.now())
	time.sleep(5*60)
	from_datetime = datetime.datetime(2023, 6, 26, 9, 00, 00, 000000)
	to_datetime = datetime.datetime(2023, 6, 27, 15, 20, 00, 000000)
	interval = "5minute"

	nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
	# print(kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False))
	dt = pd.DataFrame(nd)
	dt["EMA5"] = dt["close"].ewm(span=5,min_periods=5).mean()

	for i in range(78,len(dt)):
		if dt["EMA5"][i-2] > dt["high"][i-2]:
			# print ("First buying signal... Be alert", dt["date"][i-2])
			if dt["high"][i-1] > dt["high"][i-2]:
				itm = int(dt["high"][i-1] - dt["high"][i-1]%100)
				tsb = 'BANKNIFTY23JUN' + str(itm) +'CE'
				print ("Buy {} at".format(tsb), dt["date"][i-1])

		if dt["EMA5"][i-2] < dt["low"][i-2]:
			# print ("First buying signal... Be alert", dt["date"][i-2])
			if dt["low"][i-1] < dt["low"][i-2]:
				itm = int(dt["high"][i-1] - dt["high"][i-1]%100 +100)
				tsb = 'BANKNIFTY23JUN' + str(itm) +'PE'
				print ("Sell {} at".format(tsb), dt["date"][i-1])




"""
# Finding the inside candle pattern in today's stocks
for i in range(0,len(dt["date"])):
	start_time_hh = str(dt["date"][i]).split()[1][:2]
	start_time_mm = str(dt["date"][i]).split()[1][3:5]
	if start_time_hh == '09' and start_time_mm == '15':
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
			rsfr = first_candle_size*.62  			# Fibonacci retracement value for filtering proper stocks
	        # print ("Scanning", stk["EQ"][k],dt["date"][i] )


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
if actualRun == "Yesa":
	# placing buying orders
	# hrOfDay = int(str(datetime.datetime.now().time())[:2])
	# minOfDay = int(str(datetime.datetime.now().time())[3:5])
	# if hrOfDay > 12 :
	for stk_no in range(0,len(filtered_scan1)):
		try:
			tsb = filtered_scan1[stk_no][1]
			entry_price = round((filtered_scan1[stk_no][2] + filtered_scan1[stk_no][2]*0.0001),1)
			sl = round(filtered_scan1[stk_no][3] - filtered_scan1[stk_no][2]*0.0005,1)
			target = round((filtered_scan1[stk_no][2] + filtered_scan1[stk_no][2]*tgPct),1)
			checkOrder = len(ods_v1[(ods_v1["tradingsymbol"]==tsb) & (ods_v1["price"]==entry_price) & (ods_v1["status"]=="TRIGGER PENDING") & (ods_v1["product"]=="MIS") & (ods_v1["transaction_type"]=="BUY")])
			if checkOrder > 0:
				print ("Buy order already placed for", tsb)
			else:
				maxBuy+=1
				if maxBuy <4:
					eb = entryBuyOrder (tsb, entry_price, sl, target)
		except:
			print ("- - - - - - Error placing buy order for", tsb)

	# placing selling orders
	for stk_no in range(0,len(filtered_scan2)):
		try:
			tsb = filtered_scan2[stk_no][1]
			entry_price = round((filtered_scan2[stk_no][2] - filtered_scan2[stk_no][2]*0.0001),1)
			sl = round(filtered_scan2[stk_no][3] + filtered_scan1[stk_no][2]*0.0005,1)
			target = round((filtered_scan2[stk_no][2] - filtered_scan2[stk_no][2]*tgPct),1)
			checkOrder = len(ods_v1[(ods_v1["tradingsymbol"]==tsb) & (ods_v1["price"]==entry_price) & (ods_v1["status"]=="TRIGGER PENDING") & (ods_v1["product"]=="MIS") & (ods_v1["transaction_type"]=="SELL")])
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
"""