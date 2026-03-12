import requests
import pandas as pd
import logging
import os

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

OUTPUT_PATH = r"c:\Users\LENOVO\Desktop\antigravity 30-01\US Stock List\us_listed_stocks_fast.xlsx"

def fetch_sec_master_list():
    """Fetches the official list of US publicly traded companies from the SEC."""
    logging.info("Fetching master list from SEC EDGAR...")
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": "StockAnalyzer bot@example.com"}
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        
        records = []
        for index, info in data.items():
            records.append({
                "Ticker": info['ticker'].replace('-', '.'), 
                "Company Name": info['title'],
                "CIK": info['cik_str']
            })
            
        logging.info(f"Successfully fetched {len(records)} active companies from the SEC.")
        return records
    except Exception as e:
        logging.error(f"Failed to fetch SEC master list: {e}")
        return []


def create_fast_excel():
    records = fetch_sec_master_list()
    if not records:
        logging.error("No data fetched from SEC. Aborting.")
        return
        
    df = pd.DataFrame(records)
    
    # Sort alphabetically by Ticker
    df = df.sort_values(by="Ticker")
    
    logging.info(f"Saving to {OUTPUT_PATH}...")
    try:
        df.to_excel(OUTPUT_PATH, index=False)
        logging.info("Done!")
    except Exception as e:
        logging.error(f"Failed to save Excel file: {e}")
        
if __name__ == "__main__":
    create_fast_excel()
