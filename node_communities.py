import networkx as nx
from infomap import Infomap
from networkx.algorithms.community import k_clique_communities, greedy_modularity_communities

def map_communities(G, communities):
    """Return a mapping of community membership from a community set tuple"""
    community_map = {}
    for node in G.nodes():
        for i, comm in enumerate(communities):
            if node in comm:
                community_map[node] = i
        if community_map.get(node, None) is None:
            community_map[node] = None
    return community_map

def nodeCommunities(G, method):

    if method == 'Infomap':
        infomap_wrapper = Infomap("--two-level")

        print("Building Infomap network from a NetworkX graph...")
        for e in G.edges():
            infomap_wrapper.addLink(*e)

        print("Find communities with Infomap...")
        infomap_wrapper.run();

        print("Found {} modules with codelength: {}".format(str(infomap_wrapper.numTopModules()), str(infomap_wrapper.codelength)))

        communities = {}
        for node in infomap_wrapper.iterLeafNodes():
            communities[node.physicalId] = node.moduleIndex()

        nx.set_node_attributes(G, values=communities, name='community')

    elif method == 'CPM':
        k_clique = k_clique_communities(G, 3)
        k_clique_comm = [list(community) for community in k_clique]

        communities = map_communities(G, k_clique_comm)

        nx.set_node_attributes(G, values=communities, name='community')

    elif method == 'Modularity':
        comm = greedy_modularity_communities(G)

        communities = [list(community) for community in comm]

        communities = map_communities(G, comm)

        nx.set_node_attributes(G, values=communities, name='community')

