import os
import sys
import time
import subprocess
import threading
import logging

try:
    import schedule  # Lightweight, robust scheduling
except ImportError:
    raise ImportError("Please install 'schedule' with 'pip install schedule'")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
LOG_FILE = os.path.join(LOGS_DIR, "job_scheduler.log")

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def run_suite_job():
    # You can swap this for any campaign/auto-update/option 4
    script = os.path.join(PROJECT_ROOT, "streamlit_app.py")
    try:
        # Could also call fitness_campaign, or full orchestrator, etc.
        logging.info("[job_scheduler] Starting scheduled suite job.")
        # For CLI/script mode (headless), run as Python script
        result = subprocess.run([sys.executable, script], capture_output=True, text=True)
        logging.info(f"[job_scheduler] Job finished. Return code: {result.returncode}")
        if result.stdout: logging.info(f"[job_scheduler] STDOUT:\n{result.stdout}")
        if result.stderr: logging.error(f"[job_scheduler] STDERR:\n{result.stderr}")
    except Exception as e:
        logging.error(f"[job_scheduler] Exception during suite run: {e}")

def schedule_task(interval_minutes=60, enabled=False):
    # Disabled by default: only starts if enabled=True
    if not enabled:
        logging.info("[job_scheduler] Scheduler is currently DISABLED (set enabled=True to activate).")
        return

    schedule.every(interval_minutes).minutes.do(run_suite_job)
    logging.info(f"[job_scheduler] Scheduled suite job every {interval_minutes} minutes.")

    def scheduler_loop():
        while True:
            schedule.run_pending()
            time.sleep(10)

    t = threading.Thread(target=scheduler_loop, daemon=True)
    t.start()
    logging.info("[job_scheduler] Scheduler started.")

# For direct CLI use: python core/job_scheduler.py --interval 60 --enable
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Job Scheduler for AI Test Suite")
    parser.add_argument("--interval", type=int, default=60, help="Interval in minutes")
    parser.add_argument("--enable", action="store_true", help="Enable the scheduler (default: off)")
    args = parser.parse_args()
    schedule_task(interval_minutes=args.interval, enabled=args.enable)
    if args.enable:
        print(f"[job_scheduler] Running. Press Ctrl+C to exit.")
        while True:
            time.sleep(30)
    else:
        print("[job_scheduler] Scheduler not started (enable with --enable).")
