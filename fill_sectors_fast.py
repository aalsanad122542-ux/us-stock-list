import pandas as pd
import yfinance as yf
import requests
import logging
import os
import concurrent.futures
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Use the main file
FILE_PATH = r"c:\Users\LENOVO\Desktop\antigravity 30-01\US Stock List\us_listed_stocks.xlsx"

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
FMP_API_KEY = os.getenv("FMP_API_KEY", "")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")

def get_sector(ticker_symbol):
    """Fetches the sector using multiple APIs with failovers."""
    # 1. Primary: yfinance
    try:
        ticker = yf.Ticker(ticker_symbol)
        info_dict = ticker.info
        
        quote_type = info_dict.get('quoteType', 'Unknown')
        if quote_type == 'ETF': return 'ETF'
            
        sector = info_dict.get('sector', 'Unknown')
        if sector and sector.lower() not in ['unknown', '', 'none']:
            return sector
    except Exception:
        pass

    # 2. Fallback 1: FMP
    if FMP_API_KEY:
        try:
            url = f"https://financialmodelingprep.com/api/v3/profile/{ticker_symbol}?apikey={FMP_API_KEY}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200 and len(resp.json()) > 0:
                sector = resp.json()[0].get('sector', 'Unknown')
                if sector and sector.lower() not in ['unknown', '', 'none']: return sector
        except Exception: pass

    # 3. Fallback 2: Finnhub
    if FINNHUB_API_KEY:
        try:
            url = f"https://finnhub.io/api/v1/stock/profile2?symbol={ticker_symbol}&token={FINNHUB_API_KEY}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                sector = resp.json().get('finnhubIndustry', 'Unknown')
                if sector and sector.lower() not in ['unknown', '', 'none']: return sector
        except Exception: pass
        
    # 4. Fallback 3: Alpha Vantage
    if ALPHA_VANTAGE_API_KEY:
        try:
            url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker_symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            if "Information" not in data or "rate limit" not in data["Information"].lower():
                sector = data.get('Sector', 'Unknown')
                if sector and sector.lower() not in ['unknown', '', 'none']: return sector
        except Exception: pass

    return 'Unknown'

def process_chunk(row_data):
    index, row, ticker_col, sector_col = row_data
    ticker = str(row[ticker_col]).strip()
    
    current_sector = str(row.get(sector_col, 'Unknown'))
    
    # Only fetch if missing or unknown
    if pd.isna(current_sector) or current_sector.lower() in ['nan', 'unknown', '']:
        sector = get_sector(ticker)
        logging.info(f"Fetched: {ticker} -> {sector}")
        return index, sector
    else:
        return index, current_sector

def fill_sectors_fast():
    if not os.path.exists(FILE_PATH):
        logging.error(f"File not found: {FILE_PATH}")
        return
        
    logging.info(f"Loading {FILE_PATH}...")
    df = pd.read_excel(FILE_PATH)
    
    ticker_col = next((col for col in df.columns if str(col).lower() in ['ticker', 'symbol', 'stock']), None)
    if not ticker_col:
        logging.error("Could not find a Ticker column.")
        return
        
    sector_col = next((col for col in df.columns if str(col).lower() == 'sector'), None)
    if not sector_col:
        sector_col = 'Sector'
        df[sector_col] = 'Unknown'
        
    # Prepare rows for processing
    rows_to_process = [(index, row, ticker_col, sector_col) for index, row in df.iterrows()]
    
    logging.info(f"Fetching sectors concurrently for {len(rows_to_process)} companies. Fast mode enabled.")
    
    # We use ThreadPoolExecutor to make concurrent API requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(process_chunk, row_data): row_data for row_data in rows_to_process}
        for future in concurrent.futures.as_completed(futures):
            try:
                index, new_sector = future.result()
                df.at[index, sector_col] = new_sector
            except Exception as e:
                logging.error(f"Thread failed: {e}")
                
    logging.info("All threads completed. Saving...")
    try:
        with pd.ExcelWriter(FILE_PATH, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='US Stocks')
        logging.info(f"Successfully saved updated sectors to {FILE_PATH}!")
    except Exception as e:
        logging.error(f"Failed to save Excel file: {e}")

if __name__ == "__main__":
    fill_sectors_fast()
