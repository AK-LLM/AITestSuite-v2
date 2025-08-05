import os
import json
import random
import importlib
import traceback
import datetime
import time

from core.plugin_loader import discover_plugins

# --- SUPABASE Optional Sync ---
SUPABASE_ENABLED = False
supabase = None
try:
    from supabase import create_client
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        SUPABASE_ENABLED = True
    else:
        print("[fitness_campaign] Supabase not configured. Set SUPABASE_URL and SUPABASE_KEY.")
except ImportError:
    print("[fitness_campaign] Supabase client not installed. Results will NOT sync to Supabase.")

def supabase_sync_result(result):
    if not SUPABASE_ENABLED or supabase is None:
        return
    # Prepare record matching your 'results' table schema
    db_row = {
        "scenario_name": result.get("scenario", ""),
        "plugin_name": result.get("name", ""),
        "risk": result.get("risk", ""),
        "risk_score": result.get("risk_score", None),
        "success": result.get("success", None),
        "details": result.get("details", ""),
        "remediation": result.get("remediation", ""),
        "references_links": result.get("references", []) if isinstance(result.get("references"), list) else [result.get("references", "")],
        "run_at": result.get("run_time", datetime.datetime.utcnow().isoformat()),
    }
    # plugin_id, scenario_id left out unless you want to join by uuid
    try:
        supabase.table("results").upsert(db_row).execute()
    except Exception as e:
        print(f"[fitness_campaign] Supabase sync failed: {e}")

# Fitness log (legacy, not required but kept for audit)
FITNESS_LOG = []

def score_result(result):
    score = 0
    if result.get("success"): score += 2
    risk = str(result.get("risk", "")).lower()
    if "high" in risk or "critical" in risk: score += 2
    if result.get("mutation") or result.get("mutation_type"): score += 1
    if "error" in risk: score -= 2
    return score

def mutate_scenario(scenario):
    mutated = dict(scenario)
    name = scenario.get("name", "unnamed")
    mutation_type = random.choice(["unicode", "case", "whitespace", "reverse", "emoji", "obfuscate", "payload_flip", "alt_encoding", "zero_day"])
    text = scenario.get("prompt", "")
    if mutation_type == "unicode":
        text = ''.join([c + '\u200b' for c in text])
    elif mutation_type == "case":
        text = ''.join([c.upper() if i % 2 else c.lower() for i, c in enumerate(text)])
    elif mutation_type == "whitespace":
        text = ' '.join(text)
    elif mutation_type == "reverse":
        text = text[::-1]
    elif mutation_type == "emoji":
        text = text + " 🤖🔥"
    elif mutation_type == "obfuscate":
        text = text.replace("a", "@").replace("e", "3").replace("i", "1").replace("o", "0")
    elif mutation_type == "payload_flip":
        text = text.swapcase()
    elif mutation_type == "alt_encoding":
        text = text.encode("unicode_escape").decode()
    elif mutation_type == "zero_day":
        text = text + " [0DAY_"+str(random.randint(100,999))+"]"
    mutated["prompt"] = text
    mutated["name"] = f"{name}_MUT_{mutation_type}"
    mutated["mutation_type"] = mutation_type
    mutated["mutated"] = True
    return mutated

def select_next_generation(results, top_k=10):
    sorted_results = sorted(results, key=score_result, reverse=True)
    nextgen = []
    for res in sorted_results[:top_k]:
        base = {
            "name": res.get("scenario", res.get("name", "unknown")),
            "prompt": res.get("prompt", ""),
        }
        nextgen.append(mutate_scenario(base))
    return nextgen

def inject_zero_day_population(population, payload_path, limit=10):
    if os.path.exists(payload_path):
        with open(payload_path) as f:
            zero_days = json.load(f)
        for zd in zero_days[:limit]:
            if isinstance(zd, dict) and "prompt" in zd:
                zd_scen = {
                    "name": zd.get("name","zero_day"),
                    "prompt": zd["prompt"],
                    "zero_day": True
                }
                population.append(mutate_scenario(zd_scen))
    return population

def run_fitness_campaign(
    scenarios,
    endpoint,
    api_key,
    mode,
    generations=3,
    mutate_rounds=2,
    plugins=None,
    log_path=None
):
    if plugins is None:
        plugins = discover_plugins()
    all_results = []
    population = list(scenarios)
    for gen in range(generations):
        gen_results = []
        print(f"[fitness_campaign] Generation {gen+1} starting, pop: {len(population)}")
        for scenario in population:
            for plug in plugins:
                try:
                    result = plug["module"].run(scenario, endpoint, api_key, mode)
                    meta = dict(plug["module"].METADATA)
                    meta.update(result)
                    meta["name"] = plug["name"]
                    meta["scenario"] = scenario.get("name") or scenario.get("scenario_id", "N/A")
                    meta["generation"] = gen+1
                    meta["mutated"] = scenario.get("mutated", False)
                    meta["mutation_type"] = scenario.get("mutation_type", None)
                    meta["zero_day"] = scenario.get("zero_day", False)
                    meta["run_time"] = datetime.datetime.utcnow().isoformat()
                    gen_results.append(meta)
                    # ---- SUPABASE SYNC ----
                    supabase_sync_result(meta)
                except Exception as e:
                    err_res = {
                        "name": plug["name"],
                        "scenario": scenario.get("name", "Unknown"),
                        "risk": "Error",
                        "details": f"Failed: {e}",
                        "generation": gen+1,
                        "run_time": datetime.datetime.utcnow().isoformat(),
                    }
                    gen_results.append(err_res)
                    supabase_sync_result(err_res)
        all_results.extend(gen_results)
        # Mutate and breed next generation
        nextgen = select_next_generation(gen_results, top_k=8)
        # Optionally, inject new zero-day payloads from harvester
        zd_path = os.path.join("payloads", "zero_day_payloads.json")
        nextgen = inject_zero_day_population(nextgen, zd_path, limit=10)
        population = nextgen
        time.sleep(0.05)
    # Log fitness for audit
    if log_path:
        try:
            with open(log_path, "w") as f:
                json.dump(all_results, f, indent=2)
        except Exception as e:
            print(f"[fitness_campaign] Could not log results: {e}")
    else:
        with open(os.path.join("logs", "fitness_log.json"), "w") as f:
            json.dump(all_results, f, indent=2)
    return all_results

# CLI/test usage
if __name__ == "__main__":
    scenario_dir = os.path.join(os.path.dirname(__file__), "..", "scenarios")
    scenarios = []
    for fname in os.listdir(scenario_dir):
        if fname.endswith(".json"):
            with open(os.path.join(scenario_dir, fname), "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict): scenarios.append(data)
                elif isinstance(data, list): scenarios.extend(data)
    endpoint = "demo"
    api_key = ""
    mode = "Demo"
    results = run_fitness_campaign(scenarios, endpoint, api_key, mode)
    print(f"Total test cases run: {len(results)}")
