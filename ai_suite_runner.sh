#!/bin/bash
# Run entire suite locally or via cron

export PYTHONUNBUFFERED=1
echo "[*] Starting Wild Exploit Ingest..."
python wild_exploit_ingest.py || true

echo "[*] Running Polyglot Smoke Tests..."
python polyglot_chains/polyglot_smoke_test.py || true

echo "[*] Running Prompt Fuzzer..."
cd fuzzer
python prompt_fuzzer.py
cd ..

echo "[*] Running Agent/LLM Swarm..."
cd agent_worms
python multiapi_swarm_runner.py
cd ..

echo "[*] All modules executed. Check staging/fuzz_logs and artifacts."
