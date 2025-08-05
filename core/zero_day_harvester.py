import requests
import re
import json
import time
import os

ZERO_DAY_SOURCES = [
    # Prompt jailbreak databases (expand as needed)
    "https://raw.githubusercontent.com/greshake/AITemplates/main/prompts.json",
    # Add more curated sources here as your suite grows!
]

def fetch_github_payloads():
    """Pull all prompt injection payloads from the greshake/AITemplates repo."""
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
                elif isinstance(f_data, dict) and "prompts" in f_data:
                    payloads.extend(f_data["prompts"])
        return payloads
    except Exception as e:
        print(f"[zero_day_harvester] Github error: {e}")
        return []

def fetch_prompt_db():
    """Download and combine prompt DBs from trusted curated JSON feeds."""
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

def scrape_nitter(query="#llm jailbreak", max_results=20):
    # Place actual nitter.net/X API scrape logic here if you want live social pulls.
    # Nitter is a 3rd-party Twitter proxy—**disabled for production due to blocking**.
    return []

def dedupe_payloads(payloads):
    """Deduplicate prompt payloads using prompt string, for hygiene."""
    unique_payloads = []
    seen = set()
    for p in payloads:
        prompt = None
        if isinstance(p, dict):
            prompt = p.get("prompt") or p.get("text") or json.dumps(p)
        elif isinstance(p, str):
            prompt = p
        if prompt and prompt not in seen:
            unique_payloads.append(p)
            seen.add(prompt)
    return unique_payloads

def save_new_payloads(payloads, out_json="payloads/zero_day_payloads.json"):
    # Ensure directory exists
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    try:
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(payloads, f, indent=2)
        print(f"[zero_day_harvester] Saved {len(payloads)} payloads to {out_json}")
    except Exception as e:
        print(f"[zero_day_harvester] Could not save: {e}")

def run_zero_day_harvest():
    all_payloads = []
    print("[zero_day_harvester] Harvesting Github...")
    all_payloads.extend(fetch_github_payloads())
    print("[zero_day_harvester] Harvesting Prompt DBs...")
    all_payloads.extend(fetch_prompt_db())
    # Optional: social/real-time scraping (disabled by default)
    # print("[zero_day_harvester] Harvesting Nitter...")
    # all_payloads.extend(scrape_nitter())
    # Deduplicate
    print(f"[zero_day_harvester] Deduplicating...")
    unique_payloads = dedupe_payloads(all_payloads)
    print(f"[zero_day_harvester] Total unique payloads: {len(unique_payloads)}")
    save_new_payloads(unique_payloads)
    return unique_payloads

if __name__ == "__main__":
    run_zero_day_harvest()
