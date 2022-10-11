from helper_functions import *
from logger import logger

def greedy_up(num_edges, groups, newcid2cids, linkage, cid2edges, cid2nodes):

    M = 2/num_edges
    groups.reverse()
    last_group = groups[0]
    best_D = [0.0]
    partition_list, best_partitions, removed_comm = [], [], []

    for group in groups:
        Dc_list = []

        belonging_cid = [key  for (key, value) in newcid2cids.items() if group[0] in value][0]

        # Do not look on the communities 
        # which had partition density less than the best
        if len(set(group).intersection(removed_comm)) > 0:

            for cid in group:
                if cid < num_edges:
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

            latest_partition_list = [c for c in latest_partition_list if c != belonging_cid]

            current_group = latest_partition_list + group     

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
    
    return best_D[-1], best_partitions


def greedy_bottom(num_edges, groups, orig_cid2edge, newcid2cids, cid2edges, cid2nodes):

    M = 2/num_edges
    best_D = [0.0]
    partition_list, best_partitions, removed_comm = [], [], []
    current_group = list(orig_cid2edge.keys())

    for group in groups:
        Dc_list = []

        if len(set(group).intersection(removed_comm)) > 0:
            belonging_cid_lst = set([key for (key, value) in newcid2cids.items() if len(set(group).intersection(value)) > 0])

            removed_comm = list(removed_comm) + group + list(belonging_cid_lst) + [key for (key, value) in newcid2cids.items() if len(belonging_cid_lst.intersection(value)) > 0]
            removed_comm = set(removed_comm)

            continue

        belonging_cid = [key for (key, value) in newcid2cids.items() if group[-1] in value]

        belonging_cid_lst = set([key for (key, value) in newcid2cids.items() if len(set(group).intersection(value)) > 0])

        current_group = current_group + belonging_cid
        current_group = [cid for cid in current_group if cid not in group]

        for cid in current_group:
            m, n = len(cid2edges[cid]), len(cid2nodes[cid])
            Dc_list.append(Dc(m, n))
        
        partition_list.append(set(current_group))

        D = M * sum(Dc_list)

        if D < best_D[-1]:
            partition_list = partition_list[:-1]
            current_group = list(partition_list[-1])

            belonging_cid_lst = set([key for (key, value) in newcid2cids.items() if len(set(group).intersection(value)) > 0])

            removed_comm = list(removed_comm) + list(belonging_cid_lst) + [key for (key, value) in newcid2cids.items() if len(belonging_cid_lst.intersection(value)) > 0]
            removed_comm = set(removed_comm)

        else:
            best_D.append(D)
            best_partitions = partition_list[-1]

    return best_D[-1], best_partitions