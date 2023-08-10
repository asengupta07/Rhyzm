import json
import requests
import inflect
from pytube import YouTube
from dotenv.main import load_dotenv
import os

load_dotenv()
p = inflect.engine()
api_key = os.environ['API_KEY']
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']


def get_url(query):
    query = query.replace(" ", "%20")
    response = requests.get(
        f"https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={query}&key={api_key}"
    ).json()
    url = f'https://youtu.be/{response["items"][0]["id"]["videoId"]}'
    yt = YouTube(url)
    stream = yt.streams.get_by_itag(140)
    stream.download(
        output_path="songs/",
        filename=f'{query.replace("%20"," ").replace(" Lyrics","")}.mp4',
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


def get_response(query, N, headers):
    response = requests.get(
        f"https://api.spotify.com/v1/search?q={query}&type=track&market=IN&limit={N}",
        headers=headers,
    ).json()
    return response


# def show_json(response):
#     print(json.dumps(response, indent=4))


def print_results(response, N):
    songs = response["tracks"]["items"]
    for song in range(int(N)):
        print(f'{song + 1}.\tsong:\t{songs[song]["name"]}')
        print("\tby:\t", end="")
        li = []
        for artist in songs[song]["artists"]:
            li.append(artist["name"])
        print(p.join(li, final_sep=""))
        print(f'\tfrom:\t{songs[song]["album"]["name"]}')
        print()
    n = int(input("Which song would you like to download? "))
    name = songs[n - 1]["name"]
    li = []
    for artist in songs[n - 1]["artists"]:
        li.append(artist["name"])
    artists = p.join(li, final_sep="")
    get_url(f"{name} {artists} Lyrics")


def main():
    query, N = get_query()
    headers = get_headers()
    response = get_response(query=query, N=N, headers=headers)
    # show_json(response=response)
    print_results(response=response, N=N)


if __name__ == "__main__":
    main()
