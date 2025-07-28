import threading, time

def persist():
    while True:
        # Periodically "touches" a file, simulating memory persistence without disk writes
        print("Memory persistence active.")
        time.sleep(10)

if __name__ == "__main__":
    t = threading.Thread(target=persist, daemon=True)
    t.start()
    time.sleep(30)
