"""
fundamental_analyzer.py
Fetches stock fundamentals via yfinance and generates AI analysis via Ollama.
Applies the fundamental-analysis skill scoring methodology.
"""

import os
import time
import logging
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Try to import cache, fallback to no-op if not available
try:
    from tracker.cache import cache, get_cached_stock_data, cache_stock_data
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    def get_cached_stock_data(ticker):
        return None
    def cache_stock_data(ticker, data, ttl):
        pass

_BATCH_DELAY = float(os.getenv("OLLAMA_BATCH_DELAY_SECONDS", "1"))

def _safe_val(val, fmt=".2f", fallback="N/A"):
    """Safely format a numeric value."""
    try:
        if val is None:
            return fallback
        return format(float(val), fmt)
    except (TypeError, ValueError):
        return fallback


def fetch_stock_data(ticker: str) -> dict:
    """
    Fetch key fundamentals from yfinance for a given ticker.
    Returns a dict with all key metrics, or error info.
    Uses caching to improve performance.
    """
    # Check cache first (5 minute TTL)
    if CACHE_AVAILABLE:
        cached = get_cached_stock_data(ticker)
        if cached:
            logger.info(f"  [{ticker}] Using cached data")
            return cached
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
            logger.warning(f"  [{ticker}] No price data from yfinance")
            return {"ticker": ticker, "error": "No data available"}

        price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
        prev_close = info.get("previousClose") or price
        day_change_pct = ((price - prev_close) / prev_close * 100) if prev_close else 0

        data = {
            "ticker": ticker,
            "company_name": info.get("longName", ticker),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "country": info.get("country", "N/A"),
            "website": info.get("website", ""),
            "description": (info.get("longBusinessSummary", "") or "")[:400],
            # Price
            "price": _safe_val(price),
            "prev_close": _safe_val(prev_close),
            "day_change_pct": _safe_val(day_change_pct),
            "week_52_high": _safe_val(info.get("fiftyTwoWeekHigh")),
            "week_52_low": _safe_val(info.get("fiftyTwoWeekLow")),
            "market_cap_b": _safe_val((info.get("marketCap") or 0) / 1e9, ".1f"),
            # Valuation
            "pe_ratio": _safe_val(info.get("trailingPE")),
            "forward_pe": _safe_val(info.get("forwardPE")),
            "pb_ratio": _safe_val(info.get("priceToBook")),
            "ps_ratio": _safe_val(info.get("priceToSalesTrailing12Months")),
            "ev_ebitda": _safe_val(info.get("enterpriseToEbitda")),
            "peg_ratio": _safe_val(info.get("pegRatio")),
            # Profitability
            "revenue_b": _safe_val((info.get("totalRevenue") or 0) / 1e9, ".1f"),
            "gross_margin": _safe_val((info.get("grossMargins") or 0) * 100, ".1f"),
            "operating_margin": _safe_val((info.get("operatingMargins") or 0) * 100, ".1f"),
            "net_margin": _safe_val((info.get("profitMargins") or 0) * 100, ".1f"),
            "roe": _safe_val((info.get("returnOnEquity") or 0) * 100, ".1f"),
            "roa": _safe_val((info.get("returnOnAssets") or 0) * 100, ".1f"),
            # Growth
            "revenue_growth": _safe_val((info.get("revenueGrowth") or 0) * 100, ".1f"),
            "earnings_growth": _safe_val((info.get("earningsGrowth") or 0) * 100, ".1f"),
            "eps_ttm": _safe_val(info.get("trailingEps")),
            "eps_forward": _safe_val(info.get("forwardEps")),
            # Balance Sheet
            "debt_equity": _safe_val(info.get("debtToEquity")),
            "current_ratio": _safe_val(info.get("currentRatio")),
            "quick_ratio": _safe_val(info.get("quickRatio")),
            "free_cash_flow_b": _safe_val((info.get("freeCashflow") or 0) / 1e9, ".2f"),
            # Dividends
            "dividend_yield": _safe_val((info.get("dividendYield") or 0) * 100, ".2f"),
            "payout_ratio": _safe_val((info.get("payoutRatio") or 0) * 100, ".1f"),
            # Analyst
            "analyst_rating": info.get("recommendationKey", "N/A").upper(),
            "target_price": _safe_val(info.get("targetMeanPrice")),
            "num_analysts": str(info.get("numberOfAnalystOpinions", "N/A")),
            "beta": _safe_val(info.get("beta")),
        }
        return data

    except Exception as e:
        logger.error(f"  [{ticker}] yfinance error: {e}")
        return {"ticker": ticker, "error": str(e)}
    
    # Cache the result for 5 minutes
    if CACHE_AVAILABLE:
        cache_stock_data(ticker, data, ttl=300)
    
    return data


