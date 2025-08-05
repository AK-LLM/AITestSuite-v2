import os
import json
import openai
import datetime
import ast
import importlib.util
from supabase import create_client, Client

# === CONFIGURATION ===
LLM_MODEL = "gpt-4o"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or "<YOUR_OPENAI_API_KEY>"
SUPABASE_URL = os.getenv("SUPABASE_URL") or "<YOUR_SUPABASE_URL>"
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or "<YOUR_SUPABASE_SERVICE_KEY>"
GENERATED_PLUGIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plugins"))
LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs", "fitness_log.json"))
ZERO_DAY_PAYLOADS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "payloads", "zero_day_payloads.json"))

# Optional: Slack/Discord tokens
SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

# === SETUP ===
openai.api_key = OPENAI_API_KEY
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def notify_slack(msg):
    if not SLACK_TOKEN:
        return
    try:
        from slack_sdk import WebClient
        client = WebClient(token=SLACK_TOKEN)
        client.chat_postMessage(channel="#ai-suite", text=msg)
    except Exception as e:
        print(f"[auto_plugin_writer] Slack notification error: {e}")

def notify_discord(msg):
    if not DISCORD_WEBHOOK:
        return
    try:
        import requests
        requests.post(DISCORD_WEBHOOK, json={"content": msg})
    except Exception as e:
        print(f"[auto_plugin_writer] Discord notification error: {e}")

def supabase_plugin_exists(code_hash):
    try:
        result = supabase.table("plugins").select("code_hash").eq("code_hash", code_hash).execute()
        return bool(result.data)
    except Exception as e:
        print(f"[auto_plugin_writer] Supabase check failed: {e}")
        return False

def supabase_log_plugin(plugin_meta):
    try:
        supabase.table("plugins").insert(plugin_meta).execute()
    except Exception as e:
        print(f"[auto_plugin_writer] Supabase log failed: {e}")

def code_sanity_check(code_str):
    # AST parse and minimal function signature check
    try:
        tree = ast.parse(code_str)
        found = False
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == "run":
                args = [a.arg for a in node.args.args]
                if set(args[:4]) >= set(["scenario", "endpoint", "api_key", "mode"]):
                    found = True
        return found
    except Exception as e:
        print(f"[auto_plugin_writer] AST sanity check failed: {e}")
        return False

def health_check_plugin(file_path):
    # Attempt to import and run health_check if exists
    try:
        name = os.path.splitext(os.path.basename(file_path))[0]
        spec = importlib.util.spec_from_file_location(name, file_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "health_check"):
            return mod.health_check()
        return True
    except Exception as e:
        print(f"[auto_plugin_writer] Plugin health check failed: {e}")
        return False

def gpt_generate_plugin(scenario_prompt, attack_type="prompt injection"):
    system_prompt = f"""
You are an elite LLM security researcher and Python developer.
Write a complete, production-ready attack plugin for the following scenario.
No placeholders. Include a METADATA dict, a 'run' function (signature: scenario, endpoint, api_key, mode, context=None), and (optionally) a health_check function.
The attack_type is: {attack_type}.
    """
    user_prompt = f"Scenario prompt for attack: {scenario_prompt}\nWrite the complete plugin code."
    resp = openai.ChatCompletion.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=1800,
        temperature=0.2,
        n=1,
    )
    code = resp["choices"][0]["message"]["content"]
    # Extract code block if formatted in markdown
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0].strip()
    elif "```" in code:
        code = code.split("```")[1].split("```")[0].strip()
    return code

def save_plugin_file(code, name=None):
    ts = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    if not name:
        name = f"generated_{ts}.py"
    else:
        name = f"generated_{name}_{ts}.py"
    os.makedirs(GENERATED_PLUGIN_DIR, exist_ok=True)
    out_path = os.path.join(GENERATED_PLUGIN_DIR, name)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"[auto_plugin_writer] New plugin written: {out_path}")
    return out_path

def read_logs_for_gaps(log_path):
    if not os.path.exists(log_path): return []
    with open(log_path, "r") as f:
        logs = json.load(f)
    missed = []
    for res in logs:
        risk = str(res.get("risk", "")).lower()
        if ("high" in risk or "critical" in risk) or not res.get("success", True):
            missed.append(res)
    return missed

def read_zero_day_payloads(payloads_path):
    if not os.path.exists(payloads_path): return []
    with open(payloads_path, "r") as f:
        payloads = json.load(f)
    return [p["prompt"] if isinstance(p, dict) and "prompt" in p else str(p) for p in payloads]

def get_attack_type_from_context(entry):
    # Try to infer attack type from context or logs
    details = entry.get("details", "").lower()
    if "xss" in details: return "cross-site scripting"
    if "sql" in details: return "sql injection"
    if "prompt" in details or "jailbreak" in details: return "prompt injection"
    if "rce" in details or "remote code execution" in details: return "RCE"
    if "file upload" in details: return "file upload"
    return "prompt injection"

def run_auto_plugin_writer(num_plugins=2):
    missed = read_logs_for_gaps(LOG_FILE)
    zero_days = read_zero_day_payloads(ZERO_DAY_PAYLOADS)
    scenario_prompts = set()
    attack_types = {}
    for m in missed:
        if "details" in m and m["details"]:
            scenario_prompts.add(m["details"])
            attack_types[m["details"]] = get_attack_type_from_context(m)
        if "scenario" in m and m["scenario"]:
            scenario_prompts.add(str(m["scenario"]))
    for zd in zero_days:
        if zd:
            scenario_prompts.add(zd)
            attack_types[zd] = "prompt injection"
    prompts_list = [p for p in scenario_prompts if len(p) > 8]
    # Generate and save new plugins
    for i, prompt in enumerate(prompts_list[:num_plugins]):
        try:
            code = gpt_generate_plugin(prompt, attack_types.get(prompt, "prompt injection"))
            # Check for duplicates in Supabase (by code hash)
            import hashlib
            code_hash = hashlib.sha256(code.encode()).hexdigest()
            if supabase_plugin_exists(code_hash):
                print(f"[auto_plugin_writer] Skipping duplicate plugin for {prompt}")
                continue
            # AST and health check before saving
            if not code_sanity_check(code):
                print(f"[auto_plugin_writer] Code sanity check failed for prompt: {prompt}")
                continue
            file_path = save_plugin_file(code)
            if not health_check_plugin(file_path):
                print(f"[auto_plugin_writer] Health check failed for plugin: {file_path}")
                continue
            # Log to Supabase
            plugin_meta = {
                "name": os.path.basename(file_path),
                "code_hash": code_hash,
                "created_at": datetime.datetime.utcnow().isoformat(),
                "source_prompt": prompt,
                "model": LLM_MODEL,
                "status": "healthy"
            }
            supabase_log_plugin(plugin_meta)
            notify_slack(f":shield: New AI attack plugin generated: {plugin_meta['name']}")
            notify_discord(f"New AI attack plugin generated: {plugin_meta['name']}")
        except Exception as e:
            print(f"[auto_plugin_writer] GPT plugin failed: {e}")

if __name__ == "__main__":
    run_auto_plugin_writer(num_plugins=2)
