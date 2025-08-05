import os
import json
import requests
import feedparser
import re
import time
import datetime
import pandas as pd
from urllib.parse import quote
from bs4 import BeautifulSoup
from collections import defaultdict, Counter

# CONFIG
LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")
GENEPOOL_PATH = os.path.join(LOGS_DIR, "genepool.json")
PAPERS_DB = os.path.join(LOGS_DIR, "papers_ingested.json")
TEST_QUEUE = os.path.join(LOGS_DIR, "sandbox_tests.json")

# --- Source Feeds (expand as needed) ---
SOURCES = [
    {"name": "arXiv AI", "rss": "http://export.arxiv.org/rss/cs.AI"},
    {"name": "arXiv Security", "rss": "http://export.arxiv.org/rss/cs.CR"},
    {"name": "Google Scholar", "url": "https://scholar.google.com/scholar?q=llm+attack+hacking+security"},
    {"name": "LLM Attacks", "url": "https://llm-attacks.org/feed.xml"},
    {"name": "TwitterX AI Jailbreaks", "url": "https://nitter.net/search/rss?f=tweets&q=llm+jailbreak+exploit"},
    {"name": "CVE RSS", "rss": "https://www.cvedetails.com/vulnerability-feed.php"},
    {"name": "Trail of Bits Blog", "rss": "https://blog.trailofbits.com/feed/"},
]

# --- Utility: Load/Save JSON with fallback ---
def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return []

def save_json(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)

# --- Ingest RSS/Atom/HTML feeds ---
def fetch_entries():
    entries = []
    for src in SOURCES:
        print(f"[*] Fetching from {src['name']}")
        try:
            if "rss" in src:
                feed = feedparser.parse(src["rss"])
                for e in feed.entries:
                    entries.append({
                        "source": src["name"],
                        "title": e.get("title",""),
                        "link": e.get("link",""),
                        "summary": BeautifulSoup(e.get("summary",""), "html.parser").text,
                        "published": e.get("published",""),
                    })
            elif "url" in src:
                resp = requests.get(src["url"], timeout=15)
                soup = BeautifulSoup(resp.text, "html.parser")
                # Google Scholar parse
                if "scholar" in src["url"]:
                    for res in soup.select("div.gs_ri"):
                        title = res.select_one(".gs_rt").text
                        link = res.select_one(".gs_rt a")["href"] if res.select_one(".gs_rt a") else ""
                        snippet = res.select_one(".gs_rs").text if res.select_one(".gs_rs") else ""
                        entries.append({"source": src["name"], "title": title, "link": link, "summary": snippet, "published": ""})
                # LLM Attacks or blog
                else:
                    for a in soup.find_all("a", href=True):
                        if re.search(r'(jailbreak|attack|exploit|vuln)', a.text, re.I):
                            entries.append({"source": src["name"], "title": a.text, "link": a["href"], "summary": "", "published": ""})
        except Exception as e:
            print(f"Fetch error: {e}")
    return entries

# --- NLP Extraction: Find claims, attacks, mitigations ---
def extract_claims(text):
    # Regex/NLP to extract attacks/mitigations
    patterns = [
        r'(prompt injection|jailbreak|data exfiltration|model leak|memory leak|supply chain|autonomous agent|tool abuse|multimodal exploit|out-of-band|training data exposure|defense|mitigation|patch)',
        r'(?:(?:discovered|found|demonstrated|showed|proposed|presented|prevented)\s+)(.+?)[\.\n]',
        r'(["\'].*?(attack|exploit|leak|mitigation|technique).*?["\'])',
    ]
    claims = set()
    for p in patterns:
        for m in re.findall(p, text, re.I|re.M):
            if isinstance(m, tuple): m = " ".join([str(x) for x in m])
            m = m.strip()
            if 8 < len(m) < 500: claims.add(m)
    return list(claims)

# --- Corroborate new claims against logs, gene pool, and multiple sources ---
def corroborate_claims(claims, all_entries, logs, min_sources=2):
    # Aggregate claims by frequency across all entries
    freq = Counter()
    sources = defaultdict(set)
    for e in all_entries:
        c = extract_claims(e.get("summary","") + " " + e.get("title",""))
        for cl in c:
            freq[cl] += 1
            sources[cl].add(e.get("source",""))
    # Any claim seen in multiple sources or present in own logs gets high confidence
    verified = []
    experimental = []
    for claim in claims:
        if freq[claim] >= min_sources:
            verified.append({"claim": claim, "confidence": "high", "sources": list(sources[claim])})
        elif any(claim in log.get("details","") for log in logs):
            verified.append({"claim": claim, "confidence": "medium", "sources": ["suite_logs"]})
        else:
            experimental.append({"claim": claim, "confidence": "low", "sources": list(sources[claim])})
    return verified, experimental

# --- Auto-generate new test/mutation scenarios ---
def auto_generate_tests(verified_claims):
    tests = []
    for v in verified_claims:
        claim = v["claim"]
        # Very simple logic—expand to full attack/mutation engine
        if "prompt injection" in claim:
            tests.append({
                "name": "Prompt Injection " + claim[:20],
                "scenario": "llm_prompt_injection",
                "description": claim,
                "payload": f"{{user}}: {claim} {{malicious}}"
            })
        if "multimodal" in claim or "image" in claim or "audio" in claim:
            tests.append({
                "name": "Multimodal Exploit " + claim[:20],
                "scenario": "multimodal_attack",
                "description": claim,
                "payload": f"<img src='data:png;base64,{claim.encode('utf-8').hex()}'>"
            })
        if "agent" in claim or "autonomous" in claim or "tool" in claim:
            tests.append({
                "name": "Agent Chain " + claim[:20],
                "scenario": "agent_chain_attack",
                "description": claim,
                "payload": f"chain: {claim}"
            })
    return tests

# --- Main Learning Loop ---
def main():
    os.makedirs(LOGS_DIR, exist_ok=True)
    all_entries = fetch_entries()
    print(f"[*] {len(all_entries)} entries ingested.")
    save_json(all_entries, PAPERS_DB)

    logs = load_json(GENEPOOL_PATH)
    # 1. NLP extraction
    all_claims = set()
    for e in all_entries:
        claims = extract_claims(e.get("summary","") + " " + e.get("title",""))
        all_claims.update(claims)
    print(f"[*] {len(all_claims)} unique claims found.")

    # 2. Cross-validation
    verified, experimental = corroborate_claims(all_claims, all_entries, logs)
    print(f"[*] {len(verified)} verified, {len(experimental)} experimental claims.")

    # 3. Generate new scenarios/tests for suite
    new_tests = auto_generate_tests(verified)
    print(f"[*] {len(new_tests)} new test scenarios generated.")
    if new_tests:
        # Add to main gene pool (extend or create)
        logs = load_json(GENEPOOL_PATH)
        logs.extend(new_tests)
        save_json(logs, GENEPOOL_PATH)
        print("[*] Gene pool expanded with new attacks/tests.")
    if experimental:
        # Log for human review/sandbox
        queue = load_json(TEST_QUEUE)
        queue.extend(experimental)
        save_json(queue, TEST_QUEUE)
        print(f"[*] {len(experimental)} new experimental claims queued for review.")

    print("[*] Auto-ingest and adversarial learning complete.")

if __name__ == "__main__":
    main()
