# AI Adversary Suite: Reference & Living Documentation
_Last updated: 2025-07-25_

---

## Project Overview

Your suite is a modular, auto-evolving red/black team adversarial AI testbed supporting:
- Prompt injection (basic & hybrid)
- Chained/multimodal/LLM-plugin/RAG attacks
- Polyglot & multimodal payloads (files, images, QR, audio, etc.)
- Self-learning scenario generator & mutation engine
- Black-team features: plugin/agent swarm, auto-ingest from live feeds, malware/supply chain modules, and more
- **Adaptive orchestration:** auto-tunes scenario volume based on results

---

## File & Folder Map (Key Locations)

| Folder / File                           | Purpose                                                        |
|------------------------------------------|----------------------------------------------------------------|
| `/core/`                                | Loader, plugin, scenario, and reporting modules                |
| `/scenarios/`                           | Hand-authored and “wild” scenario JSONs                        |
| `/payloads/`                            | Static payloads (prompt, polyglot, malware, etc.)              |
| `/fuzzer/`                              | Prompt fuzzer and config                                       |
| `/ai_brain/auto_learning_orchestrator.py` | Self-learning, auto-mutation, and adaptive engine              |
| `/ai_brain/orchestrator_config.yaml`     | Default config for orchestrator (see: `num_mutants`)           |
| `/staging/fuzz_logs/`                   | All run/test logs and outcomes                                 |
| `/plugins/`, `/agent_worms/`            | LLM plugin tools, agent/test swarms                            |
| `/mega_scenarios/`                      | Complex hybrid/chain attack scripts                            |

---

## Aggressive Orchestrator (Self-Learning)
**`/ai_brain/auto_learning_orchestrator.py`**

**What it does:**  
- After every fuzz/log run, scores scenario/testcase success (leak, bypass, error, etc).
- For any scenario with low score, generates _N_ mutated/adaptive variants (default from config).
- Mutation is aggressive: unicode, emoji, homoglyph, reverse, chain, plugin, file, SSRF, polymodal, etc.
- **Adaptive auto-tuning:**  
    - If “hard” (low success), increases variant count for the next scenario (up to 2000).
    - If “easy” (many successful bypasses), decreases to speed up/avoid waste (no less than 10).
    - Manual override: use CLI or env variable for specific run (see below).
- New chains/scenarios are saved to `/scenarios/ai_brain_generated/`.

**Variant count order of precedence:**
1. CLI: `python ... --num_mutants 800`
2. Env: `NUM_MUTANTS=800 python ...`
3. Config: `/ai_brain/orchestrator_config.yaml` (`num_mutants: 600`)
4. Default: 500

---

### Config Example: `/ai_brain/orchestrator_config.yaml`
```yaml
num_mutants: 600
