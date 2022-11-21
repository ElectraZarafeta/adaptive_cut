from helper_functions import *
import random
from copy import deepcopy
from logger import logger 

def partition_density(num_edges, cid2numedges, cid2numnodes, partitions):
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
        m, n = cid2numedges[cid], cid2numnodes[cid]
        Dc_list.append(Dc(m, n))

    D = M * sum(Dc_list)

    return D


def calc_partdens_up(curr_leader, num_edges, groups, cid2numedges, cid2numnodes, newcid2cids, curr_partitions):
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

    # find belonging cid
    belonging_cid = [k for k, v in groups.items() if curr_leader in v][0]

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
    partitions = [leader_tmp for leader_tmp in partitions if leader_tmp not in groups[belonging_cid]]
    partitions.append(belonging_cid)

    # Calculate partition density
    D = partition_density(num_edges, cid2numedges, cid2numnodes, partitions)

    return partitions, D


def calc_partdens_down(curr_leader, num_edges, cid2numedges, cid2numnodes, groups, curr_partitions):
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
    group_down = groups[curr_leader]

    # update partitions
    partitions = partitions + group_down

    # Calculate partition density
    D = partition_density(num_edges, cid2numedges, cid2numnodes, partitions)

    return partitions, D


def tune_cut(similarity_value, best_D, cid2numedges, cid2numnodes, newcid2cids, groups, num_edges, level, threshold, stopping_threshold=None, montecarlo=False, epsilon=None):

    leaders = level[similarity_value] 

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

        # find belonging cid
        belonging_cid = [k for k, v in groups.items() if curr_leader in v][0]

        if belonging_cid == max(list(newcid2cids.keys())) or belonging_cid in list(groups.values())[-1]:
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

        i += 1

        if curr_direction == 'up':

            # Move one level up   

            partitions_tmp, curr_D = calc_partdens_up(curr_leader, num_edges, groups, cid2numedges, cid2numnodes, newcid2cids, curr_partitions)

        else:
            # Move one level down

            if curr_leader < num_edges:
                partitions_tmp, curr_D = curr_partitions, best_D
            else:
                partitions_tmp, curr_D = calc_partdens_down(curr_leader, num_edges, cid2numedges, cid2numnodes, groups, curr_partitions)

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

                if (a < epsilon): 
                    if curr_direction == 'up':
                        only_down_lst = list(set(only_down_lst + list(set(partitions_tmp).difference(curr_partitions))))
                    else:
                        only_up_lst = list(set(only_up_lst + list(set(partitions_tmp).difference(curr_partitions))))
                    curr_partitions = partitions_tmp
                    best_D = curr_D
                    list_D[i] = best_D
                    list_clusters[i] = len(curr_partitions)

                if i > threshold:
                    break

        if not montecarlo:
            if (i > threshold) and ((best_D - previous_D) < 0.01):
                early_stop += 1
            else:
                early_stop = 0

            if early_stop > stopping_threshold:
                break

    return list_D, list_clusters, curr_partitions