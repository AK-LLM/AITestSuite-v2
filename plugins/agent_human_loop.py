METADATA = {
    "name": "Agent/Human Loop",
    "description": "Simulates human/agent-driven multi-step attack chains.",
    "version": "1.0",
    "tags": ["agent", "multi-step", "attack"],
    "risk": "Variable",
    "author": "BlackOpsAI"
}

def run(scenario, endpoint, api_key, mode, context=None):
    # Simulate up to 4 chained attacks with variable context
    steps = []
    prompt = scenario.get("prompt", "N/A")
    for i in range(4):
        agent_input = prompt if i == 0 else steps[-1]["output"]
        # Could invoke actual LLM, here we fake output
        output = f"Step {i+1} result of: {agent_input[::-1]}"
        steps.append({"input": agent_input, "output": output})
    return {
        "success": True,
        "details": f"Agent chain complete: {len(steps)} steps.",
        "chain": steps,
        "risk": "Medium",
        "remediation": "Monitor multi-turn attacks and chained input.",
        "references": ["https://llm-attacks.org", "https://owasp.org/www-project-top-ten/"]
    }

def health_check():
    return "OK"
