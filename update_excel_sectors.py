import pandas as pd
import yfinance as yf
import requests
import logging
import os
import time

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

FILE_PATH = r"c:\Users\LENOVO\Desktop\antigravity 30-01\US Stock List\us_listed_stocks.xlsx"
BACKUP_PATH = r"c:\Users\LENOVO\Desktop\antigravity 30-01\US Stock List\us_listed_stocks_backup.xlsx"

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
FMP_API_KEY = os.getenv("FMP_API_KEY", "")

MAJOR_ETFS = [
    "SPY", "QQQ", "DIA", "IWM",
    "VTI", "VOO", "VEA", "VWO",
    "XLF", "XLK", "XLV", "XLE", "XLY", "XLP", "XLI", "XLU", "XLB", "XLRE", "XLC",
    "ARKK", "SMH", "SOXX", "KRE"
]

def fetch_sec_master_list():
    """Fetches the official list of US publicly traded companies from the SEC."""
    logging.info("Fetching master list from SEC EDGAR...")
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": "StockAnalyzer bot@example.com"}
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        
        tickers = []
        for index, info in data.items():
            tickers.append(info['ticker'].replace('-', '.')) # Format correctly for Yahoo
            
        logging.info(f"Successfully fetched {len(tickers)} tickers from the SEC.")
        return set(t.upper() for t in tickers)
    except Exception as e:
        logging.error(f"Failed to fetch SEC master list: {e}")
        return set()

def is_tradeable(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        history = ticker.history(period="1mo")
        if history.empty:
            return False
        return True
    except Exception:
        return False

def get_sector_fmp(ticker_symbol):
    if not FMP_API_KEY: return 'Unknown'
    try:
        url = f"https://financialmodelingprep.com/api/v3/profile/{ticker_symbol}?apikey={FMP_API_KEY}"
        resp = requests.get(url)
        if resp.status_code == 200 and len(resp.json()) > 0:
            return resp.json()[0].get('sector', 'Unknown')
    except Exception: pass
    return 'Unknown'

def get_sector_finnhub(ticker_symbol):
    if not FINNHUB_API_KEY: return 'Unknown'
    try:
        url = f"https://finnhub.io/api/v1/stock/profile2?symbol={ticker_symbol}&token={FINNHUB_API_KEY}"
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.json().get('finnhubIndustry', 'Unknown')
    except Exception: pass
    return 'Unknown'

def get_sector_and_type_multi_api(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        quote_type = info.get('quoteType', 'Unknown')
        
        if quote_type == 'ETF': return 'ETF', 'ETF'
            
        sector = info.get('sector', 'Unknown')
        if sector and sector.lower() not in ['unknown', '', 'none']:
            return sector, quote_type
    except Exception:
        quote_type = 'Unknown'
        sector = 'Unknown'

    logging.info(f"yfinance missed Sector for {ticker_symbol}. Trying FMP...")
    sector = get_sector_fmp(ticker_symbol)
    if sector and sector.lower() not in ['unknown', '', 'none']: return sector, quote_type

    logging.info(f"FMP missed Sector for {ticker_symbol}. Trying Finnhub...")
    sector = get_sector_finnhub(ticker_symbol)
    if sector and sector.lower() not in ['unknown', '', 'none']: return sector, quote_type

    return 'Unknown', quote_type

def process_excel():
    logging.info(f"Loading '{FILE_PATH}'...")
    if not os.path.exists(FILE_PATH):
        logging.error(f"File not found: {FILE_PATH}")
        return

    try:
        df = pd.read_excel(FILE_PATH)
    except Exception as e:
        logging.error(f"Failed to read Excel file: {e}")
        return
        
    df.to_excel(BACKUP_PATH, index=False)
    logging.info(f"Backup saved to '{BACKUP_PATH}'")

    ticker_col = next((col for col in df.columns if str(col).lower() in ['ticker', 'symbol', 'stock']), None)
    if not ticker_col:
        logging.error(f"Could not find a Ticker column. Columns: {df.columns.tolist()}")
        return
        
    sector_col = next((col for col in df.columns if str(col).lower() == 'sector'), None)
    if not sector_col:
        sector_col = 'Sector'
        df[sector_col] = 'Unknown'

    existing_tickers = set(df[ticker_col].astype(str).str.strip().str.upper().tolist())
    
    # --- PHASE 1: Sync Master List ---
    sec_tickers = fetch_sec_master_list()
    missing_from_excel = sec_tickers - existing_tickers
    
    if missing_from_excel:
        logging.info(f"Found {len(missing_from_excel)} US stocks missing from your Excel. Adding them...")
        new_rows = []
        for t in missing_from_excel:
            new_row = {ticker_col: t, sector_col: 'Unknown'}
            for col in df.columns:
                if col not in [ticker_col, sector_col]: new_row[col] = ''
            new_rows.append(new_row)
        
        missing_df = pd.DataFrame(new_rows)
        df = pd.concat([df, missing_df], ignore_index=True)

    # --- PHASE 2: Check Tradeability & Update Sectors ---
    valid_rows = []
    
    logging.info(f"Processing {len(df)} total rows. Verifying tradeability & fetching sectors...")
    for index, row in df.iterrows():
        ticker = str(row[ticker_col]).strip()
        
        if pd.isna(ticker) or ticker == 'nan' or ticker == '': continue
            
        logging.info(f"Processing: {ticker}")
        
        if is_tradeable(ticker):
            # Known tradeable stock
            current_sector = str(row[sector_col])
            if pd.isna(current_sector) or current_sector.lower() in ['nan', 'unknown', '']:
                sector, qt = get_sector_and_type_multi_api(ticker)
                row[sector_col] = sector
            
            valid_rows.append(row)
        else:
            logging.warning(f"Ticker {ticker} is NOT tradeable anymore. Removing.")

    cleaned_df = pd.DataFrame(valid_rows)
    final_existing_tickers = set(cleaned_df[ticker_col].astype(str).str.upper().tolist())
    
    # --- PHASE 3: Include ETFs ---
    new_etf_rows = []
    logging.info("Checking for missing major ETFs...")
    for etf in MAJOR_ETFS:
        if etf not in final_existing_tickers:
            logging.info(f"Adding missing ETF: {etf}")
            if is_tradeable(etf):
                new_row = {ticker_col: etf, sector_col: 'ETF'}
                for col in cleaned_df.columns:
                    if col not in [ticker_col, sector_col]: new_row[col] = ''
                new_etf_rows.append(new_row)
                
    if new_etf_rows:
        cleaned_df = pd.concat([cleaned_df, pd.DataFrame(new_etf_rows)], ignore_index=True)
        
    # Formatting Note: We can add openpyxl logic here if we need explicit colors,
    # but currently saving clean pandas dataframe via writer.
    logging.info("Saving updated list...")
    try:
        with pd.ExcelWriter(FILE_PATH, engine='openpyxl') as writer:
            cleaned_df.to_excel(writer, index=False, sheet_name='US Stocks')
        logging.info(f"Successfully updated '{FILE_PATH}'!")
        logging.info(f"Original lines: {len(existing_tickers)} -> Final lines: {len(cleaned_df)}")
    except Exception as e:
        logging.error(f"Failed to save Excel file: {e}")

if __name__ == "__main__":
    process_excel()
