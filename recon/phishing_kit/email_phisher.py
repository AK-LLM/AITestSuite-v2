import smtplib
from email.mime.text import MIMEText

SMTP = "smtp.your-lab.local"
USER = "phisher@your-lab.local"
PWD = "supersecret"
TARGET = "victim@target.com"

msg = MIMEText("Urgent: Please click this link to reset your password: http://evil.attacker/reset")
msg["Subject"] = "Security Alert"
msg["From"] = USER
msg["To"] = TARGET

with smtplib.SMTP(SMTP) as s:
    s.login(USER, PWD)
    s.send_message(msg)
    print("[+] Phishing email sent.")
