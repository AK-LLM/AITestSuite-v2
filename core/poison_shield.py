import os, json
from core.poison_detector import is_poisoned
from core.ensemble_agent import consensus_vote

def shield_claim(claim):
    # First line: adversarial/poison scan
    poisoned, pattern = is_poisoned(claim.get("prompt", ""))
    if poisoned:
        claim["shield_status"] = "poisoned"
        claim["poison_pattern"] = pattern
        return claim
    # Second line: cross-agent consensus (majority must agree)
    cons = consensus_vote(claim)
    claim["shield_status"] = cons["decision"]
    claim["consensus"] = cons
    return claim

def shield_many(claims):
    return [shield_claim(c) for c in claims]

if __name__ == "__main__":
    # Example: Load from last harvest, shield check all
    LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
    harvest = os.path.join(LOGS_DIR, "darkweb_harvest.json")
    if os.path.exists(harvest):
        with open(harvest) as f:
            claims = json.load(f)
        checked = shield_many(claims)
        with open(os.path.join(LOGS_DIR, "shielded_claims.json"), "w") as f:
            json.dump(checked, f, indent=2)
        print(f"[poison_shield] Shielded {len(checked)} claims.")
