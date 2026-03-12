import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import logging
import os
import concurrent.futures
from urllib.parse import quote

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

FILE_PATH = r"c:\Users\LENOVO\Desktop\antigravity 30-01\US Stock List\us_listed_stocks.xlsx"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive'
}

def scrape_sector_finviz(ticker):
    """Fallback 1: Scrapes Finviz for Sector data"""
    try:
        url = f"https://finviz.com/quote.ashx?t={quote(ticker)}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Finviz usually puts sector/industry in a specific table or breadcrumb
            # Based on recent layout: "Sector: [Sector] | Industry: [Industry]"
            links = soup.body.find_all('a', class_='tab-link')
            
            # The first links in this specific area are usually Sector, Industry, Country
            if len(links) >= 2:
                # Iterate and try to match standard classes
                for i, link in enumerate(links):
                    if "screener.ashx?v=111&f=sec_" in str(link.get('href', '')):
                        sector = link.text.strip()
                        return sector
    except Exception as e:
        pass
    
    return 'Unknown'

def scrape_sector_yahoo(ticker):
    """Primary Scraper: Yahoo Finance Profile Page"""
    try:
        url = f"https://finance.yahoo.com/quote/{quote(ticker)}/profile"
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Yahoo Finance recently moved Sector/Industry under specific classes or data-test attributes
            # Look for typical profile containers
            container = soup.find('div', {'data-testid': 'asset-profile'})
            if not container:
                # Try falling back to finding the label directly
                strong_tags = soup.find_all('strong')
                for i, tag in enumerate(strong_tags):
                    # We look at the preceding text/span
                    prev_text = str(tag.parent.text).lower()
                    if 'sector' in prev_text:
                        return tag.text.strip()
            else:
                # Parse container
                spans = container.find_all('span')
                for i, span in enumerate(spans):
                    if 'Sector' in span.text:
                        # usually the next span or a strong tag holds the value
                        next_strong = span.find_next_sibling('strong')
                        if next_strong: return next_strong.text.strip()
                        next_span = span.find_next_sibling('span')
                        if next_span: return next_span.text.strip()
                        
    except Exception as e:
        pass
        
    return 'Unknown'

def scrape_combined(ticker):
    """Tries Yahoo then Finviz. Returns 'Unknown' if both fail."""
    # Add a slight random delay to mimic human behavior before making the request
    # time.sleep(random.uniform(0.5, 2.0))
    
    sector = scrape_yahoo(ticker)
    if sector != 'Unknown': return sector
    
    sector = scrape_sector_finviz(ticker)
    return sector

def scrape_yahoo(ticker):
    """Uses a lightweight Yahoo scraping fallback looking directly for the sector."""
    try:
        url = f"https://finance.yahoo.com/quote/{quote(ticker)}"
        response = requests.get(url, headers=HEADERS, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Modern Yahoo Finance uses fin-streamer or data-fields. We can just look for the text 'Sector(s)'
            for p in soup.find_all('p'):
                text = p.get_text(separator='|')
                if 'Sector' in text and '|' in text:
                    parts = text.split('|')
                    for i, part in enumerate(parts):
                        if 'Sector' in part and i + 1 < len(parts):
                            val = parts[i+1].strip()
                            if val and val.lower() != 'industry':
                                return val
    except Exception:
        pass
    return 'Unknown'


def process_ticker(row_data):
    index, row, ticker_col, sector_col = row_data
    ticker = str(row[ticker_col]).strip()
    
    current_sector = str(row.get(sector_col, 'Unknown'))
    
    # Only scrape if missing or unknown
    if pd.isna(current_sector) or current_sector.lower() in ['nan', 'unknown', '']:
        sector = scrape_combined(ticker)
        if sector != 'Unknown':
            logging.info(f"SCRAPED: {ticker} -> {sector}")
            return index, sector
        else:
            logging.warning(f"Failed to scrape: {ticker}")
            return index, current_sector
    else:
        return index, current_sector

def fill_unknown_sectors():
    if not os.path.exists(FILE_PATH):
        logging.error(f"File not found: {FILE_PATH}")
        return
        
    logging.info(f"Loading {FILE_PATH}...")
    df = pd.read_excel(FILE_PATH)
    
    ticker_col = next((col for col in df.columns if str(col).lower() in ['ticker', 'symbol', 'stock']), None)
    sector_col = next((col for col in df.columns if str(col).lower() == 'sector'), None)
    
    unknown_mask = df[sector_col].isna() | df[sector_col].astype(str).str.lower().isin(['nan', 'unknown', ''])
    unknown_count = unknown_mask.sum()
    
    logging.info(f"Found {unknown_count} unknown sectors to scrape...")
    
    if unknown_count == 0:
        logging.info("Nothing to do.")
        return
        
    rows_to_process = [(index, row, ticker_col, sector_col) for index, row in df[unknown_mask].iterrows()]

    # Use a medium worker count (15) to speed up the final obscure checks
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(process_ticker, row_data): row_data for row_data in rows_to_process}
        for future in concurrent.futures.as_completed(futures):
            try:
                index, new_sector = future.result()
                df.at[index, sector_col] = new_sector
            except Exception as e:
                logging.error(f"Thread failed: {e}")
                
    remaining_unknown = (df[sector_col].isna() | df[sector_col].astype(str).str.lower().isin(['nan', 'unknown', ''])).sum()
    logging.info(f"Scraping complete. Remaining unknown: {remaining_unknown}")
    
    logging.info("Saving...")
    try:
        with pd.ExcelWriter(FILE_PATH, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='US Stocks')
        logging.info(f"Successfully saved updated list back to {FILE_PATH}!")
    except Exception as e:
        logging.error(f"Failed to save Excel file: {e}")

if __name__ == "__main__":
    fill_unknown_sectors()
