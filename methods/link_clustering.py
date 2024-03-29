from itertools import combinations, chain
from collections import defaultdict
from copy import copy
from helper_functions import *
from logger import logger

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


# Each link is initially assigned to its own community
def initialize_edges(edges):
    edge2cid, cid2edges, orig_cid2edge, cid2nodes, cid2numedges, cid2numnodes  = {}, {}, {}, {}, {}, {}
    curr_maxcid = 0

    for cid,edge in enumerate(edges):
        edge = swap(*edge) # just in case
        edge2cid[edge] = cid
        cid2edges[cid] = set([edge])
        orig_cid2edge[cid]  = edge
        cid2nodes[cid] = set( edge )
        cid2numedges[cid] = 1
        cid2numnodes[cid] = 1
    curr_maxcid = len(edges) - 1

    return edge2cid, cid2edges, orig_cid2edge, cid2nodes, curr_maxcid, cid2numedges, cid2numnodes


# Single-linkage hierarchical clustering
def single_linkage_HC(num_edges, similarities, edge2cid, cid2edges, cid2nodes, curr_maxcid, cid2numedges, cid2numnodes):

    linkage = [] # [(comm_id1, comm_id2, oms, num_edges)]
    D = 0.0 # partition density

    list_D = [(0.0, 1.0)] # (Partion density value, Similarity value)
    list_D_plot = [(0.0, 0.0)]
    S_prev = -1.0
    M = 2/num_edges
    newcid2cids = {}

    cid2numedges_tmp, cid2numnodes_tmp = copy(cid2numedges), copy(cid2numnodes)

    for i, (oms, edges) in enumerate(chain(similarities, [(1.0, (None, None))])):
        sim = 1-oms

        if sim != S_prev:

            list_D.append((D, sim))
            list_D_plot.append((D, oms))
            S_prev = sim


        edge1, edge2 = edges[0], edges[1]
        if not edge1 or not edge2: # We'll get (None, None) at the end of clustering
            continue

        comm_id1, comm_id2 = edge2cid[edge1], edge2cid[edge2]
        
        if comm_id1 == comm_id2: # already merged!
            continue

        m1, m2 = len(cid2edges[comm_id1]), len(cid2edges[comm_id2])
        n1, n2 = len(cid2nodes[comm_id1]), len(cid2nodes[comm_id2])
        Dc1, Dc2 = Dc(m1, n1), Dc(m2, n2) 

        if m2 > m1:
            comm_id1, comm_id2 = comm_id2, comm_id1

        curr_maxcid += 1
        newcid = curr_maxcid
        newcid2cids[newcid] = swap(comm_id1, comm_id2)
        cid2edges[newcid] = cid2edges[comm_id1] | cid2edges[comm_id2]
        cid2nodes[newcid] = set()


        for e in chain(cid2edges[comm_id1], cid2edges[comm_id2]):
            cid2nodes[newcid] |= set(e)
            edge2cid[e] = newcid

        del cid2edges[comm_id1], cid2edges[comm_id2]
        del cid2nodes[comm_id1], cid2nodes[comm_id2]

        m, n = len(cid2edges[newcid]), len(cid2nodes[newcid])

        cid2numedges_tmp[newcid] = m
        cid2numnodes_tmp[newcid] = n

        linkage.append((comm_id1, comm_id2, oms, m))

        Dc12 = Dc(m, n)
        D += (Dc12 - Dc1 - Dc2) * M

    return linkage, list_D_plot, newcid2cids, cid2numedges_tmp, cid2numnodes_tmp


def link_clustering(filename, delimiter):

    adj, edges = read_edgelist_unweighted(filename=filename, delimiter=delimiter)

    similarities = similarities_unweighted(adj=adj)

    edge2cid, cid2edges, orig_cid2edge, cid2nodes, curr_maxcid, cid2numedges, cid2numnodes = initialize_edges(edges=edges)

    linkage, list_D_plot, newcid2cids, cid2numedges_m, cid2numnodes_n = single_linkage_HC(num_edges=len(edges), similarities=similarities, edge2cid=edge2cid, cid2edges=cid2edges, cid2nodes=cid2nodes, curr_maxcid=curr_maxcid, cid2numedges=cid2numedges, cid2numnodes=cid2numnodes)

    return linkage, list_D_plot, newcid2cids, orig_cid2edge, cid2numedges_m, cid2numnodes_n, len(edges)
