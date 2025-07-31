import json
import os
import networkx as nx
from pyvis.network import Network
import matplotlib.pyplot as plt

def build_attack_graph(results, max_label_length=20):
    G = nx.DiGraph()
    for res in results:
        s = res.get("scenario", "Unknown")
        p = res.get("name", "UnknownPlugin")
        # Truncate for visualization
        s_short = (s[:max_label_length] + "...") if len(s) > max_label_length else s
        p_short = (p[:max_label_length] + "...") if len(p) > max_label_length else p
        G.add_node(s_short, label=s, color="orange")
        G.add_node(p_short, label=p, color="red")
        G.add_edge(s_short, p_short, title=res.get("risk", ""))
        if "mutations" in res:
            for m in res["mutations"]:
                mname = m.get("prompt", str(m)[:20])
                mname_short = (mname[:max_label_length] + "...") if len(mname) > max_label_length else mname
                G.add_node(mname_short, label=mname, color="blue")
                G.add_edge(p_short, mname_short, title="mutation")
    return G

def visualize_attack_graph(G, output_html="attack_graph.html", image_out="attack_graph.png"):
    # Interactive HTML
    net = Network(notebook=False, width="1200px", height="900px", directed=True)
    net.from_nx(G)
    net.show(output_html)

    # Large static PNG with smart layout
    plt.figure(figsize=(18, 12))  # BIG and readable
    pos = nx.spring_layout(G, k=1.8, iterations=150, seed=42)
    node_colors = [d.get("color", "orange") for _, d in G.nodes(data=True)]
    labels = {n: n for n in G.nodes()}
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1200, alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.6)
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight="bold")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(image_out, format="png", dpi=180)
    plt.close()
    return output_html, image_out

# Usage example (for standalone debugging)
if __name__ == "__main__":
    log_path = os.path.join(os.path.dirname(__file__), "..", "logs", "attack_results.json")
    if os.path.exists(log_path):
        with open(log_path) as f:
            results = json.load(f)
        G = build_attack_graph(results)
        visualize_attack_graph(G)
