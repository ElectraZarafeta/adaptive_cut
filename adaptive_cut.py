#%%

from ast import Try
import pickle
import itertools

from numpy import partition
from sklearn.exceptions import DataConversionWarning

# Load data

linkage = []
for line in open('output/linkage.txt'):
    L = line.strip().split()
    linkage.append((int(L[0]), int(L[1]), float(L[2]), int(L[3])))

with open('output/num_edges.txt') as f:
    num_edges = int(f.read())

def load_dict(filename):
    file = open("output/"+filename, "rb")

    return pickle.load(file)

newcid2cids = load_dict('newcid2cids.pkl')
cid2edges = load_dict('cid2edges.pkl')
cid2nodes = load_dict('cid2nodes.pkl')
groups = load_dict('groups.pkl')

#%%

# Link density
def Dc(m, n):
    try:
        return (m * (m - n + 1.0)) / ((n - 2.0) * (n - 1.0))
    except ZeroDivisionError:
        return 0.0

M = 2/num_edges
groups.reverse()
last_group = groups[0]
key_list = list(newcid2cids.keys())
val_list = list(newcid2cids.values())
best_D = 0
partition_list, best_partitions, child_list = [], [], []


#%%

for group in groups:
    Dc_list = []
    print('\n\nBeginning\n')
    print(group)
    print(best_D)
    print(best_partitions)

    if len(set(group).intersection(child_list)) > 0:
        continue

    if group == last_group:
        partition_list.append(set([group[0], group[1]]))
        m1, n1 = len(cid2edges[group[0]]), len(cid2nodes[group[0]])
        m2, n2 = len(cid2edges[group[1]]), len(cid2nodes[group[1]])
        Dc1, Dc2 = Dc(m1, n1), Dc(m2, n2)

        D = M * (Dc1 + Dc2)
    else:
        tmp_list = partition_list[-1]
        tmp_list2 = []
        for cid in group:
            belonging_cid = [key  for (key, value) in newcid2cids.items() if cid in value][0]
            tmp_list = [c for c in tmp_list if c != belonging_cid]
            tmp_list2.append(cid)

            m, n = len(cid2edges[cid]), len(cid2nodes[cid])
            Dc_list.append(Dc(m, n))
        
        partition_list.append(set(tmp_list + tmp_list2))


        D = M * sum(Dc_list)

    if D < best_D:
        
        for cid in group:
            child_list = child_list + [i for (key, value) in newcid2cids.items() for i in value if key == cid]

        partition_list = partition_list[:-1]
    else:
        best_D = D
        best_partitions = partition_list[-1]

    print('End\n')
    print(D)
    print(best_D)
    print(best_partitions)


#%%

