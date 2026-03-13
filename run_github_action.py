"""
GitHub Actions entry point for daily stock email.
"""

import sys

sys.path.insert(0, ".")

try:
    from tracker.daily_custom_analysis import run_daily_analysis

    success = run_daily_analysis(num_stocks=5)
    if success:
        print("SUCCESS: Daily email sent")
        sys.exit(0)
    else:
        print("FAILED: Email not sent")
        sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
