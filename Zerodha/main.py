from kite_trade import *
import pandas as pd

enctoken = "f6grC2p4MI1UjGxYV++4dMCu82eT35PllRhPkl9dsz010HXo1GAB/t0gCt2q/ArvncbGNQoSFNUTAoAzbIsD/gcS6MgmjRyjw1t3U00SAUX5bXsjfsuwBQ=="
kite = KiteApp(enctoken=enctoken)

# Basic calls
# print(kite.margins())
# print(kite.orders())
# print(kite.positions())

# Place Order
order = kite.place_order(variety=kite.VARIETY_AMO,
                         exchange=kite.EXCHANGE_NSE,
                         tradingsymbol="DRREDDY",
                         transaction_type=kite.TRANSACTION_TYPE_BUY,
                         quantity=1,
                         product=kite.PRODUCT_MIS,
                         order_type=kite.ORDER_TYPE_LIMIT,
                         price=4605.1,
                         validity=None,
                         disclosed_quantity=None,
                         trigger_price=None,
                         squareoff=None,
                         stoploss=None,
                         trailing_stoploss=None,
                         tag="TradeViaPython")
print (order)

