---
name: alpaca-expert
description: Expert skill for querying the Alpaca API for stock market data and paper trading. Use this skill when the user wants to fetch real-time or historical stock data, execute paper trades, or integrate Alpaca's services into their application.
---

# Alpaca Expert

This skill provides guidance on using the Alpaca API for fetching stock quotes, historical data, and executing trades via Alpaca's paper trading environment.

## Capabilities

1. **Market Data Retrieval**: Fetching real-time quotes, historical price bars, and latest trades using the Alpaca Market Data API.
2. **Paper Trading**: Executing mock buy/sell orders securely.
3. **Account Information**: Retrieving account balances, portfolio history, and positions.

## Typical Usage

When integrating Alpaca:
1. Always load the API keys from environment variables (`ALPACA_API_KEY` and `ALPACA_API_SECRET`).
2. Use the paper trading URL (`https://paper-api.alpaca.markets`) unless explicitly told to use the live API.
3. Utilize the official `alpaca-trade-api` or `alpaca-py` Python SDKs for smooth integration.

## Example: Getting Latest Trade (Python)

```python
import os
import alpaca_trade_api as tradeapi

api_key = os.getenv("ALPACA_API_KEY")
api_secret = os.getenv("ALPACA_API_SECRET")
base_url = "https://paper-api.alpaca.markets"

api = tradeapi.REST(api_key, api_secret, base_url=base_url)

trade = api.get_latest_trade("AAPL")
print(f"Latest AAPL Trade: {trade.price}")
```