def _score_stock(data: dict) -> tuple[float, str]:
    """
    Apply a simplified fundamental-analysis scoring framework.
    Returns (score 1-10, signal label).
    """
    score = 5.0
    notes = []
    
    config_path = os.path.join(os.path.dirname(__file__), "scoring_config.json")
    try:
        import json
        with open(config_path, "r") as f:
            cfg = json.load(f)
    except Exception as e:
        logger.warning(f"Could not load scoring_config.json, using defaults: {e}")
        cfg = {
            "pe_ratio": {"low_min": 0, "low_max": 15, "low_score": 1.5, "fair_min": 15, "fair_max": 25, "fair_score": 0.5, "high_min": 40, "high_score": -1.0},
            "revenue_growth": {"high_min": 20, "high_score": 1.5, "moderate_min": 10, "moderate_score": 0.5, "declining_max": 0, "declining_score": -1.0},
            "net_margin": {"high_min": 20, "high_score": 1.0, "moderate_min": 10, "moderate_score": 0.5, "unprofitable_max": 0, "unprofitable_score": -1.5},
            "debt_equity": {"low_max": 50, "low_score": 0.5, "high_min": 200, "high_score": -0.5},
            "roe": {"high_min": 20, "high_score": 0.5}
        }

    # P/E check
    try:
        pe = float(data.get("pe_ratio", 0))
        pe_cfg = cfg.get("pe_ratio", {})
        if pe_cfg.get("low_min", 0) < pe < pe_cfg.get("low_max", 15):
            score += pe_cfg.get("low_score", 1.5); notes.append("Low P/E")
        elif pe_cfg.get("fair_min", 15) <= pe <= pe_cfg.get("fair_max", 25):
            score += pe_cfg.get("fair_score", 0.5); notes.append("Fair P/E")
        elif pe > pe_cfg.get("high_min", 40):
            score += pe_cfg.get("high_score", -1.0); notes.append("High P/E")
    except: pass

    # Revenue growth
    try:
        rg = float(data.get("revenue_growth", 0))
        rg_cfg = cfg.get("revenue_growth", {})
        if rg > rg_cfg.get("high_min", 20): score += rg_cfg.get("high_score", 1.5); notes.append("High growth")
        elif rg > rg_cfg.get("moderate_min", 10): score += rg_cfg.get("moderate_score", 0.5); notes.append("Moderate growth")
        elif rg < rg_cfg.get("declining_max", 0): score += rg_cfg.get("declining_score", -1.0); notes.append("Declining revenue")
    except: pass

    # Net margin
    try:
        nm = float(data.get("net_margin", 0))
        nm_cfg = cfg.get("net_margin", {})
        if nm > nm_cfg.get("high_min", 20): score += nm_cfg.get("high_score", 1.0); notes.append("High margin")
        elif nm > nm_cfg.get("moderate_min", 10): score += nm_cfg.get("moderate_score", 0.5)
        elif nm < nm_cfg.get("unprofitable_max", 0): score += nm_cfg.get("unprofitable_score", -1.5); notes.append("Unprofitable")
    except: pass

    # Debt/Equity
    try:
        de = float(data.get("debt_equity", 0))
        de_cfg = cfg.get("debt_equity", {})
        if de < de_cfg.get("low_max", 50): score += de_cfg.get("low_score", 0.5); notes.append("Low debt")
        elif de > de_cfg.get("high_min", 200): score += de_cfg.get("high_score", -0.5); notes.append("High debt")
    except: pass

    # ROE
    try:
        roe = float(data.get("roe", 0))
        roe_cfg = cfg.get("roe", {})
        if roe > roe_cfg.get("high_min", 20): score += roe_cfg.get("high_score", 0.5)
    except: pass

    score = max(1.0, min(10.0, score))

    if score >= 8.5:   signal = "STRONG BUY 🟢"
    elif score >= 7.0: signal = "BUY 🟩"
    elif score >= 5.5: signal = "HOLD 🟡"
    elif score >= 4.0: signal = "SELL 🟥"
    else:              signal = "STRONG SELL 🔴"

    return round(score, 1), signal


