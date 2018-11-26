import networkx as nx
from networkx.algorithms.community import k_clique_communities
from networkx.algorithms.reciprocity import reciprocity

def calc_betweenness(graph):
    print("Calculating betweenness centralities")
    bb = nx.betweenness_centrality(graph)
    nx.set_node_attributes(graph, bb, 'betweenness')

def calc_cliques(graph):
    clique_dict = {}
    print("Finding all cliques")
    cliques = list(nx.find_cliques(graph))
    counter = 1
    for clique in cliques:
        if len(clique) > 2:
            for node in clique:
                clique_dict[node] = counter
            counter += 1
        else:
            for node in clique:
                clique_dict[node] = 0
    nx.set_node_attributes(graph, clique_dict, name="clique")
    return cliques


def find_communities(graph, cliques):
    print("Constructing communities")
    community_dict_2 = {}
    community_dict_3 = {}
    communities_k2 = list(k_clique_communities(graph, 2, cliques=cliques))
    communities_k3 = list(k_clique_communities(graph, 3, cliques=cliques))
    label = 0
    for community in communities_k2:
        for node in community:
            community_dict_2[node] = label
        label += 1

    for community in communities_k3:
        for node in community:
            community_dict_3[node] = label
        label += 1
    nx.set_node_attributes(graph, community_dict_2, name="communityktwo")
    nx.set_node_attributes(graph, community_dict_3, name="communitykthree")


def export_giant(graph):
    giant = max(nx.connected_component_subgraphs(graph), key=len)
    nx.write_gml(giant, "giant_component.gml", stringizer=nx.readwrite.gml.literal_stringizer)

def analyze(graph):
   #Done in gephi
   #calc_betweenness(graph)
   cliques = calc_cliques(graph)
   find_communities(graph, cliques)
   export_giant(graph)
   nx.write_gml(graph, "test_graph.gml", stringizer=nx.readwrite.gml.literal_stringizer)