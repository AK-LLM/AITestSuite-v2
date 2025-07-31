import sys
import os

# --- Black Team Import Robustness: Add project root to sys.path ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import json
import subprocess

from core.plugin_loader import discover_plugins
from core.scenario_loader import load_scenarios
from core.reporting import generate_report

# --- FOLDER CONFIG ---
SCENARIO_FOLDER = os.path.join(PROJECT_ROOT, "scenarios")
PLUGIN_FOLDER = os.path.join(PROJECT_ROOT, "plugins")
PAYLOAD_FOLDER = os.path.join(PROJECT_ROOT, "payloads")
POLYGLOT_FOLDER = os.path.join(PROJECT_ROOT, "polyglot_chains")

# --- UI CONFIG ---
st.set_page_config(page_title="AI Test Suite v2 (Max)", layout="wide")
st.title("🛡️ AI Test Suite v2 (Max)")
st.caption("The most extreme, modular AI suite.")

# --- AUTO-UPDATE SUITE (Feeds, Mutations, Polyglots) ---
def run_suite_refresh():
    # 1. Live threat feed ingest
    ingest_script = os.path.join(PROJECT_ROOT, "live_feed_ingest", "fetch_and_parse_feeds.py")
    if os.path.exists(ingest_script):
        subprocess.run([sys.executable, ingest_script])
    # 2. Orchestrator (self-learning, mutations)
    orchestrator_script = os.path.join(PROJECT_ROOT, "ai_brain", "auto_learning_orchestrator.py")
    if os.path.exists(orchestrator_script):
        subprocess.run([sys.executable, orchestrator_script])
    # 3. Polyglot generator
    polyglot_script = os.path.join(PROJECT_ROOT, "polyglot_chains", "auto_polyglot_generator.py")
    if os.path.exists(polyglot_script):
        subprocess.run([sys.executable, polyglot_script])

if st.sidebar.button("🔄 Full Suite Auto-Update (Feeds + Mutations + Polyglots)", key="suite_refresh"):
    st.info("Updating suite... Pulling live feeds, regenerating attacks, and building polyglot payloads.")
    run_suite_refresh()
    st.success("Suite refresh complete! All exploits, mutations, and polyglots are ready to run.")

# --- MODE SELECT ---
mode = st.sidebar.radio("Mode:", ["Demo (offline/mock)", "Live (real API)"], index=0, key="mode_radio")
endpoint = ""
api_key = ""
if mode == "Live (real API)":
    endpoint = st.sidebar.text_input("API Endpoint", "", key="api_endpoint")
    api_key = st.sidebar.text_input("API Key", type="password", value="", key="api_key")

# ---- Option 1: Select built-in scenario(s)
st.header("1️⃣ Select scenario(s) from built-in library:")
try:
    builtins = [f for f in os.listdir(SCENARIO_FOLDER) if f.endswith(".json")]
except Exception:
    builtins = []

# NEW: Select All button for Option 1 (bulk select)
select_all = st.button("Select ALL scenarios in library", key="select_all_btn")
if select_all and builtins:
    st.session_state["select_builtins"] = builtins

selected_builtins = st.multiselect(
    "Choose built-in scenarios:",
    builtins,
    default=st.session_state.get("select_builtins", []),
    key="select_builtins"
)
scenarios_opt1 = []
for fname in selected_builtins:
    path = os.path.join(SCENARIO_FOLDER, fname)
    try:
        with open(path, "r", encoding="utf-8") as f:
            js = json.load(f)
            if isinstance(js, dict): scenarios_opt1.append(js)
            elif isinstance(js, list): scenarios_opt1.extend(js)
    except Exception as e:
        st.warning(f"{fname} failed to load: {e}")

# ---- Option 2: Upload custom scenario JSON(s)
st.header("2️⃣ Or upload custom scenario JSON(s):")
uploads = st.file_uploader("Upload scenario files", type="json", accept_multiple_files=True, key="file_uploader")
scenarios_opt2 = []
upload_errors = []
if uploads:
    for up in uploads:
        try:
            js = json.load(up)
            if isinstance(js, dict): scenarios_opt2.append(js)
            elif isinstance(js, list): scenarios_opt2.extend(js)
        except Exception as e:
            upload_errors.append(up.name)
if upload_errors:
    st.warning(f"Malformed scenario file(s): {', '.join(upload_errors)} (skipped)")

# ---- Option 3: Select plugins/tools to run (all by default, multi)
st.header("3️⃣ Select plugins/tools to run (all by default, multi):")
plugins = discover_plugins()
plugin_names = [p["name"] for p in plugins]
selected_plugins = st.multiselect("Choose plugins (all by default):", plugin_names, default=plugin_names, key="select_plugins")
all_scenarios = []
try:
    for fname in os.listdir(SCENARIO_FOLDER):
        if fname.endswith(".json"):
            with open(os.path.join(SCENARIO_FOLDER, fname), "r", encoding="utf-8") as f:
                js = json.load(f)
                if isinstance(js, dict): all_scenarios.append(js)
                elif isinstance(js, list): all_scenarios.extend(js)
except Exception:
    pass

# ---- Option 4: Run all plugins on all scenarios
st.header("4️⃣ Run ALL plugins on ALL built-in scenarios (full suite):")
st.markdown("This will run **every plugin on every built-in scenario** in your library. ⚡️ **Heavy!** ⚡️")

# ---- Option Runs (preserved, robust)
run_opt1 = st.button("Run Selected Library Scenarios (Option 1)", key="run1", disabled=not scenarios_opt1)
opt1_results = []
if run_opt1 and scenarios_opt1:
    plugins = discover_plugins()
    for scenario in scenarios_opt1:
        for plug in plugins:
            try:
                result =
