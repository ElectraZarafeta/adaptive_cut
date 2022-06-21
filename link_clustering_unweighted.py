#%%

'''
- Only connected pairs of links
- Shared node k = keystone
- i and j impost nodes
'''

from itertools import combinations, chain
from collections import defaultdict
from scipy.cluster import hierarchy

#%%
def swap(a,b):
    if a > b:
        return b,a
    return a,b

# Load Les miserables preprocessed dataset
# Create adjacency dictionary
# and a set with all edges in the network
def read_edgelist(filename, delimiter=None):
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


# Similarities
def similarities(adj):
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
                similarities.append([jaccard_index, edges]) 

    return similarities.sort(key = lambda x: x[0], reverse=True)


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


# Link density
def Dc(m, n):
    return (m * (m - n + 1.0)) / ((n - 2.0) * (n - 1.0))


def merge_communities(edge1, edge2, similarity_value):

    comm_id1, comm_id2 = edge2cid[edge1], edge2cid[edge2]
    if comm_id1 == comm_id2: # already merged!
        return

    curr_maxcid += 1
    newcid = curr_maxcid
    cid2edges[newcid] = cid2edges[comm_id1] | cid2edges[comm_id2]
    cid2nodes[newcid] = set()

    for e in chain(cid2edges[comm_id1], cid2edges[comm_id2]):
        cid2nodes[newcid] |= set(e)
        edge2cid[e] = newcid

    del cid2edges[comm_id1], cid2nodes[comm_id1]
    del cid2edges[comm_id2], cid2nodes[comm_id2]
    m,n = len(cid2edges[newcid]),len(cid2nodes[newcid])

    return (comm_id1, comm_id2, similarity_value)
#%%

# Single-linkage hierarchical clustering
def single_linkage(similarities, edge2cid):  
    best_similarity = 1.0
    best_D = 0.0
    previous_similarity = -1
    linkage = []

    for sim, edges in similarities:
        best_similarity = sim
        previous_similarity = sim

        linkage.append(merge_communities(edges[0], edges[1], sim))

    return linkage

#%%

# Step 1, 2
adj, edges = read_edgelist('lesmis/lesmis.txt', '-')

#%%

# Step 3
similarities = similarities(adj)
print(similarities[:10])

# Step 4
edge2cid, cid2edges, orig_cid2edge, cid2nodes, curr_maxcid = initialize_edges(edges)

# Step 5
linkage = single_linkage(similarities, edge2cid)

linkage
#%%