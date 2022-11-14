from helper_functions import *
from scipy import cluster
import numpy as np
import random
from logger import logger 
from methods.link_clustering import *
from scipy.cluster import *


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


def calc_partdens_up(curr_leader, num_edges, cid2edges, cid2nodes, newcid2cids, curr_partitions):
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
    belonging_cid = [key  for (key, value) in newcid2cids.items() if curr_leader in value][0]

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
    curr_partitions = leaders
    early_stop = 0

    i = 0

    list_D, list_clusters = {}, {}
    list_D[i] = best_D
    list_clusters[i] = len(curr_partitions)

    while True:

        curr_leader = random.choice(curr_partitions)

        # logger.warning(curr_leader)
        # logger.warning(curr_direction)

        if curr_leader not in leaders:
            # logger.warning('Curr leader not in leaders')
            continue

        curr_direction = random.choice(direction)

        i += 1

        # logger.warning(f'Current iter {i}')

        if curr_direction == 'up':

            # Move one level up    

            partitions_tmp, curr_D = calc_partdens_up(curr_leader, num_edges, cid2edges, cid2nodes, newcid2cids, curr_partitions)

        else:
            # Move one level down

            if curr_leader < num_edges:
                partitions_tmp, curr_D = curr_partitions, best_D
            else:
                partitions_tmp, curr_D = calc_partdens_down(curr_leader, num_edges, cid2edges, cid2nodes, newcid2cids, groups, curr_partitions)

        previous_D = best_D

        if curr_D >= best_D:
            curr_partitions = partitions_tmp
            best_D = curr_D
            list_D[i] = best_D
            list_clusters[i] = len(curr_partitions)
        else:
            if montecarlo:
                a = random.uniform(0, 1)

                if i <= threshold[0]:
                    epsilon_tmp = epsilon[0]
                elif i <= (threshold[0]*2):
                    epsilon_tmp = epsilon[1]
                elif i <= (threshold[0]*2 + threshold[1]):
                    epsilon_tmp = epsilon[2]
                elif i <= (threshold[0]*2 + threshold[1]*2):
                    epsilon_tmp = epsilon[3]
                elif i <= (threshold[0]*2 + threshold[1]*3):
                    epsilon_tmp = epsilon[4]
                elif i <= (threshold[0]*2 + threshold[1]*4):
                    epsilon_tmp = epsilon[5]
                elif i <= (threshold[0]*2 + threshold[1]*5):
                    epsilon_tmp = epsilon[6]
                else:
                    break

                # logger.warning(a)
                # logger.warning(epsilon_tmp)
                # logger.warning(previous_D)
                # logger.warning(best_D)
                # logger.warning(curr_D)

                if (a < epsilon_tmp) and ((best_D - curr_D) < 0.001): #0.01
                    curr_partitions = partitions_tmp
                    best_D = curr_D
                    list_D[i] = best_D
                    list_clusters[i] = len(curr_partitions)

        if not montecarlo:
            if (i > threshold) and ((best_D - previous_D) < 0.01):
                early_stop += 1
            else:
                early_stop = 0

            if early_stop > stopping_threshold:
                break


    return list_D, list_clusters, curr_partitions