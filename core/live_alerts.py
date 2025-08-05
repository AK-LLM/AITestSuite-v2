import os, time, requests, json

LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
ALERTS_OUT = os.path.join(LOGS_DIR, "live_alerts.json")

FEEDS = [
    "https://api.abuseipdb.com/api/v2/blacklist",
    "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
    "https://www.reddit.com/r/netsec/new.json",
]

def poll_feeds():
    alerts = []
    for url in FEEDS:
        try:
            resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            if "json" in resp.headers.get("Content-Type", ""):
                data = resp.json()
                alerts.append({"feed": url, "data": data})
        except Exception as e:
            alerts.append({"feed": url, "error": str(e)})
    with open(ALERTS_OUT, "w") as f:
        json.dump(alerts, f, indent=2)
    print(f"[live_alerts] Updated {len(alerts)} feeds.")
    return alerts

if __name__ == "__main__":
    poll_feeds()
