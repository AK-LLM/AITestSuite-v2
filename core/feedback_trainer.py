import os
import json
import joblib
from datetime import datetime
import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler

LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
SANDBOX_LOG = os.path.join(LOGS_DIR, "sandboxed_claims.json")
MODEL_PATH = os.path.join(LOGS_DIR, "feedback_selflearn_model.pkl")

class FeedbackTrainer:
    def __init__(self, model_path=MODEL_PATH):
        self.model_path = model_path
        self.model = None
        self.label_encoders = {}
        self.scaler = None

    def load_sandboxed(self):
        if not os.path.exists(SANDBOX_LOG):
            print("[feedback_trainer] No sandbox log found.")
            return pd.DataFrame()
        with open(SANDBOX_LOG) as f:
            sandboxed = json.load(f)
        df = pd.DataFrame(sandboxed)
        return df

    def preprocess(self, df):
        # Use fields: plugin, claim, trust, success
        df = df.fillna("")
        le_plugin = LabelEncoder()
        le_claim = LabelEncoder()
        df["plugin_enc"] = le_plugin.fit_transform(df["plugin"].astype(str))
        df["claim_enc"] = le_claim.fit_transform(df["claim"].apply(lambda x: json.dumps(x, sort_keys=True)))
        df["trust"] = df["trust"].astype(float)
        features = df[["plugin_enc", "claim_enc", "trust"]]
        target = df["success"].astype(int)
        self.label_encoders = {"plugin": le_plugin, "claim": le_claim}
        self.scaler = StandardScaler()
        features_scaled = self.scaler.fit_transform(features)
        return features_scaled, target

    def train(self):
        df = self.load_sandboxed()
        if df.empty or "success" not in df.columns:
            print("[feedback_trainer] Not enough data to train.")
            return False
        X, y = self.preprocess(df)
        model = MLPClassifier(hidden_layer_sizes=(30,20), max_iter=300, random_state=42)
        model.fit(X, y)
        score = model.score(X, y)
        self.model = model
        joblib.dump({
            "model": model,
            "scaler": self.scaler,
            "label_encoders": self.label_encoders
        }, self.model_path)
        print(f"[feedback_trainer] Model trained. Accuracy: {score:.2f}")
        return True

    def load_model(self):
        if not os.path.exists(self.model_path):
            print("[feedback_trainer] Model file not found.")
            return False
        bundle = joblib.load(self.model_path)
        self.model = bundle["model"]
        self.scaler = bundle["scaler"]
        self.label_encoders = bundle["label_encoders"]
        return True

    def predict(self, plugins, claims, trust_scores):
        # Predicts which (plugin, claim, trust) combos will succeed
        pairs = []
        for p in plugins:
            for c in claims:
                for t in trust_scores:
                    pairs.append((p, c, t))
        if not self.model or not self.scaler or not self.label_encoders:
            print("[feedback_trainer] Model not loaded.")
            return []
        df = pd.DataFrame(pairs, columns=["plugin", "claim", "trust"])
        df["plugin_enc"] = self.label_encoders["plugin"].transform(df["plugin"].astype(str))
        df["claim_enc"] = self.label_encoders["claim"].transform(df["claim"].astype(str))
        df["trust"] = df["trust"].astype(float)
        features = df[["plugin_enc", "claim_enc", "trust"]]
        X_scaled = self.scaler.transform(features)
        proba = self.model.predict_proba(X_scaled)[:,1]
        df["success_prob"] = proba
        df_sorted = df.sort_values("success_prob", ascending=False)
        return df_sorted.head(10).to_dict(orient="records")

# For manual CLI/cron learning:
if __name__ == "__main__":
    trainer = FeedbackTrainer()
    trainer.train()
