"""
daily_custom_analysis.py
Runner script that coordinates picking 5 stocks, analyzing them with the IBKR prompt via Gemini,
and emailing the results.
"""

import os
import sys
import time
import logging
from datetime import datetime
import markdown

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tracker.stock_picker import get_next_n_stocks
from tracker.fundamental_analyzer import fetch_stock_data
from tracker.gemini_service import analyze_stock_ibkr as gemini_analyze
from tracker.apifreellm_service import analyze_stock_ibkr as apifreellm_analyze
from tracker.email_service import send_html_email


def analyze_stock_with_fallback(stock_data: dict, instruction_prompt: str) -> str:
    """Try Gemini first, fall back to ApiFreeLLM on failure."""
    try:
        result = gemini_analyze(stock_data, instruction_prompt)
        if result and "Failed" not in result and "error" not in result.lower():
            return result
    except Exception as e:
        logger.warning(f"Gemini failed: {e}")

    logger.info("Falling back to ApiFreeLLM...")
    try:
        result = apifreellm_analyze(stock_data, instruction_prompt)
        return result
    except Exception as e:
        logger.error(f"ApiFreeLLM also failed: {e}")
        return f"<h3>All AI services failed. Gemini error, ApiFreeLLM error: {e}</h3>"


logger = logging.getLogger(__name__)

_PROMPT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "IBKR Instructions.md"
)


def load_prompt() -> str:
    try:
        with open(_PROMPT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Could not load IBKR Instructions.md: {e}")
        return "You are an expert financial analyst."


def run_daily_analysis(num_stocks: int = 5):
    """
    Main workflow function for the daily stock email.
    """
    logger.info(f"Starting daily email analysis for {num_stocks} stocks...")

    # 1. Get next stocks
    stocks = get_next_n_stocks(num_stocks)
    if not stocks:
        logger.warning("No stocks retrieved to analyze.")
        return False

    logger.info(f"Selected: {[s['ticker'] for s in stocks]}")

    # 2. Load the prompt template
    instruction_prompt = load_prompt()

    # 3. Analyze each stock
    analysis_results = []

    for stock in stocks:
        ticker = stock["ticker"]
        logger.info(f"Fetching data and analyzing {ticker}...")

        # Bring in fundamental data
        data = fetch_stock_data(ticker)
        if "error" in data:
            logger.warning(
                f"Error fetching fundamental data for {ticker}: {data['error']}"
            )
            analysis_results.append(
                {
                    "ticker": ticker,
                    "company": stock["company"],
                    "markdown": f"## {ticker} Analysis\nData fetch failed: {data['error']}",
                }
            )
            continue

        # Call Gemini specific IBKR wrapper
        try:
            raw_markdown = analyze_stock_with_fallback(data, instruction_prompt)

            # Parse the rating and compliance using regex for robustness
            import re

            fundamental_rating = "N/A"
            shariaa = "N/A"

            rating_match = re.search(
                r"Fundamental Rating:\s*(.+)", raw_markdown, re.IGNORECASE
            )
            if rating_match:
                fundamental_rating = rating_match.group(1).strip()

            shariaa_match = re.search(
                r"Shariaa Compliant:\s*(.+)", raw_markdown, re.IGNORECASE
            )
            if shariaa_match:
                shariaa = shariaa_match.group(1).strip()

            # Clean up the output so it doesn't show the raw rating text twice
            clean_markdown = re.sub(
                r"Fundamental Rating:.*?\n", "", raw_markdown, flags=re.IGNORECASE
            )
            clean_markdown = re.sub(
                r"Shariaa Compliant:.*?\n", "", clean_markdown, flags=re.IGNORECASE
            )

            analysis_results.append(
                {
                    "ticker": ticker,
                    "company": stock["company"],
                    "rating": fundamental_rating,
                    "shariaa": shariaa,
                    "markdown": f"## {ticker} ({stock['company']}) Analysis\n\n{clean_markdown.strip()}",
                }
            )
        except Exception as e:
            logger.error(f"Gemini generation error for {ticker}: {e}")
            analysis_results.append(
                {
                    "ticker": ticker,
                    "company": stock["company"],
                    "rating": "Error",
                    "shariaa": "Error",
                    "markdown": f"## {ticker} Analysis\nGemini generation failed: {e}",
                }
            )

        time.sleep(2)  # Give the LLM breathing room

    # 4. Format the final combined email HTML
    date_str = datetime.now().strftime("%Y-%m-%d")

    html_parts = [
        f"<html><body style='font-family: Arial, sans-serif; line-height: 1.6; color: #333;'>"
        f"<h1 style='color: #2c3e50;'>Daily Stock Analysis Report ({date_str})</h1>"
        f"<p>Automated analysis of {num_stocks} selected US stocks using the IBKR Prompt.</p>"
        f"<h2>Executive Summary</h2>"
        f"<table style='width: 100%; border-collapse: collapse; margin-bottom: 25px;'>"
        f"<thead><tr style='background-color: #f2f2f2;'>"
        f"<th style='border: 1px solid #ddd; padding: 8px; text-align: left;'>Ticker</th>"
        f"<th style='border: 1px solid #ddd; padding: 8px; text-align: left;'>Company</th>"
        f"<th style='border: 1px solid #ddd; padding: 8px; text-align: center;'>Fundamental Rating</th>"
        f"<th style='border: 1px solid #ddd; padding: 8px; text-align: center;'>Shariaa Compliant</th>"
        f"</tr></thead><tbody>"
    ]

    # Add summary table rows
    for res in analysis_results:
        html_parts.append(f"<tr>")
        html_parts.append(
            f"<td style='border: 1px solid #ddd; padding: 8px;'><b>{res.get('ticker', '')}</b></td>"
        )
        html_parts.append(
            f"<td style='border: 1px solid #ddd; padding: 8px;'>{res.get('company', '')}</td>"
        )
        html_parts.append(
            f"<td style='border: 1px solid #ddd; padding: 8px; text-align: center;'>{res.get('rating', 'N/A')}</td>"
        )
        html_parts.append(
            f"<td style='border: 1px solid #ddd; padding: 8px; text-align: center;'>{res.get('shariaa', 'N/A')}</td>"
        )
        html_parts.append(f"</tr>")

    html_parts.append("</tbody></table><hr/>")

    # Convert markdown analysis cleanly
    for res in analysis_results:
        converted = markdown.markdown(res["markdown"], extensions=["tables"])
        html_parts.append(converted)
        html_parts.append("<br/><hr/><br/>")

    html_parts.append("</body></html>")
    full_html = "".join(html_parts)

    # 5. Send the email
    logger.info("Sending email report...")
    subject = f"Your Daily Top {num_stocks} Stock Analysis - {date_str}"

    success = send_html_email(subject, full_html)

    if success:
        logger.info("Daily stock email sent successfully.")
    else:
        logger.error("Failed to send the daily stock email.")

    return success


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_daily_analysis(5)
