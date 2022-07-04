#%%

'''
- Only connected pairs of links
- Shared node k = keystone
- i and j impost nodes
'''

from itertools import combinations, chain
from collections import defaultdict
from re import A
from scipy.cluster import hierarchy
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram
from copy import copy

#%%
def swap(a,b):
    if a > b:
        return b,a
    return a,b

# Load Les miserables preprocessed dataset
# Create adjacency dictionary
# and a set with all edges in the network
def read_edgelist_unweighted(filename, delimiter=None):
    adj = defaultdict(set)
    edges = set()
    # Loop through each edge in the network
    for line in open(filename):
        # Get the list of nodes in each edge
        L = line.strip().split(delimiter)
        ni, nj = L[0], L[1]
        if ni != nj: 
            edges.add( swap(int(ni), int(nj)) )
            # Create adjacency dictionary
            adj[ni].add(nj)
            adj[nj].add(ni)
    return dict(adj), edges

def read_edgelist_weighted(filename, delimiter=None):
    adj = defaultdict(set)
    edges = set()
    wij_dict = {}
    # Loop through each edge in the network
    for line in open(filename):
        # Get the list of nodes in each edge
        L = line.strip().split(delimiter)
        ni, nj, wij = L[0], L[1], float(L[2])
        if ni != nj: 
            edges.add( swap(int(ni), int(nj)) )
            wij_dict[ni, nj] = wij
            # Create adjacency dictionary
            adj[ni].add(nj)
            adj[nj].add(ni)
    return dict(adj), edges, wij_dict

# Step 1, 2
#adj, edges = read_edgelist_unweighted('lesmis/lesmis_unweighted.txt', '-')
adj, edges, wij = read_edgelist_weighted('lesmis/lesmis_weighted.txt', '-')

#%%

# Similarities
def similarities_unweighted(adj):
    # inclusive neighbors
    inclusive = dict( (n,adj[n] | set([n])) for n in adj)
    similarities = []
    # loop through the keystone node
    for node in adj:
        if len(adj[node]) > 1:
            # loop through the combinations of impost nodes
            for i, j in combinations(adj[node], 2):
                edges = swap(swap(int(i),int(node)), swap(int(node),int(j)))
                inc_ni, inc_nj = inclusive[i], inclusive[j]
                # Jaccard index
                jaccard_index = len(inc_ni & inc_nj) / len(inc_ni | inc_nj)
                # Create list with calculated similarities for all connected pairs of links
                similarities.append((1-jaccard_index, edges)) 

    similarities.sort(key = lambda x: (x[0], x[1]))
    return similarities

def similarities_weighted(adj, wij):
    # inclusive neighbors
    inclusive = dict( (n,adj[n] | set([n])) for n in adj)

    # Tanimoto coefficient
    Aij = copy(wij)
    a_sqrd = {}

    for node in adj:
        Aij[node, node] = sum(wij[swap(node, i)] for i in adj[node]) / len(adj[node])
        a_sqrd[node] = sum(Aij[swap(node, i)]**2 for i in inclusive[node])

    similarities = []
    # loop through the keystone node
    for node in adj:
        if len(adj[node]) > 1:
            # loop through the combinations of impost nodes
            for i, j in combinations(adj[node], 2):
                edges = swap(swap(int(i),int(node)), swap(int(node),int(j)))
                inc_ni, inc_nj = inclusive[i], inclusive[j]

                # Tanimoto coefficient
                ai_dot_aj = sum(Aij[swap(i, k)]*Aij[swap(j, k)] for k in inc_ni & inc_nj)
                
                S = ai_dot_aj/(a_sqrd[i] + a_sqrd[j] - ai_dot_aj)
                # Create list with calculated similarities for all connected pairs of links
                similarities.append((1-S, edges)) 

    similarities.sort(key = lambda x: (x[0], x[1]))
    return similarities

# Step 3
#similarities = similarities_unweighted(adj)
similarities = similarities_weighted(adj, wij)
#%%

# Each link is initially assigned to its own community
def initialize_edges(edges):
    edge2cid, cid2edges, orig_cid2edge, cid2nodes = {}, {}, {}, {}

    for cid,edge in enumerate(edges):
        edge = swap(*edge) # just in case
        edge2cid[edge] = cid
        cid2edges[cid] = set([edge])
        orig_cid2edge[cid]  = edge
        cid2nodes[cid] = set( edge )
    curr_maxcid = len(edges) - 1

    return edge2cid, cid2edges, orig_cid2edge, cid2nodes, curr_maxcid

# Step 4
edge2cid, cid2edges, orig_cid2edge, cid2nodes, curr_maxcid = initialize_edges(edges)

#%%

# Link density
def Dc(m, n):
    return (m * (m - n + 1.0)) / ((n - 2.0) * (n - 1.0))

# Single-linkage hierarchical clustering
linkage = []

for oms, edges in similarities:
    sim = 1-oms
    edge1, edge2 = edges[0], edges[1]

    comm_id1, comm_id2 = edge2cid[edge1], edge2cid[edge2]
    if comm_id1 == comm_id2: # already merged!
        continue

    m1,m2 = len(cid2edges[comm_id1]),len(cid2edges[comm_id2])
    if m2 > m1:
        comm_id1, comm_id2 = comm_id2, comm_id1

    curr_maxcid += 1
    newcid = curr_maxcid
    cid2edges[newcid] = cid2edges[comm_id1] | cid2edges[comm_id2]
    cid2nodes[newcid] = set()

    for e in chain(cid2edges[comm_id1], cid2edges[comm_id2]):
        cid2nodes[newcid] |= set(e)
        edge2cid[e] = newcid

    num_samples = len(cid2edges[comm_id1]) + len(cid2edges[comm_id2])

    del cid2edges[comm_id1], cid2nodes[comm_id1]
    del cid2edges[comm_id2], cid2nodes[comm_id2]

    linkage.append((comm_id1, comm_id2, oms, num_samples))

linkage
#%%

fig = plt.figure(figsize=(40,40))
dendrogram(linkage, labels=list(orig_cid2edge.values()))
plt.show()

#%%