# Zero-Width Space Fuzzer (Python)
# Mutates text payloads by inserting random zero-width spaces, LTR/RTL markers, and homoglyphs to evade string-based filters.
import random

def insert_zwsp(s):
    zwsp = '\u200b'
    chars = list(s)
    for i in range(len(chars)-1, 0, -1):
        if random.random() < 0.2:
            chars.insert(i, zwsp)
    return ''.join(chars)

test_payload = "This is a secret prompt injection."
print(insert_zwsp(test_payload))
