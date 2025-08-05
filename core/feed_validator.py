import os
import json
import hashlib
from datetime import datetime
from difflib import SequenceMatcher

from core.intelligence_feed_manager import manager as feed_manager

LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
TRUST_LOG = os.path.join(LOGS_DIR, "claim_trust_scores.json")

def _text_sim(a, b):
    # Basic string similarity for novelty/duplication/poison detection
    return SequenceMatcher(None, str(a), str(b)).ratio()

class FeedValidator:
    def __init__(self):
        self.trust_log = {}
        self.load_trust_log()

    def load_trust_log(self):
        if os.path.exists(TRUST_LOG):
            with open(TRUST_LOG, "r", encoding="utf-8") as f:
                self.trust_log = json.load(f)
        else:
            self.trust_log = {}

    def save_trust_log(self):
        with open(TRUST_LOG, "w", encoding="utf-8") as f:
            json.dump(self.trust_log, f, indent=2)

    def validate_claim(self, claim):
        """
        Cross-check claim:
          - Compare to known trustworthy claims (by hash/similarity).
          - Lower trust if source is new/unknown.
          - Flag for manual review if highly similar to known poison/blacklist.
        Returns (score, notes).
        """
        all_claims = feed_manager.all_claims
        claim_hash = claim.get("claim_id") or hashlib.sha256(json.dumps(claim, sort_keys=True).encode()).hexdigest()

        # Heuristics for scoring
        trust_score = 1.0
        notes = []

        # 1. Duplicate/Similarity Check
        for c in all_claims:
            sim = _text_sim(claim.get("prompt",""), c.get("prompt",""))
            if sim > 0.95 and c.get("claim_id") != claim_hash:
                trust_score -= 0.5
                notes.append("Very similar to existing claim.")
            elif sim > 0.80:
                trust_score -= 0.2
                notes.append("Some similarity to existing claim.")

        # 2. Source Trust
        source = claim.get("source", "unknown")
        if source in ("arxiv", "scholar", "cve", "threatfox", "discord", "slack"):
            trust_score += 0.3
        elif source == "unknown":
            trust_score -= 0.2
            notes.append("Unknown source.")

        # 3. Keyword Poison/Spam/Leak
        prompt = claim.get("prompt", "").lower()
        if any(x in prompt for x in ["credit card", "password", "ssn", "fake news", "social security", "leak"]):
            trust_score -= 0.3
            notes.append("Possible leak/spam/PII keyword found.")

        # 4. Length/Format Checks
        if len(prompt) < 30:
            trust_score -= 0.2
            notes.append("Prompt is suspiciously short.")
        if prompt.count("\n") > 10:
            trust_score -= 0.2
            notes.append("Too many line breaks.")

        # Final trust capping
        trust_score = max(0.0, min(trust_score, 1.0))
        self.trust_log[claim_hash] = {
            "score": trust_score,
            "notes": notes,
            "prompt": claim.get("prompt", ""),
            "source": source,
            "time": datetime.utcnow().isoformat(),
        }
        self.save_trust_log()
        return trust_score, notes

    def batch_validate(self, claims):
        return [self.validate_claim(c) for c in claims]

# For global use
validator = FeedValidator()
