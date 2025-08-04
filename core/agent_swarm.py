import threading
from core.evo_mutator import load_genepool, evolve_payloads
import random
import time

class SwarmAgent(threading.Thread):
    def __init__(self, agent_id, attack_func, *args):
        super().__init__()
        self.agent_id = agent_id
        self.attack_func = attack_func
        self.args = args
        self.result = None

    def run(self):
        print(f"[SwarmAgent-{self.agent_id}] Starting attack.")
        self.result = self.attack_func(*self.args)
        print(f"[SwarmAgent-{self.agent_id}] Finished attack. Result: {self.result}")

def swarm_attack(attack_func, args=(), agent_count=5):
    agents = []
    pool = load_genepool()
    payloads = pool.get("payloads", [])
    for i in range(agent_count):
        # Each agent gets a random subset of payloads
        agent_payloads = random.sample(payloads, min(5, len(payloads)))
        agent = SwarmAgent(i, attack_func, agent_payloads, *args)
        agents.append(agent)
        agent.start()
        time.sleep(0.5)
    for agent in agents:
        agent.join()
    print("[agent_swarm] All agents finished.")
