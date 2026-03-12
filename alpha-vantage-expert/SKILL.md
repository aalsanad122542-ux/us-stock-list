---
name: alpha-vantage-expert
description: Expert skill for querying the Alpha Vantage API for financial market data. Use this skill when the user wants to fetch historical data, intraday time series, forex rates, cryptocurrency data, or fundamental data (like earnings/income statements) using Alpha Vantage.
---

# Alpha Vantage Expert

This skill provides guidance on using the Alpha Vantage API for fetching diverse financial data, handling rate limits, and processing the JSON/CSV responses correctly.

## Capabilities

1. **Time Series Data**: Fetching intraday, daily, weekly, and monthly stock prices.
2. **Fundamental Data**: Retrieving company overviews, earnings, income statements, balance sheets, and cash flow.
3. **Forex and Crypto**: Accessing exchange rates and historical cryptocurrency data.
4. **Technical Indicators**: Fetching SMA, EMA, RSI, MACD, etc.

## Typical Usage

When integrating Alpha Vantage:
1. Load the API key from the environment variable (`ALPHA_VANTAGE_API_KEY`).
2. Construct the REST API url typically formatted as: `https://www.alphavantage.co/query?function=FUNCTION_NAME&symbol=SYMBOL&apikey=YOUR_API_KEY`.
3. Be mindful of rate limits: The standard free tier allows exactly **25 requests per day**. Do not aggressively loop over a large list of tickers.

## Example: Getting Intraday Time Series (Python)

```python
import os
import requests

api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
symbol = "AAPL"
url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={api_key}"

response = requests.get(url)
data = response.json()

if "Time Series (5min)" in data:
    print(f"Successfully fetched {symbol} intraday data")
else:
    print("Error or Rate Limit:", data.get("Information", data))
```

## Example: Getting Company Overview

```python
import os
import requests

api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
symbol = "AAPL"
url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}"

response = requests.get(url)
data = response.json()

sector = data.get("Sector", "Unknown")
industry = data.get("Industry", "Unknown")
print(f"{symbol}: Sector = {sector}, Industry = {industry}")
```
