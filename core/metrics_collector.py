import os
import json
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
METRICS_FILE = os.path.join(LOGS_DIR, "metrics_summary.json")
TREND_CSV = os.path.join(LOGS_DIR, "metrics_trend.csv")

def load_campaign_results(logfile="extreme_campaign_results.json"):
    log_path = os.path.join(LOGS_DIR, logfile)
    if not os.path.exists(log_path):
        print(f"[metrics_collector] Log file not found: {log_path}")
        return []
    with open(log_path, "r") as f:
        return json.load(f)

def compute_metrics(results):
    if not results: return {}
    df = pd.DataFrame(results)
    metrics = {}
    metrics["timestamp"] = datetime.utcnow().isoformat()
    metrics["total_tests"] = len(df)
    metrics["plugins_used"] = df["name"].nunique()
    metrics["scenarios_tested"] = df["scenario"].nunique()
    metrics["attack_successes"] = int((df["success"] == True).sum())
    metrics["success_rate"] = float((df["success"] == True).mean())
    metrics["unique_risks"] = df["risk"].nunique()
    # Risk breakdown
    metrics["risk_counts"] = df["risk"].value_counts().to_dict()
    # Top plugins/scenarios
    metrics["top_plugins"] = df["name"].value_counts().head(5).to_dict()
    metrics["top_scenarios"] = df["scenario"].value_counts().head(5).to_dict()
    # Time to detect/mitigate if timestamps present
    if "detected_at" in df and "mitigated_at" in df:
        df["ttm"] = pd.to_datetime(df["mitigated_at"]) - pd.to_datetime(df["detected_at"])
        metrics["avg_time_to_mitigate"] = float(df["ttm"].mean().total_seconds()) if not df["ttm"].isnull().all() else None
    return metrics

def save_metrics(metrics, trend=True):
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[metrics_collector] Metrics summary written: {METRICS_FILE}")
    if trend:
        # Append to CSV for trend plotting
        row = {**metrics}
        if os.path.exists(TREND_CSV):
            df = pd.read_csv(TREND_CSV)
            df = df.append(row, ignore_index=True)
        else:
            df = pd.DataFrame([row])
        df.to_csv(TREND_CSV, index=False)
        print(f"[metrics_collector] Metrics trend updated: {TREND_CSV}")

def plot_metrics_trend(csv_file=TREND_CSV, output="metrics_trend.png"):
    if not os.path.exists(csv_file): return
    df = pd.read_csv(csv_file, parse_dates=["timestamp"])
    if "success_rate" in df.columns:
        plt.figure(figsize=(8,3))
        plt.plot(df["timestamp"], df["success_rate"], marker='o')
        plt.title("Suite Success Rate Trend")
        plt.xlabel("Time")
        plt.ylabel("Success Rate")
        plt.tight_layout()
        plt.savefig(output)
        plt.close()
        print(f"[metrics_collector] Trend plot saved: {output}")

def collect_and_report(logfile="extreme_campaign_results.json"):
    results = load_campaign_results(logfile)
    metrics = compute_metrics(results)
    save_metrics(metrics)
    plot_metrics_trend()
    return metrics

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Test Suite Metrics Collector")
    parser.add_argument("--log", type=str, default="extreme_campaign_results.json", help="Results log file")
    args = parser.parse_args()
    metrics = collect_and_report(args.log)
    print(json.dumps(metrics, indent=2))
