from kite_trade import *
import pandas as pd
import time
import os
import datetime
from dotenv import load_dotenv
load_dotenv()

doM = 10  	# --> Change this everyday 
mon = 7 	# --> Change this month

def getEntryExitTime(dt,entryPrice,Tg,SL,txntype):
	if txntype == "Buy": 						# entry exit timing for buying orders
		status = "No entry"
		candleNo = None
		mae = max(dt["high"][6:])  # maximum profit after entry price and time
		maet = dt["date"][dt[dt["high"]==mae]["date"].index[0]]
		for i in range(5, len(dt)):
			if dt["high"][i] >= entryPrice:
				entryTime = dt["date"][i]
				candleNo = i
				print ("Bought at", i, "th candle")
				status = "Entered"
				break		
		if candleNo is not None:
			for cn in range(candleNo+1, len(dt)):
				if dt["low"][cn] <= SL:
					exitTime = dt["date"][cn]
					status = "SL Hit"
					print ("Buy SL Hit",cn)
					break					
				elif dt["high"][cn] >= Tg:
					exitTime = dt["date"][cn]
					status = "Target Hit"
					print ("Buy Target hit",cn)
					break
				else:
					exitTime = "No exit" 
		else:
			entryTime = "No entry"
			exitTime = "No exit" 

	elif txntype == "Sell":
		mae = min(dt["low"][6:])  # maximum profit after entry price and time
		maet = dt["date"][dt[dt["low"]==mae]["date"].index[0]] 
		status = "No entry"
		candleNo = None
		for i in range(5, len(dt)):
			if dt["low"][i] <= entryPrice:
				entryTime = dt["date"][i]
				candleNo = i
				status = "Entered"
				print ("Sold at",i,"ith candle")
				break		
		if candleNo is not None:
			for cn in range(candleNo+1, len(dt)):
				# print (dt["low"][cn],Tg,i)
				if dt["high"][cn] >= SL:
					exitTime = dt["date"][cn]
					status = "SL Hit"
					# print ("Sell SL hit",cn)
					break					
				elif dt["low"][cn] <= Tg:
					exitTime = dt["date"][cn]
					status = "Target Hit"
					# print ("Sell target meet",cn)
					break
				else:
					exitTime = "No exit" 
		else:  	 	 	 		 	 	# entry exit timing for selling orders
			entryTime = "No entry"
			exitTime = "No exit" 

	return (status,entryTime,exitTime,mae,maet)


enctoken = os.environ.get("ENC_TOKEN")
kite = KiteApp(enctoken=enctoken)
# print("Starting", kite.margins(), "loggid in")

# Capital to be deployed per stock
iniCap = 2000   # placing order for 5 stocks
tgPct = .007    # % profit targeted in a trade
# time.sleep(60)

# Get Historical Data
dir_path = os.path.dirname(os.path.realpath(__file__))
stk = pd.read_csv( dir_path+ "/itkn.csv")
scanned = []
filtered_scan1 = []; filtered_scan2 = []
noc = 5 # number of inside candles to be checked
ptf = 0   # pattern found in #stocks

