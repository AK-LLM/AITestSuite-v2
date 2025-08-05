import os, json, requests, time, re
from bs4 import BeautifulSoup

LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
OUT_JSON = os.path.join(LOGS_DIR, "darkweb_harvest.json")

TOR_PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}

DARK_SOURCES = [
    # Example .onion, pastebin, breached DBs, threat feeds
    "http://msydqstlz2kzerdg.onion",    # Dread Forum
    "http://zlal32teyptf4tvi.onion",    # The Hub
    "https://ghostbin.com/pastebin",
    "https://pastebin.com/archive",
    # Discord/Telegram and others: extend as needed
]

KEY_PATTERNS = [
    r"(jailbreak|prompt injection|flag|\bctf\b|bypass|payload|openai|llm|jailbreak code)",
    r"(leaked creds?|credit card|password dump|access token)",
]

def fetch_url(url, use_tor=True):
    try:
        resp = requests.get(url, proxies=TOR_PROXIES if use_tor else None, timeout=30)
        if resp.status_code == 200:
            return resp.text
    except Exception as e:
        print(f"[darkweb_harvester] Error fetching {url}: {e}")
    return None

def extract_claims(text):
    claims = []
    for pat in KEY_PATTERNS:
        for m in re.finditer(pat, text, re.I):
            snippet = text[max(0, m.start()-60):m.end()+60]
            claims.append({"pattern": pat, "context": snippet, "time": time.time()})
    return claims

def harvest_all():
    results = []
    for src in DARK_SOURCES:
        print(f"[darkweb_harvester] Harvesting {src}")
        html = fetch_url(src, use_tor=src.endswith(".onion"))
        if html:
            soup = BeautifulSoup(html, "lxml")
            text = soup.get_text()
            results.extend(extract_claims(text))
    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[darkweb_harvester] Done. Claims: {len(results)}")
    return results

if __name__ == "__main__":
    harvest_all()
