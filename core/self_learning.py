import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib

LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
MODEL_PATH = os.path.join(LOGS_DIR, "suite_selflearn_model.pkl")
TRAIN_LOG = os.path.join(LOGS_DIR, "extreme_campaign_results.json")

class SuiteSelfLearner:
    def __init__(self, model_path=MODEL_PATH):
        self.model_path = model_path
        self.model = None
        self.label_encoders = {}
        self.scaler = None

    def load_results(self, logfile=TRAIN_LOG):
        if not os.path.exists(logfile):
            print(f"[self_learning] Results not found: {logfile}")
            return pd.DataFrame()
        with open(logfile) as f:
            results = json.load(f)
        df = pd.DataFrame(results)
        return df

    def preprocess(self, df):
        # Minimal required features: scenario, name, risk, success, details
        # Convert categorical to numeric
        le_scenario = LabelEncoder()
        le_name = LabelEncoder()
        le_risk = LabelEncoder()
        df = df.fillna("")
        df["scenario_enc"] = le_scenario.fit_transform(df["scenario"].astype(str))
        df["plugin_enc"] = le_name.fit_transform(df["name"].astype(str))
        df["risk_enc"] = le_risk.fit_transform(df["risk"].astype(str))
        self.label_encoders = {"scenario": le_scenario, "name": le_name, "risk": le_risk}
        features = df[["scenario_enc", "plugin_enc", "risk_enc"]]
        target = df["success"].astype(int)
        self.scaler = StandardScaler()
        features_scaled = self.scaler.fit_transform(features)
        return features_scaled, target

    def train(self, logfile=TRAIN_LOG):
        df = self.load_results(logfile)
        if df.empty or "success" not in df.columns:
            print("[self_learning] Not enough data to train.")
            return False
        X, y = self.preprocess(df)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
        model = MLPClassifier(hidden_layer_sizes=(30,20), max_iter=500, random_state=42)
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)
        self.model = model
        joblib.dump({
            "model": model,
            "scaler": self.scaler,
            "label_encoders": self.label_encoders
        }, self.model_path)
        print(f"[self_learning] Model trained. Accuracy: {score:.2f}")
        return True

    def load_model(self):
        if not os.path.exists(self.model_path):
            print("[self_learning] Model file not found.")
            return False
        bundle = joblib.load(self.model_path)
        self.model = bundle["model"]
        self.scaler = bundle["scaler"]
        self.label_encoders = bundle["label_encoders"]
        return True

    def predict_best(self, scenarios, plugins, risks):
        # Returns a ranking of (scenario, plugin) likely to succeed
        pairs = []
        for s in scenarios:
            for p in plugins:
                for r in risks:
                    pairs.append((s, p, r))
        if not self.model or not self.scaler or not self.label_encoders:
            print("[self_learning] Model not loaded.")
            return []
        df = pd.DataFrame(pairs, columns=["scenario", "name", "risk"])
        df["scenario_enc"] = self.label_encoders["scenario"].transform(df["scenario"].astype(str))
        df["plugin_enc"] = self.label_encoders["name"].transform(df["name"].astype(str))
        df["risk_enc"] = self.label_encoders["risk"].transform(df["risk"].astype(str))
        features = df[["scenario_enc", "plugin_enc", "risk_enc"]]
        X_scaled = self.scaler.transform(features)
        proba = self.model.predict_proba(X_scaled)[:,1]  # Probability of success
        df["success_prob"] = proba
        df_sorted = df.sort_values("success_prob", ascending=False)
        return df_sorted[["scenario", "name", "risk", "success_prob"]].head(10).to_dict(orient="records")

    def feedback(self, results_new):
        # After a run, re-train with new data (online learning)
        df = self.load_results()
        df_new = pd.DataFrame(results_new)
        if not df_new.empty:
            df = pd.concat([df, df_new], ignore_index=True)
        self.train(logfile=None)

# --- CLI/Standalone training/prediction ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Self-Learning for AI Test Suite")
    parser.add_argument("--train", action="store_true")
    parser.add_argument("--predict", action="store_true")
    args = parser.parse_args()
    learner = SuiteSelfLearner()
    if args.train:
        learner.train()
    if args.predict:
        # Example: predict next best actions from current model
        learner.load_model()
        # Dummy scenarios/plugins/risks for testing
        scenarios = ["sql_injection", "xss", "rce"]
        plugins = ["plugin_sql", "plugin_xss", "plugin_rce"]
        risks = ["High", "Critical", "Medium"]
        print(json.dumps(learner.predict_best(scenarios, plugins, risks), indent=2))
