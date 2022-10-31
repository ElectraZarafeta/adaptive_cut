import math
from scipy.cluster import hierarchy
import numpy as np
import fastcluster

def entropy_calc(linkage, newcid2cids, num_edges):

    linkage_np = np.array(linkage)
    similarity_vals = sorted(set(linkage_np[:,2].tolist()), )
    similarity_vals.reverse()

    total_leaves = num_edges
    E = []

    for val in similarity_vals[1:]:

        logs = []

        T = hierarchy.fcluster(np.array(linkage), t=val, criterion='distance')
        curr_partitions = hierarchy.leaders(np.array(linkage), T)[0].tolist()

        #print(curr_partitions)

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

            logs.append(abs(probj*math.log(probj)))

        E.append(sum(logs)/max(logs))

    return E