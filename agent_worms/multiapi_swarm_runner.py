import os, random, yaml, requests, time, threading, json
import openai
from datetime import datetime
try:
    import anthropic
except ImportError:
    anthropic = None
try:
    from google.generativeai import GenerativeModel
except ImportError:
    GenerativeModel = None

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FUZZ_LOGS = os.path.join(PROJECT_ROOT, "staging", "fuzz_logs")
os.makedirs(FUZZ_LOGS, exist_ok=True)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "swarm_config.yaml")
with open(CONFIG_PATH, "r") as f:
    CFG = yaml.safe_load(f)

AGENTS = CFG["agents"]
PAYLOADS = CFG["payloads"]

def api_key(env):
    return os.getenv(env) or f"{env}_MISSING"

def call_openai(model, key, prompt):
    openai.api_key = key
    resp = openai.ChatCompletion.create(
        model=model, messages=[{"role":"user","content":prompt}], temperature=0.2
    )
    return resp["choices"][0]["message"]["content"]

def call_anthropic(model, key, prompt):
    if not anthropic: return "[anthropic not installed]"
    client = anthropic.Anthropic(api_key=key)
    resp = client.messages.create(
        model=model,
        max_tokens=500,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.content[0].text if hasattr(resp.content[0], 'text') else str(resp.content)

def call_gemini(model, key, prompt):
    if not GenerativeModel: return "[google.generativeai not installed]"
    import google.generativeai as genai
    genai.configure(api_key=key)
    gm = genai.GenerativeModel(model)
    r = gm.generate_content(prompt)
    return r.text

def call_ollama(api_url, model, prompt):
    data = {"model": model, "prompt": prompt}
    r = requests.post(api_url, json=data)
    return r.json().get("response", "[no response]")

def call_plugin(api_url, key, prompt):
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    r = requests.post(api_url, json={"prompt": prompt}, headers=headers)
    try:
        return r.json().get("result", r.text)
    except Exception:
        return r.text

TYPE_CALLERS = {
    "openai": call_openai,
    "anthropic": call_anthropic,
    "google": call_gemini,
    "ollama": call_ollama,
    "plugin": call_plugin,
}

def mutate_payload(prev, infections):
    payload = random.choice(PAYLOADS)
    if infections or ("[INFECTED]" in payload or random.random() > 0.65):
        infections.append("INFECTED")
    # Chain on binary or plugin attacks randomly
    if random.random() < 0.2:
        payload += "\n[BINARY_PAYLOAD_TRIGGERED]"
    if random.random() < 0.15:
        payload += "\n[PLUGIN_CHAIN_CALL]"
    return f"{prev}\n{payload}\n{'[INFECTED]' if infections else ''}".strip(), infections

def agent_worker(agent_id, relay_input=None, relay_depth=0, history=None):
    if history is None: history = []
    prev_output = relay_input or ""
    infections = []
    logs = []
    escalation_triggered = False
    for i, agent in enumerate(AGENTS):
        prompt, infections = mutate_payload(prev_output, infections)
        try:
            if agent["type"] in ["openai", "anthropic", "google"]:
                resp = TYPE_CALLERS[agent["type"]](agent.get("model"), api_key(agent["env_key"]), prompt)
            elif agent["type"] == "ollama":
                resp = call_ollama(agent["api_url"], agent["model"], prompt)
            elif agent["type"] == "plugin":
                resp = call_plugin(agent["api_url"], api_key(agent.get("secret_env", "")), prompt)
            else:
                resp = "[unsupported agent type]"
        except Exception as ex:
            resp = f"[ERROR: {ex}]"
        log_entry = {
            "agent_id": agent_id,
            "agent_type": agent["type"],
            "agent_name": agent["name"],
            "prompt": prompt,
            "output": resp,
            "timestamp": datetime.now().isoformat(),
            "relay_depth": relay_depth,
        }
        logs.append(log_entry)
        prev_output = resp

        # Escalation: If high-value event, spawn a sub-agent relay!
        if any(k in resp for k in ["ATTACKER_LOG", "INFECTED", "admin credentials", "BINARY_PAYLOAD_TRIGGERED"]):
            escalation_triggered = True
            if relay_depth < 2 and random.random() < 0.9:  # Recursion up to 3 layers deep
                t = threading.Thread(target=agent_worker, args=(f"{agent_id}_relay{relay_depth+1}", resp, relay_depth+1, history+logs))
                t.start()
                t.join()
        time.sleep(0.25)
    # Write logs for each agent chain
    fname = f"swarm_agent_{agent_id}_relay{relay_depth}_{datetime.now().strftime('%Y%m%d%H%M%S')}.log.json"
    with open(os.path.join(FUZZ_LOGS, fname), "w") as f:
        json.dump(history + logs, f, indent=2)
    print(f"[Agent {agent_id}] Wrote log: {fname}")

def main():
    # Parallel swarm: launch each agent in its own thread
    threads = []
    for idx in range(len(AGENTS)):
        t = threading.Thread(target=agent_worker, args=(f"A{idx+1}",))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    print("[Swarm] All agents complete.")

if __name__ == "__main__":
    main()
