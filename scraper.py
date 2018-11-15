import sys
import spotipy
import spotipy.util as util
import _pickle as pickle
import os
from collections import defaultdict
from collections import Counter
import graph_builder
from track import Track

max_playlists = 10000
scope = 'user-library-read'
data = {}
playlist_names = {}
#Link a track ID to a track object
track_data = {}

def is_good_playlist(items):
    artists = set()
    albums = set()
    for item in items:
        track = item['track']
        if track:
            artists.add(track['artists'][0]['id'])
            albums.add(track['album']['id'])
    return len(artists) > 1 and len(albums) > 1


def process_playlist(playlist):
    global data
    global track_data
    global playlist_names

    pid = playlist['id']
    name = playlist['name']
    playlist_names[pid] = name
    uid = playlist['owner']['id']

    try:
        results = sp.user_playlist_tracks(uid, playlist['id'])
        # fields="items.track(!album)")

        if results and 'items' in results and is_good_playlist(results['items']):

            data[pid] = {}
            for item in results['items']:
                track = item['track']
                if track and track['name'] and track['artists']:
                    tid = track['id']
                    title = track['name']
                    artist = track['artists'][0]['name']
                    track_data[tid] = Track(title, artist)
                    data[pid][tid] = Track(title, artist)
        else:
            print('mono playlist skipped')
    except spotipy.SpotifyException:
        print('trouble, skipping')


def save():
    out = open('tracks.pkl', 'wb')
    pickle.dump(data, out, -1)
    out.close()


def load():
    global data
    global playlist_names
    if os.path.exists('tracks.pkl'):
        infile = open('tracks.pkl', 'rb')
        data = pickle.load(infile)
    else:
        data = {}
        playlist_names = {}
    return data


def crawl_playlists():
    queries = ['the']
    limit = 50
    max = 2
    count = 0
    for query in queries:
        which = 0
        results = sp.search(query, limit=limit, type='playlist')
        playlist = results['playlists']
        while playlist and count < max:
            count += 1
            for item in playlist['items']:
                print("Processing playlist: ", which)
                process_playlist(item)
                which += 1
            if playlist['next']:
                try:
                    results = sp.next(playlist)
                    playlist = results['playlists']
                except spotipy.client.SpotifyException:
                    playlist = None
            else:
                playlist = None

def print_playlists():
    for key in data:
        print("Playlist: ", key, "\t", playlist_names[key])
        for track in data[key]:
            song = data[key][track].title
            artist =  data[key][track].artist
            print("\t Track: ", track, "\t", song, "\t", artist)

def build_edge_list():
    edges = defaultdict(list)
    # Look at a playlist and add an edge for every track to every other.
    for tracklist in data.values():
        for track in tracklist:
            for other_track in tracklist:
                if track != other_track:
                    edges[track].append(other_track)
    return edges

def combine_edges(edges):
    new_edges = defaultdict(list)
    for edge in edges.keys():
        track_1 = edge
        counts = Counter(edges[edge])
        for next_track in counts.keys():
            info = (next_track, counts[next_track])
            new_edges[track_1].append(info)
    return new_edges

if __name__ == '__main__':
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print("Usage: %s username" % (sys.argv[0],))
        sys.exit()

    token = util.prompt_for_user_token(username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        # data = load()
        crawl_playlists()
        edges = build_edge_list()
        edges = combine_edges(edges)
        graph_builder.build_graph(edges, track_data)
    else:
        print("Can't get token for", username)
