import networkx as nx
from networkx.algorithms.community import k_clique_communities

def betweenness(graph):
    print("Calculating betweenness centralities")
    bb = nx.betweenness_centrality(graph)
    nx.set_node_attributes(graph, bb, 'betweenness')

def cliques(graph):
    community_dict = {}
    print("Finding all cliques")
    cliques = nx.find_cliques(graph)
    print("Constructing communities")
    communities = list(k_clique_communities(graph, 3, cliques=cliques))
    label = 0
    for community in communities:
        for node in community:
            community_dict[node] = label
        label += 1
    nx.set_node_attributes(graph, community_dict, name="community")

def analyze(graph):
   betweenness(graph)
   cliques(graph)
   nx.write_gml(graph, "test_graph.gml", stringizer=nx.readwrite.gml.literal_stringizer)