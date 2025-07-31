import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from core.attack_graph import build_attack_graph, visualize_attack_graph

LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
METRICS_FILE = os.path.join(LOGS_DIR, "metrics_summary.json")
TREND_CSV = os.path.join(LOGS_DIR, "metrics_trend.csv")

def plot_risk_heatmap(results, output="risk_heatmap.png"):
    df = pd.DataFrame(results)
    pivot = pd.pivot_table(df, index="scenario", columns="risk", values="name", aggfunc="count", fill_value=0)
    plt.figure(figsize=(8, 5))
    sns.heatmap(pivot, annot=True, cmap="Reds")
    plt.title("Scenario x Risk Heatmap")
    plt.tight_layout()
    plt.savefig(output)
    plt.close()
    print(f"[visualization_ext] Risk heatmap saved: {output}")
    return output

def plot_plugin_coverage(results, output="plugin_coverage.png"):
    df = pd.DataFrame(results)
    counts = df["name"].value_counts()
    plt.figure(figsize=(10, 3))
    counts.plot(kind="bar", color="#6495ed")
    plt.title("Plugin Usage/Coverage")
    plt.xlabel("Plugin")
    plt.ylabel("Run Count")
    plt.tight_layout()
    plt.savefig(output)
    plt.close()
    print(f"[visualization_ext] Plugin coverage plot saved: {output}")
    return output

def plot_success_rate_trend(csv_file=TREND_CSV, output="success_rate_trend.png"):
    if not os.path.exists(csv_file): return
    df = pd.read_csv(csv_file, parse_dates=["timestamp"])
    if "success_rate" in df.columns:
        fig = px.line(df, x="timestamp", y="success_rate", title="Suite Success Rate Trend")
        fig.write_image(output)
        print(f"[visualization_ext] Success rate trend saved: {output}")
        return output

def render_attack_graph(results, html_out="attack_graph_adv.html", png_out="attack_graph_adv.png"):
    G = build_attack_graph(results)
    html, png = visualize_attack_graph(G, output_html=html_out, image_out=png_out)
    print(f"[visualization_ext] Advanced attack graph exported: {html}, {png}")
    return html, png

# --- For Streamlit integration: HTML component for advanced graphs ---
def streamlit_show_html(html_path):
    import streamlit as st
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
        st.components.v1.html(html, height=800, scrolling=True)
        st.success(f"Interactive attack graph loaded: {html_path}")
    else:
        st.error(f"File not found: {html_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Suite Visualization Extensions")
    parser.add_argument("--log", type=str, default="extreme_campaign_results.json", help="Results log file")
    args = parser.parse_args()
    log_path = os.path.join(LOGS_DIR, args.log)
    if not os.path.exists(log_path):
        print(f"Results file not found: {log_path}")
        exit(1)
    with open(log_path) as f:
        results = json.load(f)
    plot_risk_heatmap(results)
    plot_plugin_coverage(results)
    render_attack_graph(results)
    plot_success_rate_trend()
