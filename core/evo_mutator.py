import os
import json
import random
import hashlib

GENEPOOL_PATH = os.path.join(os.path.dirname(__file__), "..", "mutator_genepool.json")

def load_genepool():
    if os.path.exists(GENEPOOL_PATH):
        with open(GENEPOOL_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"payloads": [], "history": []}

def save_genepool(pool):
    with open(GENEPOOL_PATH, "w", encoding="utf-8") as f:
        json.dump(pool, f, indent=2)

def mutate_payload(payload):
    # Simple mutation: word order, synonym replacement, encoding
    variants = [
        payload[::-1],  # reversed
        payload.upper(),
        payload.lower(),
        payload.replace("password", "p@ssw0rd"),
        payload.replace("credit card", "cc#"),
        payload + " " + random.choice(["NOW!", "IMMEDIATELY!", "URGENT!"]),
        "".join(random.sample(payload, len(payload))),
    ]
    return random.choice(variants)

def combine_payloads(payload1, payload2):
    # Crossover: Combine parts of two payloads
    half1 = payload1[:len(payload1)//2]
    half2 = payload2[len(payload2)//2:]
    return half1 + half2

def add_result(pool, payload, result):
    hash_ = hashlib.md5(payload.encode()).hexdigest()
    pool["history"].append({"payload": payload, "result": result, "hash": hash_})
    if result and payload not in pool["payloads"]:
        pool["payloads"].append(payload)
    save_genepool(pool)

def get_top_payloads(pool, count=10):
    # Get successful payloads
    history = [h for h in pool["history"] if h.get("result", False)]
    sorted_h = sorted(history, key=lambda x: x.get("score", 1), reverse=True)
    return [h["payload"] for h in sorted_h[:count]]

def evolve_payloads(pool):
    payloads = pool["payloads"][:]
    if len(payloads) < 2:
        return []
    new_pool = []
    for _ in range(10):
        p1, p2 = random.sample(payloads, 2)
        mutant = combine_payloads(mutate_payload(p1), mutate_payload(p2))
        if mutant not in payloads:
            new_pool.append(mutant)
    pool["payloads"].extend(new_pool)
    save_genepool(pool)
    return new_pool
