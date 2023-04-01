from kite_trade import *
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

enctoken = os.environ.get("ENC_TOKEN")
kite = KiteApp(enctoken=enctoken)

# Get Historical Data
import datetime
dir_path = os.path.dirname(os.path.realpath(__file__))
stk = pd.read_csv( dir_path+ "/itkn.csv")
scanned = []
filtered_scan1 = []; filtered_scan2 = []

ptf = 0

# Lopping through the list of FNO stocks (having high volumes)
for k in range(0,len(stk)):
	# if stk["itkn"][k] != 225537: continue
	# getting historical data
	instrument_token = stk["itkn"][k]    # DRREDDY 225537
	from_datetime = datetime.datetime.now() - datetime.timedelta(days=2)     # From last & days
	to_datetime = datetime.datetime.now()
	interval = "15minute"
	nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
	# print(kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False))
	dt = pd.DataFrame(nd)

	if len(dt) < 7:
		print ("Error fetching data for", stk["EQ"][k])
		continue
	# else:
	# 	print ("Data fetched for", stk["EQ"][k], instrument_token, len(dt))

	# Finding the inside candle pattern in today's stocks
	for i in range(0,len(dt["date"])):
		start_time_hh = str(dt["date"][i]).split()[1][:2]
		start_time_mm = str(dt["date"][i]).split()[1][3:5]
		if start_time_hh == '09' and start_time_mm == '15':
			if dt["high"][i] <150:
				continue
			else:
				first_15m_high = dt["high"][i]
				first_15m_low = dt["low"][i]
				first_candle_size = first_15m_high - first_15m_low
				pct_candle = round(100*first_candle_size/first_15m_high,2)
				rsfr = first_candle_size*.62
		        # print ("Scanning", stk["EQ"][k],dt["date"][i] )
				if first_15m_high > max(dt["high"][i+1:i+5]) and first_15m_low < min(dt["low"][i+1:i+5]):
					ptf += 1
					# print (stk["EQ"][k], "formed pattern with candle size of", first_candle_size, "percentage.")
					# print (dt.loc[i:i+5])
					scanned.append((pct_candle, stk["EQ"][k]))
					# print (first_15m_high,rsfr, first_15m_low, min(dt["low"][i+1:i+5]), first_15m_high- rsfr )

					if min(dt["low"][i+1:i+5]) >= (first_15m_high - rsfr):
						# print ("Condition to place buy order")
						if pct_candle <= 1.5:
							filtered_scan1.append((pct_candle, stk["EQ"][k], first_15m_high))
					if max(dt["high"][i+1:i+5]) <= (first_15m_low + rsfr):
		            	# print ("Condition satisfied to place sell order")
						if pct_candle <= 1.5:
							filtered_scan2.append((pct_candle, stk["EQ"][k], first_15m_low))

filtered_scan1 = sorted(filtered_scan1)
filtered_scan2 = sorted(filtered_scan2)

print ("Total stocks found", len(scanned))
print ("Stocks to Buy",len(filtered_scan1), filtered_scan1)
print ("Stocks for Sell",len(filtered_scan2), filtered_scan2)

# Next task
# place buy order for top 3 filtered_scan1 stocks - SL .6% below the entry and Target .7% above the entry

