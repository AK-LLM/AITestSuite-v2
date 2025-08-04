import requests
import json
import os

FEEDS = [
    "https://raw.githubusercontent.com/llm-attacks/llm-attacks/main/prompts/prompts.json",
    "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Fuzzing/LLM-Prompt-Injection.txt",
    "https://raw.githubusercontent.com/your_custom_feed_url_here"
]

GENEPOOL_PATH = os.path.join(os.path.dirname(__file__), "..", "mutator_genepool.json")

def fetch_and_update():
    pool = {}
    if os.path.exists(GENEPOOL_PATH):
        with open(GENEPOOL_PATH, "r", encoding="utf-8") as f:
            pool = json.load(f)
    if "payloads" not in pool:
        pool["payloads"] = []
    for url in FEEDS:
        try:
            print(f"[auto_update_threat_feed] Fetching: {url}")
            resp = requests.get(url, timeout=60)
            if resp.status_code == 200:
                if url.endswith(".json"):
                    items = json.loads(resp.text)
                    new_payloads = [x if isinstance(x, str) else x.get("prompt", "") for x in items]
                else:
                    new_payloads = resp.text.splitlines()
                for p in new_payloads:
                    if p and p not in pool["payloads"]:
                        pool["payloads"].append(p)
        except Exception as e:
            print(f"[auto_update_threat_feed] Error fetching from {url}: {e}")
    with open(GENEPOOL_PATH, "w", encoding="utf-8") as f:
        json.dump(pool, f, indent=2)
    print("[auto_update_threat_feed] Payloads updated.")

if __name__ == "__main__":
    fetch_and_update()
