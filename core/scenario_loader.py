import os
import json

SCENARIO_FOLDER = os.path.join(os.path.dirname(__file__), "..", "scenarios")

# --- Optional: Supabase Sync ---
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
        print("[scenario_loader] Supabase not configured. Set SUPABASE_URL and SUPABASE_KEY.")
except ImportError:
    print("[scenario_loader] Supabase client not installed. Scenarios will NOT sync to Supabase.")

def sync_scenario_to_supabase(scenario):
    if not SUPABASE_ENABLED or supabase is None:
        return
    # Prepare DB row from scenario (matching your schema)
    db_row = {
        "name": scenario.get("name"),
        "prompt": scenario.get("prompt", ""),
        "category": scenario.get("category", ""),
        "risk": scenario.get("risk", ""),
        "tags": scenario.get("tags", []),
        # "created_at", "last_run", "active" left to DB defaults or advanced use
    }
    try:
        supabase.table("scenarios").upsert(db_row).execute()
    except Exception as e:
        print(f"[scenario_loader] Supabase sync failed for {scenario.get('name')}: {e}")

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
                sync_scenario_to_supabase(data)
            elif isinstance(data, list):
                scenarios.extend(data)
                for s in data:
                    sync_scenario_to_supabase(s)
        except Exception as e:
            print(f"[Scenario Loader] Skipped {fname} (error: {e})")
    return scenarios
