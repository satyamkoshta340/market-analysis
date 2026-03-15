import requests
import pandas as pd
from datetime import datetime
import calendar
import os
import time


class Kite:

    def __init__(self, enctoken):

        self.session = requests.Session()

        self.headers = {
            "Authorization": f"enctoken {enctoken}",
            "X-Kite-Version": "3",
            "User-Agent": "Mozilla/5.0"
        }

        self.root = "https://kite.zerodha.com/oms"

    def historical(self, token, start, end, interval):

        url = f"{self.root}/instruments/historical/{token}/{interval}"

        params = {
            "from": start.strftime("%Y-%m-%d %H:%M:%S"),
            "to": end.strftime("%Y-%m-%d %H:%M:%S"),
            "continuous": 0,
            "oi": 0
        }

        r = self.session.get(url, headers=self.headers, params=params)

        js = r.json()

        if js["status"] != "success":
            print(js)
            return pd.DataFrame()

        candles = js["data"]["candles"]

        df = pd.DataFrame(
            candles,
            columns=["date","open","high","low","close","volume"]
        )

        return df


# ---------------- CONFIG ----------------

ENCTOKEN = os.environ.get("ENC_TOKEN")
interval = "5minute"

start_year = 2023
end_year = 2026

output_folder = "index_data"

# indices to download
indices = {
    "NIFTY":256265,
    "SENSEX":265
}

# ----------------------------------------

os.makedirs(output_folder, exist_ok=True)

kite = Kite(ENCTOKEN)


for name, token in indices.items():

    print(f"\n====== {name} ======")

    for year in range(start_year, end_year + 1):

        print(f"\nDownloading {name} {year}")

        yearly_file = f"{output_folder}/{name}_{year}.csv"

        year_df = pd.DataFrame()

        for month in range(1,13):

            start_date = datetime(year, month, 1, 9, 15)

            last_day = calendar.monthrange(year, month)[1]

            end_date = datetime(year, month, last_day, 15, 30)

            print(f"{name} {year}-{month}")

            df = kite.historical(
                token,
                start_date,
                end_date,
                interval
            )

            if df.empty:
                continue

            year_df = pd.concat([year_df, df])

            # save progress monthly
            year_df.to_csv(yearly_file, index=False)

            time.sleep(0.5)

        print(f"Saved {yearly_file}")