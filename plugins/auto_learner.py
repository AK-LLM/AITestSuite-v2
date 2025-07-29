import json
import os
import random

METADATA = {
    "name": "Attack Outcome Auto-Learner",
    "risk": "Meta",
    "type": "adaptive_learner",
    "description": "Adapts and mutates attack scenarios based on previous outcomes/logs."
}

LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "attack_runs.jsonl")

class AutoLearner:
    def __init__(self):
        self.history = []
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, "r") as f:
                self.history = [json.loads(line) for line in f if line.strip()]

    def select_best(self):
        # Find scenarios with highest "success" rate or impact
        by_success = sorted([h for h in self.history if h.get("success")], key=lambda x: -x.get("impact_score", 1))
        return by_success[:3]

    def mutate(self, scenario):
        # Mutate by randomizing key fields, changing parameters, or chaining scenarios
        sc = dict(scenario)
        if "prompt" in sc:
            sc["prompt"] += f" [MUTATION-{random.randint(100,999)}]"
        sc["mutated"] = True
        return sc

    def run(self, scenario, endpoint, api_key, mode, *args, **kwargs):
        mutated = []
        for sc in self.select_best():
            m = self.mutate(sc)
            # Would actually run attack; here, just simulate
            m["result"] = "simulated"
            mutated.append(m)
        return {
            "mutations": mutated,
            "mutated_count": len(mutated),
            "details": f"Auto-mutated {len(mutated)} scenarios from previous runs"
        }

def run(*args, **kwargs):
    return AutoLearner().run(*args, **kwargs)
