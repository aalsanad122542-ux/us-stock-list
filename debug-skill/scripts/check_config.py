"""Check all API configurations and settings."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")

REQUIRED_VARS = {
    "GEMINI_API_KEY": "Google Gemini AI",
    "SMTP_SERVER": "SMTP Server",
    "SMTP_PORT": "SMTP Port",
    "SENDER_EMAIL": "From Email",
    "SENDER_PASSWORD": "SMTP Password",
    "RECIPIENT_EMAIL": "To Email",
}

OPTIONAL_VARS = {
    "ALPACA_API_KEY": "Alpaca Trading API",
    "ALPACA_SECRET_KEY": "Alpaca Secret",
    "ALPHA_VANTAGE_KEY": "Alpha Vantage",
}


def check_config():
    print("=" * 50)
    print("CONFIGURATION CHECK")
    print("=" * 50)

    all_ok = True

    print("\n[REQUIRED]")
    for var, desc in REQUIRED_VARS.items():
        value = os.getenv(var, "").strip()
        if value:
            # Show masked value
            masked = (
                value[:4] + "*" * (len(value) - 8) + value[-4:]
                if len(value) > 8
                else "***"
            )
            print(f"  [OK] {var}: {masked}")
        else:
            print(f"  [MISSING] {var}: NOT SET ({desc})")
            all_ok = False

    print("\n[OPTIONAL]")
    for var, desc in OPTIONAL_VARS.items():
        value = os.getenv(var, "").strip()
        if value:
            masked = (
                value[:4] + "*" * (len(value) - 8) + value[-4:]
                if len(value) > 8
                else "***"
            )
            print(f"  [OK] {var}: {masked}")
        else:
            print(f"  [-] {var}: NOT SET ({desc})")

    print("\n" + "=" * 50)
    if all_ok:
        print("STATUS: All required config OK")
    else:
        print("STATUS: Missing required configuration!")
    print("=" * 50)

    return all_ok


if __name__ == "__main__":
    success = check_config()
    sys.exit(0 if success else 1)
