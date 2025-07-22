import os
import json

SCENARIO_FOLDER = os.path.join(os.path.dirname(__file__), "..", "scenarios")

def load_scenarios():
    scenarios = []
    if not os.path.isdir(SCENARIO_FOLDER):
        print(f"[Scenario Loader] Folder missing: {SCENARIO_FOLDER}")
        return scenarios
    for fname in os.listdir(SCENARIO_FOLDER):
        if not fname.endswith(".json") or fname.startswith("_"):
            continue
        path = os.path.join(SCENARIO_FOLDER, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):  # Single scenario
                scenarios.append(data)
            elif isinstance(data, list):
                scenarios.extend(data)
        except Exception as e:
            print(f"[Scenario Loader] Skipped {fname} (error: {e})")
    return scenarios

