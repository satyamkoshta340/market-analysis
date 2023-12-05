from kite_trade import *
import pandas as pd

from dotenv import load_dotenv
load_dotenv()

enctoken = os.environ.get("ENC_TOKEN")
kite = KiteApp(enctoken=enctoken)

pd.DataFrame(kite.instruments("NSE")).to_csv("All_stocks.csv")
print(kite.instruments("NSE"))
# Basic calls
# print(kite.margins())
# print(kite.orders())
# print(kite.positions())

# Place Order
