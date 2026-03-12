"""Test email sending independently."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

load_dotenv(project_root / ".env")


def test_email():
    print("=" * 50)
    print("TEST EMAIL")
    print("=" * 50)

    try:
        from tracker.email_service import send_html_email

        test_html = """
        <html><body>
        <h2>Test Email</h2>
        <p>This is a test from the debug skill.</p>
        <p>If you receive this, the email system is working!</p>
        </body></html>
        """

        print("\nSending test email...")
        success = send_html_email("DEBUG: Test Email", test_html)

        if success:
            print("\n[OK] Test email sent successfully!")
        else:
            print("\n[FAIL] Failed to send test email!")

        return success

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_email()
    sys.exit(0 if success else 1)
