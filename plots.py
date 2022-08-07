import networkx as nx
from seaborn import color_palette, set_style, palplot
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram

def create_color_map(G, attribute, seaborn_palette="colorblind"):
    """Return a list of hex color mappings for node attributes"""
    attributes = [G.nodes[label][attribute] for label in G.nodes()]

    # get the set of possible attributes
    attributes_unique = list(set(attributes))
    num_values = len(attributes_unique)

    # generate color palette from seaborn
    palette = color_palette(seaborn_palette, num_values).as_hex()

    # create a mapping of attribute to color
    color_map = dict(zip(attributes_unique, palette))

    # map the attribute for each node to the color it represents
    node_colors = [color_map[attribute] for attribute in attributes]

    nx.draw(G, node_color=node_colors, with_labels=True)

def dendrogram_dens(linkage, orig_cid2edge, list_D_plot):
    fig = plt.figure(figsize=(50,50))

    plt.subplot(1,2,1)
    plt.margins(0)
    dendrogram(linkage, labels=list(orig_cid2edge.values()))

    plt.subplot(1,2,2)
    plt.axhline(y=max(list_D_plot,key=lambda item:item[0])[1])
    plt.plot(*zip(*list_D_plot))
    plt.margins(0)
    plt.yticks([])
    
    plt.savefig('output/imgs/output_unweighted.png')

#%%

orig_cid2edge = {}
for line in open('output/orig_cid2edge.txt'):
    L = line.strip().split()
    e0, e1 = L[1].split(',') 
    orig_cid2edge[int(L[0])] = (int(e0), int(e1))

linkage = []
for line in open('output/linkage.txt'):
    L = line.strip().split()
    linkage.append((int(L[0]), int(L[1]), float(L[2]), int(L[3])))

list_D_plot = []
for line in open('output/list_D_plot.txt'):
    L = line.strip().split()
    list_D_plot.append((float(L[0]), float(L[1])))

dendrogram_dens(linkage, orig_cid2edge, list_D_plot)

#%%