#%%
from helper_functions import *
from scipy import cluster
import numpy as np
import random
from copy import deepcopy
from logger import logger 
#from link_clustering import *

def partition_density(num_edges, cid2edges, cid2nodes, partitions):
    '''
    Calculate the Partition Density 

    Input:
        - partitions: the partitions for which we want to calculate the partition density
    Output:
        - D: partition density value
    '''

    M = 2/num_edges

    Dc_list = []
    for cid in partitions:
        m, n = len(cid2edges[cid]), len(cid2nodes[cid])
        Dc_list.append(Dc(m, n))

    D = M * sum(Dc_list)

    return D


def calc_partdens_up(curr_leader, num_edges, groups, cid2edges, cid2nodes, newcid2cids, curr_partitions):
    '''
    Identify the partitions in case we have to move the current leader one level up. 
    This means that we have to identify the community id in which the current leader
    belongs to and remove from the current partitions any children belonging to this 
    community id.

    Based on the extracted partitions, we calculate the Partition Density.

    Input:
        - curr_leader: the id of the current leader
        - newcid2cids: dictionary which shows from which pair of cids each new cid has been created
        - curr_partitions: the list of leader ids from the current partitions 
    Output:
        - partitions: list of the identified partitions' leaders
        - D: calculated partition density
    '''

    #print(curr_leader)

    belonging_group = [group for group in groups if curr_leader in group][0]

    # find belonging cid
    belonging_cid = max([key for v in belonging_group for (key, value) in newcid2cids.items() if v in value])

    # find belonging cid's children
    value = newcid2cids[belonging_cid]
    value = list(value)
    result = value.copy()
    for item in result:
        if newcid2cids.get(item):
            result.extend(newcid2cids[item])

    # add belonging cid in partitions 
    # remove belonging cid's children from partitions
    partitions = [leader_tmp for leader_tmp in curr_partitions if leader_tmp not in result]
    partitions = [leader_tmp for leader_tmp in partitions if leader_tmp not in belonging_group]
    partitions.append(belonging_cid)

    # Calculate partition density
    D = partition_density(num_edges, cid2edges, cid2nodes, partitions)

    return partitions, D


def calc_partdens_down(curr_leader, num_edges, cid2edges, cid2nodes, newcid2cids, groups, curr_partitions):
    '''
    Identify the partitions in case we have to move the current leader one level down. 
    This means that we have to identify the children ids which the current leader
    has and remove from the current partitions the current leader.

    Based on the extracted partitions, we calculate the Partition Density.

    Input:
        - curr_leader: the id of the current leader
        - newcid2cids: dictionary which shows from which pair of cids each new cid has been created
        - curr_partitions: the list of leader ids from the current partitions 
    Output:
        - partitions: list of the identified partitions' leaders
        - D: calculated partition density
    '''

    # remove current leader
    partitions = [leader_tmp for leader_tmp in curr_partitions if leader_tmp != curr_leader]

    # find children
    child = newcid2cids[curr_leader][0]

    try:
        group_down = [group for group in groups if child in group][0]
    except:
        group_down = [group for group in groups if newcid2cids[child][0] in group][0]

    # update partitions
    partitions = partitions + group_down

    # Calculate partition density
    D = partition_density(num_edges, cid2edges, cid2nodes, partitions)

    return partitions, D


