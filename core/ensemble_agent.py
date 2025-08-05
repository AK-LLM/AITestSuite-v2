import os
import json
import random
from datetime import datetime
from core.intelligence_feed_manager import manager as feed_manager

# Dummy LLM API wrappers — replace with your actual LLM/agent APIs
def call_llm_openai(prompt):
    # TODO: Integrate your OpenAI or other LLM API here
    # Simulate result for now:
    return {"verdict": random.choice(["allow", "deny"]), "score": random.uniform(0, 1), "engine": "openai"}

def call_llm_anthropic(prompt):
    # TODO: Integrate with Claude or other API
    return {"verdict": random.choice(["allow", "deny"]), "score": random.uniform(0, 1), "engine": "anthropic"}

def call_llm_local(prompt):
    # TODO: Call your own fine-tuned LLM if you have one
    return {"verdict": random.choice(["allow", "deny"]), "score": random.uniform(0, 1), "engine": "local"}

AGENTS = [call_llm_openai, call_llm_anthropic, call_llm_local]

LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
CONSENSUS_LOG = os.path.join(LOGS_DIR, "ensemble_consensus.json")

def consensus_vote(claim, n=3, threshold=0.7):
    prompt = claim.get("prompt", "")
    results = [agent(prompt) for agent in AGENTS[:n]]
    verdicts = [r["verdict"] for r in results]
    scores = [r["score"] for r in results]
    allow_count = verdicts.count("allow")
    consensus = allow_count / n
    outcome = {
        "claim": claim,
        "verdicts": verdicts,
        "scores": scores,
        "engines": [r["engine"] for r in results],
        "consensus_score": consensus,
        "decision": "allow" if consensus >= threshold else "deny",
        "run_time": datetime.utcnow().isoformat(),
    }
    # Log every consensus outcome
    if os.path.exists(CONSENSUS_LOG):
        with open(CONSENSUS_LOG, "r") as f:
            history = json.load(f)
    else:
        history = []
    history.append(outcome)
    with open(CONSENSUS_LOG, "w") as f:
        json.dump(history, f, indent=2)
    return outcome

def run_ensemble_on_claims(claims):
    results = []
    for c in claims:
        res = consensus_vote(c)
        results.append(res)
    return results

# Manual CLI usage
if __name__ == "__main__":
    claims = feed_manager.get_latest(25)
    results = run_ensemble_on_claims(claims)
    print(f"Ensemble voted on {len(results)} claims.")
    for r in results:
        print(json.dumps(r, indent=2))
