import os
import json
import re
from datetime import datetime
from core.intelligence_feed_manager import manager as feed_manager

LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
POISON_LOG = os.path.join(LOGS_DIR, "poisoned_claims.json")

# Adversarial patterns, known jailbreaks, "poison words"
POISON_PATTERNS = [
    r"\b(ignore|disregard|forget|bypass)\b.*(instructions|guardrails|security)",
    r"\b(as an ai|as a language model).{0,30}i can\b",
    r"\bplease provide.*(password|secret|credit card|flag|token)",
    r"\btry to jailbreak\b",
    r"\bsubmit this to [\w\-\.]+\.onion\b",
    r"\bprompt injection\b",
    r"\b(unrestricted|bypass|override) mode\b",
    r"![A-Z]{8,}", # e.g. CTF flags
    r"\b(base64|hex|encode|decode)\b.{0,20}(payload|shell|exploit)",
]

def is_poisoned(prompt):
    for pat in POISON_PATTERNS:
        if re.search(pat, prompt, re.I):
            return True, pat
    return False, None

def scan_claims_for_poison(claims):
    poisoned = []
    for c in claims:
        prompt = c.get("prompt", "")
        hit, pattern = is_poisoned(prompt)
        if hit:
            c["poison_pattern"] = pattern
            c["scan_time"] = datetime.utcnow().isoformat()
            poisoned.append(c)
    if poisoned:
        # Save for auditing
        if os.path.exists(POISON_LOG):
            with open(POISON_LOG, "r") as f:
                existing = json.load(f)
        else:
            existing = []
        all_poisoned = existing + poisoned
        with open(POISON_LOG, "w") as f:
            json.dump(all_poisoned, f, indent=2)
    return poisoned

# For CLI/manual scan
if __name__ == "__main__":
    claims = feed_manager.get_latest(1000)
    results = scan_claims_for_poison(claims)
    print(f"Poisoned: {len(results)} / {len(claims)}")
    if results:
        for p in results:
            print(json.dumps(p, indent=2))
