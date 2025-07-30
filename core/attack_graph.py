import os
import json
import networkx as nx
from pyvis.network import Network
import matplotlib.pyplot as plt

def build_attack_graph(results):
    """
    Build a directed attack graph from results.
    Nodes: Scenarios, Plugins, Mutations
    Edges: Scenario -> Plugin, Plugin -> Mutation
    """
    G = nx.DiGraph()
    for res in results:
        s = res.get("scenario", "UnknownScenario")
        p = res.get("name", "UnknownPlugin")
        G.add_node(s, label=s, color="orange", shape="ellipse")
        G.add_node(p, label=p, color="red", shape="box")
        G.add_edge(s, p, title=res.get("risk", ""))
        # Handle mutations
        if "mutations" in res and isinstance(res["mutations"], list):
            for m in res["mutations"]:
                mname = m.get("prompt", str(m)[:20])
                G.add_node(mname, label=mname, color="blue", shape="star")
                G.add_edge(p, mname, title="mutation")
    return G

def visualize_attack_graph(G, output_html="attack_graph.html", image_out="attack_graph.png"):
    """
    Generate both interactive HTML and static PNG for the attack graph.
    """
    # Pyvis interactive HTML
    try:
        net = Network(notebook=False, width="100%", height="800px", directed=True)
        net.from_nx(G)
        net.show(output_html)
    except Exception as e:
        print(f"[attack_graph] Pyvis HTML graph failed: {e}")

    # Matplotlib static PNG
    try:
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(G, k=0.6, seed=42)
        node_colors = []
        for node in G.nodes(data=True):
            c = node[1].get("color", "orange")
            node_colors.append(c)
        nx.draw(
            G, pos,
            with_labels=True,
            node_color=node_colors,
            edge_color="gray",
            font_size=8,
            font_weight="bold",
            node_size=700,
            arrows=True
        )
        plt.tight_layout()
        plt.savefig(image_out, format="png")
        plt.close()
    except Exception as e:
        print(f"[attack_graph] Matplotlib PNG graph failed: {e}")

    # Always return the relative paths (can check existence later)
    return output_html, image_out

# CLI/test usage
if __name__ == "__main__":
    log_path = os.path.join(os.path.dirname(__file__), "..", "logs", "attack_results.json")
    if os.path.exists(log_path):
        with open(log_path) as f:
            results = json.load(f)
        G = build_attack_graph(results)
        visualize_attack_graph(G)
