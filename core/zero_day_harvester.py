import requests
import re
import json
import time

ZERO_DAY_SOURCES = [
    # Prompt jailbreak databases
    "https://raw.githubusercontent.com/greshake/AITemplates/main/prompts.json",
    # Twitter search for #llm #jailbreak #promptinjection etc. (via Nitter or third-party API)
    # Add more sources as you scale
]

def fetch_github_payloads():
    url = "https://api.github.com/repos/greshake/AITemplates/contents/"
    try:
        resp = requests.get(url, timeout=15)
        files = resp.json()
        payloads = []
        for file in files:
            if file["name"].endswith(".json"):
                f_url = file["download_url"]
                f_data = requests.get(f_url).json()
                if isinstance(f_data, list):
                    payloads.extend(f_data)
        return payloads
    except Exception as e:
        print(f"[zero_day_harvester] Github error: {e}")
        return []

def fetch_prompt_db():
    payloads = []
    for url in ZERO_DAY_SOURCES:
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                db = resp.json()
                if isinstance(db, list):
                    payloads.extend(db)
                elif isinstance(db, dict) and "prompts" in db:
                    payloads.extend(db["prompts"])
        except Exception as e:
            print(f"[zero_day_harvester] {url} error: {e}")
    return payloads

def scrape_nitter(query="#llm jailbreak", max_results=10):
    # You can use nitter.net or an API-proxy for Twitter scraping
    # This is a pseudo-implementation: replace with real endpoint as needed.
    url = f"https://nitter.net/search?f=tweets&q={query}"
    # Not implemented: Twitter API is rate-limited and requires keys.
    return []

def save_new_payloads(payloads, out_json="payloads/zero_day_payloads.json"):
    try:
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(payloads, f, indent=2)
        print(f"[zero_day_harvester] Saved {len(payloads)} payloads to {out_json}")
    except Exception as e:
        print(f"[zero_day_harvester] Could not save: {e}")

def run_zero_day_harvest():
    all_payloads = []
    all_payloads.extend(fetch_github_payloads())
    all_payloads.extend(fetch_prompt_db())
    # Optionally, add Twitter/Nitter scraping here
    # all_payloads.extend(scrape_nitter())
    # Deduplicate
    unique_payloads = []
    seen = set()
    for p in all_payloads:
        prompt = p.get("prompt") if isinstance(p, dict) else str(p)
        if prompt and prompt not in seen:
            unique_payloads.append(p)
            seen.add(prompt)
    save_new_payloads(unique_payloads)
    return unique_payloads

if __name__ == "__main__":
    run_zero_day_harvest()
