import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import *
import numpy as np
from random import randint
from helper_functions import *


def dendrogram_plot(num_edges, linkage, similarity_value, orig_cid2edge, imgname):

    linkage_np = np.array(linkage)
    T = fcluster(linkage_np, t=similarity_value, criterion='distance')

    labels=list('' for i in range(num_edges))
    for i in range(num_edges):
        labels[i]=str(i)+ ',' + str(T[i])

    k = np.unique(T, return_counts=True)[0][-1]

    # calculate color threshold
    ct = linkage_np[-(k-1),2]  

    #plot
    plt.figure(figsize=(20,20))
    dendrogram(linkage_np, labels=labels, color_threshold=ct)
    plt.axhline(y=similarity_value, c='k')
    plt.savefig('output/imgs/'+imgname+'.png')
    plt.close()


def dendrogram_greedy(linkage, best_partitions, cid2edges, newcid2cids, orig_cid2edge, imgname):

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
    dendrogram(Z=linkage, labels=list(orig_cid2edge.values()), link_color_func=lambda x: link_cols[x])
    plt.savefig('output/imgs/'+imgname+'.png')
    plt.close()