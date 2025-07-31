import os
import requests
import smtplib
from email.mime.text import MIMEText

# --- SLACK ALERTING ---
def send_slack_alert(message, webhook_url=None):
    webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("[alerting] No Slack webhook configured.")
        return False
    payload = {"text": message}
    r = requests.post(webhook_url, json=payload)
    if r.status_code == 200:
        print("[alerting] Slack alert sent.")
        return True
    else:
        print(f"[alerting] Slack alert failed: {r.text}")
        return False

# --- MS TEAMS ALERTING ---
def send_teams_alert(message, webhook_url=None):
    webhook_url = webhook_url or os.getenv("TEAMS_WEBHOOK_URL")
    if not webhook_url:
        print("[alerting] No Teams webhook configured.")
        return False
    payload = {"text": message}
    r = requests.post(webhook_url, json=payload)
    if r.status_code in [200, 201]:
        print("[alerting] Teams alert sent.")
        return True
    else:
        print(f"[alerting] Teams alert failed: {r.text}")
        return False

# --- DISCORD ALERTING ---
def send_discord_alert(message, webhook_url=None):
    webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("[alerting] No Discord webhook configured.")
        return False
    payload = {"content": message}
    r = requests.post(webhook_url, json=payload)
    if r.status_code == 204:
        print("[alerting] Discord alert sent.")
        return True
    else:
        print(f"[alerting] Discord alert failed: {r.text}")
        return False

# --- EMAIL ALERTING ---
def send_email_alert(subject, message, recipient, smtp_host=None, smtp_port=587, smtp_user=None, smtp_pass=None):
    smtp_host = smtp_host or os.getenv("SMTP_HOST")
    smtp_port = int(smtp_port or os.getenv("SMTP_PORT", 587))
    smtp_user = smtp_user or os.getenv("SMTP_USER")
    smtp_pass = smtp_pass or os.getenv("SMTP_PASS")
    sender = smtp_user
    if not all([smtp_host, smtp_user, smtp_pass, recipient]):
        print("[alerting] Email config incomplete.")
        return False
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(sender, [recipient], msg.as_string())
        print("[alerting] Email alert sent.")
        return True
    except Exception as e:
        print(f"[alerting] Email alert failed: {e}")
        return False

# --- SMS ALERTING (TWILIO) ---
def send_sms_alert(message, to_number, from_number=None, account_sid=None, auth_token=None):
    from_number = from_number or os.getenv("TWILIO_FROM")
    account_sid = account_sid or os.getenv("TWILIO_SID")
    auth_token = auth_token or os.getenv("TWILIO_AUTH")
    if not all([account_sid, auth_token, from_number, to_number]):
        print("[alerting] Twilio config incomplete.")
        return False
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    data = {
        "From": from_number,
        "To": to_number,
        "Body": message
    }
    r = requests.post(url, data=data, auth=(account_sid, auth_token))
    if r.status_code == 201:
        print("[alerting] SMS alert sent.")
        return True
    else:
        print(f"[alerting] SMS alert failed: {r.text}")
        return False

# --- MASTER ALERT ROUTER ---
def send_alert(
    message,
    level="CRITICAL",
    slack=True, teams=False, discord=False, email=None, sms=None,
    **kwargs
):
    # Always print for logging
    print(f"[alerting] {level} ALERT: {message}")
    ok = False
    if slack: ok |= send_slack_alert(message)
    if teams: ok |= send_teams_alert(message)
    if discord: ok |= send_discord_alert(message)
    if email: ok |= send_email_alert(f"[AI Suite {level}]", message, recipient=email)
    if sms: ok |= send_sms_alert(message, to_number=sms)
    return ok

# --- EXAMPLE CLI TEST USAGE ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Send alert to channel(s)")
    parser.add_argument("--msg", type=str, default="🚨 CRITICAL: Test finding from AI Test Suite")
    parser.add_argument("--slack", action="store_true")
    parser.add_argument("--teams", action="store_true")
    parser.add_argument("--discord", action="store_true")
    parser.add_argument("--email", type=str, default=None)
    parser.add_argument("--sms", type=str, default=None)
    args = parser.parse_args()
    send_alert(
        args.msg, level="CRITICAL",
        slack=args.slack,
        teams=args.teams,
        discord=args.discord,
        email=args.email,
        sms=args.sms
    )
