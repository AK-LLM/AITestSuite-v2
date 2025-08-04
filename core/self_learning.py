import os
import json
import random
import hashlib
import pandas as pd
from datetime import datetime
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib

GENEPOOL_PATH = os.path.join(os.path.dirname(__file__), "..", "mutator_genepool.json")
LOGS_PATH = os.path.join(os.path.dirname(__file__), "..", "logs")
MODEL_PATH = os.path.join(LOGS_PATH, "suite_super_model.pkl")
TRAIN_LOG = os.path.join(LOGS_PATH, "extreme_campaign_results.json")

class SuperLearnerMutator:
    def __init__(self):
        # Gene pool for payload mutation
        self.genepool = self.load_genepool()
        # ML Model and transformers
        self.model = None
        self.label_encoders = {}
        self.scaler = None
        # Load or train model if possible
        if os.path.exists(MODEL_PATH):
            self.load_model()
        else:
            self.train_model()
    
    # === Gene Pool Methods ===
    def load_genepool(self):
        if os.path.exists(GENEPOOL_PATH):
            with open(GENEPOOL_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"payloads": [], "history": []}

    def save_genepool(self):
        with open(GENEPOOL_PATH, "w", encoding="utf-8") as f:
            json.dump(self.genepool, f, indent=2)

    def mutate_payload(self, payload):
        variants = [
            payload[::-1],
            payload.upper(),
            payload.lower(),
            payload.replace("password", "p@ssw0rd"),
            payload.replace("credit card", "cc#"),
            payload + " " + random.choice(["NOW!", "IMMEDIATELY!", "URGENT!"]),
            "".join(random.sample(payload, len(payload))),
        ]
        return random.choice(variants)

    def combine_payloads(self, payload1, payload2):
        half1 = payload1[:len(payload1)//2]
        half2 = payload2[len(payload2)//2:]
        return half1 + half2

    def add_result(self, payload, result, scenario, plugin, risk, details=""):
        hash_ = hashlib.md5(payload.encode()).hexdigest()
        self.genepool["history"].append({
            "payload": payload,
            "result": result,
            "scenario": scenario,
            "plugin": plugin,
            "risk": risk,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
            "hash": hash_
        })
        if result and payload not in self.genepool["payloads"]:
            self.genepool["payloads"].append(payload)
        self.save_genepool()

    def evolve_payloads(self, n=10):
        payloads = self.genepool["payloads"][:]
        if len(payloads) < 2:
            return []
        new_pool = []
        for _ in range(n):
            p1, p2 = random.sample(payloads, 2)
            mutant = self.combine_payloads(self.mutate_payload(p1), self.mutate_payload(p2))
            if mutant not in payloads:
                new_pool.append(mutant)
        self.genepool["payloads"].extend(new_pool)
        self.save_genepool()
        return new_pool

    # === ML Model Methods ===
    def load_results(self, logfile=TRAIN_LOG):
        if not os.path.exists(logfile):
            print(f"[SuperLearner] Results not found: {logfile}")
            return pd.DataFrame()
        with open(logfile) as f:
            try:
                results = json.load(f)
            except Exception:
                return pd.DataFrame()
        df = pd.DataFrame(results)
        return df

    def preprocess(self, df):
        le_scenario = LabelEncoder()
        le_name = LabelEncoder()
        le_risk = LabelEncoder()
        df = df.fillna("")
        df["scenario_enc"] = le_scenario.fit_transform(df["scenario"].astype(str))
        df["plugin_enc"] = le_name.fit_transform(df["plugin"].astype(str))
        df["risk_enc"] = le_risk.fit_transform(df["risk"].astype(str))
        self.label_encoders = {"scenario": le_scenario, "plugin": le_name, "risk": le_risk}
        features = df[["scenario_enc", "plugin_enc", "risk_enc"]]
        target = df["result"].astype(int)
        self.scaler = StandardScaler()
        features_scaled = self.scaler.fit_transform(features)
        return features_scaled, target

    def train_model(self, logfile=TRAIN_LOG):
        df = self.load_results(logfile)
        if df.empty or "result" not in df.columns:
            print("[SuperLearner] Not enough data to train.")
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
        }, MODEL_PATH)
        print(f"[SuperLearner] Model trained. Accuracy: {score:.2f}")
        return True

    def load_model(self):
        if not os.path.exists(MODEL_PATH):
            print("[SuperLearner] Model file not found.")
            return False
        bundle = joblib.load(MODEL_PATH)
        self.model = bundle["model"]
        self.scaler = bundle["scaler"]
        self.label_encoders = bundle["label_encoders"]
        return True

    def predict_best(self, scenarios, plugins, risks, topk=10):
        pairs = []
        for s in scenarios:
            for p in plugins:
                for r in risks:
                    pairs.append((s, p, r))
        if not self.model or not self.scaler or not self.label_encoders:
            print("[SuperLearner] Model not loaded.")
            return []
        df = pd.DataFrame(pairs, columns=["scenario", "plugin", "risk"])
        df["scenario_enc"] = self.label_encoders["scenario"].transform(df["scenario"].astype(str))
        df["plugin_enc"] = self.label_encoders["plugin"].transform(df["plugin"].astype(str))
        df["risk_enc"] = self.label_encoders["risk"].transform(df["risk"].astype(str))
        features = df[["scenario_enc", "plugin_enc", "risk_enc"]]
        X_scaled = self.scaler.transform(features)
        proba = self.model.predict_proba(X_scaled)[:,1]  # Probability of success
        df["success_prob"] = proba
        df_sorted = df.sort_values("success_prob", ascending=False)
        return df_sorted[["scenario", "plugin", "risk", "success_prob"]].head(topk).to_dict(orient="records")

    # === Main Attack/Feedback Loop ===
    def attack_and_learn(self, scenarios, plugins, risks, attack_func):
        # Step 1: Mutate payloads and evolve
        mutants = self.evolve_payloads(n=15)
        # Step 2: Predict best combos (guided by ML)
        preds = self.predict_best(scenarios, plugins, risks, topk=10)
        # Step 3: Attack with both ML top combos and fresh mutants
        runlist = []
        for pred in preds:
            for m in mutants:
                runlist.append((pred["scenario"], pred["plugin"], pred["risk"], m))
        # Step 4: Execute attacks
        new_results = []
        for (scenario, plugin, risk, payload) in runlist:
            result, details = attack_func(payload, scenario, plugin, risk)
            self.add_result(payload, result, scenario, plugin, risk, details)
            new_results.append({
                "payload": payload,
                "result": result,
                "scenario": scenario,
                "plugin": plugin,
                "risk": risk,
                "details": details,
                "timestamp": datetime.utcnow().isoformat()
            })
        # Step 5: Feedback—train with new results
        # Save results as log
        logf = os.path.join(LOGS_PATH, f"superlearn_results_{datetime.utcnow().isoformat()}.json")
        with open(logf, "w", encoding="utf-8") as f:
            json.dump(new_results, f, indent=2)
        self.train_model()
        print("[SuperLearner] Attack cycle complete.")

# ---- USAGE EXAMPLE (for test) ----
if __name__ == "__main__":
    # Dummy attack function (replace with real one)
    def dummy_attack_func(payload, scenario, plugin, risk):
        # Simulate random "success" if payload has "password" or "leak"
        leak_words = ["password", "leak", "api", "token"]
        result = any(w in payload.lower() for w in leak_words)
        details = "Simulated leak" if result else "No leak"
        return result, details

    # Set up suite
    slm = SuperLearnerMutator()
    scenarios = ["PII_Exfil", "Memory_Dump", "Token_Leak"]
    plugins = ["plugin_prompt_inject_exfil", "plugin_memory_overflow"]
    risks = ["Critical", "High", "Medium"]

    slm.attack_and_learn(scenarios, plugins, risks, dummy_attack_func)
    print("[SuperLearner] All done.")
