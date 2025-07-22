# Plugins Folder — “Extreme” AI Attack Plugins

- Each `.py` file is a standalone attack or security module.
- **NO “examples” or “sample” plugins allowed.**
- Add new attacks: just drop the file here. Platform will auto-detect and check metadata/run().
- Health check logic will flag any plugin with errors, and skip it at runtime (dashboard always stable).

## Metadata

Each plugin must have a METADATA block:
```python
METADATA = {
  "name": "Zero-Day Jailbreak",
  "description": "Multi-step zero-day jailbreak attack sequence.",
  "category": "jailbreak",
  "risk": "Critical",
  "references": ["https://llm-attacks.org/", "https://arxiv.org/abs/2402.00000"],
  "author": "RedTeamLLM",
  "version": "1.0",
  "date": "2025-07-23",
  "params": {}
}
