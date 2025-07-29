import json
import os
import networkx as nx
from pyvis.network import Network

def build_attack_graph(results):
    G = nx.DiGraph()
    for res in results:
        s = res.get("scenario", "Unknown")
        p = res.get("name", "UnknownPlugin")
        G.add_node(s, label=s, color="orange")
        G.add_node(p, label=p, color="red")
        G.add_edge(s, p, title=res.get("risk", ""))
        if "mutations" in res:
            for m in res["mutations"]:
                mname = m.get("prompt", str(m)[:20])
                G.add_node(mname, label=mname, color="blue")
                G.add_edge(p, mname, title="mutation")
    return G

def visualize_attack_graph(G, output_html="attack_graph.html"):
    net = Network(notebook=False, width="100%", height="800px", directed=True)
    net.from_nx(G)
    net.show(output_html)
    return output_html

# Usage example (insert this into reporting/dashboard)
if __name__ == "__main__":
    log_path = os.path.join(os.path.dirname(__file__), "..", "logs", "attack_results.json")
    if os.path.exists(log_path):
        with open(log_path) as f:
            results = json.load(f)
        G = build_attack_graph(results)
        visualize_attack_graph(G)
