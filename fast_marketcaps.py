import pandas as pd
import requests
import logging
import os
import yfinance as yf
import concurrent.futures

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

FILE_PATH = r"c:\Users\LENOVO\Desktop\antigravity 30-01\US Stock List\us_listed_stocks.xlsx"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def clean_market_cap(val_str):
    if not val_str or pd.isna(val_str):
        return None
    try:
        val_str = str(val_str).replace(',', '').replace('$', '').strip()
        if not val_str:
            return None
        return float(val_str)
    except Exception:
        return None

def fetch_from_yfinance(ticker):
    try:
        t = yf.Ticker(ticker)
        cap = t.info.get('marketCap')
        return cap
    except Exception:
        return None

def process_fallback(row_data):
    index, ticker = row_data
    cap = fetch_from_yfinance(ticker)
    if cap:
        logging.info(f"Fallback YFinance MATCH: {ticker} -> {cap}")
    return index, cap

def add_marketcaps():
    if not os.path.exists(FILE_PATH):
        logging.error(f"File not found: {FILE_PATH}")
        return
        
    logging.info(f"Loading {FILE_PATH}...")
    df = pd.read_excel(FILE_PATH)
    
    ticker_col = next((col for col in df.columns if str(col).lower() in ['ticker', 'symbol', 'stock']), None)
    if not ticker_col:
        logging.error("No Ticker column found.")
        return
        
    mc_col = 'Market Cap'
    if mc_col not in df.columns:
        df[mc_col] = None

    logging.info("Step 1: Downloading master list from official Nasdaq API endpoint for instant bulk processing...")
    url = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25&offset=0&download=true"
    
    mc_map = {}
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()
        
        rows = data.get('data', {}).get('rows', [])
        logging.info(f"Successfully fetched {len(rows)} stocks from Nasdaq!")
        
        for r in rows:
            sym = str(r.get('symbol', '')).upper()
            cap_raw = r.get('marketCap', '')
            cap_clean = clean_market_cap(cap_raw)
            if sym and cap_clean:
                mc_map[sym] = cap_clean
                
    except Exception as e:
        logging.error(f"Failed to fetch Nasdaq bulk API: {e}")

    mapped_count = 0
    missing_indices = []
    
    # Apply nasdaq mappings
    for idx, row in df.iterrows():
        ticker = str(row[ticker_col]).strip().upper()
        # If it's already mapped and we want to overwrite, or if it is null
        current_mc = row.get(mc_col)
        if pd.isna(current_mc) or current_mc == '' or current_mc == 'Unknown':
            if ticker in mc_map:
                df.at[idx, mc_col] = mc_map[ticker]
                mapped_count += 1
            else:
                missing_indices.append((idx, ticker))

    logging.info(f"Instantly mapped {mapped_count} market caps via bulk data!")
    logging.info(f"Falling back to concurrent yfinance for remaining {len(missing_indices)} obscure tickers...")

    yf_mapped_count = 0
    
    # Use ThreadPoolExecutor to make concurrent API requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(process_fallback, row_data): row_data for row_data in missing_indices}
        for future in concurrent.futures.as_completed(futures):
            try:
                index, cap = future.result()
                if cap:
                    df.at[index, mc_col] = cap
                    yf_mapped_count += 1
            except Exception as e:
                pass
                
    logging.info(f"Mapped {yf_mapped_count} market caps via yfinance fallback.")

    # Fill remaining unmappable with "Unknown" or leave blank
    df[mc_col] = df[mc_col].fillna("Unknown")

    logging.info("Saving updated file...")
    try:
        with pd.ExcelWriter(FILE_PATH, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='US Stocks')
        logging.info(f"Successfully saved Market Caps to {FILE_PATH}!")
    except Exception as e:
        logging.error(f"Failed to save Excel file: {e}")

if __name__ == "__main__":
    add_marketcaps()
