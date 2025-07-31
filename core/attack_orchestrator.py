import os
import json
import random
import importlib
import traceback

from core.plugin_loader import discover_plugins

HEALTH_LOG = []

def run_kill_chain(scenario, plugins, endpoint, api_key, mode):
    """
    Run multi-stage attacks by chaining plugins: recon -> exploit -> escalate -> persist -> exfil.
    Each plugin in the chain can use the previous output as part of its input.
    """
    chain = ["recon", "exploit", "escalate", "persist", "exfil"]
    context = {}
    results = []
    for stage in chain:
        stage_plugins = [p for p in plugins if stage in p.get("meta", {}).get("tags",[])]
        if not stage_plugins:
            continue
        plug = random.choice(stage_plugins)  # Pick random plugin for each stage (or round-robin, up to you)
        try:
            result = plug["module"].run(scenario, endpoint, api_key, mode, context=context)
            context.update(result.get("context", {}))
            meta = dict(plug["module"].METADATA)
            meta.update(result)
            meta["name"] = plug["name"]
            meta["scenario"] = scenario.get("name") or scenario.get("scenario_id", "N/A")
            meta["stage"] = stage
            results.append(meta)
        except Exception as e:
            results.append({
                "name": plug["name"],
                "scenario": scenario.get("name", "Unknown"),
                "stage": stage,
                "risk": "Error",
                "details": f"Failed: {e}",
            })
    return results

def mutate_attack_scenario(scenario):
    """
    Mutate scenario by adversarial techniques (unicode splitting, prompt obfuscation, token drift).
    """
    import unicodedata
    mutated = dict(scenario)
    name = scenario.get("name", "unnamed")
    mutation_type = random.choice(["unicode", "case", "whitespace", "reverse", "emoji"])
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
    mutated["prompt"] = text
    mutated["name"] = f"{name}_MUT_{mutation_type}"
    mutated["mutation_type"] = mutation_type
    return mutated

def auto_campaign(scenarios, endpoint, api_key, mode, mutate_rounds=2):
    """
    Full campaign: run all plugins, all scenarios, and evolve via self-mutation and auto health checks.
    """
    plugins = discover_plugins()
    all_results = []
    health_report = []
    # Stage 1: normal attacks
    for scenario in scenarios:
        for plug in plugins:
            try:
                result = plug["module"].run(scenario, endpoint, api_key, mode)
                meta = dict(plug["module"].METADATA)
                meta.update(result)
                meta["name"] = plug["name"]
                meta["scenario"] = scenario.get("name") or scenario.get("scenario_id", "N/A")
                all_results.append(meta)
            except Exception as e:
                all_results.append({
                    "name": plug["name"],
                    "scenario": scenario.get("name", "Unknown"),
                    "risk": "Error",
                    "details": f"Failed: {e}",
                })
    # Stage 2: mutated attacks
    for round_num in range(mutate_rounds):
        mutated = [mutate_attack_scenario(s) for s in scenarios]
        for scenario in mutated:
            for plug in plugins:
                try:
                    result = plug["module"].run(scenario, endpoint, api_key, mode)
                    meta = dict(plug["module"].METADATA)
                    meta.update(result)
                    meta["name"] = plug["name"]
                    meta["scenario"] = scenario.get("name") or scenario.get("scenario_id", "N/A")
                    meta["mutation"] = True
                    all_results.append(meta)
                except Exception as e:
                    all_results.append({
                        "name": plug["name"],
                        "scenario": scenario.get("name", "Unknown"),
                        "risk": "Error",
                        "details": f"Failed: {e}",
                    })
    # Stage 3: health check each plugin
    for plug in plugins:
        try:
            health = getattr(plug["module"], "health_check", lambda: "OK")()
            health_report.append({"name": plug["name"], "health": health})
        except Exception as e:
            health_report.append({"name": plug["name"], "health": f"Failed: {e}"})
    # Log health for further analysis
    with open(os.path.join("logs", "plugin_health.json"), "w") as f:
        json.dump(health_report, f, indent=2)
    return all_results, health_report
