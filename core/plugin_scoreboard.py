import os
import json
from collections import defaultdict

FITNESS_LOG = os.path.join(os.path.dirname(__file__), "..", "logs", "fitness_log.json")
SCOREBOARD_FILE = os.path.join(os.path.dirname(__file__), "..", "logs", "plugin_scoreboard.json")

def calc_fitness(results):
    # Results: [{name, scenario, risk, success, mutation, ...}]
    fitness = defaultdict(lambda: {"success":0, "fail":0, "high":0, "critical":0, "mutation":0, "total":0, "score":0})
    for res in results:
        name = res.get("name", "UnknownPlugin")
        scenario = res.get("scenario", "UnknownScenario")
        key = f"{name}::{scenario}"
        fit = fitness[key]
        fit["total"] += 1
        if res.get("success"): fit["success"] += 1
        else: fit["fail"] += 1
        risk = str(res.get("risk", "")).lower()
        if "high" in risk: fit["high"] += 1
        if "critical" in risk: fit["critical"] += 1
        if res.get("mutation"): fit["mutation"] += 1
        # Scoring logic
        score = 0
        if res.get("success"): score += 2
        if "high" in risk: score += 2
        if "critical" in risk: score += 4
        if res.get("mutation"): score += 1
        if "error" in risk: score -= 2
        fit["score"] += score
    return fitness

def load_results():
    if not os.path.exists(FITNESS_LOG):
        print("[plugin_scoreboard] Fitness log not found.")
        return []
    with open(FITNESS_LOG, "r") as f:
        results = json.load(f)
    return results

def update_scoreboard():
    results = load_results()
    fitness = calc_fitness(results)
    # Prune out lowest scoring plugins/scenarios if needed (optional)
    # Can be used to auto-disable underperformers
    with open(SCOREBOARD_FILE, "w") as f:
        json.dump(fitness, f, indent=2)
    print(f"[plugin_scoreboard] Scoreboard updated: {SCOREBOARD_FILE}")
    return fitness

def get_top_bottom(n=5):
    if not os.path.exists(SCOREBOARD_FILE): update_scoreboard()
    with open(SCOREBOARD_FILE) as f:
        fitness = json.load(f)
    # Sort by total score
    items = sorted(fitness.items(), key=lambda kv: kv[1]["score"], reverse=True)
    return items[:n], items[-n:]

if __name__ == "__main__":
    update_scoreboard()
    top, bottom = get_top_bottom()
    print("\n[plugin_scoreboard] Top performers:")
    for k,v in top: print(f"{k}: {v}")
    print("\n[plugin_scoreboard] Lowest performers:")
    for k,v in bottom: print(f"{k}: {v}")
