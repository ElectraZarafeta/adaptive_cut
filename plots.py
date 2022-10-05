#%%
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster import *
import numpy as np
from random import randint
from helper_functions import *
import networkx as nx
from methods.link_clustering import link_clustering
import igviz as ig
from collections import defaultdict
from logger import logger


def dendrogram_plot(num_edges, linkage, similarity_value, orig_cid2edge, main_path, imgname):

    linkage_np = np.array(linkage)
    T = hierarchy.fcluster(linkage_np, t=similarity_value, criterion='distance')

    labels=list('' for i in range(num_edges))
    for i in range(num_edges):
        labels[i]=str(i)+ ',' + str(T[i])

    k = np.unique(T, return_counts=True)[0][-1]

    # calculate color threshold
    ct = linkage_np[-(k-1),2]  

    #plot
    plt.figure(figsize=(20,20))
    hierarchy.dendrogram(linkage_np, labels=labels, color_threshold=ct)
    plt.axhline(y=similarity_value, c='k')
    plt.savefig(main_path+imgname+'.png')
    plt.close()


def dendrogram_greedy(linkage, best_partitions, cid2edges, newcid2cids, orig_cid2edge, main_path, imgname):

    linkage_np = np.array(linkage)
    best_partitions = sorted(best_partitions, reverse=True)

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

    link_cols = {}
    for i, i12 in enumerate(linkage_np[:,:2].astype(int)):
        c1, c2 = (D_leaf_colors[x] for x in i12)
        link_cols[i+1+len(linkage_np)] = c1


    plt.figure(figsize=(20,20))
    hierarchy.dendrogram(Z=linkage, labels=list(orig_cid2edge.values()), link_color_func=lambda x: link_cols[x])
    plt.savefig(main_path+imgname+'.png')
    plt.close()

def tuning_metrics(list_D, list_clusters, threshold, main_path, imgname1, imgname2):

    sns.set_style('darkgrid')
    sns.set_palette('pastel')

    p = sns.lineplot(x=list_D.keys(), y=list_D.values())
    p.set(title='Partition density for each iteration')
    p.set_xlabel('Iterations', fontsize=10)
    p.set_ylabel('Partition density', fontsize=10)
    plt.axvline(threshold, color='#AA4A44')
    #plt.text(threshold-5, max(list_D.values())-0.003, "Threshold", rotation='vertical', size='small', color='#AA4A44')
    plt.savefig(main_path+imgname1+'.png')
    plt.close()

    p = sns.lineplot(x=list_clusters.keys(), y=list_clusters.values())
    p.set(title='Number of clusters for each iteration')
    p.set_xlabel('Iterations', fontsize=10)
    p.set_ylabel('Number of Clusters', fontsize=10)
    plt.savefig(main_path+imgname2+'.png')
    plt.close()

#%%


# n = len(leaders)
# node_color = {}
# edge_color = {}
# partition = [0 for _ in range(G.number_of_nodes())]
# i = 1

# for leader in leaders:
#     if leader < num_edges:
#         color = '#808080'

#         # for n in cid2nodes[leader]:

#         #     partition[n] = 0

#         # color map
#         node_color.update({node: color for node in cid2nodes[leader]})
#         edge_color.update({edge: color for edge in cid2edges[leader]})

#     else:
#         color = '#%06X' % randint(0, 0xFFFFFF)

#         value = newcid2cids[leader]
#         value = list(value)
#         result = value.copy()
#         for item in result:
#             if newcid2cids.get(item):
#                 result.extend(newcid2cids[item])

#         for val in result:
#             if val < num_edges:
#                 for n in cid2nodes[val]:
#                     partition[n] = i

#         i += 1

#         # color map

#         node_color.update({node: color for val in result for node in cid2nodes[val] if val < num_edges})
#         edge_color.update({edge: color for val in result for edge in cid2edges[val] if val < num_edges})
    

# node_color = dict(sorted(node_color.items()))
# edge_color = dict(sorted(edge_color.items()))
# partition.sort()
# #%%

# def _inter_community_edges(G, partition):
#     edges = defaultdict(list)

#     for (i, j) in G.edges():
#         c_i = partition[i]
#         c_j = partition[j]

#         if c_i == c_j:
#             continue

#         edges[(c_i, c_j)].append((i, j))

#     return edges

# def _position_communities(G, partition, **kwargs):
#     hypergraph = nx.Graph()
#     hypergraph.add_nodes_from(set(partition))

#     inter_community_edges = _inter_community_edges(G, partition)
#     for (c_i, c_j), edges in inter_community_edges.items():
#         hypergraph.add_edge(c_i, c_j, weight=len(edges))

#     pos_communities = nx.spring_layout(hypergraph, **kwargs)

#     # Set node positions to positions of its community
#     pos = dict()
#     for node, community in enumerate(partition):
#         pos[node] = pos_communities[community]

#     return pos


# def _position_nodes(G, partition, **kwargs):
#     communities = defaultdict(list)
#     for node, community in enumerate(partition):
#         communities[community].append(node)

#     pos = dict()
#     for c_i, nodes in communities.items():
#         subgraph = G.subgraph(nodes)
#         pos_subgraph = nx.spring_layout(subgraph, **kwargs)
#         pos.update(pos_subgraph)

    

#     return pos


# # Adapted from: https://stackoverflow.com/questions/43541376/how-to-draw-communities-with-networkx
# def community_layout(G, partition):
#     pos_communities = _position_communities(G, partition, scale=10.0)
#     pos_nodes = _position_nodes(G, partition, scale=5.0)

#     # Combine positions
#     pos = dict()
#     for node in G.nodes():
#         pos[node] = pos_communities[node] + pos_nodes[node]

#     return pos



# pos = community_layout(G, partition)

# #%%

# d = nx.degree(G)

# plt.figure(figsize=(20,10))
# nx.draw(G, node_color=list(node_color.values()), edge_color=list(edge_color.values()), alpha=0.8, node_size=[(d[node]+1) * 100 for node in G.nodes()])
# plt.show()
#%%