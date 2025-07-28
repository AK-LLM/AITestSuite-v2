import random

UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "curl/8.0.1",
    "Wget/1.21.1",
    "python-requests/2.31.0",
    "Go-http-client/2.0"
]

def get_ua():
    return random.choice(UAS)

# Example usage with requests:
# import requests
# ua = get_ua()
# requests.get("https://ifconfig.me", headers={"User-Agent": ua})
