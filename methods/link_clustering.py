from itertools import combinations, chain
from collections import defaultdict
from copy import copy
import logging
from helper_functions import *
from logger import logger
import numpy as np

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
    edge2cid, cid2edges, orig_cid2edge, cid2nodes, is_grouped = {}, {}, {}, {}, {}
    curr_maxcid = 0

    for cid,edge in enumerate(edges):
        edge = swap(*edge) # just in case
        edge2cid[edge] = cid
        cid2edges[cid] = set([edge])
        orig_cid2edge[cid]  = edge
        cid2nodes[cid] = set( edge )
        is_grouped[edge] = False
    curr_maxcid = len(edges) - 1

    return edge2cid, cid2edges, orig_cid2edge, cid2nodes, curr_maxcid, is_grouped


# Single-linkage hierarchical clustering
def single_linkage_HC(edges, num_edges, similarities, is_grouped, edge2cid, cid2edges, cid2nodes, curr_maxcid):

    linkage = [] # [(comm_id1, comm_id2, oms, num_edges)]
    D = 0.0 # partition density

    list_D = [(0.0, 1.0)] # (Partion density value, Similarity value)
    list_D_plot = [(0.0, 0.0)]
    S_prev = -1.0
    M = 2/num_edges
    newcid2cids = {}
    groups_tmp, groups = [], []

    for i, (oms, edges) in enumerate(chain(similarities, [(1.0, (None, None))])):
        sim = 1-oms

        if sim != S_prev:
            
            for k in is_grouped:
                is_grouped[k] = False

            list_D.append((D, sim))
            list_D_plot.append((D, oms))
            S_prev = sim


        edge1, edge2 = edges[0], edges[1]
        if not edge1 or not edge2: # We'll get (None, None) at the end of clustering
            if len(groups_tmp) > 0:
                groups.append(list(set(groups_tmp)))
            continue

        comm_id1, comm_id2 = edge2cid[edge1], edge2cid[edge2]
        
        if comm_id1 == comm_id2: # already merged!
            continue

        # logging.warning(f'loop {i}')
        # logging.warning(f'oms {oms}')
        # logging.warning(f'edge1 {edge1}, edge2 {edge2}')
        # logging.warning(f'comm1 {comm_id1}, comm2 {comm_id2}')

        if is_grouped[edge1] and is_grouped[edge2]:
            groups_tmp.append(comm_id1)
            groups_tmp.append(comm_id2)

            # logging.warning('Case 1')

        elif is_grouped[edge1]:

            # logging.warning('Case 2')
            groups_tmp.append(comm_id2)

            if comm_id1 > num_edges:
                cids = newcid2cids[comm_id1]
                for row in linkage_np:
                    if (int(row[0]) == cids[0] and int(row[1]) == cids[1]) or (int(row[1]) == cids[0] and int(row[0]) == cids[1]):
                        if row[2] == oms:
                            groups_tmp.append(comm_id1)

                            break


            # if comm_id1 == 2830:
            #     logger.warning(f'groups_tmp {groups_tmp}')

        elif is_grouped[edge2]:

            # logging.warning('Case 3')
            groups_tmp.append(comm_id1)

            if comm_id2 > num_edges:
                cids = newcid2cids[comm_id2]
                for row in linkage_np:
                    if (int(row[0]) == cids[0] and int(row[1]) == cids[1]) or (int(row[1]) == cids[0] and int(row[0]) == cids[1]):
                        if row[2] == oms:
                            groups_tmp.append(comm_id2)

                            break


        else:

            # logging.warning('Case 4')
            if len(groups_tmp) > 0:
                groups.append(list(set(groups_tmp)))
            groups_tmp = []
            groups_tmp.append(comm_id1)
            groups_tmp.append(comm_id2)


        # if comm_id1 == 398 or comm_id2 == 398:


        #     break

        is_grouped[edge1] = True
        is_grouped[edge2] = True
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

        m, n = len(cid2edges[newcid]), len(cid2nodes[newcid])

        linkage.append((comm_id1, comm_id2, oms, m))

        linkage_np = np.array(linkage)

        Dc12 = Dc(m, n)
        D += (Dc12 - Dc1 - Dc2) * M

    return linkage, list_D_plot, groups, newcid2cids


def link_clustering(filename, delimiter):
    adj, edges = read_edgelist_unweighted(filename=filename, delimiter=delimiter)
    #adj, edges, wij = read_edgelist_weighted('lesmis/lesmis_weighted.txt', '-')

    similarities = similarities_unweighted(adj=adj) #similarities_weighted(adj, wij)

    edge2cid, cid2edges, orig_cid2edge, cid2nodes, curr_maxcid, is_grouped = initialize_edges(edges=edges)

    linkage, list_D_plot, groups, newcid2cids = single_linkage_HC(edges=edges, num_edges=len(edges), similarities=similarities, is_grouped=is_grouped, edge2cid=edge2cid, cid2edges=cid2edges, cid2nodes=cid2nodes, curr_maxcid=curr_maxcid)

    return linkage, list_D_plot, groups, newcid2cids, orig_cid2edge, cid2edges, cid2nodes, len(edges)


