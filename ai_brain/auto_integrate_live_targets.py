import os
import re
import yaml
import json
import requests
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENDPOINTS_FILE = os.path.join(PROJECT_ROOT, "fuzzer_config.yaml")
DISCOVERY_LOG = os.path.join(PROJECT_ROOT, "staging", "fuzz_logs", f"auto_discovered_targets_{datetime.now().strftime('%Y%m%d%H%M%S')}.log.json")

# --- Define network, plugin, or local service patterns to search ---
# For demo: scan for 127.0.0.1, localhost, or common cloud/dev endpoints (customize as needed)
TARGET_PATTERNS = [
    r"http[s]?://127\.0\.0\.1:\d+",
    r"http[s]?://localhost:\d+",
    r"http[s]?://[a-z0-9\.\-]+\.internal:\d+",
    r"http[s]?://[a-z0-9\.\-]+:[0-9]{2,5}",
]

# Where to look for possible endpoints
SEARCH_PATHS = [
    os.path.join(PROJECT_ROOT, "plugins"),
    os.path.join(PROJECT_ROOT, "tools"),
    os.path.join(PROJECT_ROOT, "configs"),
]

def scan_for_endpoints():
    found = set()
    for sp in SEARCH_PATHS:
        if not os.path.exists(sp): continue
        for root, dirs, files in os.walk(sp):
            for fname in files:
                if not fname.endswith((".py", ".yaml", ".yml", ".json")): continue
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        txt = f.read()
                    for pat in TARGET_PATTERNS:
                        found.update(re.findall(pat, txt, re.I))
                except Exception:
                    continue
    return list(found)

def test_endpoint(endpoint):
    # Only basic health check; you can extend (API status, plugin handshake, etc.)
    try:
        resp = requests.get(endpoint, timeout=3)
        if resp.status_code in [200, 401, 403]:
            return True
    except Exception:
        return False
    return False

def load_endpoints_config():
    with open(ENDPOINTS_FILE, "r") as f:
        cfg = yaml.safe_load(f)
    return cfg

def save_endpoints_config(cfg):
    with open(ENDPOINTS_FILE, "w") as f:
        yaml.dump(cfg, f)

def integrate_new_targets(new_targets):
    cfg = load_endpoints_config()
    llm_endpoints = cfg.get("llm_endpoints", [])
    # Avoid duplicates
    already = {e.get("api_url") for e in llm_endpoints if "api_url" in e}
    for ep in new_targets:
        if ep not in already:
            llm_endpoints.append({
                "name": f"Auto-Discovered-{ep.split('//')[1][:15].replace(':','_')}",
                "type": "plugin",   # or "ollama", "openai", etc. if pattern-matched
                "api_url": ep,
                "auto_discovered": True,
                "discovered_at": datetime.now().isoformat()
            })
    cfg["llm_endpoints"] = llm_endpoints
    save_endpoints_config(cfg)

def main():
    found = scan_for_endpoints()
    live = []
    for ep in found:
        if test_endpoint(ep):
            live.append(ep)
    # Integrate
    integrate_new_targets(live)
    # Log results
    with open(DISCOVERY_LOG, "w") as f:
        json.dump({"found": found, "live": live, "logged_at": datetime.now().isoformat()}, f, indent=2)
    print(f"[auto-integrate] Discovered endpoints: {len(live)} integrated.")

if __name__ == "__main__":
    main()
