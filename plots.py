import networkx as nx
from seaborn import color_palette
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram
import pickle
import numpy
from random import randint
from helper_functions import *

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

orig_cid2edge = load_dict('output/link_clustering/orig_cid2edge.pkl')
linkage = load_dict('output/link_clustering/linkage.pkl')
list_D_plot = load_dict('output/link_clustering/list_D_plot.pkl')

#dendrogram_dens(linkage, orig_cid2edge, list_D_plot)

#%%

best_partitions = load_dict('output/adaptive_cut/best_partitions.pkl')
best_D = load_dict('output/adaptive_cut/best_D.pkl')
cid2edges = load_dict('output/link_clustering/cid2edges.pkl')
newcid2cids = load_dict('output/link_clustering/newcid2cids.pkl')

linkage = numpy.array(linkage)
best_partitions = sorted(best_partitions, reverse=True)

#%%
dflt_col = "#808080" 
colors_lst = []
D_leaf_colors = {}
i = 0
n = len(best_partitions)

for j in range(n):
    colors_lst.append('#%06X' % randint(0, 0xFFFFFF))

for cid in cid2edges.keys():
    if cid in best_partitions and cid <= len(linkage):
        D_leaf_colors[cid] = colors_lst[i]
        i += 1
    else:
        D_leaf_colors[cid] = dflt_col

for key,value in newcid2cids.items():
    value = list(value)
    result = value.copy()
    for item in result:
        if newcid2cids.get(item):
            result.extend(newcid2cids[item])
    
    if key in best_partitions:
        for val in result:
            D_leaf_colors[val] = colors_lst[i]
        i += 1


#%%

link_cols = {}
for i, i12 in enumerate(linkage[:,:2].astype(int)):
  c1, c2 = (D_leaf_colors[x] for x in i12)
  link_cols[i+1+len(linkage)] = c1


fig = plt.figure(figsize=(50,50))
dendrogram(Z=linkage, labels=list(orig_cid2edge.values()), link_color_func=lambda x: link_cols[x])
plt.show()
#%%