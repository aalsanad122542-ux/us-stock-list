"""
email_service.py
Handles sending the daily stock analysis HTML reports via email.
"""

import os
import smtplib
from email.message import EmailMessage
from email.utils import formatdate
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def send_html_email(subject: str, html_content: str, recipient: str = None) -> bool:
    """
    Sends an HTML email using the configured SMTP server.
    Falls back to environment variables if recipient is not provided.
    """
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    recipient_email = recipient or os.getenv("RECIPIENT_EMAIL")

    if not all([sender_email, sender_password, recipient_email]):
        logger.error("Email configuration missing. Please check .env file.")
        return False

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Date'] = formatdate(localtime=True)
    msg.set_content("Please enable HTML to view this message.")
    msg.add_alternative(html_content, subtype='html')

    try:
        logger.info(f"Connecting to SMTP server {smtp_server}:{smtp_port}...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            
        logger.info(f"Successfully sent email to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

if __name__ == "__main__":
    # Test the email config
    logging.basicConfig(level=logging.INFO)
    test_html = "<h1>Test Email</h1><p>If you see this, the email configuration is working.</p>"
    send_html_email("YTStock Test Email", test_html)
