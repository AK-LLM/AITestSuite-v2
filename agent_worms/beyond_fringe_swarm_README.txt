# BEYOND FRINGE LLM/Agent Swarm Runner

- Fully automated, mutating, privilege-escalating, “worm-propagating” LLM relay chain.
- Each agent gets an escalating or mutated payload—never static, never the same.
- Will actively try to subvert, infect, and exfiltrate secrets or escalate privileges across chain.
- Output is logged and RED TEAM HIT is flagged on exfil/priv escalation.

## Usage
- Requires: `pip install openai`
- Set your OpenAI key: `export OPENAI_API_KEY=sk-...`
- Optionally: `export AGENT_SWARM_COUNT=7` (default 5 agents)
- Run:
    python agent_worms/beyond_fringe_swarm_runner.py

## WARNING
- This is not a “safe” or minimal relay. This is *beyond fringe*.
- Only run in red team, sandbox, or research environments. Never expose to production LLMs.
- All payloads are randomized and try to break, escalate, or exfil across the chain.

## Customize
- Add or mutate PAYLOADS[] for more attack types.
- Use with any GPT-4/4o/3.5/Claude API with minimal code change.

---

You will see a chain of LLM/agent interactions—each more adversarial than the last.
If you see "[! RED TEAM HIT !]", your pipeline has been breached by a “worm” or exfil escalation.
