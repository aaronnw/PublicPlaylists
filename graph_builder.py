import networkx as nx


#An edge-tuple can be a 2-tuple of nodes or a 3-tuple with 2 nodes followed by an edge attribute dictionary, e.g., (2, 3, {'weight': 3.1415})

def build_graph(edges, track_data):
    G = nx.Graph()
    unique_tracks = list(track_data)
    graph_edges = []
    graph_nodes = []
    for tid in unique_tracks:
        #Count the number of times a song is related to others
        max_connections = max([edge[1] for edge in edges[tid]])
        if max_connections > 1:
            G.add_node(tid, title=track_data[tid].title, artist=track_data[tid].artist)
            for related in edges[tid]:
                if related[1] > 1:
                    graph_edges.append((tid, related[0], {'weight' : related[1]}))
    G.add_edges_from(graph_edges)
    nx.write_gml(G, "test_graph.gml")

def export_edge_list(edges):
    with open("edges.txt", 'w') as file:
        for key in edges.keys():
            for val in edges[key]:
                rep = key + ' ' + str(val[0]) + ' ' + str(val[1]) + '\n'
                file.write(rep)