from kite_trade import *
import pandas as pd
import time
# Run this file on every market trading day at 10:45:10 to get the orders placed
import os
from dotenv import load_dotenv
load_dotenv()


enctoken = os.environ.get("ENC_TOKEN")
kite = KiteApp(enctoken=enctoken)
# print("Starting", kite.margins(), "loggid in")

# time.sleep(5*60)
# Capital to be deployed per stock
iniCap = 2000   # placing order for 5 stocks
tgPct = .007    # % profit targeted in a trade
# time.sleep(60)

# Get Historical Data
import datetime
dir_path = os.path.dirname(os.path.realpath(__file__))
stk = pd.read_csv( dir_path+ "/itkn.csv")
scanned = []
filtered_scan1 = []; filtered_scan2 = []
noc = 5 # number of inside candles to be checked
ptf = 0   # pattern found in #stocks

# Lopping through the list of FNO stocks (having high volumes)
for k in range(0,len(stk)):
	# if stk["itkn"][k] != 225537: continue
	# getting historical data
	instrument_token = stk["itkn"][k]    # DRREDDY 225537
	# from_datetime = datetime.datetime.now() - datetime.timedelta(days=3)     # From last & days
	# to_datetime = datetime.datetime.now()
	doM = 18; mon = 4
	from_datetime = datetime.datetime(2023, mon, doM, 9, 00, 00, 000000)
	to_datetime = datetime.datetime(2023, mon, doM, 11, 00, 00, 000000)
	interval = "15minute"
	try:
		nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
		# print(kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False))
		dt = pd.DataFrame(nd)
	except:
		print ("Data not available for", stk["EQ"][k])
		continue

	if len(dt) < 6:
		print ("Error fetching data for", stk["EQ"][k])
		continue
	# else:
	# 	print ("Data fetched for", stk["EQ"][k], instrument_token, len(dt))

	# Finding the inside candle pattern in today's stocks
	for i in range(0,len(dt["date"])):
		start_time_hh = str(dt["date"][i]).split()[1][:2]
		start_time_mm = str(dt["date"][i]).split()[1][3:5]
		if start_time_hh == '09' and start_time_mm == '15':
			if dt["high"][i] <150 or dt["high"][i] > 7999:
				continue
			else:
				first_15m_high = dt["high"][i]
				first_15m_low = dt["low"][i]
				sec_15m_high = max(dt["high"][i+1:len(dt)])
				sec_15m_low = min(dt["low"][i+1:len(dt)])

				first_candle_size = first_15m_high - first_15m_low
				pct_candle = round(100*first_candle_size/first_15m_high,2)
				rsfr = first_candle_size*.62  			# Fibonacci retracement value for filtering proper stocks
		        # print ("Scanning", stk["EQ"][k],dt["date"][i] )
				if first_15m_high > max(dt["high"][i+1:i+noc]) and first_15m_low < min(dt["low"][i+1:i+noc]):
					ptf += 1
					# print (stk["EQ"][k], "formed pattern with candle size of", first_candle_size, "percentage.")
					# print (dt.loc[i:i+noc])
					scanned.append((pct_candle, stk["EQ"][k]))
					# print (first_15m_high,rsfr, first_15m_low, min(dt["low"][i+1:i+noc]), first_15m_high- rsfr )

					if min(dt["low"][i+1:i+noc]) >= (first_15m_high - rsfr):
						print ("Condition satisfied to place buy order", stk["EQ"][k], dt["close"][i+noc], dt["volume"][i+noc],dt["date"][i+noc])
						print ("Stop loss", sec_15m_low)
						if pct_candle <= 3.5:
							filtered_scan1.append((pct_candle, stk["EQ"][k], first_15m_high, sec_15m_low))
					if max(dt["high"][i+1:i+noc]) <= (first_15m_low + rsfr):
						print ("Condition satisfied to place sell order", stk["EQ"][k], dt["close"][i+noc], dt["volume"][i+noc],dt["date"][i+noc])
						if pct_candle <= 3.5:
							filtered_scan2.append((pct_candle, stk["EQ"][k], first_15m_low, sec_15m_high))

filtered_scan1 = sorted(filtered_scan1)
filtered_scan2 = sorted(filtered_scan2)


print ("Total stocks found", len(scanned), sorted(scanned))
print ("\nStocks for Sell",len(filtered_scan2), filtered_scan2)
print ("\nStocks to Buy",len(filtered_scan1), filtered_scan1)

test_run = "No"