def tune_cut(linkage, similarity_value, best_D, cid2edges, cid2nodes, newcid2cids, groups, num_edges, threshold, stopping_threshold=None, montecarlo=False, epsilon=None):

    linkage_np = np.array(linkage)
    T = cluster.hierarchy.fcluster(linkage_np, t=similarity_value, criterion='distance')
    leaders = cluster.hierarchy.leaders(linkage, T)[0].tolist()

    direction = ['up', 'down']
    curr_partitions = deepcopy(leaders)
    early_stop = 0

    i = 0

    list_D, list_clusters = {}, {}
    list_D[i] = best_D
    list_clusters[i] = len(curr_partitions)

    only_down_lst, only_up_lst = [], []

    while True:

        curr_leader = random.choice(curr_partitions)
        #print(curr_leader)
        
        # print(f'current leader {curr_leader}')

        # logger.warning(curr_leader)
        # logger.warning(curr_direction)

        # if curr_leader not in leaders:
        #     print('not in list')
        #     print(curr_leader)
        #     # logger.warning('Curr leader not in leaders')
        #     continue

        #if curr_leader < num_edges:
        try:
            belonging_group = [group for group in groups if curr_leader in group][0]
            # find belonging cid
            belonging_cid = max([key for v in belonging_group for (key, value) in newcid2cids.items() if v in value])
        except:
            belonging_cid = [k for k, v in newcid2cids.items() if curr_leader in v]

        if belonging_cid == max(list(newcid2cids.keys())) or belonging_cid in groups[-1]:
            curr_direction = 'down'

        elif (len(only_down_lst)>0 or len(only_up_lst)>0):
            if curr_leader in only_down_lst:
                curr_direction = 'down'
            elif curr_leader in only_up_lst:
                curr_direction = 'up'
            else:
                curr_direction = random.choice(direction)
        else:
            curr_direction = random.choice(direction)
        #print(curr_direction)

        i += 1

        # logger.warning(f'Current iter {i}')

        if curr_direction == 'up':

            # Move one level up   

            partitions_tmp, curr_D = calc_partdens_up(curr_leader, num_edges, groups, cid2edges, cid2nodes, newcid2cids, curr_partitions)

        else:
            # Move one level down

            if curr_leader < num_edges:
                partitions_tmp, curr_D = curr_partitions, best_D
            else:
                partitions_tmp, curr_D = calc_partdens_down(curr_leader, num_edges, cid2edges, cid2nodes, newcid2cids, groups, curr_partitions)

        previous_D = best_D

        if curr_D >= best_D:
            if curr_direction == 'up':
                only_down_lst = list(set(only_down_lst + list(set(partitions_tmp).difference(curr_partitions))))
            else:
                only_up_lst = list(set(only_up_lst + list(set(partitions_tmp).difference(curr_partitions))))
            curr_partitions = partitions_tmp
            best_D = curr_D
            list_D[i] = best_D
            list_clusters[i] = len(curr_partitions)
        else:
            if montecarlo:
                a = random.uniform(0, 1)

                if i <= threshold:
                    epsilon_tmp = epsilon[0]
                elif i <= (threshold*2):
                    epsilon_tmp = epsilon[1]
                elif i <= (threshold*3):
                    epsilon_tmp = epsilon[2]
                elif i <= (threshold*4):
                    epsilon_tmp = epsilon[3]
                # elif i <= (threshold*5):
                #     epsilon_tmp = epsilon[4]
                else:
                    break

                # logger.warning(a)
                # logger.warning(epsilon_tmp)
                # logger.warning(previous_D)
                # logger.warning(best_D)
                # logger.warning(curr_D)

                if (a < epsilon_tmp): #and ((best_D - curr_D) < 0.05): 
                    if curr_direction == 'up':
                        only_down_lst = list(set(only_down_lst + list(set(partitions_tmp).difference(curr_partitions))))
                    else:
                        only_up_lst = list(set(only_up_lst + list(set(partitions_tmp).difference(curr_partitions))))
                    curr_partitions = partitions_tmp
                    best_D = curr_D
                    list_D[i] = best_D
                    list_clusters[i] = len(curr_partitions)

        # print(curr_partitions)
        # print(only_down_lst)
        # print(only_up_lst)

        if not montecarlo:
            if (i > threshold) and ((best_D - previous_D) < 0.01):
                early_stop += 1
            else:
                early_stop = 0

            if early_stop > stopping_threshold:
                break

        # print(partitions_tmp)
        # print(curr_partitions)
        # print(only_down_lst)
        # print(only_up_lst)

    return list_D, list_clusters, curr_partitions

#%%

# dataset = '/mnt/c/Users/ezara/OneDrive/Documents/thesis folder/data/Celegans metabolic.txt'
# delimiter = '-'

# linkage, list_D_plot, newcid2cids, orig_cid2edge, cid2edges, cid2nodes, num_edges = link_clustering(filename=dataset, delimiter=delimiter)
# best_D_LC, similarity_LC = max(list_D_plot,key=lambda item:item[0])
# #%%
# colors_dict_tmp = color_dict(cid2edges)
# groups = groups_generator(linkage, newcid2cids, num_edges)

# threshold = 1000
# epsilon = [0.1, 0.05, 0.01, 0.001, 0]

# # threshold = 10000 
# # stopping_threshold = 5

# list_D, list_clusters, best_partitions = tune_cut(num_edges=num_edges, groups=groups, newcid2cids=newcid2cids, cid2edges=cid2edges, cid2nodes=cid2nodes, linkage=linkage, similarity_value=similarity_LC, best_D=best_D_LC, threshold=threshold, montecarlo=True, epsilon=epsilon)
# #%%

# import pandas as pd
# import numpy as np

# def groups_generator(linkage, newcid2cids, num_edges):

#     df = pd.DataFrame(np.array(linkage), columns = ['cid1','cid2','sim','num_edges'])
#     df['pairs'] = df.apply(lambda x: [x['cid1'], x['cid2']], axis=1)
#     df = df[['pairs', 'sim']]
#     df_grouped = df.groupby('sim').agg(lambda x: list(x))
#     total_groups = []
    
#     for index, row in df_grouped.iterrows():

#         curr_level = row['pairs']
#         #print(curr_level)

#         flat_list = [item for sublist in curr_level for item in sublist]
#         checked = {x: False for x in flat_list}
#         groups = []

#         for pair in curr_level:
#             cid1, cid2 = pair[0], pair[1]

#             flag = False

#             checked[cid1] = True
#             checked[cid2] = True

#             if cid1 < num_edges and cid2 < num_edges:

