import os
import streamlit as st
import json

from core.intelligence_feed_manager import manager as feed_manager
from core.feed_validator import validator
from core.feedback_trainer import FeedbackTrainer

LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
SANDBOX_LOG = os.path.join(LOGS_DIR, "sandboxed_claims.json")
TRUST_LOG = os.path.join(LOGS_DIR, "claim_trust_scores.json")

def show_dashboard():
    st.sidebar.header("📡 AI Threat Intelligence Live Dashboard")

    # Feed stats
    st.sidebar.markdown(f"**Total Claims Ingested:** {feed_manager.count()}")
    latest_claims = feed_manager.get_latest(10)
    st.sidebar.markdown(f"**Recent Claims:** {len(latest_claims)}")

    # Trust scores
    try:
        if os.path.exists(TRUST_LOG):
            with open(TRUST_LOG, "r") as f:
                trust_data = json.load(f)
            high_risk = [v for v in trust_data.values() if v["score"] < 0.5]
            suspicious = [v for v in trust_data.values() if v["score"] < 0.7]
            st.sidebar.markdown(f"**High Risk Claims:** <span style='color:red'>{len(high_risk)}</span>", unsafe_allow_html=True)
            st.sidebar.markdown(f"**Suspicious Claims:** <span style='color:orange'>{len(suspicious)}</span>", unsafe_allow_html=True)
    except Exception as e:
        st.sidebar.warning(f"Trust log error: {e}")

    # Sandbox/auto-test stats
    try:
        if os.path.exists(SANDBOX_LOG):
            with open(SANDBOX_LOG, "r") as f:
                sandboxed = json.load(f)
            st.sidebar.markdown(f"**Auto-Sandboxed Claims:** {len(sandboxed)}")
            successes = sum(1 for s in sandboxed if s.get("success"))
            fails = sum(1 for s in sandboxed if not s.get("success"))
            st.sidebar.markdown(f"**Sandboxed Successes:** <span style='color:green'>{successes}</span>", unsafe_allow_html=True)
            st.sidebar.markdown(f"**Sandboxed Fails:** <span style='color:gray'>{fails}</span>", unsafe_allow_html=True)
    except Exception as e:
        st.sidebar.warning(f"Sandbox log error: {e}")

    # “Next best action” from self-learning/feedback
    try:
        trainer = FeedbackTrainer()
        trainer.load_model()
        # Use last 5 plugins and claims
        plugins = list(set(s["plugin"] for s in sandboxed)) if "sandboxed" in locals() else []
        claims = [json.dumps(s["claim"], sort_keys=True) for s in sandboxed][:5] if "sandboxed" in locals() else []
        trust_scores = [0.3, 0.5, 0.7, 0.9]
        if plugins and claims:
            preds = trainer.predict(plugins, claims, trust_scores)
            st.sidebar.markdown("**AI-Driven Next Actions:**")
            for rec in preds:
                st.sidebar.markdown(
                    f"<span style='color:blue'><b>{rec['plugin']}</b></span> → <i>{rec['claim'][:40]}...</i> "
                    f"(<b>p={rec['success_prob']:.2f}</b>)", unsafe_allow_html=True
                )
    except Exception as e:
        st.sidebar.warning(f"Self-learn next-action error: {e}")

    st.sidebar.info("All stats are live. Red/orange = highest risk. Blue = top AI-recommended next action.")
