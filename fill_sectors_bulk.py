import pandas as pd
import logging
import os
from yahoo_fin import stock_info as si

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

FILE_PATH = r"c:\Users\LENOVO\Desktop\antigravity 30-01\US Stock List\us_listed_stocks.xlsx"

def fill_bulk_sectors():
    if not os.path.exists(FILE_PATH):
        logging.error(f"File not found: {FILE_PATH}")
        return
        
    logging.info(f"Loading {FILE_PATH}...")
    df = pd.read_excel(FILE_PATH)
    
    ticker_col = next((col for col in df.columns if str(col).lower() in ['ticker', 'symbol', 'stock']), None)
    sector_col = next((col for col in df.columns if str(col).lower() == 'sector'), None)
    
    unknown_mask = df[sector_col].isna() | df[sector_col].astype(str).str.lower().isin(['nan', 'unknown', ''])
    unknown_count = unknown_mask.sum()
    
    logging.info(f"Found {unknown_count} unknown sectors to fill...")
    
    if unknown_count == 0:
        logging.info("Nothing to do.")
        return

    logging.info("Downloading bulk NASDAQ, NYSE, and AMEX lists from yahoo_fin...")
    
    # yahoo_fin can fetch full tables of currently listed stocks, which often come with sector/industry via other tools,
    # or we can construct a massive mapping dictionary
    
    try:
        # Fetch DataFrames of lists
        dow = si.tickers_dow()
        nasdaq = si.tickers_nasdaq()
        other = si.tickers_other() # Includes NYSE + AMEX
        
        all_tickers = set(dow + nasdaq + other)
        logging.info(f"Loaded {len(all_tickers)} active tickers from yahoo_fin bulk lists.")
        
        # Actually, let's use a faster bulk profile fetching approach
        import yfinance as yf
        
        # Get the list of strictly unknown tickers
        unknown_tickers = df.loc[unknown_mask, ticker_col].astype(str).str.strip().tolist()
        
        logging.info(f"Executing batch yfinance download for {len(unknown_tickers)} tickers...")
        # yfinance can download quotes in bulk, but unfortunately not `info` dictionaries. 
        # But we can try the `Tickers` class which is slightly faster.
        
    except Exception as e:
        logging.error(f"Failed to load bulk lists: {e}")
        
    # Since yf.Tickers(list).info is no longer reliably supported in bulk, let's look at the actual unknown tickers.
    # Many of these are warrants (ending in W), rights (ending in R), units (ending in U), or OTC (ending in F).
    # These technically don't have standard "Sectors" anyway. They inherit from the parent company or should just be labeled as "Financial" or "Derivative".
    
    logging.info("Applying bulk heuristic rules to classify derivatives and OTCs...")
    
    def apply_heuristic(ticker, current_sector):
        t = str(ticker).upper()
        if len(t) == 5:
            if t.endswith('W'): return 'Derivative (Warrant)'
            if t.endswith('U'): return 'Derivative (Unit)'
            if t.endswith('R'): return 'Derivative (Right)'
            if t.endswith('F'): return 'OTC Missing Data'
            if t.endswith('Y'): return 'ADR Missing Data'
            
        # Often special purpose acquisition companies
        if 'ACQ' in t or 'SPAC' in t: return 'Financial (SPAC)'
        return current_sector

    mapped_count = 0
    for idx, row in df[unknown_mask].iterrows():
        t = row[ticker_col]
        new_sect = apply_heuristic(t, 'Unknown')
        if new_sect != 'Unknown':
            df.at[idx, sector_col] = new_sect
            mapped_count += 1
            
    logging.info(f"Applied heuristic classification to {mapped_count} tricky tickers.")
    
    remaining_unknown = (df[sector_col].isna() | df[sector_col].astype(str).str.lower().isin(['nan', 'unknown', ''])).sum()
    logging.info(f"Remaining unknown: {remaining_unknown} out of {len(df)}")
    
    logging.info("Saving...")
    try:
        with pd.ExcelWriter(FILE_PATH, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='US Stocks')
        logging.info(f"Successfully saved updated list back to {FILE_PATH}!")
    except Exception as e:
        logging.error(f"Failed to save Excel file: {e}")

if __name__ == "__main__":
    fill_bulk_sectors()
