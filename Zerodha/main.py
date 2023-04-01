from kite_trade import *
import pandas as pd

# user_id = "ZZ4000"       # Login Id
# password = "waitforit"      # Login password
# twofa = "652136"         # Login Pin or TOTP
# enctoken = get_enctoken(user_id, password, twofa)

enctoken = "f6grC2p4MI1UjGxYV++4dMCu82eT35PllRhPkl9dsz010HXo1GAB/t0gCt2q/ArvncbGNQoSFNUTAoAzbIsD/gcS6MgmjRyjw1t3U00SAUX5bXsjfsuwBQ=="
kite = KiteApp(enctoken=enctoken)

# Basic calls
# print(kite.margins())
# print(kite.orders())
# print(kite.positions())


# Get instrument or exchange
# print(kite.instruments())
# print(kite.instruments("NSE"))
# print(kite.instruments("NFO"))
df = pd.DataFrame(kite.instruments("NSE")).to_csv("NSE.csv")
df = pd.DataFrame(kite.instruments("NFO")).to_csv("NFO.csv")

# Get Live Data
# print(kite.ltp("NSE:RELIANCE"))
# print(kite.ltp(["NSE:NIFTY 50", "NSE:NIFTY BANK"]))
# print(kite.quote(["NSE:NIFTY BANK", "NSE:ACC", "NFO:NIFTY22SEPFUT"]))

# Get Historical Data
import datetime
instrument_token = 2880769
from_datetime = datetime.datetime.now() - datetime.timedelta(days=1)     # From last & days
to_datetime = datetime.datetime.now()
interval = "15minute"
nd = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
# print(kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False))
dt = pd.DataFrame(nd)
dt.to_csv("Sample.csv")
print (dt.head)

# Place Order
# order = kite.place_order(variety=kite.VARIETY_REGULAR,
#                          exchange=kite.EXCHANGE_NSE,
#                          tradingsymbol="ACC",
#                          transaction_type=kite.TRANSACTION_TYPE_BUY,
#                          quantity=1,
#                          product=kite.PRODUCT_MIS,
#                          order_type=kite.ORDER_TYPE_MARKET,
#                          price=None,
#                          validity=None,
#                          disclosed_quantity=None,
#                          trigger_price=None,
#                          squareoff=None,
#                          stoploss=None,
#                          trailing_stoploss=None,
#                          tag="TradeViaPython")

# print (order)


