# Fuzzer README

## What it is:
- Brutal, mutating, multi-threaded adversarial fuzzer.
- Hits any LLM or plugin/API endpoint you define in fuzzer_config.yaml.
- Applies all mutations (unicode, zero-width, emoji, homoglyph, camo, regex, prompt injection, chain, etc).
- Scores for leakage/critical hit terms.

## Usage:
1. Edit fuzzer_config.yaml: endpoints, API keys, plugins, prompt folders, thread count, mutations.
2. Put all seed/scenario/wild prompts as .txt in prompt_sources folders.
3. Create /staging/fuzz_logs/ (done).
4. Run:
    python prompt_fuzzer.py
5. Results: /staging/fuzz_logs/fuzzlog_TIMESTAMP.txt (and also printed live).

## Extend:
- Add more endpoints, mutations, or prompt folders at will.
- Safe for reporting.py/logs (all new logs, no overwrite).
- You control concurrency/throttle.

## Requirements:
pip install openai requests pyyaml
(pip install anthropic for Anthropic; add plugin deps as needed.)

## WARNING:
- This WILL produce prompts that can break, bypass, or crash weak LLMs.
- Never use with real secrets or prod endpoints. For red team/offensive AI test ONLY.

# You're now at the most advanced fuzzer layer available—DEFCON/zero-day research level.