if test_run == "No":
	print ("\nData fetched for", str(dt["date"][i]).split()[0], "placing orders...\n" )
	ft = 0
	while ft <30:
		ft = ft+5
		time.sleep(5)
		print ("Time remaining to cancel the order...", 30-ft)
		print ("... Press ctrl+Insert+Fn to break" )

	# Next task
	# place buy order for top 3 filtered_scan1 stocks - SL .6% below the entry and Target .7% above the entry

	# ============================== Placing buy orders ================================== #
	# Placing order for top 1 stock
	if len(filtered_scan1) >= 1:
		stk_no = 0
		tsb = filtered_scan1[stk_no][1]
		entry_price = round((filtered_scan1[stk_no][2] + filtered_scan1[stk_no][2]*0.0001),1)
		sl = round(filtered_scan1[stk_no][3] - filtered_scan1[stk_no][2]*0.0005,1)
		target = round((filtered_scan1[stk_no][2] + filtered_scan1[stk_no][2]*tgPct),1)
		qty = int(5*iniCap/entry_price)
		exProfit = int((target-entry_price)*qty)
		exLoss = int((sl-entry_price)*qty)
		print ("\nExpected profit {}, loss {}".format(exProfit, exLoss))
		print ("Placing 1st buying order for", tsb, "at", entry_price, "qty", qty, "SL",sl,"Target",target)
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
		print (order)
		time.sleep(1)
		# Placing order for 2nd stock
		try:
			stk_no = 1
			tsb = filtered_scan1[stk_no][1]
			entry_price = round((filtered_scan1[stk_no][2] + filtered_scan1[stk_no][2]*0.0001),1)
			sl = round(filtered_scan1[stk_no][3] - filtered_scan1[stk_no][2]*0.0005,1)
			target = round((filtered_scan1[stk_no][2] + filtered_scan1[stk_no][2]*tgPct),1)
			qty = int(5*iniCap/entry_price)
			exProfit = int((target-entry_price)*qty)
			exLoss = int((sl-entry_price)*qty)
			print ("\nExpected profit {}, loss {}".format(exProfit, exLoss))
			print ("Placing 2nd buying order for", tsb, "at", entry_price, "qty", qty, "SL",sl,"Target",target )
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
			print (order)
			time.sleep(1)

		except:
			print("only 1 stock matched pattern for buying")

		# Placing buy order for 3rd stock
		try:
			stk_no = 2
			entry_price = round((filtered_scan1[stk_no][2] + filtered_scan1[stk_no][2]*0.0001),1)
			tsb = filtered_scan1[stk_no][1]
			sl = round(filtered_scan1[stk_no][3] - filtered_scan1[stk_no][2]*0.0005,1)
			target = round((filtered_scan1[stk_no][2] + filtered_scan1[stk_no][2]*tgPct),1)
			qty = int(5*iniCap/entry_price)
			exProfit = int((target-entry_price)*qty)
			exLoss = int((sl-entry_price)*qty)
			print ("\nExpected profit {}, loss {}".format(exProfit, exLoss))
			print ("Placing 3rd buying order for", tsb, "at", entry_price, "qty", qty, "SL",sl,"Target",target )
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
			print (order)
			time.sleep(1)
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
		sl = round(filtered_scan2[stk_no][3] + filtered_scan1[stk_no][2]*0.0005,1)
		target = round((filtered_scan2[stk_no][2] - filtered_scan2[stk_no][2]*tgPct),1)
		qty = int(5*iniCap/entry_price)
		exProfit = int((entry_price-target)*qty)
		exLoss = int((entry_price-sl)*qty)
		print ("\nExpected profit {}, loss {}".format(exProfit, exLoss))

		print ("Placing 1st selling order for", tsb, "at", entry_price, "qty", qty, "SL",sl,"Target",target )
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
		print (order)
		time.sleep(1)

		# Placing sell order for 2nd stock
		try:
			stk_no = 1
			tsb = filtered_scan2[stk_no][1]
			entry_price = round((filtered_scan2[stk_no][2] - filtered_scan2[stk_no][2]*0.0001),1)
			sl = round(filtered_scan2[stk_no][3] + filtered_scan1[stk_no][2]*0.0005,1)
			target = round((filtered_scan2[stk_no][2] - filtered_scan2[stk_no][2]*tgPct),1)
			qty = int(5*iniCap/entry_price)
			exProfit = int((entry_price - target)*qty)
			exLoss = int((entry_price-sl)*qty)
			print ("\nExpected profit {}, loss {}".format(exProfit, exLoss))
			print ("Placing 2nd selling order for", tsb, "at", entry_price, "qty", qty, "SL",sl,"Target",target )
			order = kite.place_order(variety=kite.VARIETY_REGULAR,
			                         exchange=kite.EXCHANGE_NSE,
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
			print (order)
		except:
			print("only 1 stock matched pattern for selling")



