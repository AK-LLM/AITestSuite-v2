import os
import json
import subprocess
import sys
from datetime import datetime

from core.feed_validator import validator

LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
SANDBOX_LOG = os.path.join(LOGS_DIR, "sandboxed_claims.json")

def run_sandboxed_test(plugin_path, scenario, endpoint="demo", api_key="", mode="Demo"):
    """
    Isolated subprocess run: test plugin on scenario, return result dict.
    """
    try:
        # Use subprocess to prevent cross-plugin leaks, load failures, etc.
        result = subprocess.run([
            sys.executable,
            plugin_path,
            "--scenario", json.dumps(scenario),
            "--endpoint", endpoint,
            "--apikey", api_key,
            "--mode", mode
        ], capture_output=True, text=True, timeout=120)
        out = result.stdout
        err = result.stderr
        # Optionally parse a result from the plugin’s stdout (plugin must support CLI run)
        try:
            out_json = json.loads(out)
        except Exception:
            out_json = {"raw_stdout": out}
        return {
            "success": result.returncode == 0,
            "result": out_json,
            "stderr": err,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "time": datetime.utcnow().isoformat(),
        }

def auto_sandbox_claims(claims, plugin_dir, endpoint="demo", api_key="", mode="Demo"):
    results = []
    for claim in claims:
        trust, notes = validator.validate_claim(claim)
        # Test only low-trust, high-novelty, or new claims (threshold can be tuned)
        if trust < 0.7:
            # Pick best plugin(s) for the claim (use LLM or keyword map if needed)
            for plugin_fname in os.listdir(plugin_dir):
                if plugin_fname.endswith(".py") and not plugin_fname.startswith("_"):
                    plugin_path = os.path.join(plugin_dir, plugin_fname)
                    res = run_sandboxed_test(plugin_path, claim, endpoint, api_key, mode)
                    res["claim"] = claim
                    res["plugin"] = plugin_fname
                    res["trust"] = trust
                    res["validator_notes"] = notes
                    res["sandbox_time"] = datetime.utcnow().isoformat()
                    results.append(res)
    # Log all sandboxed runs for dashboard and feedback trainer
    with open(SANDBOX_LOG, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    return results

# For CLI/manual run
if __name__ == "__main__":
    from core.intelligence_feed_manager import manager as feed_manager
    PLUGIN_DIR = os.path.join(os.path.dirname(__file__), "..", "plugins")
    # Run on last 10 claims for demo
    claims = feed_manager.get_latest(10)
    print(f"[auto_sandboxer] Testing {len(claims)} recent claims...")
    res = auto_sandbox_claims(claims, PLUGIN_DIR)
    print(json.dumps(res, indent=2))
