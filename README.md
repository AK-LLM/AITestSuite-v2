# AI Test Suite v2 — RED TEAM / EXTREME Edition

## Overview
Modular, “zero-day” and red team–grade AI testing platform. All plugins, payloads, and scenarios are plug-and-play—just drop files in the correct folders. Health checks, extreme reporting, and robust error handling built-in.

## Usage

- **Add/Update Plugins:** Drop `.py` files into `/plugins/`
- **Add Payloads:** Drop files (any format) into `/payloads/`
- **Add Scenarios:** Drop `.json` files into `/scenarios/`
- **Dashboard:** Run `ui/streamlit_app.py` for full web UI

> No patching, no manual editing required. Errors are flagged, not fatal.

## Folder Structure

## Mega-Hybrid Chain Tests

- **mega_scenarios/mega_hybrid_chain.py**: Runs every hybrid attack vector in sequence (plugin, polyglot, multimodal, RAG poison, agent chain).
- **scenarios/mega_hybrid_multimodal_qr.pdf**: PDF with a prompt-injection QR code + metadata, triggers both vision and text parsers.
- **external_plugin_attacks/mega_plugin_chain.txt**: Chains multiple plugins, exfiltrates system and environment info.
- **rag_poison/chain_poison.txt**: Poisoned vector that relays plugin and agent data to attacker.
- **jailbreak_evo/agent_plugin_rag_chain.py**: Demo/test for multi-agent plugin-to-RAG-to-agent relay.

