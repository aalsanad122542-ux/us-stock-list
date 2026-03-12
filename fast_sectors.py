import pandas as pd
import yfinance as yf
import requests
import logging
import os
import concurrent.futures

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

INPUT_PATH = r"c:\Users\LENOVO\Desktop\antigravity 30-01\US Stock List\us_listed_stocks_fast.xlsx"
OUTPUT_PATH = r"c:\Users\LENOVO\Desktop\antigravity 30-01\US Stock List\us_listed_stocks_fast_with_sectors.xlsx"

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
FMP_API_KEY = os.getenv("FMP_API_KEY", "")

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
    except Exception as e:
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

    return 'Unknown'

def process_chunk(row):
    ticker = row['Ticker']
    sector = get_sector(ticker)
    logging.info(f"Fetched: {ticker} -> {sector}")
    return {"Ticker": ticker, "Company Name": row.get('Company Name', ''), "CIK": row.get('CIK', ''), "Sector": sector}

def add_sectors_concurrently():
    if not os.path.exists(INPUT_PATH):
        logging.error(f"File not found: {INPUT_PATH}")
        return
        
    logging.info(f"Loading {INPUT_PATH}...")
    df = pd.read_excel(INPUT_PATH)
    
    rows = df.to_dict('records')
    results = []
    
    logging.info(f"Fetching sectors concurrently for {len(rows)} companies using 20 threads. This will be much faster...")
    
    # We use ThreadPoolExecutor to make concurrent API requests, significantly speeding up the wait times.
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(process_chunk, row): row for row in rows}
        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()
                results.append(data)
            except Exception as e:
                logging.error(f"Thread failed: {e}")
                
    logging.info("All threads completed. Formatting and saving...")
    final_df = pd.DataFrame(results)
    final_df = final_df.sort_values(by="Ticker")
    final_df.to_excel(OUTPUT_PATH, index=False)
    logging.info(f"Successfully saved to {OUTPUT_PATH}!")

if __name__ == "__main__":
    add_sectors_concurrently()
