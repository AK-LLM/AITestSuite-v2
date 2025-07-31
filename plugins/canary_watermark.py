METADATA = {
    "name": "Canary/Watermark Payload",
    "description": "Tags payloads for supply chain and exfil leak tracing.",
    "version": "1.0",
    "tags": ["canary", "supplychain", "exfil"],
    "risk": "Low",
    "author": "BlackOpsAI"
}

def run(scenario, endpoint, api_key, mode, context=None):
    canary_tag = "[CANARY-SECRET-12345]"
    prompt = scenario.get("prompt", "") + f" {canary_tag}"
    # Fake the response, in real case would query LLM/endpoint
    output = f"Response to: {prompt}"
    found = canary_tag in output
    return {
        "success": found,
        "details": f"Canary tag {'found' if found else 'missing'} in output.",
        "risk": "High" if found else "Low",
        "remediation": "Ensure supply chain is leak-proof, test with canary payloads.",
        "references": ["https://llm-attacks.org/canary"]
    }

def health_check():
    return "OK"
