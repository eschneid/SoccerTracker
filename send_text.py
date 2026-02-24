#!/usr/bin/env python3
"""
Send SMS via Email Gateway

This script sends SMS messages via email-to-SMS gateways (Verizon, AT&T, T-Mobile, etc.)
Much cheaper than Twilio - uses your existing email account!

Usage:
    python send_text.py "Your message here"
    echo "Your message" | python send_text.py
"""

import argparse
import smtplib
import sys
from email.message import EmailMessage
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configuration from .env
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMS_RECIPIENTS = os.getenv("SMS_RECIPIENTS", "")
SMS_SEND_MODE = os.getenv("SMS_SEND_MODE", "individual")


def send_text(message):
    """Send SMS via email gateway to one or more recipients"""
    
    # Validate configuration
    if not EMAIL_FROM or not EMAIL_PASSWORD:
        print("❌ Missing EMAIL_FROM or EMAIL_PASSWORD in .env file")
        print("Please configure your email credentials.")
        return False
    
    if not SMS_RECIPIENTS:
        print("❌ No SMS_RECIPIENTS configured in .env file")
        return False
    
    print("📩 Sending text message...")
    
    # Handle single number or comma-separated list
    if isinstance(SMS_RECIPIENTS, str):
        recipients = [num.strip() for num in SMS_RECIPIENTS.split(',') if num.strip()]
    elif isinstance(SMS_RECIPIENTS, list):
        recipients = SMS_RECIPIENTS
    else:
        recipients = [SMS_RECIPIENTS]
    
    if not recipients:
        print("❌ No recipients configured")
        return False
    
    send_mode = SMS_SEND_MODE.lower() if SMS_SEND_MODE else "individual"
    
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
            
            if send_mode == "group":
                # Group mode: All recipients see each other (like group text)
                msg = EmailMessage()
                msg["From"] = EMAIL_FROM
                msg["To"] = ", ".join(recipients)
                msg["Subject"] = ""
                msg.set_content(message)
                smtp.send_message(msg)
                print(f"✅ Text sent to {len(recipients)} recipient(s) [GROUP MODE - all visible]")
            else:
                # Individual mode: Send separately (BCC-style, recipients hidden)
                for recipient in recipients:
                    msg = EmailMessage()
                    msg["From"] = EMAIL_FROM
                    msg["To"] = recipient
                    msg["Subject"] = ""
                    msg.set_content(message)
                    smtp.send_message(msg)
                print(f"✅ Text sent to {len(recipients)} recipient(s) [INDIVIDUAL MODE - hidden from each other]")
        
        return True
        
    except Exception as e:
        print(f"❌ Error sending text: {e}")
        return False


def main():
    """Main function"""
    print("📩 Preparing to send text message...")
    
    parser = argparse.ArgumentParser(
        description="Send an SMS via email-to-SMS gateway (supports multiple carriers)"
    )
    parser.add_argument(
        "message",
        nargs="?",
        help="Text message to send (optional if piping from stdin)"
    )
    args = parser.parse_args()
    
    if args.message:
        message = args.message
    else:
        message = sys.stdin.read().strip()
    
    if not message:
        print("❌ No message provided", file=sys.stderr)
        sys.exit(1)
    
    # Keep SMS short (160 characters is standard SMS limit)
    if len(message) > 160:
        print(f"⚠️  Message truncated from {len(message)} to 160 characters")
        message = message[:160]
    
    success = send_text(message)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
