# This program should be run once the inside candle scanner code has been run and orders are placed for the scanned stocks
from kite_trade import *
import pandas as pd
import time
import datetime
import os
from dotenv import load_dotenv
load_dotenv()
from FifteenMin_IC import getEntryExit
enctoken = os.environ.get("ENC_TOKEN")
kite = KiteApp(enctoken=enctoken)

# One hour makes 12 candles of 5 minutes 
# This program will run every 5 minute to check the order book and to place/cancel orders
t = 0 	# starting at 10:30 AM every trading day
tries = 0
while t < 12*5:
	t+=1
	tries = 0
	while tries < 10:
		try:
			ods = pd.DataFrame(kite.orders()) 	# getting the order object
			pos = pd.DataFrame(kite.positions()) # getting the position object from Kite
			tries =10
		except:
			tries += 1
			print ("Connection issue... please try after some time.")
			time.sleep(7)

	posHeld = []; posExited =[]; entryTriggered = []
	print("==================Getting the entryPrice and symbol name for the positions held and exited=====================")

	for i in range(0,len(pos)):
		if pos["net"][i]["product"] == "MIS" :
			tsb = pos["net"][i]["tradingsymbol"]
			entryTriggered.append(tsb)
		if pos["net"][i]["product"] == "MIS" and pos["net"][i]["quantity"] != 0:
			# print (pos["net"][i])
			ts = pos["net"][i]["tradingsymbol"]
			qty = pos["net"][i]["quantity"]
			entryPrice = pos["net"][i]["average_price"]
			posHeld.append((ts, qty, entryPrice))

		elif pos["net"][i]["product"] == "MIS" and pos["net"][i]["quantity"] == 0:
			# print (pos["net"][i])
			ts = pos["net"][i]["tradingsymbol"]
			qty = pos["net"][i]["quantity"]
			entryPrice = pos["net"][i]["average_price"]
			posExited.append((ts, qty, entryPrice))

	print ("We are holding {} positions as of now".format(len(posHeld)))
	if len(posHeld)>0:
		print (posHeld)
	print ("We have exited {} positions as of now".format(len(posExited)))
	if len(posExited)>0:
		print (posExited)
	ordInSystem = len(ods[(ods["status"]=="TRIGGER PENDING") & (ods["product"]=="MIS")])
	today = datetime.datetime.now().date()
	pendingEntries = ods[(ods["status"]=="TRIGGER PENDING") & (ods["product"]=="MIS")]["tradingsymbol"]
	if ordInSystem > 0:
		print ("We have {} entry pending orders {}".format(ordInSystem,today))
		print (pendingEntries)

	# Placing SL and target orders for the open positions in the account
	for k in range(0,len(posHeld)):
		qty = posHeld[k][1]
		tsb = posHeld[k][0]
		entryPrice = posHeld[k][2]
		if "BANKNIFTY" in tsb or "SHRIRAMFIN23APR1400PE" in tsb or "MFSL23APR630CE" in tsb  or "HCLTECH23APR1050CE" in tsb:
			print ("Having position in options MIS... skipping", tsb)
			continue
		checkLOrder = len(ods[(ods["tradingsymbol"]==tsb) & (ods["status"]=="OPEN")])
		checkTPOrder = len(ods[(ods["tradingsymbol"]==tsb) & (ods["status"]=="TRIGGER PENDING")])

		# below code will place orders for buying entry only
		if qty > 0 :
			tgPct = 0.015 		# have a fixed target of 1.5%
			slPct = 0.005		# have a fixed SL of 0.6%
			# print("# Placing SL and target orders for the open positions in the account")
			try:
				slPrice = getEntryExit(tsb)[1]
				tgPrice = getEntryExit(tsb)[2]
				# print (tsb, "optimized SL and target choosen")
			except:
				slPrice = round(entryPrice - entryPrice*slPct,1)
				tgPrice = round(entryPrice + entryPrice*tgPct,1)
				print ("Taking hard coded SL and target", tsb)
			# Stop loss order will be a stop loss order while target order will be a limit order
			if checkLOrder > 0:
				print ("Limit/Target Order already placed for {} in the sytem... Skipping...".format(tsb))
				continue
			else:
				print (tsb, "qty", qty, "entryPrice", entryPrice, "slPrice", slPrice, "tgPrice", tgPrice)
				targetOrder = 	kite.place_order(variety=kite.VARIETY_REGULAR,
							exchange=kite.EXCHANGE_NSE,
							tradingsymbol=tsb,
							transaction_type=kite.TRANSACTION_TYPE_SELL,
							quantity=qty,product=kite.PRODUCT_MIS,
							order_type=kite.ORDER_TYPE_LIMIT,
							price=tgPrice,
							validity=None,	disclosed_quantity=None,
							trigger_price=None,	squareoff=None,	stoploss=None,
							trailing_stoploss=None,	tag="TradeViaPython")
				print ("Placed taget order for", tsb, "at", tgPrice)
				time.sleep(5)
			# If the price is below the trigger this order won't be placed, so using try and except
			if checkTPOrder > 0:
				print ("Target Order already placed for {} in the sytem... Skipping...".format(tsb))
				continue
			else:
				try:
					slOrder = 	kite.place_order(variety=kite.VARIETY_REGULAR,
								exchange=kite.EXCHANGE_NSE,
								tradingsymbol=tsb,
								transaction_type=kite.TRANSACTION_TYPE_SELL,
								quantity=qty,product=kite.PRODUCT_MIS,
								order_type=kite.ORDER_TYPE_SL,
								price=slPrice,validity=None,
								disclosed_quantity=None,trigger_price=slPrice,
								squareoff=None,stoploss=None,
								trailing_stoploss=None,tag="TradeViaPython")
					print ("Place sl order for", tsb,"at", slPrice)
				except:
					print ("Price is below SL trigger price, exiting positions at market price", tsb, slPrice)
					slOrder = 	kite.place_order(variety=kite.VARIETY_REGULAR,
					exchange=kite.EXCHANGE_NSE,
					tradingsymbol=tsb,transaction_type=kite.TRANSACTION_TYPE_SELL,
					quantity=qty,product=kite.PRODUCT_MIS,
					order_type=kite.ORDER_TYPE_MARKET,
					price=None,validity=None,disclosed_quantity=None,
					trigger_price=None,squareoff=None,stoploss=None,
					trailing_stoploss=None,
					tag="TradeViaPython")

		# Placing SL and target order for stocks shorted
		if qty < 0 :
			qty = abs(qty)
			tgPct = 0.015 		# have a fixed target of 1.5%
			slPct = 0.006		# have a fixed SL of 0.6%
			tsb = posHeld[k][0]
			entryPrice = posHeld[k][2]
			try:
				slPrice = getEntryExit(tsb)[1]
				tgPrice = getEntryExit(tsb)[2]
				# print (tsb,"Optimized SL and target choosen")
			except:
				slPrice = round(entryPrice + entryPrice*slPct,1)
				tgPrice = round(entryPrice - entryPrice*tgPct,1)
				print ("Taking hard coded SL and target",tsb)
			# Stop loss order will be a stop loss order while target order will be a limit order
			if checkTPOrder > 0:
				print ("Target Order already placed for {} in the sytem... Skipping...".format(tsb))
				continue
			else:	
				print (tsb, "qty", qty, "entryPrice", entryPrice, "slPrice", slPrice, "tgPrice", tgPrice)
				targetOrder = 	kite.place_order(variety=kite.VARIETY_REGULAR,
							exchange=kite.EXCHANGE_NSE,
							tradingsymbol=tsb,
							transaction_type=kite.TRANSACTION_TYPE_BUY,
							quantity=qty,product=kite.PRODUCT_MIS,
							order_type=kite.ORDER_TYPE_LIMIT,
							price=tgPrice,
							validity=None,	disclosed_quantity=None,
							trigger_price=None,	squareoff=None,	stoploss=None,
							trailing_stoploss=None,	tag="TradeViaPython")
				print ("Placed taget order for", tsb, "at", tgPrice)
				time.sleep(5)
			# If the price is below the trigger this order won't be placed, so using try and except
			if checkLOrder > 0:
				print ("Limit/Target Order already placed for {} in the sytem... Skipping...".format(tsb))
				continue
			else:
				try:
					slOrder = 	kite.place_order(variety=kite.VARIETY_REGULAR,
								exchange=kite.EXCHANGE_NSE,
								tradingsymbol=tsb,
								transaction_type=kite.TRANSACTION_TYPE_BUY,
								quantity=qty,product=kite.PRODUCT_MIS,
								order_type=kite.ORDER_TYPE_SL,
								price=slPrice,validity=None,
								disclosed_quantity=None,trigger_price=slPrice,
								squareoff=None,stoploss=None,
								trailing_stoploss=None,tag="TradeViaPython")
					print ("Place sl order for", tsb,"at", slPrice)
				except:
					print ("Price is below SL trigger price, exiting positions at market price", tsb, slPrice)
					slOrder = 	kite.place_order(variety=kite.VARIETY_REGULAR,
					exchange=kite.EXCHANGE_NSE,
					tradingsymbol=tsb,transaction_type=kite.TRANSACTION_TYPE_BUY,
					quantity=qty,product=kite.PRODUCT_MIS,
					order_type=kite.ORDER_TYPE_MARKET,
					price=None,validity=None,disclosed_quantity=None,
					trigger_price=None,squareoff=None,stoploss=None,
					trailing_stoploss=None,
					tag="TradeViaPython")

	# Cancelling other open/SL orders once the position is exited for a stock
	if len(posExited) == 0:
		print ("No additional orders in queue for the positions exited.")
	tobeCancelled=[]
	for l in range(0,len(posExited)):
		tsb = posExited[l][0]
		# get order id of the open order
		getOIDs = ods[(ods["tradingsymbol"]==tsb) & (ods["status"]=="OPEN")]["order_id"]
		# get order id of the trigger pending i.e. SL order
		getTPIDs =	ods[(ods["tradingsymbol"]==tsb) & (ods["status"]=="TRIGGER PENDING")]["order_id"]
		if len(getOIDs) != 0:
			for getOID in getOIDs:
				tobeCancelled.append(getOID)
				print ("SL HIT!... Cancelling limit order for", tsb, getOID)
				cancelOrder = kite.cancel_order(variety=kite.VARIETY_REGULAR, order_id = getOID)

		if len(getTPIDs) != 0:
			for getTPID in getTPIDs:
				print ("Target HIT!... Cancelling SL order for", tsb, getTPID)
				tobeCancelled.append(getTPID)
				cancelOrder = kite.cancel_order(variety=kite.VARIETY_REGULAR, order_id = getTPID)

	# Cancelling the orders if entry was not triggered even after 1 o' clock

	hrOfDay = int(str(datetime.datetime.now().time())[:2])
	minOfDay = int(str(datetime.datetime.now().time())[3:5])
	if hrOfDay >= 14:
		print ("\nWe are trading past 1-1/2 o' clock... checking pending triggers and cancelling...")
		# getting the name of the stocks that have pending orders 
		stk = ods[ods["status"]=="TRIGGER PENDING"]["tradingsymbol"]
		for stk in stk:
			if stk not in entryTriggered:
				getTPID = ods[(ods["status"]=="TRIGGER PENDING") & (ods["tradingsymbol"]==stk) ]["order_id"]
				for getTPID in getTPID:
					print ("Cancelling order for", stk, getTPID)
					cancelOrder = kite.cancel_order(variety=kite.VARIETY_REGULAR, order_id = getTPID)
		if len(posHeld) == 0:
			print ("No positions held... Shutting down...")
			break
	if hrOfDay >=15 and minOfDay >=20:
		print ("Running past market hours... exiting", hrOfDay, minOfDay)
		break
	print (datetime.datetime.now().time())
	restTime = 5
	print ("---------------------- Taking rest for {} minute -------------------------------".format(restTime))
	time.sleep(restTime*60)
