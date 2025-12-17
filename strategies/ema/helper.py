import yfinance as yf

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


# Example usage:
nifty_5min = download_index_data("nifty50", "5min", "5d")
banknifty_1hr = download_index_data("niftybank", "1hr", "1mo")

print(nifty_5min.tail())
print(banknifty_1hr.tail())
