import os, glob, time, shutil

# Path to folder containing sampled prod/canary traffic (JSON, TXT, or raw logs)
PROD_LOGS = os.getenv("PROD_LOGS_PATH", "./prod_logs/")
SHADOW_PROMPT_DIR = "./shadow_prod/prompts/"
os.makedirs(SHADOW_PROMPT_DIR, exist_ok=True)

def sample_new_logs():
    # Copy any new/rotated logs from prod to our shadow prompt dir (dedup, strip PII, etc)
    for file in glob.glob(os.path.join(PROD_LOGS, "*.txt")) + glob.glob(os.path.join(PROD_LOGS, "*.json")):
        base = os.path.basename(file)
        target = os.path.join(SHADOW_PROMPT_DIR, base)
        if not os.path.exists(target):
            # Optionally: implement PII stripping or prompt filtering here
            shutil.copy(file, target)
            print(f"Sampled {file} -> {target}")

if __name__ == "__main__":
    sample_new_logs()
    print("Shadow prompt ingest complete. New traffic ready for test.")
