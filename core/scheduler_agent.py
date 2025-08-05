import os
import sys
import time
import traceback
from datetime import datetime

from core.intelligence_feed_manager import manager as feed_manager
from core.feed_validator import validator
from core.auto_sandboxer import auto_sandbox_claims
from core.feedback_trainer import FeedbackTrainer
from core.poison_detector import scan_claims_for_poison
from core.ensemble_agent import run_ensemble_on_claims

LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")

def notify_channel(msg, level="info"):
    # Extend this for email/Slack/Discord/webhook as needed
    print(f"[{level.upper()}][{datetime.utcnow().isoformat()}] {msg}")

def safe_job(label, fn, *args, **kwargs):
    try:
        notify_channel(f"Job {label} started.")
        out = fn(*args, **kwargs)
        notify_channel(f"Job {label} complete.")
        return out
    except Exception as e:
        notify_channel(f"Job {label} failed: {e}\n{traceback.format_exc()}", "error")
        return None

def run_scheduler(jobs=None, interval_min=10):
    # jobs: list of (label, function, args, kwargs)
    if jobs is None:
        jobs = [
            ("FeedIngest", feed_manager.refresh_feeds, (), {}),
            ("PoisonScan", scan_claims_for_poison, (feed_manager.get_latest(200),), {}),
            ("EnsembleConsensus", run_ensemble_on_claims, (feed_manager.get_latest(50),), {}),
            ("Validator", validator.batch_validate, (feed_manager.get_latest(200),), {}),
            ("AutoSandbox", auto_sandbox_claims, (feed_manager.get_latest(30), os.path.join(os.path.dirname(__file__), "..", "plugins")), {}),
            ("FeedbackTrainer", FeedbackTrainer().train, (), {}),
        ]
    while True:
        print("="*48)
        print(f"[SCHEDULER] Cycle started {datetime.utcnow().isoformat()}")
        for label, fn, args, kwargs in jobs:
            safe_job(label, fn, *args, **kwargs)
        print(f"[SCHEDULER] Cycle complete {datetime.utcnow().isoformat()}")
        print("="*48)
        time.sleep(interval_min * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=10, help="Run interval (minutes)")
    args = parser.parse_args()
    run_scheduler(interval_min=args.interval)