# ============================== Placing buy orders ================================== #
# Defining parameters
iniCap = 2000
# Placing order for top 1 stock
if len(filtered_scan1) >= 1:
	stk_no = 0
	tsb = filtered_scan1[stk_no][1]
	entry_price = round((filtered_scan1[stk_no][2] + filtered_scan1[stk_no][2]*0.0001),1)
	qty = int(5*iniCap/entry_price)
	print ("Placing 1st buying order for", tsb, "at", entry_price)
	order = kite.place_order(variety=kite.VARIETY_AMO,
	                         exchange=kite.EXCHANGE_NSE,
	                         tradingsymbol=tsb,
	                         transaction_type=kite.TRANSACTION_TYPE_BUY,
	                         quantity=qty,
	                         product=kite.PRODUCT_MIS,
	                         order_type=kite.ORDER_TYPE_LIMIT,
	                         price=entry_price,
	                         validity=None,
	                         disclosed_quantity=None,
	                         trigger_price=None,
	                         squareoff=None,
	                         stoploss=None,
	                         trailing_stoploss=None,
	                         tag="TradeViaPython")
	print (order)

	# Placing order for 2nd stock
	try:
		stk_no = 1
		tsb = filtered_scan1[stk_no][1]
		entry_price = round((filtered_scan1[stk_no][2] + filtered_scan1[stk_no][2]*0.0001),1)
		qty = int(5*iniCap/entry_price)
		print ("Placing 2nd buying order for", tsb, "at", entry_price)
		order = kite.place_order(variety=kite.VARIETY_AMO,
		                         exchange=kite.EXCHANGE_NSE,
		                         tradingsymbol=tsb,
		                         transaction_type=kite.TRANSACTION_TYPE_BUY,
		                         quantity=qty,
		                         product=kite.PRODUCT_MIS,
		                         order_type=kite.ORDER_TYPE_LIMIT,
		                         price=entry_price,
		                         validity=None,
		                         disclosed_quantity=None,
		                         trigger_price=None,
		                         squareoff=None,
		                         stoploss=None,
		                         trailing_stoploss=None,
		                         tag="TradeViaPython")
		print (order)
	except:
		print("only 1 stock matched pattern for buying")

	# Placing buy order for 3rd stock
	try:
		stk_no = 2
		entry_price = round((filtered_scan1[stk_no][2] + filtered_scan1[stk_no][2]*0.0001),1)
		tsb = filtered_scan1[stk_no][1]
		qty = int(5*iniCap/entry_price)
		print ("Placing 3rd buying order for", tsb, "at", entry_price)
		order = kite.place_order(variety=kite.VARIETY_AMO,
		                         exchange=kite.EXCHANGE_NSE,
		                         tradingsymbol=tsb,
		                         transaction_type=kite.TRANSACTION_TYPE_BUY,
		                         quantity=qty,
		                         product=kite.PRODUCT_MIS,
		                         order_type=kite.ORDER_TYPE_LIMIT,
		                         price=entry_price,
		                         validity=None,
		                         disclosed_quantity=None,
		                         trigger_price=None,
		                         squareoff=None,
		                         stoploss=None,
		                         trailing_stoploss=None,
		                         tag="TradeViaPython")
		print (order)
	except:
		print ("Only 2 stocks found for buying")
else:
	print ("Could not find a single stock with the pattern")

# ============================== Placing sell orders ================================== #
# 1st Sell order
flag = "Sell"
if len(filtered_scan2) >= 1 :
	stk_no = 0
	tsb = filtered_scan2[stk_no][1]
	entry_price = round((filtered_scan2[stk_no][2] - filtered_scan2[stk_no][2]*0.0001),1)
	qty = int(5*iniCap/entry_price)
	print ("Placing 1st sell order for", tsb, "at", entry_price)
	order = kite.place_order(variety=kite.VARIETY_AMO,
	                         exchange=kite.EXCHANGE_NSE,
	                         tradingsymbol=tsb,
	                         transaction_type=kite.TRANSACTION_TYPE_SELL,
	                         quantity=qty,
	                         product=kite.PRODUCT_MIS,
	                         order_type=kite.ORDER_TYPE_LIMIT,
	                         price=entry_price,
	                         validity=None,
	                         disclosed_quantity=None,
	                         trigger_price=None,
	                         squareoff=None,
	                         stoploss=None,
	                         trailing_stoploss=None,
	                         tag="TradeViaPython")
	print (order)

	# Placing order for 2nd stock
	try:
		stk_no = 1
		tsb = filtered_scan2[stk_no][1]
		entry_price = round((filtered_scan2[stk_no][2] - filtered_scan2[stk_no][2]*0.0001),1)
		qty = int(5*iniCap/entry_price)
		print ("Placing 2nd sell order for", tsb, "at", entry_price)
		order = kite.place_order(variety=kite.VARIETY_AMO,
		                         exchange=kite.EXCHANGE_NSE,
		                         tradingsymbol=tsb,
		                         transaction_type=kite.TRANSACTION_TYPE_SELL,
		                         quantity=qty,
		                         product=kite.PRODUCT_MIS,
		                         order_type=kite.ORDER_TYPE_LIMIT,
		                         price=entry_price,
		                         validity=None,
		                         disclosed_quantity=None,
		                         trigger_price=None,
		                         squareoff=None,
		                         stoploss=None,
		                         trailing_stoploss=None,
		                         tag="TradeViaPython")
		print (order)
	except:
		print("only 1 stock matched pattern for buying")
