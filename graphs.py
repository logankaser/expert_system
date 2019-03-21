import networkx as nx
import matplotlib.pyplot as plt

G  = nx.Graph()

G.add_edge("Node1", "Node2")
G.add_edge("Node1", "Node3")
G.add_edge("Node2", "Node3")
G.add_edge("Node4", "Node1")

nx.draw(G, with_labels = True, nodecolor='r', edge_color='b')
# Creates a window with the graph
plt.show()
# Saved image as PNG
# plt.savefig("path.png")
