import json
import requests
import inflect
from pytube import YouTube
from dotenv.main import load_dotenv
import os
from flask import redirect, session
from functools import wraps


def main():
    query, N = get_query()
    tracks = get_tracks(query=query, N=N)
    print_results(tracks=tracks)


load_dotenv()
p = inflect.engine()
api_key = json.loads(os.environ["API_KEY"])
client_id = os.environ["CLIENT_ID"]
client_secret = os.environ["CLIENT_SECRET"]
i = 0


def get_url(query):
    query = query.replace(" ", "%20")
    if "/" in query:
        query = query.replace("/", "%20")
    global i
    for _ in range(2):
        while i < len(api_key):
            try:
                response = requests.get(
                    f"https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={query}&key={api_key[i]}"
                ).json()
                url = make_url(code=response["items"][0]["id"]["videoId"])
                return url
            except KeyError:
                i += 1
                continue
        if i > (len(api_key) - 1):
            i = 0
    return None


def make_url(code):
    return f"https://youtu.be/{code}"


def download_audio(url, title, path):
    yt = YouTube(url)
    stream = yt.streams.get_by_itag(140)
    stream.download(
        output_path=path,
        filename=f"{title}.mp4",
    )


def get_query():
    query = input("Enter search query: ")
    query = query.replace(" ", "-")
    N = input("Enter the number of results to show: ")
    print()
    return query, N


def get_headers():
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}"
    token = requests.post(url, headers=headers, data=data).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers


def get_top():
    headers = get_headers()
    response = requests.get(
        f"https://api.spotify.com/v1/playlists/37i9dQZEVXbMDoHDwVN2tF?market=IN&fields=tracks.items(track(name,artists(name),album(name,images)))&additional_types=track",
        headers=headers,
    ).json()
    top = []
    for track in response["tracks"]["items"]:
        song = {
            "track": track["track"]["name"],
            "artists": list_artists(track["track"]["artists"]),
            "album": track["track"]["album"]["name"],
            "image": track["track"]["album"]["images"][0]["url"],
        }
        top.append(song)
    return top


def get_tracks(query, N):
    headers = get_headers()
    response = requests.get(
        f"https://api.spotify.com/v1/search?q={query}&type=track&market=IN&limit={N}",
        headers=headers,
    ).json()
    songs = response["tracks"]["items"]
    tracks = []
    for song in range(int(N)):
        name = songs[song]["name"]
        artists = list_artists(songs[song]["artists"])
        track = {
            "track": f"{name}",
            "artists": f"{artists}",
            "album": f'{songs[song]["album"]["name"]}',
            "image": f'{songs[song]["album"]["images"][0]["url"]}',
        }
        tracks.append(track)
    return tracks


def print_results(tracks):
    for i, song in enumerate(tracks):
        print(f'{i + 1}.\tsong:\t{song["track"]}')
        print(f'\tby:\t{song["artists"]}')
        print(f'\tfrom:\t{song["album"]}')
        print()
    n = int(input("Which song would you like to download? Enter 0 to exit! "))
    if n == 0:
        return
    name = tracks[n - 1]["track"]
    artists = tracks[n - 1]["artists"]
    url = get_url(f"{name} {artists} Lyrics")
    download_audio(url=url, title=f"{name} - {artists}", path="downloads")


def list_artists(artists):
    li = []
    for artist in artists:
        li.append(artist["name"])
    return p.join(li, final_sep="")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


if __name__ == "__main__":
    main()
