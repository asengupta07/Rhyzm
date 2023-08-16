import json
import requests
import inflect
from pytube import YouTube
from dotenv.main import load_dotenv
import os
from flask import redirect, session
from functools import wraps


p = inflect.engine()
i = 0

# Load environment variables from dotenv
load_dotenv()
api_key = json.loads(os.environ["API_KEY"])
client_id = os.environ["CLIENT_ID"]
client_secret = os.environ["CLIENT_SECRET"]


def main():
    # Get input from user
    query, N = get_query()
    # Get tracks
    tracks = get_tracks(query=query, N=N)
    # Print results
    print_results(tracks=tracks)


def get_url(query):
    # Format query to prepare url
    query = query.replace(" ", "%20")
    if "/" in query:
        query = query.replace("/", "%20")

    # Get url from youtube
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
    # Make youtu.be url with video id
    return f"https://youtu.be/{code}"


def download_audio(url, title, path):
    # Use pytube library to download the video with a predetermined stream itag
    yt = YouTube(url)
    stream = yt.streams.get_by_itag(140)
    stream.download(
        output_path=path,
        filename=f"{title}.mp4",
    )


def get_query():
    # Accepting user input
    query = input("Enter search query: ")
    query = query.replace(" ", "-")
    N = input("Enter the number of results to show: ")
    print()
    return query, N


def get_headers():
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}"

    # Getting Bearer token from spotify API
    token = requests.post(url, headers=headers, data=data).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Returning Bearer token as formatted header
    return headers


def get_top():
    # Get headers
    headers = get_headers()

    # Get list of top tracks as response and convert it into json
    response = requests.get(
        f"https://api.spotify.com/v1/playlists/37i9dQZEVXbMDoHDwVN2tF?market=IN&fields=tracks.items(track(name,artists(name),album(name,images)))&additional_types=track",
        headers=headers,
    ).json()

    top = []

    # Store required parts of the response in a list of dicts
    for track in response["tracks"]["items"]:
        song = {
            "track": track["track"]["name"],
            "artists": list_artists(track["track"]["artists"]),
            "album": track["track"]["album"]["name"],
            "image": track["track"]["album"]["images"][0]["url"],
        }
        top.append(song)

    # Return the list of dicts
    return top


def get_tracks(query, N):
    # Get headers
    headers = get_headers()

    # Get search results as response and store it as json
    response = requests.get(
        f"https://api.spotify.com/v1/search?q={query}&type=track&market=IN&limit={N}",
        headers=headers,
    ).json()

    songs = response["tracks"]["items"]
    tracks = []

    # Store required parts of the response in a list of dicts
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

    # Return the list of dicts
    return tracks


def print_results(tracks):
    # Print search results
    for i, song in enumerate(tracks):
        print(f'{i + 1}.\tsong:\t{song["track"]}')
        print(f'\tby:\t{song["artists"]}')
        print(f'\tfrom:\t{song["album"]}')
        print()

    # Ask for download
    n = int(input("Which song would you like to download? Enter 0 to exit! "))
    if n == 0:
        return
    # Download the song requested by user
    name = tracks[n - 1]["track"]
    artists = tracks[n - 1]["artists"]
    url = get_url(f"{name} {artists} Lyrics")
    download_audio(url=url, title=f"{name} - {artists}", path="downloads")


def list_artists(artists):
    li = []
    # Create a list of artists
    for artist in artists:
        li.append(artist["name"])
    # Join the list of artists
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
