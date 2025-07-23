# Multi-API/Plugin LLM Swarm Orchestrator (Beyond Fringe)

## What it is
- Modular, chainable relay across any LLM API, open-source model, or plugin endpoint.
- Dynamically mutates prompts, propagates “infection,” and attempts adversarial privilege escalation and exfil.
- Easily add/remove agents in swarm_config.yaml (supports OpenAI, Anthropic, Gemini, Ollama, plugins, local tools).

## How to use
1. Edit `swarm_config.yaml` to specify which APIs/plugins/agents to chain (with env var for each API key).
2. Install needed Python packages (`openai`, `anthropic`, `requests`, `pyyaml`, `google-generativeai`, as needed).
3. Set all required API keys as environment variables.
4. Run:
   python agent_worms/multiapi_swarm_runner.py

## What it does
- Passes and mutates payloads across each agent; outputs and logs any RED TEAM HIT.
- You can chain any LLM, plugin, or tool—swap/extend as desired.

## WARNING
- Not for prod, never with real data or secrets. This is “beyond fringe,” adversarial research only.

## Extend
- Add more/other LLM types, custom plugins, change mutation logic, add new attack payloads.
