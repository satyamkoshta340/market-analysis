from kite_trade import *
import pandas as pd

enctoken = "f6grC2p4MI1UjGxYV++4dMCu82eT35PllRhPkl9dsz010HXo1GAB/t0gCt2q/ArvncbGNQoSFNUTAoAzbIsD/gcS6MgmjRyjw1t3U00SAUX5bXsjfsuwBQ=="
kite = KiteApp(enctoken=enctoken)

# Get Historical Data
import datetime
stk = pd.read_csv("itkn.csv")
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
		            	filtered_scan1.append((pct_candle, stk["EQ"][k], first_15m_high))
		            if max(dt["high"][i+1:i+5]) <= (first_15m_low + rsfr):
		            	# print ("Condition satisfied to place sell order")
		            	filtered_scan2.append((pct_candle, stk["EQ"][k], first_15m_low))

print ("Total stocks found", len(scanned))
print ("Stocks with FR",len(filtered_scan1), sorted(filtered_scan1))

# Next task
# place buy order for top 3 filtered_scan1 stocks - SL .6% below the entry and Target .7% above the entry



