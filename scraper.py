import sys
import spotipy
import spotipy.util as util
import pprint as pp
import _pickle as pickle
import atexit
import os

max_playlists = 10000
scope = 'user-library-read'
data = {}
playlist_names = {}

def is_good_playlist(items):
    artists = set()
    albums = set()
    for item in items:
        track = item['track']
        if track:
            artists.add(track['artists'][0]['id'])
            albums.add(track['album']['id'])
    return len(artists) > 1 and len(albums) > 1


def process_playlist(which, total, playlist):
    global data
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
                if track:
                    tid = track['id']
                    title = track['name']
                    artist = track['artists'][0]['name']
                    data[pid][tid] = tuple((title, artist))
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
        total = playlist['total']
        while playlist and count < max:
            count += 1
            for item in playlist['items']:
                process_playlist(which, total, item)
                which += 1
            if playlist['next']:
                results = sp.next(playlist)
                playlist = results['playlists']
            else:
                playlist = None

def print_playlists():
    for key in data:
        print("Playlist: ", key, "\t", playlist_names[key])
        for track in data[key]:
            song = data[key][track][0]
            artist =  data[key][track][1]
            print("\t Track: ", track, "\t", song, "\t", artist)

def build_edge_list():
    # Look at a playlist and add an edge for every track to every other.
    for key in data:
        print("Playlist: ", key, "\t", playlist_names[key])
        for track in data[key]:
            song = data[key][track][0]
            artist =  data[key][track][1]
            print("\t Track: ", track, "\t", song, "\t", artist)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print("Usage: %s username" % (sys.argv[0],))
        sys.exit()

    token = util.prompt_for_user_token(username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        data = load()
        crawl_playlists()
        print_playlists()
        build_edge_list()
    else:
        print("Can't get token for", username)