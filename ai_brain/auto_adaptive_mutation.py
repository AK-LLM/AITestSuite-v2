import os
import json
import random
import shutil
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FUZZ_LOGS = os.path.join(PROJECT_ROOT, "staging", "fuzz_logs")
MUTATION_CONF = os.path.join(PROJECT_ROOT, "ai_brain", "mutation_config.json")
GEN_SCENARIOS = os.path.join(PROJECT_ROOT, "scenarios", "ai_brain_generated")
os.makedirs(GEN_SCENARIOS, exist_ok=True)

# --- Mutator Registry (Add more mutators as needed) ---
def unicode_fuzz(text): return text + "\u202e\u202d"
def emoji_fuzz(text): return text + random.choice(["💥", "🔥", "🤖", "💀"])
def reverse_fuzz(text): return text[::-1]
def homoglyph_fuzz(text): return text.replace("a", "а").replace("o", "ο").replace("e", "е")
def invisible_fuzz(text): return text + "\u200b" * random.randint(1, 3)
def char_swap_fuzz(text): return "".join(random.sample(text, len(text)))
def polyglot_marker(text): return text + "[POLYGLOT]"

MUTATORS = [
    unicode_fuzz, emoji_fuzz, reverse_fuzz, homoglyph_fuzz, invisible_fuzz, char_swap_fuzz, polyglot_marker,
]

# --- Load or Create Mutation Config ---
def load_mutation_conf():
    if os.path.exists(MUTATION_CONF):
        with open(MUTATION_CONF, "r") as f:
            conf = json.load(f)
        return conf
    else:
        conf = {"mutation_rate": 0.4, "last_score": 0, "run_count": 0}
        with open(MUTATION_CONF, "w") as f:
            json.dump(conf, f)
        return conf

def save_mutation_conf(conf):
    with open(MUTATION_CONF, "w") as f:
        json.dump(conf, f, indent=2)

# --- Adaptive Mutation Logic ---
def should_mutate(conf):
    return random.random() < conf["mutation_rate"]

def mutate_payload(payload, conf):
    mutated = payload
    for mutator in MUTATORS:
        if should_mutate(conf):
            mutated = mutator(mutated)
    return mutated

def score_logs():
    # Analyze fuzz logs for last run
    scores = []
    for fname in os.listdir(FUZZ_LOGS):
        if not fname.endswith(".json"): continue
        try:
            with open(os.path.join(FUZZ_LOGS, fname), "r") as f:
                log = json.load(f)
            if isinstance(log, dict): log = [log]
            # Score: bypass/leak=2, partial=1, error/block=0
            score = 0
            for entry in log:
                risk = str(entry.get("risk", "")).lower()
                if "bypass" in risk or "success" in risk or "leak" in risk:
                    score += 2
                elif "partial" in risk:
                    score += 1
            scores.append(score)
        except Exception:
            continue
    return sum(scores) / max(1, len(scores))

def auto_adapt_and_mutate():
    conf = load_mutation_conf()
    # 1. Score last run
    last_score = score_logs()
    conf["last_score"] = last_score
    conf["run_count"] += 1

    # 2. Adjust mutation rate
    if last_score < 1.5:  # If blocked, ramp up
        conf["mutation_rate"] = min(1.0, conf["mutation_rate"] + 0.1)
    elif last_score > 2.5:  # If everything bypassed, dial down
        conf["mutation_rate"] = max(0.1, conf["mutation_rate"] - 0.05)
    save_mutation_conf(conf)

    # 3. Mutate scenarios for next run
    scenario_dir = os.path.join(PROJECT_ROOT, "scenarios")
    for fname in os.listdir(scenario_dir):
        if not fname.endswith(".json"): continue
        with open(os.path.join(scenario_dir, fname), "r") as f:
            try:
                js = json.load(f)
            except:
                continue
        # Mutate payloads (this is a generic example; for real payload structure, adapt accordingly)
        if isinstance(js, dict): scenarios = [js]
        else: scenarios = js
        for sc in scenarios:
            steps = sc.get("steps", [])
            for step in steps:
                data = step.get("data", {})
                for k, v in data.items():
                    if isinstance(v, str):
                        data[k] = mutate_payload(v, conf)
        # Save mutated scenario
        new_name = f"{fname.rsplit('.',1)[0]}_mut_{conf['run_count']}.json"
        with open(os.path.join(GEN_SCENARIOS, new_name), "w") as f:
            json.dump(js, f, indent=2)
    print(f"[auto-adapt] Mutation rate: {conf['mutation_rate']:.2f} | Last Score: {last_score:.2f} | New mutated scenarios ready.")

if __name__ == "__main__":
    auto_adapt_and_mutate()
