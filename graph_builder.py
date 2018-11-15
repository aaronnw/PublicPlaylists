import networkx as nx



#An edge-tuple can be a 2-tuple of nodes or a 3-tuple with 2 nodes followed by an edge attribute dictionary, e.g., (2, 3, {'weight': 3.1415})

def build_graph(edges):
    G = nx.Graph()
    unique_tracks = list(edges.keys())
    graph_edges = []
    for track in unique_tracks:
        G.add_node(track)
        for related in edges[track]:
            graph_edges.append((track, related[0], {'weight' : related[1]}))
    G.add_edges_from(graph_edges)
    nx.write_gml(G, "test_graph.gml")

def export_edge_list(edges):
    with open("edges.txt", 'w') as file:
        for key in edges.keys():
            for val in edges[key]:
                rep = key + ' ' + str(val[0]) + ' ' + str(val[1]) + '\n'
                file.write(rep)