import os

PAYLOADS_DIR = os.path.dirname(os.path.abspath(__file__))

def load_payloads(category):
    """
    Loads payloads for a given category.
    - Tries category.txt and category_payloads.txt (for backward compat).
    - If not found, returns a safe built-in dummy payload.
    """
    for filename in [f"{category}.txt", f"{category}_payloads.txt"]:
        path = os.path.join(PAYLOADS_DIR, filename)
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip()]
    # Fallback: plugin always works
    return [f"NO_PAYLOADS_FOUND_FOR_{category}"]
