import pandas as pd
import numpy as np

def groups_generator(linkage, newcid2cids, num_edges):

    df = pd.DataFrame(np.array(linkage), columns = ['cid1','cid2','sim','num_edges'])
    df['pairs'] = df.apply(lambda x: [x['cid1'], x['cid2']], axis=1)
    df = df[['pairs', 'sim']]
    df_grouped = df.groupby('sim').agg(lambda x: list(x))
    total_groups = [] #{}
    
    for index, row in df_grouped.iterrows():

        #total_groups[str(index)] = []
        curr_level = row['pairs']

        flat_list = [item for sublist in curr_level for item in sublist]
        groups = []

        for pair in curr_level:
            cid1, cid2 = pair[0], pair[1]

            if cid1 < num_edges and cid2 < num_edges:

                groups.append([int(cid1), int(cid2)])
  
            elif cid1 > num_edges and cid2 > num_edges:

                cids1_1, cids1_2 = newcid2cids[cid1][0], newcid2cids[cid1][1]
                cids2_1, cids2_2 = newcid2cids[cid2][0], newcid2cids[cid2][1]

                if (cids1_1 in flat_list) and (cids1_2 in flat_list) and (cids2_1 in flat_list) and (cids2_2 in flat_list):

                    groups_tmp = [cids1_1, cids1_2, cids2_1, cids2_2]

                    for group in groups:
                        if cids1_1 in group and cids1_2 not in group:
                            groups_tmp = list(set(groups_tmp + group))
                            groups_tmp.remove(cids1_2)
                            break
                        if cids2_1 in group and cids2_2 not in group:
                            groups_tmp = list(set(groups_tmp + group))
                            groups_tmp.remove(cids2_2)
                            break

                    groups = [group for group in groups if len(set(group).intersection(groups_tmp)) == 0]
                    groups.append(groups_tmp)

                elif (cids1_1 in flat_list) and (cids1_2 in flat_list):

                    groups_tmp = [cids1_1, cids1_2, int(cid2)]

                    for group in groups:
                        if cids1_1 in group and cids1_2 not in group:
                            groups_tmp = list(set(groups_tmp + group))
                            groups_tmp.remove(cids1_2)
                            break

                    groups = [group for group in groups if len(set(group).intersection(groups_tmp)) == 0]
                    groups.append(groups_tmp)

                elif (cids2_1 in flat_list) and (cids2_2 in flat_list):

                    groups_tmp = [cids2_1, cids2_2, int(cid1)]

                    for group in groups:
                        if cids2_1 in group and cids2_2 not in group:
                            groups_tmp = list(set(groups_tmp + group))
                            groups_tmp.remove(cids2_2)
                            break
                    
                    groups = [group for group in groups if len(set(group).intersection(groups_tmp)) == 0]
                    groups.append(groups_tmp)


                else:
                    groups.append([int(cid1), int(cid2)])

            elif cid1 > num_edges:

                cids1_1, cids1_2 = newcid2cids[cid1][0], newcid2cids[cid1][1]

                if (cids1_1 in flat_list) and (cids1_2 in flat_list):

                    groups_tmp = [cids1_1, cids1_2, int(cid2)]

                    for group in groups:
                        if cids1_1 in group and cids1_2 not in group:
                            groups_tmp = list(set(groups_tmp + group))
                            groups_tmp.remove(cids1_2)
                            break

                    groups = [group for group in groups if len(set(group).intersection(groups_tmp)) == 0]
                    groups.append(groups_tmp)

                else:
                    groups.append([int(cid1), int(cid2)])

            
            elif cid2 > num_edges:

                cids2_1, cids2_2 = newcid2cids[cid2][0], newcid2cids[cid2][1]

                if (cids2_1 in flat_list) and (cids2_2 in flat_list):

                    groups_tmp = [cids2_1, cids2_2, int(cid1)]

                    for group in groups:
                        if cids2_1 in group and cids2_2 not in group:
                            groups_tmp = list(set(groups_tmp + group))
                            groups_tmp.remove(cids2_2)
                            break

                    groups = [group for group in groups if len(set(group).intersection(groups_tmp)) == 0]
                    groups.append(groups_tmp)


                else:
                    groups.append([int(cid1), int(cid2)])

        #total_groups[str(index)].append(groups)
        total_groups.append(groups)

    total_groups = [item for sublist in total_groups for item in sublist]

    return total_groups