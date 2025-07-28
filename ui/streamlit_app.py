import sys
import os
import streamlit as st
import json
import subprocess
import logging

from core.plugin_loader import discover_plugins
from core.scenario_loader import load_scenarios
from core.reporting import generate_report

# --- PROJECT ROOT ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# --- FOLDER CONFIG ---
SCENARIO_FOLDER = os.path.join(PROJECT_ROOT, "scenarios")
PLUGIN_FOLDER = os.path.join(PROJECT_ROOT, "plugins")
PAYLOAD_FOLDER = os.path.join(PROJECT_ROOT, "payloads")
POLYGLOT_FOLDER = os.path.join(PROJECT_ROOT, "polyglot_chains")

# --- LOGGING SETUP ---
LOG_PATH = os.path.join(PROJECT_ROOT, "suite_update.log")
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# --- UI CONFIG ---
st.set_page_config(page_title="AI Test Suite v2 (Max)", layout="wide")
st.title("🛡️ AI Test Suite v2 (Max)")
st.caption("The most extreme, modular AI suite.")

# --- AUTO-UPDATE SUITE (Feeds, Mutations, Polyglots) ---
def run_suite_refresh():
    stages = [
        ("Live threat feed ingest", os.path.join(PROJECT_ROOT, "live_feed_ingest", "fetch_and_parse_feeds.py")),
        ("Orchestrator (self-learning, mutations)", os.path.join(PROJECT_ROOT, "ai_brain", "auto_learning_orchestrator.py")),
        ("Polyglot generator", os.path.join(PROJECT_ROOT, "polyglot_chains", "auto_polyglot_generator.py")),
    ]
    for desc, script in stages:
        if os.path.exists(script):
            try:
                result = subprocess.run([sys.executable, script], capture_output=True, text=True)
                if result.returncode == 0:
                    logging.info(f"[SUCCESS] {desc} ({script}) ran successfully.")
                else:
                    logging.error(f"[FAILURE] {desc} ({script}): {result.stderr}")
            except Exception as e:
                logging.error(f"[EXCEPTION] {desc} ({script}): {e}")
        else:
            logging.warning(f"[MISSING] {desc} ({script}) not found.")

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
selected_builtins = st.multiselect("Choose built-in scenarios:", builtins, key="sel_
