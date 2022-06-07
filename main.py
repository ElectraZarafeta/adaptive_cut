#%%

%load_ext autoreload
%autoreload 2

import networkx as nx
from node_communities import nodeCommunities
from plots import create_color_map

G = nx.karate_club_graph()

# Select 'Infomap', 'CPM' or 'Modularity'
nodeCommunities(G, method='Modularity')

create_color_map(G, 'community')

#%%