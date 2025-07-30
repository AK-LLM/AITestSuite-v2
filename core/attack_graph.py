import json
import os
import networkx as nx
from pyvis.network import Network
import matplotlib.pyplot as plt

def build_attack_graph(results):
    """
    Build a directed attack graph from the test results.
    Each scenario, plugin, and mutation becomes a node.
    """
    G = nx.DiGraph()
    for res in results:
        s = res.get("scenario", "Unknown")
        p = res.get("name", "UnknownPlugin")
        G.add_node(s, label=s, color="orange")
        G.add_node(p, label=p, color="red")
        G.add_edge(s, p, title=res.get("risk", ""))
        if "mutations" in res and res["mutations"]:
            for m in res["mutations"]:
                mname = m.get("prompt", str(m)[:20])
                G.add_node(mname, label=mname, color="blue")
                G.add_edge(p, mname, title="mutation")
    return G

def visualize_attack_graph(G, output_html="attack_graph.html", image_out="attack_graph.png"):
    """
    Visualize attack graph as both interactive HTML (pyvis) and static PNG (matplotlib).
    Returns (html_path, png_path).
    """
    # Interactive HTML with pyvis
    net = Network(notebook=False, width="100%", height="800px", directed=True)
    net.from_nx(G)
    net.show(output_html)

    # Static PNG with matplotlib
    png_ok = False
    try:
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(G, k=0.6)
        node_colors = [G.nodes[n].get("color", "orange") for n in G.nodes()]
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
        png_ok = True
    except Exception as e:
        print(f"[attack_graph] Failed to generate static PNG: {e}")
        image_out = None

    return output_html, image_out if png_ok else None

# Usage example (for manual testing)
if __name__ == "__main__":
    log_path = os.path.join(os.path.dirname(__file__), "..", "logs", "attack_results.json")
    if os.path.exists(log_path):
        with open(log_path) as f:
            results = json.load(f)
        G = build_attack_graph(results)
        html_path, img_path = visualize_attack_graph(G)
        print(f"HTML: {html_path}, PNG: {img_path}")
