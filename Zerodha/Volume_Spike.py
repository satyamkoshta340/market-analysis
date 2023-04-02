from kite_trade import *
import pandas as pd
import time
from Bourses import *
from dotenv import load_dotenv
load_dotenv()

enctoken = os.environ.get("ENC_TOKEN")
kite = KiteApp(enctoken=enctoken)

# Get Historical Data
dir_path = os.path.dirname(os.path.realpath(__file__))
stk = pd.read_csv( dir_path+ "/itkn.csv")

# Capital to be deployed per stock
iniCap = 2000   # placing order for 5 stocks

# Get Historical Data
import datetime
scanned = []
filtered_scan1 = []; filtered_scan2 = []

ptf = 0   # pattern found in #stocks

# Lopping through the list of FNO stocks (having high volumes)
for k in range(0,len(stk)):
	# if stk["itkn"][k] != 225537: continue
	# getting historical data
	instrument_token = stk["itkn"][k]    # DRREDDY 225537
	# from_datetime = datetime.datetime.now() - datetime.timedelta(days=3)     # From last & days
	# to_datetime = datetime.datetime.now()
	from_datetime = datetime.datetime(2023, 3, 30, 14, 00, 00, 000000)
	to_datetime = datetime.datetime(2023, 3, 31, 18, 00, 00, 000000)
	interval = "5minute"
	nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
	# print(kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False))
	dt = pd.DataFrame(nd)

	if len(dt) < 7:
		print ("Error fetching data for", stk["EQ"][k])
		continue

	dt = ema_Vol(dt,14)
	# Finding the inside candle pattern in today's stocks
	for i in range(14,len(dt["date"])):
	    if dt["close"][i] < 50 or dt["close"][i]>3000:
	    	continue

	    # skipping stocks with large shadows
	    actBody = dt["close"][i] - dt["open"][i]		
	    if actBody>0:  # this suggests a green candle
	    	if dt["high"][i] - dt["close"][i] > actBody*.5:
		    	continue
	    else:
	    	if dt["close"][i] - dt["low"][i] > actBody*.5:
		    	continue

	    if dt["volume"][i] >= 3*dt["EMA_volume"][i]:
	    	scanned.append(stk["EQ"][k])
	    	v_ratio = round(dt["volume"][i]/dt["EMA_volume"][i],1)
	    	print (stk["EQ"][k], dt["close"][i],"has seen large volumes at",v_ratio,dt["date"][i])
	    	if dt["close"][i] > dt["close"][i-1]:
	    		filtered_scan1.append(stk["EQ"][k])
	    	else:
	    		filtered_scan2.append(stk["EQ"][k])

filtered_scan1 = sorted(filtered_scan1)
# filtered_scan2 = sorted(filtered_scan2)

print ("Total stocks found", len(scanned))
print ("Stocks to Buy",len(filtered_scan1), filtered_scan1)
# print ("Stocks for Sell",len(filtered_scan2), filtered_scan2)


