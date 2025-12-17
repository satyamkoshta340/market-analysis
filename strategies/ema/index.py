# streamlit app
import streamlit as st
import pandas as pd
import yfinance as yf
import os

def download_index_data(index_name: str, candle_size: str = "1d", period: str = "1mo"):
    """
    Download historical OHLC data for Nifty indices.
    
    Parameters:
        index_name (str): "nifty50" or "niftybank"
        candle_size (str): "5m", "15m", "1h", "1d"
        period (str): how much data to pull → ("1d", "5d", "1mo", "3mo", "1y", "max")

    Returns:
        pandas.DataFrame: OHLCV data
    """

    # Yahoo ticker mapping
    ticker_map = {
        "nifty50": "^NSEI",
        "niftybank": "^NSEBANK"
    }

    if index_name.lower() not in ticker_map:
        raise ValueError("Invalid index name! Use 'nifty50' or 'niftybank'.")

    ticker = ticker_map[index_name.lower()]

    # Yahoo uses 60m for 1hr candles
    interval_map = {
        "5min": "5m",
        "15min": "15m",
        "1hr": "60m",
        "1day": "1d",
        "5m": "5m",
        "15m": "15m",
        "1h": "60m",
        "1d": "1d"
    }

    if candle_size not in interval_map:
        raise ValueError("Invalid candle_size. Use: 5min, 15min, 1hr, 1day")

    interval = interval_map[candle_size]

    df = yf.download(
        tickers=ticker,
        interval=interval,
        period=period,
        progress=False
    )

    return df


    data = dp['Close']
    ema = data.ewm(span=5, adjust=False).mean()
    len = data.size

    signals = []

    for i in range(1, len):
        if dp['Low'][i-1] > ema[i-1] and dp['Low'][i] < ema[i]:
            signal = {}
            signal_candle_low = dp['Low'][i]
            signal_candle_high = dp['High'][i]
            signal_candle_body = abs(dp['Close'][i] - dp['Open'][i])
            
            signal['index'] = i
            signal['Date'] = dp['Date'][i] if 'Date' in dp else None
            signal['Time'] = dp['Time'][i] if 'Time' in dp else None
            signal['entry'] = signal_candle_low
            signal['stop_loss'] = signal_candle_high
            signal['target'] = signal['entry'] - 2 * signal_candle_body
            signal['Low'] = dp['Low'][i]
            signal['EMA_5'] = ema[i]

            # print(f"Signal: {signal}")
            signals.append(signal)
    return pd.DataFrame(signals)


def find_signals(dp: pd.DataFrame):
    data = dp['Close']
    ema = data.ewm(span=5, adjust=False).mean()
    len = data.size

    signals = []

    for i in range(1, len):
        if dp['Low'][i-1] > ema[i-1] and dp['Low'][i] < ema[i]:
            signal = {}
            signal_candle_low = dp['Low'][i]
            signal_candle_high = dp['High'][i]
            signal_candle_body = abs(dp['Close'][i] - dp['Open'][i])
            
            signal['index'] = i
            signal['Datetime'] = dp['Datetime'][i] if 'Datetime' in dp else None
            signal['entry'] = signal_candle_low
            signal['stop_loss'] = signal_candle_high
            signal['target'] = signal['entry'] - 2 * signal_candle_body
            signal['Low'] = dp['Low'][i]
            signal['EMA_5'] = ema[i]

            # print(f"Signal: {signal}")
            signals.append(signal)
    return pd.DataFrame(signals)


import pandas as pd

def get_signal_stats(df, dynamic_interval=None):
    """
    df must contain column 'Datetime'
    dynamic_interval (int): custom minutes value
    """
    
    intervals = list(range(5, 376, 5))
    if dynamic_interval is not None:
        intervals.append(dynamic_interval)

    intervals = sorted(intervals)

    # Ensure datetime is sorted
    df = df.sort_values("Datetime").reset_index(drop=True)

    results = {
        "label": [f"{i}min" for i in range(5, 376, 5)],
        "count": []
    }
    used_indices = set()  # Keep track of signals already counted

    for interval in intervals:
        count = 0
        last_time = None
        last_idx = None

        for idx, row in df.iterrows():

            # Skip if already used in smaller interval
            if idx in used_indices:
                continue

            if last_time is None:
                last_time = row["Datetime"]
                last_idx = idx
            elif (row["Datetime"] - last_time).total_seconds() == interval * 60:
                count += 1
                last_time = row["Datetime"]
                used_indices.add(idx)
                used_indices.add(last_idx)
                last_idx = idx
            elif (row["Datetime"] - last_time).total_seconds() > interval * 60:
                last_time = None
                last_idx = None


        results["count"].append(count)

    return results


# Streamlit app
st.title("5-EMA Trading Strategy Analyzer")

# show the dropdowns (render in one row)
# ticker = "nifty50"
# candle_size = "5m"
# period = "1d"
col1, col2, col3 = st.columns(3)
with col1:
    ticker = st.selectbox("Select Index", ["nifty50", "niftybank"])
with col2:
    candle_size = st.selectbox("Select Candle Size", ["5m", "15m", "1h", "1d"])
with col3:
    period = st.selectbox("Select Period", ["1d", "5d", "1mo", "3mo", "1y", "max"])

df = pd.DataFrame()
# Download datas on button click 
if st.button("Download Data"):
    st.write(f"Downloading data for {ticker} with {candle_size} candles over {period} period...")
    df = download_index_data(ticker, candle_size, period)
    df = df.reset_index()
    df.columns = df.columns.droplevel(1)
    st.subheader("Downloaded Data")
    st.dataframe(df.tail())

if not df.empty:
    signals_df = find_signals(df)
    st.subheader("Generated Signals")
    # show whole signals_df with max 10 rows rest scroll bar
    st.dataframe(signals_df)

    if signals_df is not None and not signals_df.empty:
        st.subheader("Signal Analysis Summary")
        data = get_signal_stats(signals_df)
        dq = pd.DataFrame(data)
        # Desired order
        order = [f"{i}min" for i in range(5, 376, 5)]

        dq["label"] = pd.Categorical(dq["label"], categories=order, ordered=True)
        dq = dq.sort_values("label")

        st.bar_chart(dq.set_index("label"))
    else:
        st.write("No signals generated to analyze.")