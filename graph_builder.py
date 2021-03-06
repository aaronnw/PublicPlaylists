import networkx as nx
import math
import random

#An edge-tuple can be a 2-tuple of nodes or a 3-tuple with 2 nodes followed by an edge attribute dictionary, e.g., (2, 3, {'weight': 3.1415})

def add_node(graph, track_id, track):
    title = track.title
    artist = track.artist
    graph.add_node(track_id, title=title, artist=artist)

def build_graph(edges, track_data):
    G = nx.Graph()
    unique_tracks = list(track_data)
    sampled_tracks = random.sample(unique_tracks, 2000)
    graph_edges = []
    for tid in sampled_tracks:
        #Count the number of times a song is related to others
        max_connections = max([edge[1] for edge in edges[tid]])
        if max_connections > 1:
            # Convert weird characters to work with the write
            add_node(G, tid, track_data[tid])
            for related in edges[tid]:
                if related[1] > 1:
                    related_track = related[0]
                    add_node(G, related_track, track_data[related_track])
                    graph_edges.append((tid, related[0], {'weight' : related[1]}))
    G.add_edges_from(graph_edges)
    return G

def export_edge_list(edges):
    with open("edges.txt", 'w') as file:
        for key in edges.keys():
            for val in edges[key]:
                rep = key + ' ' + str(val[0]) + ' ' + str(val[1]) + '\n'
                file.write(rep)