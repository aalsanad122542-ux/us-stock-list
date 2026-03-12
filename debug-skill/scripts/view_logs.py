"""View recent error logs from the application."""

import os
import sys
from pathlib import Path


def view_logs():
    print("=" * 50)
    print("VIEW LOGS")
    print("=" * 50)

    # Common log locations
    project_root = Path(__file__).parent.parent.parent

    # Check for log files
    log_files = [
        project_root / "debug.log",
        project_root / "app.log",
        project_root / "logs" / "app.log",
    ]

    found_logs = [f for f in log_files if f.exists()]

    if not found_logs:
        # Show last email scheduler run
        print("\nNo log files found. Showing recent Python errors:")
        print("(This feature works best when logging is configured)")
        print("\nCheck the scheduler output by running:")
        print("  python run_email_scheduler.py")
        return

    for log_file in found_logs:
        print(f"\n--- {log_file.name} (last 50 lines) ---")
        try:
            lines = log_file.read_text(encoding="utf-8").splitlines()
            for line in lines[-50:]:
                print(line)
        except Exception as e:
            print(f"Error reading: {e}")


if __name__ == "__main__":
    view_logs()
