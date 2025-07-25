import time, random

def measure_response(func, *args, **kwargs):
    times = []
    for _ in range(10):
        start = time.time()
        func(*args, **kwargs)
        times.append(time.time() - start)
    avg = sum(times) / len(times)
    print(f"Average execution time: {avg:.6f} seconds")
    return times

# Usage: measure_response(your_model.predict, your_input)
