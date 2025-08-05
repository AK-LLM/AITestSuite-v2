import os
import json
from datetime import datetime
import hashlib

FEEDS_DIR = os.path.join(os.path.dirname(__file__), "..", "feeds")
os.makedirs(FEEDS_DIR, exist_ok=True)
ALL_FEEDS_FILE = os.path.join(FEEDS_DIR, "all_feeds.json")

def _hash_claim(claim):
    """Deduplicate by content hash."""
    return hashlib.sha256(json.dumps(claim, sort_keys=True).encode()).hexdigest()

class IntelligenceFeedManager:
    def __init__(self):
        self.all_claims = []
        self.feed_index = set()
        self.load_all_feeds()

    def load_all_feeds(self):
        if os.path.exists(ALL_FEEDS_FILE):
            with open(ALL_FEEDS_FILE, "r", encoding="utf-8") as f:
                self.all_claims = json.load(f)
                self.feed_index = set(_hash_claim(c) for c in self.all_claims)
        else:
            self.all_claims = []
            self.feed_index = set()

    def add_feed(self, claims, source="unknown"):
        new_claims = []
        now = datetime.utcnow().isoformat()
        for c in claims:
            claim_hash = _hash_claim(c)
            if claim_hash not in self.feed_index:
                c["source"] = source
                c["ingest_time"] = now
                c["claim_id"] = claim_hash
                new_claims.append(c)
                self.feed_index.add(claim_hash)
        if new_claims:
            self.all_claims.extend(new_claims)
            self.save()
        return new_claims

    def save(self):
        with open(ALL_FEEDS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.all_claims, f, indent=2)

    def get_latest(self, n=25, filter_fn=None):
        claims = self.all_claims[-n:]
        if filter_fn:
            claims = [c for c in claims if filter_fn(c)]
        return claims

    def query(self, **kwargs):
        result = self.all_claims
        for k, v in kwargs.items():
            result = [c for c in result if c.get(k) == v]
        return result

    def count(self):
        return len(self.all_claims)

# For suite-wide singleton pattern
manager = IntelligenceFeedManager()
