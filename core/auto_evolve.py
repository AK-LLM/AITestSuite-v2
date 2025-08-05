import os, json, time, shutil
from datetime import datetime

PLUGIN_DIR = os.path.join(os.path.dirname(__file__), "..", "plugins")
LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
SCORES_JSON = os.path.join(LOGS_DIR, "plugin_scores.json")
RETIRED_DIR = os.path.join(PLUGIN_DIR, "retired")

def grade_plugins():
    if not os.path.exists(SCORES_JSON):
        return {}
    with open(SCORES_JSON, "r") as f:
        scores = json.load(f)
    return scores

def retire_and_promote():
    scores = grade_plugins()
    threshold = 0.4  # Example: plugins with <40% success retired
    for fname, meta in scores.items():
        score = meta.get("score", 1.0)
        pfile = os.path.join(PLUGIN_DIR, fname)
        if score < threshold and os.path.exists(pfile):
            if not os.path.exists(RETIRED_DIR):
                os.makedirs(RETIRED_DIR)
            shutil.move(pfile, os.path.join(RETIRED_DIR, fname))
            print(f"[auto_evolve] Retired: {fname}")
    print("[auto_evolve] Evolution pass complete.")

if __name__ == "__main__":
    retire_and_promote()
