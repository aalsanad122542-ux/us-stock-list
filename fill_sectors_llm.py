import pandas as pd
import logging
import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

FILE_PATH = r"c:\Users\LENOVO\Desktop\antigravity 30-01\US Stock List\us_listed_stocks.xlsx"

# The Google GenAI SDK requires a GEMINI_API_KEY environment variable. 
# Make sure this is in your .env file or environment!
# e.g., os.environ['GEMINI_API_KEY'] = "your_key_here"

def resolve_unknowns_with_llm():
    if not os.path.exists(FILE_PATH):
        logging.error(f"File not found: {FILE_PATH}")
        return
        
    logging.info(f"Loading {FILE_PATH}...")
    df = pd.read_excel(FILE_PATH)
    
    ticker_col = next((col for col in df.columns if str(col).lower() in ['ticker', 'symbol', 'stock']), None)
    sector_col = next((col for col in df.columns if str(col).lower() == 'sector'), None)
    
    unknown_mask = df[sector_col].isna() | df[sector_col].astype(str).str.lower().isin(['nan', 'unknown', ''])
    unknown_tickers = df.loc[unknown_mask, ticker_col].astype(str).str.strip().tolist()
    
    if not unknown_tickers:
        logging.info("No unknown sectors left to resolve.")
        return
        
    logging.info(f"Preparing to send {len(unknown_tickers)} obscure tickers to Gemini for sector classification.")
    
    # Check if API Key exists
    if not os.getenv("GEMINI_API_KEY"):
        logging.error("GEMINI_API_KEY not found in environment. Please add it to your .env file.")
        return
        
    # Initialize the client
    try:
        client = genai.Client()
    except Exception as e:
        logging.error(f"Failed to initialize Gemini Client: {e}")
        return
        
    prompt = f"""
    You are an expert financial analyst. 
    I have a list of highly obscure or recently delisted US stock tickers that traditional APIs failed to classify.
    
    For each ticker, please map it to the most likely GICS Sector (e.g., 'Financial Services', 'Healthcare', 'Technology', 'Industrials', 'Consumer Cyclical', 'Basic Materials', 'Energy', 'Real Estate', 'Utilities', 'Communication Services', 'Consumer Defensive', or 'ETF').
    If it is a SPAC, warrant, or blank-check company, classify it as 'Financial'.
    If you are absolutely unsure or it represents a completely dead/unknown instrument, output 'Unknown'.
    
    Return the result EXCLUSIVELY as a valid JSON object mapping the ticker to its sector. Do not output markdown code blocks or any other explanation text. Just the raw JSON.
    
    Tickers to classify:
    {json.dumps(unknown_tickers)}
    """
    
    logging.info("Querying Gemini 2.5 Flash for bulk classification...")
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0
            )
        )
        
        # Parse the JSON response
        result_text = response.text.strip()
        # Clean up in case the model ignored instructions and wrapped in markdown
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        sector_map = json.loads(result_text)
        logging.info(f"Gemini successfully returned mapped {len(sector_map)} tickers.")
        
        # Apply the mapping
        mapped_count = 0
        for idx, row in df[unknown_mask].iterrows():
            ticker = str(row[ticker_col]).strip()
            if ticker in sector_map:
                new_sec = sector_map[ticker]
                if new_sec != 'Unknown':
                    df.at[idx, sector_col] = new_sec
                    mapped_count += 1
                    logging.info(f"LLM MATCH: {ticker} -> {new_sec}")
                    
        logging.info(f"Applied {mapped_count} sector resolutions from LLM.")
        
        remaining_unknown = (df[sector_col].isna() | df[sector_col].astype(str).str.lower().isin(['nan', 'unknown', ''])).sum()
        logging.info(f"Remaining unknown completely: {remaining_unknown} out of {len(df)}")
        
        logging.info("Saving...")
        with pd.ExcelWriter(FILE_PATH, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='US Stocks')
        logging.info(f"Successfully saved to {FILE_PATH}!")
        
    except Exception as e:
        logging.error(f"Gemini API request failed: {e}")

if __name__ == "__main__":
    import asyncio
    resolve_unknowns_with_llm()
