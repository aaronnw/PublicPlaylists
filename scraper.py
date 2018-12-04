import sys
import spotipy
import spotipy.util as util
import _pickle as pickle
import os
from collections import defaultdict
from collections import Counter
import graph_builder
import graph_analyzer
from track import Track

'''Originally forked from https://github.com/plamere/playlistminer for importing spotify playlist data with spotipy'''

#Set number of playlists to query for
max_playlists = 10000
data = {}
playlist_names = {}
#Link a track ID to a track object
track_data = {}
album_genres = {}

#Test if a playlist has more than one artist and album to avoid useless ones
def is_good_playlist(items):
    artists = set()
    albums = set()
    for item in items:
        track = item['track']
        if track:
            artists.add(track['artists'][0]['id'])
            albums.add(track['album']['id'])
    return len(artists) > 1 and len(albums) > 1

'''
Removed genre details
Made queries longer, lack of spotify genre data, difficult comparisons with genre lists

def get_album_genre(album_id):
    global album_genres
    if album_id in album_genres.keys():
        return album_genres[album_id]
    album = sp.album(album_id)
    genre_list = album['genres']
    if len(genre_list) < 1:
        album_genres[album_id] = "N/A"
        return "N/A"
    else:
        genre_string = ""
        for genre in genre_list:
            genre_string += ","
            genre_string += genre
        album_genres[album_id] = genre_string
        return genre_string
        '''

# Process data from a playlist id into data structures for building the graph
def process_playlist(playlist):
    global data
    global track_data
    global playlist_names

    pid = playlist['id']
    name = playlist['name']
    playlist_names[pid] = name
    uid = playlist['owner']['id']

    #Query the playlist id from spotify
    try:
        results = sp.user_playlist_tracks(uid, playlist['id'])
        # fields="items.track(!album)")

        # Check if we got a good playlist
        if results and 'items' in results and is_good_playlist(results['items']):
            data[pid] = {}
            # Look at every track in the playlist
            for item in results['items']:
                track = item['track']
                # Check if the track has the data it should
                if track and (track['name'] is not None) and (track['artists'] is not None):
                    # Create a track item with the title and artist
                    tid = track['id']
                    title = track['name']
                    album_id = track['album']['id']
                    artist = track['artists'][0]['name']
                    track_data[tid] = Track(title, artist)
                    # Add the playlist and associated tracks to the data dict
                    data[pid][tid] = Track(title, artist)
        else:
            print('mono playlist skipped')
    except spotipy.SpotifyException:
        print('trouble, skipping')
    except ConnectionError:
        print('Connection error, skipping')
    except:
        print("Skipping due to other error")

# Save the global data
def save():
    playlists_out = open('playlists.pkl', 'wb')
    tracks_out = open('tracks.pkl', 'wb')

    pickle.dump(data, playlists_out, -1)
    pickle.dump(track_data, tracks_out, -1)

    playlists_out.close()
    tracks_out.close()

# Save the processed graph data
def save_graph(G):
    graph_out = open('graph_bin.pkl', 'wb')
    pickle.dump(G, graph_out, -1)
    graph_out.close()

# Load the graph if one already exists
def load_graph():
    if os.path.exists('graph_bin.pkl'):
        graph_in = open('graph_bin.pkl', 'rb')
        graph = pickle.load(graph_in)
        graph_in.close()
        return graph
    else:
        return None

# Load data files if they already exist
def load_data():
    global data
    global track_data
    global playlist_names
    if os.path.exists('tracks.pkl') and os.path.exists('playlists.pkl'):
        playlist_file = open('playlists.pkl', 'rb')
        track_file = open('tracks.pkl', 'rb')
        data = pickle.load(playlist_file)
        track_data = pickle.load(track_file)
    else:
        data = {}
        track_data = {}
        playlist_names = {}
    return data

# Query for playlists and process their data
def crawl_playlists():
    # Search for playlists for the word "the"
    # There is probably a cleaner way to get random playlists
    # Could be used to limit graph size
    queries = ['the']
    # Max number we can get from the spotify api per query
    limit = 50
    # The number of times we need to query
    num_queries = max_playlists/limit
    count = 0
    for query in queries:
        which = 0
        results = sp.search(query, limit=limit, type='playlist')
        playlist = results['playlists']
        while playlist and count < num_queries:
            count += 1
            # For each playlist we get
            for item in playlist['items']:
                # Turn it into usable data
                print("Processing playlist: ", which)
                process_playlist(item)
                which += 1
            # If the query returned more, use those
            if playlist['next']:
                try:
                    results = sp.next(playlist)
                    playlist = results['playlists']
                except spotipy.client.SpotifyException:
                    playlist = None
            else:
                playlist = None

# Print all the playlist data
def print_playlists():
    for key in data:
        print("Playlist: ", key, "\t", playlist_names[key])
        for track in data[key]:
            song = data[key][track].title
            artist =  data[key][track].artist
            print("\t Track: ", track, "\t", song, "\t", artist)

# Build an edge list off the stored data
def build_edge_list():
    edges = defaultdict(list)
    count = 1
    # Look at a playlist and add an edge for every track to every other.
    for tracklist in data.values():
        print("Building edges for playlist number: ", count)
        for track in tracklist:
            for other_track in tracklist:
                # No self-loops
                if track != other_track:
                    edges[track].append(other_track)
        count += 1
    return edges

# Turn repeated connections into weights
def combine_edges(edges):
    new_edges = defaultdict(list)
    for edge in edges.keys():
        track_1 = edge
        counts = Counter(edges[edge])
        for next_track in counts.keys():
            info = (next_track, counts[next_track])
            new_edges[track_1].append(info)
    return new_edges

# Create graph given a username with spotify access
def create_graph(username):
    # Set up the global spotipy and data objects
    global sp
    global data
    scope = 'user-library-read'
    token = util.prompt_for_user_token(username, scope)

    # If we can get spotify access
    if token:
        sp = spotipy.Spotify(auth=token)
        # See if we already downloaded the data
        data = load_data()
        if len(data) == 0:
            crawl_playlists()
            save()
        # Format the data to build the graph
        edges = build_edge_list()
        edges = combine_edges(edges)
        # Get all the graph info into the right format
        G = graph_builder.build_graph(edges, track_data)
        save_graph(G)
    else:
        print("Can't get token for", username)
        sys.exit()
    return G

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Need to be given a spotify username
        username = sys.argv[1]
    else:
        print("Usage: %s username" % (sys.argv[0],))
        sys.exit()

    # Create a graph if it doesn't exist
    graph = load_graph()
    if graph is None:
        graph = create_graph(username)

    # Analyze the graph
    graph_analyzer.analyze(graph)
