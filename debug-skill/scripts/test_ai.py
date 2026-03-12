"""Test AI analysis with sample stock data."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

load_dotenv(project_root / ".env")


def test_ai():
    print("=" * 50)
    print("TEST AI ANALYSIS")
    print("=" * 50)

    # Sample stock data for testing
    sample_stock = {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "price": 178.50,
        "market_cap_b": "2800B",
        "pe_ratio": 28.5,
        "forward_pe": 25.2,
        "pb_ratio": 45.0,
        "revenue_growth": 8.5,
        "net_margin": 24.5,
        "roe": 150.0,
        "debt_equity": 1.8,
        "free_cash_flow_b": "110B",
        "dividend_yield": 0.55,
        "analyst_rating": "Strong Buy",
        "target_price": 200.0,
        "beta": 1.2,
        "week_52_high": 199.62,
        "week_52_low": 143.90,
        "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
    }

    try:
        from tracker.gemini_service import analyze_stock_ibkr

        instruction_prompt = """You are an expert financial analyst. Provide analysis in markdown format."""

        print(
            f"\nAnalyzing {sample_stock['ticker']} ({sample_stock['company_name']})..."
        )

        result = analyze_stock_ibkr(sample_stock, instruction_prompt)

        print("\n" + "-" * 50)
        print("AI RESPONSE:")
        print("-" * 50)
        print(result[:1000] if len(result) > 1000 else result)

        if "Failed" in result:
            print("\n[FAIL] AI analysis failed!")
            return False
        else:
            print("\n[OK] AI analysis completed!")
            return True

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_ai()
    sys.exit(0 if success else 1)
