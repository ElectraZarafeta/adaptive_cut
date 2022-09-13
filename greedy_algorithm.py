#%%
from helper_functions import *

# Load data

with open('output/link_clustering/num_edges.txt') as f:
    num_edges = int(f.read())

newcid2cids = load_dict('output/link_clustering/newcid2cids.pkl')
cid2edges   = load_dict('output/link_clustering/cid2edges.pkl')
cid2nodes   = load_dict('output/link_clustering/cid2nodes.pkl')
groups      = load_dict('output/link_clustering/groups.pkl')
linkage     = load_dict('output/link_clustering/linkage.pkl')

#%%

# Link density


M = 2/num_edges
groups.reverse()
last_group = groups[0]
best_D = [0.0]
partition_list, best_partitions, removed_comm = [], [], []

#%%

for group in groups:
    Dc_list = []

    belonging_cid = [key  for (key, value) in newcid2cids.items() if group[0] in value][0]

    # Do not look on the communities 
    # which had partition density less than the best
    if len(set(group).intersection(removed_comm)) > 0:

        for cid in group:
            if cid <= len(linkage):
                removed_comm = removed_comm + [cid]
            else:
                removed_comm = removed_comm + [i for (key, value) in newcid2cids.items() for i in value if key == cid]
            
        continue

    if group == last_group:
        for cid in group:
            m, n = len(cid2edges[cid]), len(cid2nodes[cid])
            Dc_list.append(Dc(m, n))

        partition_list.append(set(group))

        D = M * sum(Dc_list)
    else:
        latest_partition_list = partition_list[-1]

        # # TEST
        # tmp=[]
        # for cid in group:
        #     tmp = tmp + [key  for (key, value) in newcid2cids.items() if cid in value]

        # if not(all(p == tmp[0] for p in tmp)):
        #     print('\nPROBLEM 2')
        #     print(tmp)
        #     print(group)
        #     continue

        latest_partition_list = [c for c in latest_partition_list if c != belonging_cid]

        current_group = latest_partition_list + group     

        list_of_cids = []
        for cid in current_group:
            m, n = len(cid2edges[cid]), len(cid2nodes[cid])
            Dc_list.append(Dc(m, n))
        
        partition_list.append(set(current_group))

        D = M * sum(Dc_list)

    if D < best_D[-1]:
        partition_list = partition_list[:-1]
        partition_list[-1].add(belonging_cid)

        for cid in group:
            removed_comm = removed_comm + [i for (key, value) in newcid2cids.items() for i in value if key == cid]

        # TEST
        if belonging_cid in removed_comm:
            print('\nPROBLEM 1')
            break
        
    else:
        best_D.append(D)
        best_partitions = partition_list[-1]


#%%

save_dict(best_D, 'output/greedy_algorithm/best_D.pkl')
save_dict(best_partitions, 'output/greedy_algorithm/best_partitions.pkl')
#%%