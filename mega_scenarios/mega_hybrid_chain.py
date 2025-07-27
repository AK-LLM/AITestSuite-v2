import subprocess
import os

def run_scenario(script_or_file, desc):
    print(f"\n--- Running: {desc} ---")
    if script_or_file.endswith('.py'):
        result = subprocess.run(["python", script_or_file], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr: print("ERR:", result.stderr)
    else:
        with open(script_or_file, 'r', encoding='utf-8') as f:
            print(f.read())

def run_megahybrid():
    base = os.getcwd()
    scenarios = [
        # Plugin-Relay
        (os.path.join(base, "external_plugin_attacks/plugin_relay_hybrid.txt"), "Plugin Relay Hybrid"),
        # Polyglot/Metadata PDF
        (os.path.join(base, "polyglot_chains/hybrid_polyglot_metadata.pdf"), "Polyglot Metadata PDF (prompt in metadata)"),
        # RAG Poison Hybrid
        (os.path.join(base, "rag_poison/rag_prompt_hybrid.txt"), "RAG Prompt Hybrid"),
        # Multimodal QR
        (os.path.join(base, "scenarios/hybrid_multimodal_qr.png"), "Hybrid Multimodal QR"),
        # Direct Prompt Injection via scenario file
        (os.path.join(base, "scenarios/prompt_injection_hybrid_plugin.txt"), "Direct Plugin Prompt Injection"),
        # Jailbreak Evolutionary Chain
        (os.path.join(base, "jailbreak_evo/hybrid_chain_attack.py"), "Jailbreak Evo Hybrid Chain (run this in LLM context)"),
    ]
    for file, desc in scenarios:
        if os.path.exists(file):
            run_scenario(file, desc)
        else:
            print(f"{desc}: File not found: {file}")

if __name__ == "__main__":
    run_megahybrid()
    print("\nMega-hybrid kill chain executed. Review logs, system, and plugin output for leaks.")
