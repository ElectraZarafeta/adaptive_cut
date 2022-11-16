import pickle
from random import randint
import pandas as pd
import numpy as np

def save_dict(dictname, filename):
    f = open(filename,"wb")

    pickle.dump(dictname,f)

    f.close()


def load_dict(filename):
    file = open(filename, "rb")

    return pickle.load(file)
    

def Dc(m, n):
    try:
        return (m * (m - n + 1.0)) / ((n - 2.0) * (n - 1.0))
    except ZeroDivisionError:
        return 0.0

def swap(a,b):
    if a > b:
        return b,a
    return a,b

def color_dict(cid2edges):
    colors_dict = {}

    for cid in cid2edges.keys():
        colors_dict[cid] = '#%06X' % randint(0, 0xFFFFFF)

    return colors_dict


def groups_generator(linkage, newcid2cids, num_edges):

    df = pd.DataFrame(np.array(linkage), columns = ['cid1','cid2','sim','num_edges'])
    df['pairs'] = df.apply(lambda x: [x['cid1'], x['cid2']], axis=1)
    df = df[['pairs', 'sim']]
    df_grouped = df.groupby('sim').agg(lambda x: list(x))
    total_groups, level = {}, {}

    # -1 corresponds to the leaves level
    level[-1] = [i for i in range(num_edges)]
    
    for index, row in df_grouped.iterrows():

        curr_level = row['pairs']

        flat_list = [item for sublist in curr_level for item in sublist]
        groups = {}

        for pair in curr_level:
            cid1, cid2 = pair[0], pair[1]

            if cid1 in list(groups.keys()) and cid2 in list(groups.keys()):
                belonging_cid = max([key for v in [cid1, cid2] for (key, value) in newcid2cids.items() if v in value])
                
                groups[belonging_cid] = groups[cid1] + groups[cid2]

                del groups[cid1]
                del groups[cid2]

            elif cid1 in list(groups.keys()):
                belonging_cid = [key for (key, value) in newcid2cids.items() if cid1 in value][0]
                
                groups[belonging_cid] = groups[cid1] + [cid2]

                del groups[cid1]
            
            elif cid2 in list(groups.keys()):
                belonging_cid = [key for (key, value) in newcid2cids.items() if cid2 in value][0]
                
                groups[belonging_cid] = groups[cid2] + [cid1]

                del groups[cid2]

            else:

                if cid1 < num_edges and cid2 < num_edges:

                    belonging_cid = max([key for v in [cid1, cid2] for (key, value) in newcid2cids.items() if v in value])
                    groups[belonging_cid] = [int(cid1), int(cid2)]
    
                elif cid1 >= num_edges and cid2 >= num_edges:

                    cids1_1, cids1_2 = newcid2cids[cid1][0], newcid2cids[cid1][1]
                    cids2_1, cids2_2 = newcid2cids[cid2][0], newcid2cids[cid2][1]

                    if (cids1_1 in flat_list) and (cids1_2 in flat_list) and (cids2_1 in flat_list) and (cids2_2 in flat_list):

                        belonging_cid = max([key for v in groups_tmp for (key, value) in newcid2cids.items() if v in value])
                        groups[belonging_cid] = groups_tmp

                    elif (cids1_1 in flat_list) and (cids1_2 in flat_list):

                        groups_tmp = [cids1_1, cids1_2, int(cid2)]

                        belonging_cid = max([key for v in groups_tmp for (key, value) in newcid2cids.items() if v in value])
                        groups[belonging_cid] = groups_tmp

                    elif (cids2_1 in flat_list) and (cids2_2 in flat_list):

                        belonging_cid = max([key for v in groups_tmp for (key, value) in newcid2cids.items() if v in value])
                        groups[belonging_cid] = groups_tmp

                    else:

                        belonging_cid = max([key for v in [int(cid1), int(cid2)] for (key, value) in newcid2cids.items() if v in value])
                        groups[belonging_cid] = [int(cid1), int(cid2)]

                elif cid1 >= num_edges:

                    cids1_1, cids1_2 = newcid2cids[cid1][0], newcid2cids[cid1][1]

                    if (cids1_1 in flat_list) and (cids1_2 in flat_list):

                        groups_tmp = [cids1_1, cids1_2, int(cid2)]

                        belonging_cid = max([key for v in groups_tmp for (key, value) in newcid2cids.items() if v in value])
                        groups[belonging_cid] = groups_tmp

                    else:
                        belonging_cid = max([key for v in [int(cid1), int(cid2)] for (key, value) in newcid2cids.items() if v in value])
                        groups[belonging_cid] = [int(cid1), int(cid2)]

                
                elif cid2 >= num_edges:

                    cids2_1, cids2_2 = newcid2cids[cid2][0], newcid2cids[cid2][1]

                    if (cids2_1 in flat_list) and (cids2_2 in flat_list):

                        groups_tmp = [cids2_1, cids2_2, int(cid1)]

                        belonging_cid = max([key for v in groups_tmp for (key, value) in newcid2cids.items() if v in value])
                        groups[belonging_cid] = groups_tmp

                    else:
                        belonging_cid = max([key for v in [int(cid1), int(cid2)] for (key, value) in newcid2cids.items() if v in value])
                        groups[belonging_cid] = [int(cid1), int(cid2)]

        curr_partitions = list(groups.keys()) + [v for v in list(level.values())[-1] if v not in flat_list]
        level[index] = curr_partitions
        total_groups.update(groups)

    return total_groups, level