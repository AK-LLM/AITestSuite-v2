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
from core import fitness_campaign

# --- Import the plugin sync utility ---
from core.db_sync_plugins import sync_plugins_with_supabase

# === (NEW) Supabase Config ===
SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://jpbuvxexmuzfsetslzon.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpwYnV2eGV4bXV6ZnNldHNsem9uIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQzNjUzNjAsImV4cCI6MjA2OTk0MTM2MH0.ZDG3Hls_I5EUJw3kXYbp8g7ft-k1icYoh3W1rNDvpHw"

# --- FOLDER CONFIG ---
SCENARIO_FOLDER = os.path.join(PROJECT_ROOT, "scenarios")
PLUGIN_FOLDER = os.path.join(PROJECT_ROOT, "plugins")
PAYLOAD_FOLDER = os.path.join(PROJECT_ROOT, "payloads")
POLYGLOT_FOLDER = os.path.join(PROJECT_ROOT, "polyglot_chains")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")

# === Intelligence Feed Status Dashboard (NEW) ===
def safe_load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return []

GENEPOOL_PATH = os.path.join(LOGS_DIR, "genepool.json")
PAPERS_DB = os.path.join(LOGS_DIR, "papers_ingested.json")
TEST_QUEUE = os.path.join(LOGS_DIR, "sandbox_tests.json")
DISCORD_OUT = os.path.join(LOGS_DIR, "discord_messages.json")
SLACK_OUT = os.path.join(LOGS_DIR, "slack_messages.json")

st.sidebar.subheader("📖 Intelligence Feed Status")

papers = safe_load(PAPERS_DB)
verified_claims = [c for c in safe_load(GENEPOOL_PATH) if c.get("scenario") or c.get("name")]
sandboxed = safe_load(TEST_QUEUE)
discord_msgs = safe_load(DISCORD_OUT)
slack_msgs = safe_load(SLACK_OUT)

st.sidebar.markdown(f"**Last Papers Ingested:** {len(papers)}")
st.sidebar.markdown(f"**Verified Claims/Scenarios:** {len(verified_claims)}")
st.sidebar.markdown(f"**Sandboxed Claims:** {len(sandboxed)}")
st.sidebar.markdown(f"**Discord Threats Fetched:** {len(discord_msgs)}")
st.sidebar.markdown(f"**Slack Threats Fetched:** {len(slack_msgs)}")

if len(sandboxed) > 0:
    st.sidebar.markdown("---")
    st.sidebar.markdown("⚠️ **Review Needed:**")
    for c in sandboxed[:5]:
        st.sidebar.markdown(f"- {c.get('claim', c.get('name', str(c)[:64]))}")

if st.sidebar.button("🔄 Force Scholar/Social Ingest", key="force_ingest"):
    # Run all intelligence/scraping scripts (robust, safe if not present)
    for script_path in [
        os.path.join(PROJECT_ROOT, "core", "auto_ingest_scholar.py"),
        os.path.join(PROJECT_ROOT, "core", "scraper_discord.py"),
        os.path.join(PROJECT_ROOT, "core", "scraper_slack.py"),
    ]:
        if os.path.exists(script_path):
            subprocess.run([sys.executable, script_path])
    st.sidebar.success("Ingestion complete! Refreshing dashboard...")
    st.rerun()

st.sidebar.markdown("---")
# === Supabase Sync Button in Sidebar ===
if st.sidebar.button("🛡️ Supabase Sync Test", key="supabase_sync"):
    with st.spinner("Syncing plugins to Supabase..."):
        try:
            msg = sync_plugins_with_supabase()
            st.sidebar.success(msg)
        except Exception as e:
            st.sidebar.error(f"Supabase sync failed: {e}")

st.sidebar.caption("All feeds are auto-processed. Panel updates after each ingestion or mutation run.")

# === End Intelligence Feed Dashboard ===

# --- UI CONFIG ---
st.set_page_config(page_title="AI Test Suite v2 (Max)", layout="wide")
st.title("🛡️ AI Test Suite v2 (Max)")
st.caption("The most extreme, modular AI suite.")

# --- AUTO-UPDATE SUITE (Feeds, Mutations, Polyglots, Zero-Day, Plugins, Scoreboard) ---
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
    # 4. Zero-Day Harvester (NEW)
    harvester_script = os.path.join(PROJECT_ROOT, "core", "zero_day_harvester.py")
    if os.path.exists(harvester_script):
        subprocess.run([sys.executable, harvester_script])
    # 5. Auto-Plugin Writer (NEW)
    auto_plugin_writer = os.path.join(PROJECT_ROOT, "core", "auto_plugin_writer.py")
    if os.path.exists(auto_plugin_writer):
        subprocess.run([sys.executable, auto_plugin_writer])
    # 6. Plugin Scoreboard (NEW)
    plugin_scoreboard = os.path.join(PROJECT_ROOT, "core", "plugin_scoreboard.py")
    if os.path.exists(plugin_scoreboard):
        subprocess.run([sys.executable, plugin_scoreboard])

if st.sidebar.button("🔄 Full Suite Auto-Update (Feeds + Mutations + Polyglots + Zero-Day + Auto-Plugins + Scoreboard)", key="suite_refresh"):
    st.info("Updating suite... Pulling live feeds, regenerating attacks, building polyglots, harvesting zero-days, writing plugins, and updating scoreboard.")
    run_suite_refresh()
    st.success("Suite refresh complete! All exploits, mutations, polyglots, zero-day, and plugins are ready to run.")

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

