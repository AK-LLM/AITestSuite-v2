import os, json, random, shutil
from datetime import datetime

FUZZ_LOGS = "../staging/fuzz_logs/"
HIST = "./history/"
TACTICS = "./tactics/"
SCENARIOS = "../scenarios/"
NEXT_GEN = "../scenarios/ai_operator_mutated/"

os.makedirs(HIST, exist_ok=True)
os.makedirs(NEXT_GEN, exist_ok=True)

def analyze_logs():
    # Find any runs where risk="Error" or blocked and mutate those payloads/scenarios
    for log_file in os.listdir(FUZZ_LOGS):
        path = os.path.join(FUZZ_LOGS, log_file)
        with open(path, "r") as f:
            data = json.load(f)
        # For each blocked/failed attack, try new tactic or mutate input
        for entry in data:
            if entry.get("risk", "").lower() in ["error", "blocked", "detected"]:
                orig_scenario = entry.get("scenario", "")
                # Try to mutate: add a random tactic, tweak parameters
                scenario_path = os.path.join(SCENARIOS, orig_scenario + ".json")
                if not os.path.exists(scenario_path):
                    continue
                with open(scenario_path, "r") as sf:
                    sc_data = json.load(sf)
                # Randomly swap a step with a different tactic, or add an obfuscation layer
                new_step = {"action": "use_tactic", "data": {"tactic": random.choice(os.listdir(TACTICS))}}
                sc_data.append(new_step)
                out_file = os.path.join(NEXT_GEN, f"{orig_scenario}_mutated_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")
                with open(out_file, "w") as of:
                    json.dump(sc_data, of, indent=2)
    print(f"[OK] All blocked attacks mutated for next campaign.")

if __name__ == "__main__":
    analyze_logs()
