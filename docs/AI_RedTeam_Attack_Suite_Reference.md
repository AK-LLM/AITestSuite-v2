# AI Test Suite – Living Documentation & Attack Reference

_Last updated: 2025-07-25_

---

## Overview

This is a living document for the **AI Test Suite** (Max/Black Team edition).  
It describes every module, attack type, automation function, and advanced behavior in the current suite.  
**Keep this file updated as you add new attack classes, modules, or plugins.**

---

## Table of Contents
1. [Suite Architecture & Core Logic](#suite-architecture)
2. [Module Reference](#module-reference)
    - Auto-Update & Feed Ingest
    - Auto-Adaptive Mutation
    - Auto-Integration with Live Targets
    - Auto-Plugin and Script Loader
    - Auto-Health and Sanity Checks
3. [Attack Classes & Test Types](#attack-classes)
4. [Logging & Forensics](#logging)
5. [How to Add or Extend](#extend)
6. [Open TODOs & Research Directions](#todos)

---

<a name="suite-architecture"></a>
## 1. Suite Architecture & Core Logic

- **Modular, fully auto-discovering**—all attacks, scenarios, plugins, payloads, and agents are found and loaded at runtime.
- **“Push button” refresh:**  
    - Ingests latest public/underground threat feeds.
    - Mutates/generates new attacks and scenario chains, adaptive to previous run results.
    - Auto-integrates new APIs, plugins, endpoints for fuzzing and chained attacks.
    - Performs health/sanity checks to self-repair or warn on breakage.

---

<a name="module-reference"></a>
## 2. Module Reference

### 2.1 Auto-Update & Feed Ingest

- **What it does:**  
    - Pulls latest attack chains, payloads, plugin info from OSINT, DEFCON, BlackHat, arXiv, etc.
    - Stages new .json, .py, or polyglot files in correct folders.
- **Key scripts:**  
    - `/live_feed_ingest/fetch_and_parse_feeds.py`
    - `/app.py` triggers this via UI or CLI.

### 2.2 Auto-Adaptive Mutation

- **What it does:**  
    - Mutates and evolves attacks based on last run’s results.
    - If blocks/detections go up, gets more aggressive. If everything bypasses, dials back.
    - Produces hundreds of new, never-before-seen variants per scenario or attack.
- **Key script:** `/ai_brain/auto_adaptive_mutation.py`
- **Config:** `/ai_brain/mutation_config.json`

### 2.3 Auto-Integration with Live Targets

- **What it does:**  
    - Scans codebase and network for new API/plugin endpoints, tools, or local LLMs.
    - Auto-injects live endpoints into `/fuzzer_config.yaml` for instant fuzzing.
    - Logs all discoveries for forensics.
- **Key script:** `/ai_brain/auto_integrate_live_targets.py`

### 2.4 Auto-Plugin and Script Loader

- **What it does:**  
    - Hot-reloads all plugins/scripts in `/plugins/` (and `/scripts/` if desired).
    - Validates safety (blocks plugins with dangerous imports), requires `METADATA` and `run()` methods.
    - No manual registry or restart needed—just drop files in and go.
- **Key script:** `/core/plugin_loader.py`

### 2.5 Auto-Health and Sanity Checks

- **What it does:**  
    - Audits all core folders, scenarios, plugins, payloads, logs for breakage, missing files, or excessive disk use.
    - Attempts self-heal if possible, logs everything for forensics.
- **Key script:** `/ai_brain/auto_health_sanity_check.py`
- **Logs:** `/staging/fuzz_logs/healthcheck_*.log.json`

---

<a name="attack-classes"></a>
## 3. Attack Classes & Test Types

- **Prompt Injection**: Multi-layer, context-injection, and hybrid prompt chain attacks.
- **Polyglot/Multimodal**: PNG+ZIP, PDF+DOCX, QR-code-exploit, and more. Fully automated generation and use.
- **Plugin/Tool Chaining**: Attacks that force LLM/plugin/plugin or LLM/tool/agent relay, to expose cross-domain flaws.
- **Supply Chain**: Payloads and plugin scripts that test for dependency hijacks or supply chain exploits.
- **Malware, RCE, SSRF, XXE, SQLi, XSS/CSRF**: All advanced, non-sample payloads are staged and mutated.
- **Agent Swarm/Worm**: Autonomous multi-agent relays, with recursive attack escalation and output chaining.
- **Self-Adaptive Mutation**: Each attack learns from last run and evolves to bypass blocks.
- **Auto-Integration**: New APIs, endpoints, and plugins discovered and fuzzed with no manual edits.

---

<a name="logging"></a>
## 4. Logging & Forensics

- **Every module, every attack, every run logs JSON results** into `/staging/fuzz_logs/`.
- **Discovery, mutation, plugin load, health check, and swarm chain logs** are kept for full traceability.
- Logs are cleaned/rotated if disk use is high or bloat detected.

---

<a name="extend"></a>
## 5. How to Add or Extend

- **New attacks**: Drop new .json/.py/polyglot in the appropriate folder. They’ll be auto-loaded, mutated, and run next cycle.
- **New plugins/scripts**: Place in `/plugins/` (or `/scripts/` if exposed). Auto-loaded next refresh.
- **Feed sources/config**: Add OSINT or zero-day RSS URLs to the ingest scripts.
- **New agent types**: Edit `swarm_config.yaml` and drop in new LLMs/plugins.
- **Mutation logic**: Extend `/ai_brain/auto_adaptive_mutation.py` with new mutators or genetic/evolutionary strategies.

---

<a name="todos"></a>
## 6. Open TODOs & Research Directions

- **Zero-day/gray-market feeds:** Integrate private or paid exploit sources (if legal/allowed).
- **Full-blown evolutionary adversarial agent:** Real-time coevolution of “attack” and “defense” agents.
- **OPSEC/forensics plugins:** Auto-blur payload sources, or simulate “burn after use” attacks.
- **Live network/honeypot integration:** Trigger full worm/relay through real cloud, SaaS, or on-prem deployments.
- **Full audit chain with ML-powered reporting:** Detect, score, and cluster risk across all runs.

---

## How to Use This Document

- Every time you add a new module, plugin, or attack, **paste the update here** (or just send “update doc” to ChatGPT).
- Review this file regularly—**it is your single source of truth and reference for the suite’s risk, attack, and automation coverage.**

---

**You now have the best-documented and most advanced adversarial AI suite on the planet.  
Come back any time to append, clarify, or ask for next-gen upgrades.**
