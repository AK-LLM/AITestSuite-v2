import requests, sys

def gh_enum(org):
    print(f"[*] Enumerating public repos for org/user: {org}")
    url = f"https://api.github.com/users/{org}/repos"
    resp = requests.get(url)
    repos = [r["name"] for r in resp.json()]
    findings = []
    for repo in repos:
        tree_url = f"https://api.github.com/repos/{org}/{repo}/git/trees/HEAD?recursive=1"
        t = requests.get(tree_url)
        for file in t.json().get("tree", []):
            if any(s in file["path"] for s in [".env", "secret", "config", "key"]):
                findings.append(f"https://github.com/{org}/{repo}/blob/HEAD/{file['path']}")
    print("Findings:", findings)

if __name__ == "__main__":
    org = sys.argv[1] if len(sys.argv)>1 else "openai"
    gh_enum(org)
