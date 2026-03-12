"""Run full daily analysis as dry-run with verbose output."""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

load_dotenv(project_root / ".env")

# Set up verbose logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


def dry_run():
    print("=" * 50)
    print("DRY RUN - Daily Analysis")
    print("=" * 50)
    print("This will run the full pipeline but not send email.\n")

    try:
        from tracker.stock_picker import get_next_n_stocks
        from tracker.fundamental_analyzer import fetch_stock_data
        from tracker.gemini_service import analyze_stock_ibkr

        # Step 1: Get stocks
        print("[1] Fetching stocks...")
        stocks = get_next_n_stocks(3)  # Only 3 for testing
        if not stocks:
            print("[FAIL] No stocks retrieved!")
            return False
        print(f"  Got: {[s['ticker'] for s in stocks]}")

        # Step 2: Load prompt
        print("\n[2] Loading instruction prompt...")
        prompt_file = project_root / "IBKR Instructions.md"
        with open(prompt_file, "r", encoding="utf-8") as f:
            instruction_prompt = f.read()[:500]  # First 500 chars
        print(f"  Loaded prompt ({len(instruction_prompt)} chars)")

        # Step 3: Analyze first stock only
        print("\n[3] Analyzing first stock...")
        stock = stocks[0]
        ticker = stock["ticker"]
        print(f"  Fetching data for {ticker}...")

        data = fetch_stock_data(ticker)
        if "error" in data:
            print(f"  [FAIL] Error: {data['error']}")
            return False

        print(f"  Running AI analysis...")
        result = analyze_stock_ibkr(data, instruction_prompt)

        if "Failed" in result:
            print(f"  [FAIL] AI failed: {result[:200]}")
            return False

        print(f"  [OK] Analysis completed!")
        print("\n" + "-" * 50)
        print("RESULT PREVIEW:")
        print("-" * 50)
        print(result[:800] + "..." if len(result) > 800 else result)

        print("\n[OK] Dry run completed successfully!")
        return True

    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = dry_run()
    sys.exit(0 if success else 1)
