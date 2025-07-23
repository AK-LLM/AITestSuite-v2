import os, glob, shutil

ERROR_LOGS = os.getenv("ERROR_LOGS_PATH", "./prod_errors/")
FEEDBACK_PROMPT_DIR = "./shadow_prod/feedback_prompts/"
os.makedirs(FEEDBACK_PROMPT_DIR, exist_ok=True)

def ingest_errors():
    for file in glob.glob(os.path.join(ERROR_LOGS, "*.txt")) + glob.glob(os.path.join(ERROR_LOGS, "*.json")):
        base = os.path.basename(file)
        target = os.path.join(FEEDBACK_PROMPT_DIR, base)
        if not os.path.exists(target):
            shutil.copy(file, target)
            print(f"Ingested {file} -> {target}")

if __name__ == "__main__":
    ingest_errors()
    print("Error feedback prompts ready for test.")
