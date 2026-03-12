import pandas as pd
import requests
import logging
import os

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

FILE_PATH = r"c:\Users\LENOVO\Desktop\antigravity 30-01\US Stock List\us_listed_stocks.xlsx"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def fill_sectors_nasdaq_api():
    if not os.path.exists(FILE_PATH):
        logging.error(f"File not found: {FILE_PATH}")
        return
        
    logging.info(f"Loading {FILE_PATH}...")
    df = pd.read_excel(FILE_PATH)
    
    ticker_col = next((col for col in df.columns if str(col).lower() in ['ticker', 'symbol', 'stock']), None)
    sector_col = next((col for col in df.columns if str(col).lower() == 'sector'), None)
    
    unknown_mask = df[sector_col].isna() | df[sector_col].astype(str).str.lower().isin(['nan', 'unknown', ''])
    unknown_count = unknown_mask.sum()
    
    logging.info(f"Found {unknown_count} strictly unknown sectors before checking the Nasdaq API...")
    
    logging.info("Downloading master sector list from official Nasdaq API endpoint...")
    url = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25&offset=0&download=true"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()
        
        rows = data.get('data', {}).get('rows', [])
        logging.info(f"Successfully fetched {len(rows)} stocks with sector mapping from Nasdaq in 1 HTTP Request!")
        
        # Build mapping
        sector_map = {}
        for r in rows:
            sym = str(r.get('symbol', '')).upper()
            sec = str(r.get('sector', '')).strip()
            if sym and sec and sec.lower() not in ['', 'nan', 'na', 'unknown']:
                sector_map[sym] = sec
                
        # Fill unknown sectors in existing DataFrame directly from the map
        mapped_count = 0
        for idx, row in df[unknown_mask].iterrows():
            ticker = str(row[ticker_col]).strip().upper()
            if ticker in sector_map:
                df.at[idx, sector_col] = sector_map[ticker]
                mapped_count += 1
                logging.info(f"NASQAQ BULK MATCH: {ticker} -> {sector_map[ticker]}")
                
        logging.info(f"Instantly mapped {mapped_count} remaining tickers!")
        
        remaining_unknown = (df[sector_col].isna() | df[sector_col].astype(str).str.lower().isin(['nan', 'unknown', ''])).sum()
        logging.info(f"Remaining unknown completely: {remaining_unknown} out of {len(df)}")
        
        logging.info("Saving...")
        with pd.ExcelWriter(FILE_PATH, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='US Stocks')
        logging.info(f"Successfully saved to {FILE_PATH}!")
        
    except Exception as e:
        logging.error(f"Failed to fetch or process Nasdaq bulk API: {e}")

if __name__ == "__main__":
    fill_sectors_nasdaq_api()