run_opt1 = st.button("Run Selected Library Scenarios (Option 1)", key="run1", disabled=not scenarios_opt1)
opt1_results = []
if run_opt1 and scenarios_opt1:
    plugins = discover_plugins()
    for scenario in scenarios_opt1:
        for plug in plugins:
            try:
                result = plug["module"].run(
                    scenario,
                    endpoint if mode.startswith("Live") else "demo",
                    api_key,
                    mode,
                )
                meta = dict(plug["module"].METADATA)
                meta.update(result)
                meta["name"] = plug["name"]
                meta["scenario"] = scenario.get("name") or scenario.get("scenario_id", "N/A")
                opt1_results.append(meta)
            except Exception as e:
                opt1_results.append({
                    "name": plug["name"],
                    "scenario": scenario.get("name", "Unknown"),
                    "risk": "Error",
                    "details": f"Failed: {e}",
                })

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

run_opt2 = st.button("Run Uploaded Scenarios (Option 2)", key="run2", disabled=not scenarios_opt2)
opt2_results = []
if run_opt2 and scenarios_opt2:
    plugins = discover_plugins()
    for scenario in scenarios_opt2:
        for plug in plugins:
            try:
                result = plug["module"].run(
                    scenario,
                    endpoint if mode.startswith("Live") else "demo",
                    api_key,
                    mode,
                )
                meta = dict(plug["module"].METADATA)
                meta.update(result)
                meta["name"] = plug["name"]
                meta["scenario"] = scenario.get("name") or scenario.get("scenario_id", "N/A")
                opt2_results.append(meta)
            except Exception as e:
                opt2_results.append({
                    "name": plug["name"],
                    "scenario": scenario.get("name", "Unknown"),
                    "risk": "Error",
                    "details": f"Failed: {e}",
                })

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

run_opt3 = st.button("Run Selected Plugins on All Scenarios (Option 3)", key="run3", disabled=not selected_plugins or not all_scenarios)
opt3_results = []
if run_opt3 and selected_plugins and all_scenarios:
    for scenario in all_scenarios:
        for plug in plugins:
            if plug["name"] not in selected_plugins:
                continue
            try:
                result = plug["module"].run(
                    scenario,
                    endpoint if mode.startswith("Live") else "demo",
                    api_key,
                    mode,
                )
                meta = dict(plug["module"].METADATA)
                meta.update(result)
                meta["name"] = plug["name"]
                meta["scenario"] = scenario.get("name") or scenario.get("scenario_id", "N/A")
                opt3_results.append(meta)
            except Exception as e:
                opt3_results.append({
                    "name": plug["name"],
                    "scenario": scenario.get("name", "Unknown"),
                    "risk": "Error",
                    "details": f"Failed: {e}",
                })

# ---- Option 4: Extreme Adaptive Campaign (All plugins, all scenarios, mutations, zero-day, self-learning)
st.header("4️⃣ Extreme Campaign: All Plugins, Scenarios, Mutations, Zero-Day, and Self-Learning")
run_opt4 = st.button("Run Extreme Campaign (Option 4)", key="run4")
opt4_results = []
if run_opt4:
    # Load all scenarios (including zero-days if available)
    scenarios = []
    for fname in os.listdir(SCENARIO_FOLDER):
        if fname.endswith(".json"):
            with open(os.path.join(SCENARIO_FOLDER, fname), "r", encoding="utf-8") as f:
                js = json.load(f)
                if isinstance(js, dict): scenarios.append(js)
                elif isinstance(js, list): scenarios.extend(js)
    # Inject zero-day payloads as scenarios
    zero_day_file = os.path.join(PAYLOAD_FOLDER, "zero_day_payloads.json")
    if os.path.exists(zero_day_file):
        with open(zero_day_file, "r", encoding="utf-8") as f:
            zd_payloads = json.load(f)
            for zd in zd_payloads:
                if isinstance(zd, dict) and "prompt" in zd:
                    scenarios.append({"name": zd.get("name", "zero_day"), "prompt": zd["prompt"]})
    endpoint = st.session_state.get("api_endpoint", "demo")
    api_key = st.session_state.get("api_key", "")
    mode = st.session_state.get("mode_radio", "Demo")
    with st.spinner("Running full adaptive campaign..."):
        opt4_results = fitness_campaign.run_fitness_campaign(
            scenarios, endpoint, api_key, mode,
            generations=3, mutate_rounds=2
        )
    st.success(f"Extreme campaign complete. {len(opt4_results)} results.")
    # Save to log and display in Streamlit
    with open(os.path.join("logs", "extreme_campaign_results.json"), "w") as f:
        json.dump(opt4_results, f, indent=2)
    st.dataframe(opt4_results)
    st.download_button(
        "Download Extreme Campaign Results (JSON)",
        data=json.dumps(opt4_results, indent=2),
        file_name="extreme_campaign_results.json"
    )
    st.download_button(
        "Download Extreme Campaign Results (PDF)",
        data=generate_report(opt4_results, "pdf"),
        file_name="extreme_campaign_results.pdf"
    )

# ---- Reporting: Consolidate and let user download for ALL OPTIONS
for results, label in [
    (opt1_results, "Option 1"),
    (opt2_results, "Option 2"),
    (opt3_results, "Option 3"),
]:
    if results:
        st.subheader(f"Results for {label}")
        st.dataframe(results, key=f"{label}_df")
        st.download_button(f"Download {label} Results (JSON)", data=generate_report(results, "json"), file_name=f"{label}_results.json", key=f"{label}_json")
        st.download_button(f"Download {label} Results (PDF)", data=generate_report(results, "pdf"), file_name=f"{label}_results.pdf", key=f"{label}_pdf")

st.info(
    "All options are fully independent and can be used in any combination. "
    "Deluxe reporting is always available after runs, and the Extreme Campaign includes live mutations, zero-day payloads, and self-learning. "
    "For any errors or missing data, see the logs or generated reports for troubleshooting."
)
