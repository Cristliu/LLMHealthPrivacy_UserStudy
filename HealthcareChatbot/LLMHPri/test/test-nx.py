from __future__ import division
import matplotlib.pyplot as plt
import networkx as nx
import os

# baseDir = os.path.dirname(os.path.abspath(__name__))  # 获取当前脚本的完整路径
# pngdir = os.path.join(baseDir, 'static', 'img')
# pngname = os.path.join(pngdir, "nx.png")
G = nx.generators.directed.random_k_out_graph(10, 3, 0.5)
pos = nx.layout.spring_layout(G)

node_sizes = [3 + 10 * i for i in range(len(G))]
M = G.number_of_edges()
edge_colors = range(2, M + 2)
edge_alphas = [(5 + i) / (M + 4) for i in range(M)]

nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='blue')
edges = nx.draw_networkx_edges(G, pos, node_size=node_sizes, arrowstyle='->',
                               arrowsize=10, edge_color=edge_colors,
                               edge_cmap=plt.cm.Blues, width=2)
# set alpha value for each edge
for i in range(M):
    edges[i].set_alpha(edge_alphas[i])

ax = plt.gca()
ax.set_axis_off()
# plt.savefig('D:\\nx.png')
plt.show()
