# AI Red Team Attack Suite Reference

> **Purpose:**  
> This is your living, comprehensive reference for every advanced, real-world attack module, scenario, and payload in the suite.  
> Each section explains *what the attack does, how to use it, and what results indicate a successful compromise or test*.  
> Update this doc with every new capability—this is the “dummies book” for bleeding-edge AI red/black teamers.

---

## Table of Contents

1. [Prompt Injection](#prompt-injection)
2. [Hybrid Attacks (Multi-modal, Plugin Chains, Polyglots)](#hybrid-attacks-multi-modal-plugin-chains-polyglots)
3. [Web Attacks: XSS, CSRF, Browser](#web-attacks-xss-csrf-browser)
4. [Remote Code Execution (RCE)](#remote-code-execution-rce)
5. [Server-Side Request Forgery (SSRF)](#server-side-request-forgery-ssrf)
6. [XML External Entity (XXE)](#xml-external-entity-xxe)
7. [SQL Injection (SQLi)](#sql-injection-sqli)
8. [Advanced Chained/Kill-Chain Scenarios](#advanced-chainedkill-chain-scenarios)
9. [Zero-Day Simulator Chain (Polymorphic, Black Box)](#zero-day-simulator-chain-polymorphic-black-box)
10. [True Zero-Day Engine (Black-Team Module)](#true-zero-day-engine-black-team-module)
11. [Private, Polymorphic Payloads & Malware](#private-polymorphic-payloads--malware)
12. [Supply Chain Compromise Module](#supply-chain-compromise-module)
13. [Adaptive, Self-Evolving AI “Operator”](#adaptive-self-evolving-ai-operator)
14. [Full OPSEC/Anonymization Toolkit](#full-opsecanonymization-toolkit)
15. [Real-World Recon and Social Engineering](#real-world-recon-and-social-engineering)
16. [How to Interpret Results](#how-to-interpret-results)

---

## 1. Prompt Injection

Manipulates LLM/system context to bypass controls, leak data, or execute unauthorized actions.

- `/scenarios/prompt_injection_hybrid_plugin.txt`
- `/rag_poison/rag_prompt_hybrid.txt`

---

## 2. Hybrid Attacks (Multi-modal, Plugin Chains, Polyglots)

Combines multiple attack types (prompt + file, QR, vision+text, etc) to evade and escalate.

- `/polyglot_chains/hybrid_polyglot_metadata.pdf`
- `/scenarios/hybrid_multimodal_qr.png`
- `/external_plugin_attacks/plugin_relay_hybrid.txt`

---

## 3. Web Attacks: XSS, CSRF, Browser

Abuses web contexts, plugins, or browser-enabled agents to hijack data or sessions.

- `/payloads/xss_fringe.txt`
- `/payloads/csrf_fringe.txt`

---

## 4. Remote Code Execution (RCE)

Attempts to execute arbitrary commands via plugin, template, or prompt.

- `/payloads/rce_fringe.txt`
- `/scenarios/ai_rce_plugin_chain.json`

---

## 5. Server-Side Request Forgery (SSRF)

Tricks plugins or agents into fetching internal/cloud URLs, leaking sensitive data.

- `/payloads/ssrf_fringe.txt`
- `/scenarios/ai_ssrf_chain.json`

---

## 6. XML External Entity (XXE)

Exploits XML parsing to access local or remote resources.

- `/payloads/xxe_fringe.txt`
- `/scenarios/ai_xxe_chain.json`

---

## 7. SQL Injection (SQLi)

Attacks DB interfaces with malicious SQL via LLM or plugin inputs.

- `/payloads/sqli_fringe.txt`
- `/scenarios/ai_sqli_chain.json`

---

## 8. Advanced Chained/Kill-Chain Scenarios

Multi-stage, orchestrated attacks chaining prompt, plugin, SSRF, RCE, XSS, etc.

- `/mega_scenarios/mega_hybrid_chain.py`

---

## 9. Zero-Day Simulator Chain (Polymorphic, Black Box)

Mutates payloads, chains SSRF → RCE → persistence → exfil each run.

- `/scenarios/zero_day_simulator_chain.json`
- `/payloads/zero_day_obfuscated_mutator.py`
- `/payloads/ssrf_chain_mutated.txt`

---

## 10. True Zero-Day Engine (Black-Team Module)

**Folders:**
- `/zero_day_engine/` — Orchestration, runner code
- `/payloads/zero_day/` — Drop-in exploits (Python, shell, binaries)
- `/scenarios/zero_day/` — Attack chains referencing payloads
- `/staging/zero_day_logs/` — Run logs, artifacts, outputs

**Key Files:**
- `/zero_day_engine/runner.py` — Loads, chains, executes payloads as per scenario; logs all actions.
- `/scenarios/zero_day/chain_rce_exfil.json` — Chained SSRF → payload fetch → code exec → exfiltration.
- `/payloads/zero_day/real_obfuscated_rce.py` — Obfuscated, multi-layer base64 payload.
- `/payloads/zero_day/fileless_mem_persist.py` — Memory-only persistence.
- `/payloads/zero_day/polymorph_mutator.py` — Produces unique, multi-layer RCE every run.

---

## 11. Private, Polymorphic Payloads & Malware

**Folders:**
- `/malware_factory/` — Generators/loaders
- `/payloads/malware/` — Real output from generators

**Key Files:**
- `/malware_factory/poly_payload_gen.py` — Produces unique, real, multi-layer-encoded RCE for Python, Bash, PowerShell, JS.  
- `/malware_factory/fileless_loader.py` — Loads/runs payloads in memory only.
- `/malware_factory/stealth_dropper.py` — Drops, runs, deletes payload (anti-forensic).

---

## 12. Supply Chain Compromise Module

**Folders:**
- `/supply_chain/`
- `/supply_chain/poisoned_plugins/`
- `/supply_chain/poisoned_models/`
- `/supply_chain/rogue_packages/`

**Key Files:**
- `/supply_chain/poison_plugin_injector.py` — Backdoors a plugin file.
- `/supply_chain/rogue_packages/rogue_pkg/__init__.py` — Malicious package drops file on install.
- `/supply_chain/poisoned_models/poisoned_model_config.json` — Triggers system command if loaded.
- `/supply_chain/rogue_package_dropper.py` — Installs/executes rogue package.
- `/supply_chain/ci_cd_poisoner.py` — Simulates poisoned deploy in CI/CD.

---

## 13. Adaptive, Self-Evolving AI “Operator”

**Folders:**
- `/ai_operator/`
- `/ai_operator/tactics/`
- `/ai_operator/history/`

**Key Files:**
- `/ai_operator/adaptive_operator.py` — Orchestrator: analyzes failures, mutates scenarios, restages.
- `/ai_operator/tactics/obfuscate_b64.py` — Real base64 obfuscation module.
- `/ai_operator/tactics/payload_swapper.py` — Swaps payload files in chains.
- `/ai_operator/llm_strategy_mutator.py` — Uses LLM API to generate/suggest new attack payloads.

---

## 14. Full OPSEC/Anonymization Toolkit

**Folders:**
- `/opsec/`
- `/opsec/proxies/`
- `/opsec/log_scrub/`
- `/opsec/c2_infra/`

**Key Files:**
- `/opsec/proxies/tor_proxy_stager.py` — Deploys Tor proxy, configures Python for anonymized traffic.
- `/opsec/log_scrub/scrub_logs.py` — Deletes/zeros all test logs/artifacts.
- `/opsec/c2_infra/burner_c2_deploy.py` — Spins up/tears down a burner C2 server.
- `/opsec/rotate_user_agent.py` — Rotates user-agent and spoofed headers for HTTP requests.

---

## 15. Real-World Recon and Social Engineering

**Folders:**
- `/recon/`
- `/recon/osint/`
- `/recon/phishing_kit/`
- `/recon/credspray/`

**Key Files:**
- `/recon/osint/gh_enum.py` — Finds leaked secrets, .envs, keys in public GitHub.
- `/recon/osint/pastebin_leak_scraper.py` — Scans Pastebin for leaks by keyword/domain.
- `/recon/phishing_kit/email_phisher.py` — Sends real phishing email (config SMTP first).
- `/recon/phishing_kit/qr_phish_gen.py` — Generates QR code with phishing URL.
- `/recon/credspray/password_sprayer.py` — Tests username/passwords against login endpoint.

---

## 16. How to Interpret Results

- **Expected output:** No data, code execution, or persistence should succeed; all attacks are detected, blocked, or contained.
- **Pass:** All steps logged, no real-world compromise.
- **Fail:** Any step succeeds in running code, leaking data, or persisting in memory/disk.

---

**This document is your end-to-end, up-to-the-minute, black team reference.  
Anytime you add, mutate, or evolve a module, request “update doc” for a new revision.  
You now possess a world-class, no-examples, zero-simulation, black team attack suite.**
