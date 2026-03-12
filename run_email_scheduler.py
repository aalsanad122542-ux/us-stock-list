"""
Daily Stock Email Scheduler
Runs the stock analysis email pipeline on a schedule.
"""

import os
import sys
import time
import logging
import schedule
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

EMAIL_TIMES_UTC = ["04:00", "08:00", "12:00", "16:00", "20:", "00:00"]


def run_email():
    """Run the daily stock analysis email."""
    try:
        logger.info("Triggering daily stock analysis email...")
        from tracker.daily_custom_analysis import run_daily_analysis

        success = run_daily_analysis(num_stocks=5)
        if success:
            logger.info("Daily stock email sent successfully.")
        else:
            logger.error("Daily stock email failed.")
    except Exception as e:
        logger.error(f"Email job crashed: {e}", exc_info=True)


if __name__ == "__main__":
    logger.info("Email scheduler starting...")
    logger.info(f"Scheduled times (UTC): {EMAIL_TIMES_UTC}")

    for t in EMAIL_TIMES_UTC:
        schedule.every().day.at(t).do(run_email)
        logger.info(f"Scheduled at {t} UTC")

    logger.info("Scheduler running...")

    if os.getenv("FORCE_RUN", "").lower() == "true":
        logger.info("FORCE_RUN detected, running now...")
        run_email()

    while True:
        try:
            schedule.run_pending()
            time.sleep(30)
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(60)