def generate_ai_analysis(data: dict, video_context: str = "") -> dict:
    """"
    Use Gemini to generate an investment thesis and risk summary for the stock.
    Returns {thesis, risks, summary} or fallback if Gemini unavailable.
    """
    try:
        from tracker.gemini_service import analyze_stock
        return analyze_stock(data)
    except Exception as e:
        logger.error(f"  [{data.get('ticker', '?')}] Gemini error: {e}")
        return {
            "thesis": f"AI analysis unavailable: {str(e)[:100]}",
            "risks": "N/A",
            "summary": "Error"
        }


def analyze_ticker(ticker: str, video_context: str = "", skip_ai: bool = False) -> dict:
    """
    Full analysis pipeline for one ticker.
    Returns combined fundamental data + AI analysis + scoring.
    """
    logger.info(f"  Analyzing {ticker}...")
    data = fetch_stock_data(ticker)

    if "error" in data:
        return {**data, "score": 0, "signal": "N/A", "ai": {"thesis": "Data unavailable", "risks": "N/A", "summary": ""}}

    score, signal = _score_stock(data)
    data["score"] = score
    data["signal"] = signal
    data["video_context"] = video_context

    if not skip_ai:
        time.sleep(_BATCH_DELAY)  # Respect rate limits
        ai = generate_ai_analysis(data, video_context)
        data["ai"] = ai

    return data


def analyze_all_tickers(global_tickers: list[dict], videos: list[dict] = None, max_stocks: int = 20) -> list[dict]:
    """
    Analyze top N tickers from global_tickers list.
    Returns list of full analysis dicts.
    """
    # Take top N by mention count (already sorted)
    top = global_tickers[:max_stocks]
    results = []
    
    video_map = {v.get("video_id"): v for v in videos} if videos else {}
    stocks_for_batch_ai = []
    
    for entry in top:
        ticker = entry["ticker"]
        
        # Build video context
        context_parts = []
        for v_stub in entry.get("videos", []):
            vid_id = v_stub.get("video_id")
            full_video = video_map.get(vid_id, {})
            transcript = full_video.get("transcript", "")
            if transcript:
                # Take up to 2500 chars per video for context
                snippet = transcript[:2500]
                context_parts.append(f"From video '{full_video.get('title', 'Unknown')}':\n{snippet}...")
        
        video_context = "\n\n".join(context_parts)
        
        analysis = analyze_ticker(ticker, video_context=video_context, skip_ai=True)
        # Merge with video source info
        analysis["source_videos"] = entry.get("videos", [])
        analysis["total_mentions"] = entry.get("total_mentions", 1)
        results.append(analysis)
        
        if "error" not in analysis:
            stocks_for_batch_ai.append(analysis)

    logger.info(f"  Running batched AI analysis on {len(stocks_for_batch_ai)} stocks...")
    if stocks_for_batch_ai:
        try:
            from tracker.gemini_service import analyze_stocks_batch
            ai_results = analyze_stocks_batch(stocks_for_batch_ai)
        except Exception as e:
            logger.error(f"  Batched Gemini error: {e}")
            ai_results = {}
    else:
        ai_results = {}

    for res in results:
        ticker = res.get("ticker", "?")
        if ticker in ai_results:
            res["ai"] = ai_results[ticker]
        else:
            res["ai"] = {
                "thesis": "AI analysis skipped or unavailable",
                "risks": "N/A",
                "summary": "Error"
            }

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = analyze_ticker("AAPL")
    import json
    print(json.dumps(result, indent=2))
