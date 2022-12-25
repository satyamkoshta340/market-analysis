import pandas as pd
dt = pd.read_csv("BANKNIFTY50_5MIN_25072022_to_22092022.csv")
# dt["only_dates"] = [dt["Datetime"][i].split(" ")[0] for i in range(len(dt))]



slPoints= 80; profitPoints = 100
signal = 0; profitableSignals = 0; lossSignals = 0
for j in range(0,len(dt)-1,75):    
# for j in range(0,len(dt),75):    
    # print (j, dt["Datetime"][j], "high", dt["High"][j], "Low", dt["Low"][j])
    first5minHigh = int(dt["High"][j])
    first5minLow= int(dt["Low"][j])
    
    for k in range(1,10):
        # print (dt["Datetime"][j+k], dt["Low"][j+k] , first5minLow,first5minHigh)
        ## Finding bullish trade for the day
        if dt["High"][j+k] > first5minHigh:
            signal+=1
            entryTimeBull = j+k
            entryPrice = first5minHigh+5       
            print ("\n",j,dt["Datetime"][j],"first5minHigh", first5minHigh, "first5minLow", first5minLow)
            print ("Bullish Set-up found ", dt["Datetime"][j+k], "EntryPrice", entryPrice)
            ## Exit conditions
            for l in range(1,12):
                if dt["Low"][j+k+l] < entryPrice - slPoints:
                    print ("Bull SL Hit",  dt["Datetime"][j+k+l], "Close", int(dt["Close"][j+k+l]),"Low", int(dt["Low"][j+k+l]))
                    lossSignals += 1
                    break
                elif dt["High"][j+k+l] > entryPrice + profitPoints:
                    print ("Bull Profit Booked",  dt["Datetime"][j+k+l], "Close", int(dt["Close"][j+k+l]),"High", int(dt["High"][j+k+l]))
                    profitableSignals += 1
                    break
            break

        ## Finding bearish trade for the day
        elif dt["Low"][j+k] < first5minLow:
            signal+=1
            entryTimeBear = j+k
            entryPrice = first5minLow-5       
            print ("\n",j,dt["Datetime"][j],"first5minHigh", first5minHigh, "first5minLow", first5minLow)
            print ("Bearish Set-up found ", dt["Datetime"][j+k], "EntryPrice", entryPrice)
            ## Exit conditions
            for l in range(1,12):
                if dt["High"][j+k+l] > entryPrice + slPoints:
                    lossSignals += 1
                    print ("Bear SL Hit",  dt["Datetime"][j+k+l], "Close", int(dt["Close"][j+k+l]),"Low", int(dt["Low"][j+k+l]))
                    break
                elif dt["Low"][j+k+l] < entryPrice - profitPoints:
                    profitableSignals += 1
                    print ("Bear Profit Booked",  dt["Datetime"][j+k+l], "Close", int(dt["Close"][j+k+l]),"High", int(dt["High"][j+k+l]))
                    break
            break

    else:
        print ("\n",j, "No set-up found on", dt["Datetime"][j], "first5minHigh", first5minHigh, "first5minLow", first5minLow)
        break

print (signal, profitableSignals,lossSignals)


