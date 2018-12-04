import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import math
from networkx.algorithms.community import k_clique_communities

# Plot the degree distributions
def plot_dist(graph):
    # Get all the degrees from the graph
    degrees = [val for (node, val) in graph.degree()]
    # Get the count of each degree
    deg_counts = Counter(degrees)
    k = range(1,max(degrees))
    p = [0] * max(degrees)

    # Get the probability distribution for a node to be <=k
    for degree in k:
        p[degree] = 0
        for other_degree, count in deg_counts.items():
            if other_degree > degree:
                p[degree] += count

    p = [val for val in p if val > 0]

    # Create a linear plot
    plt.plot(k, p)
    plt.xlabel("k")
    plt.ylabel("p(k)")
    plt.title("Linear plot of degree distribution")
    plt.show()

    # Create the log-log plot
    log_k = [math.log(val) for val in k]
    log_p = [math.log(val) for val in p if val > 0]
    plt.plot(log_k, log_p)
    plt.xlabel("log(k)")
    plt.ylabel("log(p(k))")
    plt.title("Log-Log plot of degree distribution")
    plt.show()

# Calculate betweenness centralities with networkX
def calc_betweenness(graph):
    print("Calculating betweenness centralities")
    bb = nx.betweenness_centrality(graph)
    nx.set_node_attributes(graph, bb, 'betweenness')

# Find all the cliques in the graph
def calc_cliques(graph):
    clique_dict = {}
    print("Finding cliques\n")
    # This returns a list of cliques, stored as lists
    cliques = list(nx.find_cliques(graph))
    counter = 1
    # For every clique list
    for clique in cliques:
        # Ignore 2-cliques
        if len(clique) > 2:
            # Assign the nodes to a new clique value
            for node in clique:
                clique_dict[node] = counter
            counter += 1
        else:
            # Assign 2-cliques and below to not be part of a clique
            for node in clique:
                clique_dict[node] = 0
    nx.set_node_attributes(graph, clique_dict, name="clique")
    return cliques

# Using cliques, do clique percolation to find communities
def find_communities(graph, cliques, graph_type):
    print("Calculating for: ", graph_type)
    print("Constructing communities")

    # Can also be done for k=2 if we didn't ignore 2-cliques above
    community_dict_3 = {}
    communities_k3 = list(k_clique_communities(graph, 3, cliques=cliques))
    label = 0
    sizes = []
    # Assign labels to each node based on their community
    for community in communities_k3:
        size = 0
        for node in community:
            community_dict_3[node] = label
            size += 1
        sizes.append(size)
        label += 1

    avg_size = sum(sizes) / len(sizes)
    print("Number of communities: ", len(sizes))
    print("Average community size: ", avg_size)
    print("Number of songs in communities: ", sum(sizes), "\n")

    nx.set_node_attributes(graph, community_dict_3, name="communitykthree")

'''Call a variety of graph analzying methods, some from networkx, and add the attributes to the graph object before
 exporting'''
def analyze(graph):
   #Done in gephi
   #calc_betweenness(graph)
   plot_dist(graph)
   giant = max(nx.connected_component_subgraphs(graph), key=len)
   all_cliques = calc_cliques(graph)
   find_communities(graph, all_cliques, "Entire Graph")

   giant_cliques = calc_cliques(giant)
   find_communities(giant, giant_cliques, "Giant Component")
   nx.write_gml(giant, "giant_component.gml", stringizer=nx.readwrite.gml.literal_stringizer)
   nx.write_gml(graph, "test_graph.gml", stringizer=nx.readwrite.gml.literal_stringizer)