# Get fundamentals 
import yfinance as yf
import pandas as pd

path = 'E:/Abhishek_Koshta/Personal/Investment/Back Testing/market-analysis/Zerodha/Dont_Upload/'
df = pd.read_csv(path+'2023-08-28_ATR_BREAK_STOCKS.csv')
# Define the stock symbols
stock_symbols = df.Stock
# print (stock_symbols)

# Create a dictionary to store fundamental data
fundamentals = {}
import requests
from bs4 import BeautifulSoup


# Define the URL of the Screener.in page for the company (replace with the company you want)
url = "https://www.screener.in/company/BHARATWIRE/"

try:
    # Send an HTTP GET request to the website
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find and extract the fundamental data you need
        company_name = soup.find('h1', {'class': 'company-name'}).text.strip()
        market_cap = soup.find('div', {'class': 'market-cap'}).text.strip()
        pe_ratio = soup.find('div', {'class': 'stockdata'}).find_all('span')[0].text.strip()
        eps = soup.find('div', {'class': 'stockdata'}).find_all('span')[1].text.strip()
        dividend_yield = soup.find('div', {'class': 'stockdata'}).find_all('span')[3].text.strip()

        # Print the fundamental data
        print(f"Company Name: {company_name}")
        print(f"Market Cap: {market_cap}")
        print(f"P/E Ratio: {pe_ratio}")
        print(f"Earnings Per Share (EPS): {eps}")
        print(f"Dividend Yield: {dividend_yield}")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

except Exception as e:
    print(f"An error occurred: {str(e)}")
