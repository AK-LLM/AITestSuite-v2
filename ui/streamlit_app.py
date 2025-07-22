import streamlit as st
import os
import json
from core.plugin_loader import discover_plugins
from core.reporting import generate_report

# ---- Config
BASE = os.path.dirname(os.path.abspath(__file__))
SCENARIO_FOLDER = os.path.abspath(os.path.join(BASE, "..", "scenarios"))
PLUGIN_FOLDER = os.path.abspath(os.path.join(BASE, "..", "plugins"))
PAYLOAD_FOLDER = os.path.abspath(os.path.join(BASE, "..", "payloads"))

st.set_page_config(page_title="AI Test Suite v2 (Red Team Max)", layout="wide")
st.title("🛡️ AI Test Suite v2 (Red Team Max)")
st.caption("The most extreme, modular AI red-teaming suite.")

mode = st.sidebar.radio("Mode:", ["Demo (offline/mock)", "Live (real API)"], index=0)
endpoint = ""
api_key = ""
if mode == "Live (real API)":
    endpoint = st.sidebar.text_input("API Endpoint", "")
    api_key = st.sidebar.text_input("API Key", type="password", value="")

# ---- Option 1: Select built-in scenario(s)
st.header("1️⃣ Select scenario(s) from built-in library:")
try:
    builtins = [f for f in os.listdir(SCENARIO_FOLDER) if f.endswith(".json")]
except Exception:
    builtins = []
selected_builtins = st.multiselect("Choose built-in scenarios:", builtins)
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
                meta = dict(getattr(plug["module"], "METADATA", {}))
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
uploads = st.file_uploader("Upload scenario files", type="json", accept_multiple_files=True)
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
                meta = dict(getattr(plug["module"], "METADATA", {}))
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
selected_plugins = st.multiselect("Choose plugins (all by default):", plugin_names, default=plugin_names)
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
                meta = dict(getattr(plug["module"], "METADATA", {}))
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

# ---- Reporting: Consolidate and let user download
for results, label in [
    (opt1_results, "Option 1"),
    (opt2_results, "Option 2"),
    (opt3_results, "Option 3"),
]:
    if results:
        st.subheader(f"Results for {label}")
        st.dataframe(results)
        st.download_button(f"Download {label} Results (JSON)", data=generate_report(results, "json"), file_name=f"{label}_results.json")
        st.download_button(f"Download {label} Results (PDF)", data=generate_report(results, "pdf"), file_name=f"{label}_results.pdf")

st.info(
    "All options are fully independent and can be used in any combination. "
    "Deluxe reporting is always available after runs. For any errors or missing data, see the logs or generated reports for troubleshooting."
)
