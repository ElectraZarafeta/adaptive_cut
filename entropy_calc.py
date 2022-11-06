#%%
import math
from scipy.cluster import hierarchy
import numpy as np
from methods.link_clustering import *
from plots import *
import collections
from collections import defaultdict

def entropy_calc(linkage, newcid2cids, num_edges):

    linkage_np = np.array(linkage)
    similarity_vals = sorted(set(linkage_np[:,2].tolist()), reverse=True)

    total_leaves = num_edges
    E = {}

    for i, val in enumerate(similarity_vals):

        logs = 0

        T = hierarchy.fcluster(np.array(linkage), t=val, criterion='distance')
        curr_partitions = sorted(set(hierarchy.leaders(np.array(linkage), T)[0].tolist()))

        for leader in curr_partitions:

            # Find leaves
            if leader < num_edges:
                num_leaves = 1
            else:
                value = newcid2cids[leader]
                value = list(value)
                result = value.copy()
                for item in result:
                    if newcid2cids.get(item):
                        result.extend(newcid2cids[item])
                
                num_leaves = len(set([val for val in result if val < num_edges]))
                
            probj = num_leaves/total_leaves
            logs += -(probj * math.log(probj, 2))
            #logs.append(-(probj * math.log(probj, 2)))

        # if max(logs) == 0:
        #     continue
        # else:
        #     E[i+1] = sum(logs)/max(logs)
        E[i] = logs #/len(curr_partitions)

    logs = 0

    for c in range(num_edges):
        num_leaves = 1

        probj = num_leaves/total_leaves
        logs += -(probj * math.log(probj, 2))

    E[i+1] = logs #/num_edges
        
    max_E = max(E.values())

    E_n = {key:value/max_E for key,value in E.items()} 
    #collections.OrderedDict(sorted(E_n.items()))
    #E_n.update({i+1:1.0})

    return E

dataset = f'data/TrumpWorld.txt'
delimiter = '-'
main_path = 'output/'

linkage, list_D_plot, groups, newcid2cids, orig_cid2edge, cid2edges, cid2nodes, num_edges = link_clustering(filename=dataset, delimiter=delimiter)

entropy = entropy_calc(linkage, newcid2cids, num_edges)
entropy_plot(entropy, main_path)

#%%