# Lopping through the list of FNO stocks (having high volumes)
for k in range(0,len(stk)):
	tsb = stk["EQ"][k]
	# if stk["itkn"][k] != 225537: continue
	# getting historical data
	instrument_token = stk["itkn"][k]    # DRREDDY 225537 SBILIFE 5582849
	# from_datetime = datetime.datetime.now() - datetime.timedelta(days=3)     # From last & days
	# to_datetime = datetime.datetime.now()
	from_datetime = datetime.datetime(2023, mon, doM, 9, 00, 00, 000000)
	to_datetime = datetime.datetime(2023, mon, doM, 15, 00, 00, 000000)
	tradingDay = datetime.datetime(2023, mon, doM, 9, 00, 00, 000000).date()
	interval = "15minute"
	try:
		nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
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
				if first_15m_high > max(dt["high"][i+1:i+noc]) and first_15m_low < min(dt["low"][i+1:i+noc]):
					ptf += 1
					# print (stk["EQ"][k], "formed pattern with candle size of", first_candle_size, "percentage.")
					# print (dt.loc[i:i+noc])
					scanned.append((pct_candle, stk["EQ"][k]))
					# print (first_15m_high,rsfr, first_15m_low, min(dt["low"][i+1:i+noc]), first_15m_high- rsfr )
					buyfib = round((first_15m_high - min(dt["low"][i+1:i+noc])) / first_candle_size,2)
					sellfib = round((max(dt["high"][i+1:i+noc]) - first_15m_low) / first_candle_size,2)
					if min(dt["low"][i+1:i+noc]) >= (first_15m_high - rsfr):
						if first_15m_close > first_15m_low + 0.6*first_candle_size:
							# print ("Condition satisfied to place buy order", stk["EQ"][k], dt["close"][i+noc], buyfib)
							SLBuy = round(max(sec_15m_low,first_15m_high-first_15m_high*.005),1)
							if pct_candle <= 3.5:
								entryPrice = first_15m_high
								tgBuy = round((entryPrice + entryPrice*tgPct),1)
								results = getEntryExitTime(dt,entryPrice,tgBuy,SLBuy,"Buy")
								entryTime = results[1]
								exitTime = results[2]
								status = results[0]
								mae = results[3]
								maet = results[4]
								qty = int(5*iniCap/entryPrice)
								exProfit = int((-entryPrice+tgBuy)*qty)
								exLoss = int((entryPrice-SLBuy)*qty)
								print ("BUY", tsb, "at", entryPrice, "qty", qty, "SL",SLBuy,"Target",tgBuy )
								print ("Expected profit {}, loss {}".format(exProfit, exLoss), )
								print (results[0],"Entry time", results[1], "Exit time", results[2],"\n" )
								filtered_scan1.append((pct_candle, stk["EQ"][k], first_15m_high, SLBuy,buyfib,tgBuy,"Buy",status,entryTime,exitTime,mae,maet,tradingDay))

					if max(dt["high"][i+1:i+noc]) <= (first_15m_low + rsfr):
						if first_15m_close < first_15m_high - 0.6*first_candle_size:	
							# print ("Condition satisfied to place sell order", stk["EQ"][k], dt["close"][i+noc], sellfib)
							slSell = round(min(sec_15m_high,first_15m_low+first_15m_low*.005),1)
							if pct_candle <= 3.5:
								entryPrice = first_15m_low
								tgSell = round((entryPrice - entryPrice*tgPct),1)
								results = getEntryExitTime(dt,entryPrice,tgSell,slSell,"Sell")
								entryTime = results[1]
								exitTime = results[2]
								status = results[0]
								mae = results[3]
								maet = results[4]
								qty = int(5*iniCap/entryPrice)
								exProfit = int((entryPrice-tgSell)*qty)
								exLoss = int((entryPrice-slSell)*qty)
								print ("SELL", tsb, "at", entryPrice, "qty", qty, "SL",slSell,"Target",tgSell )
								print ("Expected profit {}, loss {}".format(exProfit, exLoss))
								print (results[0],"Entry time", results[1], "Exit time", results[2], "\n")
								filtered_scan2.append((pct_candle, stk["EQ"][k], first_15m_low, slSell, sellfib,tgSell,"Sell",status,entryTime,exitTime,mae,maet,tradingDay))

	# if stk["EQ"][k] == "SBILIFE":
	# 	print ("Exiting here")
	# 	break

filtered_scan1 = sorted(filtered_scan1)
filtered_scan2 = sorted(filtered_scan2)


# print ("Total stocks found", len(scanned), sorted(scanned))
# print ("\nStocks for Sell",len(filtered_scan2), filtered_scan2)
# print ("\nStocks to Buy",len(filtered_scan1), filtered_scan1)

finalStocks = filtered_scan1 + filtered_scan2
orderbook = pd.DataFrame()
today = datetime.datetime.now().date()

orderbook["date"] = [s[12] for s in finalStocks]
orderbook["Order"] = [s[6] for s in finalStocks]
orderbook["Stock"] = [s[1] for s in finalStocks]
orderbook["pctCandle"] = [s[0] for s in finalStocks]
orderbook["fibRetr"] = [s[4] for s in finalStocks]
orderbook["entryPrice"] = [s[2] for s in finalStocks]
orderbook["SL"] = [s[3] for s in finalStocks]
orderbook["Target"] = [s[5] for s in finalStocks]
orderbook["Status"] = [s[7] for s in finalStocks]
orderbook["entryTime"] = [s[8] for s in finalStocks]
orderbook["exitTime"] = [s[9] for s in finalStocks]
orderbook["maxTarget"] = [s[10] for s in finalStocks]
orderbook["maxTargetTime"] = [s[11] for s in finalStocks]

print (os.getcwd())
orderbook.to_csv("E:\\Abhishek_Koshta\\Personal\\Investment\\Back Testing\\market-analysis\\Zerodha\\Dont_Upload\\orderbook_{}_{}_2023.csv".format(doM,mon))

print (orderbook)
