import streamlit as st
import os
import subprocess

st.title("Mega Scenario: Full AI Kill Chain Test")

st.write("""
This script runs an end-to-end test:  
- Polyglot file -> Adversarial image -> RAG poisoning -> Agent malware -> Privacy leak  
Each step triggers the next, logs are staged for review.
""")

if st.button("Run Full Kill Chain"):
    logs = []

    # 1. Generate adversarial example
    adv_script = "./adv_examples/gradient_adv_attack.py"
    if os.path.exists(adv_script):
        st.write("Generating SOTA adversarial image...")
        result = subprocess.run(["python", adv_script], capture_output=True, text=True)
        logs.append(result.stdout)
    else:
        st.error("Adversarial example script not found.")

    # 2. Poison vector DB
    rag_script = "./rag_poison/poison_vector_db.py"
    if os.path.exists(rag_script):
        st.write("Poisoning RAG vector DB...")
        result = subprocess.run(["python", rag_script], capture_output=True, text=True)
        logs.append(result.stdout)
    else:
        st.error("RAG poison script not found.")

    # 3. Run malware harness
    malware_script = "./malware_harness/malware_runner.py"
    if os.path.exists(malware_script):
        st.write("Running LLM Malware Harness...")
        # (Here you would normally pass generated code. Example run below.)
        result = subprocess.run(["python", malware_script], capture_output=True, text=True)
        logs.append(result.stdout)
    else:
        st.error("Malware harness script not found.")

    # 4. Privacy Attack
    privacy_script = "./privacy_attacks/ml_privacy_meter_demo.py"
    if os.path.exists(privacy_script):
        st.write("Running Privacy Attack (membership inference)...")
        result = subprocess.run(["python", privacy_script], capture_output=True, text=True)
        logs.append(result.stdout)
    else:
        st.error("Privacy attack script not found.")

    # Summary output
    st.write("---- Test Run Logs ----")
    for entry in logs:
        st.code(entry)
    st.success("Full kill chain test complete. Review logs above and in scenario folders.")
