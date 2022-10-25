import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os


BILLBOARD_HOT_100 = "https://www.billboard.com/charts/hot-100/"
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
SPOTIFY_REDIRECT_URI = "http://billboard-to-spotify.com/callback/"
scope = "playlist-modify-private"
MY_SPOTIFY_ID = os.getenv("MY_SPOTIFY_ID")

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=scope,
        cache_path=".cache"
    )
)

input_date = input("Which year do you want to travel to? Type the date in this format. YYYY-MM-DD: ")

response = requests.get(f"{BILLBOARD_HOT_100}{input_date}/").text
soup = BeautifulSoup(response, features="html.parser")

songs = soup.select("li.o-chart-results-list__item #title-of-a-story")
songs_list = [item.string.strip() for item in songs]
artists = soup.select("li.o-chart-results-list__item #title-of-a-story + span.c-label")
list_of_artists = [item.string.strip() for item in artists]

# print(len(songs_list))
# print(len(list_of_artists))
# print(songs_list)
# print(list_of_artists)

songs_for_playlist = []
for i in range(len(songs_list)):
    result = sp.search(q=f"track:{songs_list[i]} artist:{list_of_artists[i]}", type="track")
    try:
        song_uri = result["tracks"]["items"][0]["uri"]
        songs_for_playlist.append(song_uri)
    except IndexError:
        result = sp.search(q=f"track:{songs_list[i]} year:{input_date.split('-')[0]}", type="track")
        try:
            song_uri = result["tracks"]["items"][0]["uri"]
            songs_for_playlist.append(song_uri)
        except IndexError:
            result = sp.search(q=f"track:{songs_list[i]} year:{str(int(input_date.split('-')[0]) + 1)}", type="track")
            try:
                song_uri = result["tracks"]["items"][0]["uri"]
                songs_for_playlist.append(song_uri)
            except IndexError:
                print(f"{songs_list[i]} does not exist in Spotify")

billboard_playlist = sp.user_playlist_create(user=MY_SPOTIFY_ID, name=f"Billboard 100 on {input_date}", public=False, collaborative=False)
playlist_id = billboard_playlist["id"]
sp.playlist_add_items(playlist_id=playlist_id, items=songs_for_playlist)
