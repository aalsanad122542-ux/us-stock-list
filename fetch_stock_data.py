import time
import pandas as pd
import logging
import yfinance as yf
import os
from dotenv import load_dotenv

load_dotenv()
# Note: To run this script, you must install the following packages:
# pip install yfinance alpaca-trade-api finnhub-python requests python-dotenv

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ==========================================
# 1. Yahoo Finance (yfinance) - Completely Free
# ==========================================
def fetch_sector_with_yfinance(ticker_symbol: str):
    """
    Fetches the sector of a given stock ticker using the yfinance library.
    This is highly recommended for unstructured data mapping like filling out Excel sheets.
    """
    logging.info(f"Fetching sector for {ticker_symbol} using yfinance...")
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        sector = info.get('sector', 'Unknown')
        industry = info.get('industry', 'Unknown')
        logging.info(f"Result -> {ticker_symbol}: Sector = {sector}, Industry = {industry}")
        return sector, industry
    except Exception as e:
        logging.error(f"Error fetching data via yfinance: {e}")
        return None, None

# ==========================================
# 2. Alpaca API - Free Tier (Paper Trading / Basic Data)
# ==========================================
def fetch_quotes_with_alpaca(api_key: str, api_secret: str, ticker_symbol: str):
    """
    Fetches the latest trades using Alpaca's REST API.
    Requires an Alpaca account (free to create paper trading keys).
    """
    import alpaca_trade_api as tradeapi
    logging.info(f"Fetching quotes for {ticker_symbol} using Alpaca...")
    
    # Initialize Alpaca API (Paper trading environment)
    api = tradeapi.REST(api_key, api_secret, base_url='https://paper-api.alpaca.markets')
    try:
        # On the free tier, market data relies on IEX
        trade = api.get_latest_trade(ticker_symbol)
        logging.info(f"Result -> {ticker_symbol} Latest Trade Price: ${trade.price} at {trade.timestamp}")
        return trade.price
    except Exception as e:
        logging.error(f"Error fetching data via Alpaca: {e}")
        return None

# ==========================================
# 3. Finnhub API - Generous Free Tier (Fundamentals & Prices)
# ==========================================
def fetch_company_profile_finnhub(api_key: str, ticker_symbol: str):
    """
    Fetches company profile (including sector/industry) using Finnhub.
    Allows up to 300 calls per minute for fundamental data on the free tier.
    """
    import finnhub
    logging.info(f"Fetching profile for {ticker_symbol} using Finnhub...")
    
    # Setup client
    finnhub_client = finnhub.Client(api_key=api_key)
    try:
        profile = finnhub_client.company_profile2(symbol=ticker_symbol)
        if profile:
            sector = profile.get('finnhubIndustry', 'Unknown')
            name = profile.get('name', 'Unknown')
            logging.info(f"Result -> {ticker_symbol}: Name = {name}, Sector = {sector}")
            return sector
        else:
            logging.warning(f"No profile found for {ticker_symbol} on Finnhub.")
            return None
    except Exception as e:
        logging.error(f"Error fetching data via Finnhub: {e}")
        return None

# ==========================================
# 4. Alpha Vantage API - Fundamental & Historical Data
# ==========================================
def fetch_company_overview_alpha_vantage(api_key: str, ticker_symbol: str):
    """
    Fetches company overview (including sector and industry) using Alpha Vantage.
    The free tier is strictly limited to 25 requests per day.
    """
    import requests
    logging.info(f"Fetching overview for {ticker_symbol} using Alpha Vantage...")
    
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker_symbol}&apikey={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        
        # Check if we hit the rate limit
        if "Information" in data and "rate limit" in data["Information"].lower():
            logging.warning(f"Alpha Vantage Rate Limit Hit: {data['Information']}")
            return None
            
        sector = data.get('Sector', 'Unknown')
        industry = data.get('Industry', 'Unknown')
        name = data.get('Name', 'Unknown')
        
        logging.info(f"Result -> {ticker_symbol}: Name = {name}, Sector = {sector}, Industry = {industry}")
        return sector
    except Exception as e:
        logging.error(f"Error fetching data via Alpha Vantage: {e}")
        return None

if __name__ == "__main__":
    print("--- Stock API Demonstration ---")
    
    # Example 1: yfinance (Runs without any API keys)
    fetch_sector_with_yfinance("AAPL")
    fetch_sector_with_yfinance("MSFT")
    
    # Alpaca using .env keys
    alpaca_api_key = os.getenv("ALPACA_API_KEY")
    alpaca_api_secret = os.getenv("ALPACA_API_SECRET")
    if alpaca_api_key and alpaca_api_secret:
        fetch_quotes_with_alpaca(alpaca_api_key, alpaca_api_secret, "AAPL")
        
    # Alpha Vantage using .env key
    alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if alpha_vantage_api_key:
        fetch_company_overview_alpha_vantage(alpha_vantage_api_key, "AAPL")
    
    # For Finnhub, you would populate with your key:
    # fetch_company_profile_finnhub("YOUR_FINNHUB_API_KEY", "AAPL")