#                 groups.append([int(cid1), int(cid2)])
  
#             elif cid1 >= num_edges and cid2 >= num_edges:

#                 cids1_1, cids1_2 = newcid2cids[cid1][0], newcid2cids[cid1][1]
#                 cids2_1, cids2_2 = newcid2cids[cid2][0], newcid2cids[cid2][1]

#                 if (cids1_1 in flat_list) and (cids1_2 in flat_list) and (cids2_1 in flat_list) and (cids2_2 in flat_list):

#                     if checked[cids1_1] and checked[cids1_2] and checked[cids2_1] and checked[cids2_2]:
#                         continue
                    
#                     groups_tmp = [cids1_1, cids1_2, cids2_1, cids2_2]

#                     for group in groups:
#                         if cids1_1 in group and cids1_2 not in group:
#                             groups_tmp = list(set(groups_tmp + group))
#                             groups_tmp.remove(cids1_2)
#                             break
#                         if cids2_1 in group and cids2_2 not in group:
#                             groups_tmp = list(set(groups_tmp + group))
#                             groups_tmp.remove(cids2_2)
#                             break

#                     groups = [group for group in groups if len(set(group).intersection(groups_tmp)) == 0]
#                     groups.append(groups_tmp)

#                 elif (cids1_1 in flat_list) and (cids1_2 in flat_list):

#                     # if checked[cids1_1] and checked[cids1_2]:
#                     #     continue

#                     groups_tmp = [cids1_1, cids1_2, int(cid2)]

#                     for group in groups:
#                         if cids1_1 in group and cids1_2 not in group:
#                             groups_tmp = list(set(groups_tmp + group))
#                             groups_tmp.remove(cids1_2)
#                             break

#                     groups = [group for group in groups if len(set(group).intersection(groups_tmp)) == 0]
#                     groups.append(groups_tmp)

#                 elif (cids2_1 in flat_list) and (cids2_2 in flat_list):

#                     # if checked[cids2_1] and checked[cids2_2]:
#                     #     continue

#                     groups_tmp = [cids2_1, cids2_2, int(cid1)]

#                     for group in groups:
#                         if cids2_1 in group and cids2_2 not in group:
#                             groups_tmp = list(set(groups_tmp + group))
#                             groups_tmp.remove(cids2_2)
#                             break
                    
#                     groups = [group for group in groups if len(set(group).intersection(groups_tmp)) == 0]
#                     groups.append(groups_tmp)


#                 else:
#                     groups.append([int(cid1), int(cid2)])

#             elif cid1 >= num_edges:
                

#                 cids1_1, cids1_2 = newcid2cids[cid1][0], newcid2cids[cid1][1]

#                 if (cids1_1 in flat_list) and (cids1_2 in flat_list):

#                     # if checked[cids1_1] and checked[cids1_2]:
#                     #     continue

#                     groups_tmp = [cids1_1, cids1_2, int(cid2)]

#                     for i, group in enumerate(groups):
#                         if (cids1_1 >= num_edges and newcid2cids[cids1_1][0] in group) or (cids1_2 >= num_edges and newcid2cids[cids1_2][0] in group):
#                             flag = True
#                             groups[i].append(int(cid2))
#                             break
#                         elif cids1_1 in group and cids1_2 not in group:
#                             groups_tmp = list(set(groups_tmp + group))
#                             groups_tmp.remove(cids1_2)
#                             break

#                     if not flag:
#                         groups = [group for group in groups if len(set(group).intersection(groups_tmp)) == 0]
#                         groups.append(groups_tmp)



#                 else:
#                     groups.append([int(cid1), int(cid2)])

            
#             elif cid2 >= num_edges:

#                 cids2_1, cids2_2 = newcid2cids[cid2][0], newcid2cids[cid2][1]

#                 if (cids2_1 in flat_list) and (cids2_2 in flat_list):

#                     # if checked[cids2_1] and checked[cids2_2]:
#                     #     continue

#                     groups_tmp = [cids2_1, cids2_2, int(cid1)]

#                     for i, group in enumerate(groups):
#                         if (cids2_1 >= num_edges and newcid2cids[cids2_1][0] in group) or (cids2_2 >= num_edges and newcid2cids[cids2_2][0] in group):
#                             flag = True
#                             groups[i].append(int(cid1))
#                             break
#                         elif cids2_1 in group and cids2_2 not in group:
#                             groups_tmp = list(set(groups_tmp + group))
#                             groups_tmp.remove(cids2_2)
#                             break

#                     if not flag:
#                         groups = [group for group in groups if len(set(group).intersection(groups_tmp)) == 0]
#                         groups.append(groups_tmp)


#                 else:
#                     groups.append([int(cid1), int(cid2)])

#             print(pair)
#             print(groups)
#         total_groups.append(groups)

#     total_groups = [item for sublist in total_groups for item in sublist]

#     return total_groups

# groups = groups_generator(linkage, newcid2cids, num_edges)

# # %%
