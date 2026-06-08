#!/usr/bin/env python3
"""Send a test email to the local Mailpit SMTP server.

Mimics what the Mendix Email Connector does so you can confirm Mailpit is
reachable before wiring it into Mendix.

Usage:
    python3 scripts/send-test-email.py
    python3 scripts/send-test-email.py --host localhost --port 1025
    MP_SMTP_PORT=2025 python3 scripts/send-test-email.py
"""

import argparse
import os
import smtplib
import sys
from datetime import datetime
from email.message import EmailMessage


def main() -> int:
    parser = argparse.ArgumentParser(description="Send a test email to Mailpit.")
    parser.add_argument("--host", default=os.environ.get("MP_SMTP_HOST", "localhost"))
    parser.add_argument(
        "--port", type=int, default=int(os.environ.get("MP_SMTP_PORT", "1025"))
    )
    parser.add_argument("--from", dest="sender", default="dev@example.test")
    parser.add_argument("--to", default="inbox@example.test")
    parser.add_argument("--user", default="test", help="SMTP username (Mailpit accepts any)")
    parser.add_argument("--password", default="test", help="SMTP password (Mailpit accepts any)")
    parser.add_argument("--no-auth", action="store_true", help="Skip SMTP AUTH")
    args = parser.parse_args()

    msg = EmailMessage()
    msg["From"] = args.sender
    msg["To"] = args.to
    msg["Subject"] = f"Mailpit test {datetime.now():%Y-%m-%d %H:%M:%S}"
    msg.set_content(
        "Plain-text body: if you can read this in Mailpit, SMTP works.\n"
    )
    msg.add_alternative(
        "<h2>Mailpit test</h2>"
        "<p>If you can read this in Mailpit, <strong>SMTP works</strong>.</p>",
        subtype="html",
    )

    print(f"Connecting to {args.host}:{args.port} ...")
    try:
        with smtplib.SMTP(args.host, args.port, timeout=10) as smtp:
            smtp.ehlo()
            if not args.no_auth:
                try:
                    smtp.login(args.user, args.password)
                except smtplib.SMTPException as exc:
                    print(f"  (AUTH skipped: {exc})")
            smtp.send_message(msg)
    except (OSError, smtplib.SMTPException) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        print("Is Mailpit running?  ->  docker compose up -d", file=sys.stderr)
        return 1

    print("Sent. Open the Mailpit UI to view it: http://localhost:8025")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
