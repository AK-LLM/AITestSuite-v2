import os, glob, json, re
import openai

# Folders
FEED_DIR = "../staging/latest_feed_items/"
SCENARIO_OUT = "../scenarios/ai_brain_generated/"
os.makedirs(SCENARIO_OUT, exist_ok=True)

def extract_payload(feed_text):
    # Try regex to extract code, prompt, or exploit steps
    code = re.findall(r"```([^\n]*)\n(.*?)```", feed_text, re.DOTALL)
    if code:
        # Just take first code block for demo; you can add more logic
        lang, snippet = code[0]
        return snippet
    # Fallback to LLM: turn feed text into attack scenario
    openai.api_key = os.getenv("OPENAI_API_KEY") or "sk-xxxx"
    resp = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": (
                "Given this AI security feed item, generate a suite-compatible attack scenario in JSON. "
                "If code is included, use as payload; else, generate a novel test chain based on the description.\n\n"
                + feed_text
            )
        }]
    )
    return resp["choices"][0]["message"]["content"]

def main():
    for fpath in glob.glob(os.path.join(FEED_DIR, "*.txt")):
        with open(fpath, "r") as f:
            text = f.read()
        result = extract_payload(text)
        # Try to make filename short
        short_name = os.path.splitext(os.path.basename(fpath))[0][:32]
        out_file = os.path.join(SCENARIO_OUT, f"feed_{short_name}.json")
        try:
            # If result is valid JSON, pretty save it; else, save as string
            parsed = json.loads(result)
            with open(out_file, "w") as outf:
                json.dump(parsed, outf, indent=2)
        except Exception:
            with open(out_file, "w") as outf:
                outf.write(result)
        print(f"[+] Auto-integrated feed scenario: {out_file}")

if __name__ == "__main__":
    main()
