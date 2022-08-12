#%%

import pickle

# Load data

linkage = []
for line in open('output/linkage.txt'):
    L = line.strip().split()
    linkage.append((int(L[0]), int(L[1]), float(L[2]), int(L[3])))

def load_dict(filename):
    file = open("output/"+filename, "rb")

    return pickle.load(file)

newcid2cids = load_dict('newcid2cids.pkl')
cid2edges = load_dict('cid2edges.pkl')
cid2nodes = load_dict('cid2nodes.pkl')

#%%


