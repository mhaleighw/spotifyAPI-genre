from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    
    headers = {
        "Authorization" : "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization" : "Bearer " + token}

def get_available_genres(token):
    url = "https://api.spotify.com/v1/recommendations/available-genre-seeds"
    headers = get_auth_header(token)
    
    result = get(url, headers=headers)
    available_genres = json.loads(result.content)["genres"]
    
    return available_genres

def search_genre(token, genre_name):
    url = "https://api.spotify.com/v1/browse/categories"
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    categories = json.loads(result.content)["categories"]["items"]

    genre_id = None

    for category in categories:
        if genre_name.lower() == category["name"].lower():
            genre_id = category["id"]
            break

    if not genre_id:
        print("No genre with this name exists.")
        return None

    return genre_id

def get_top_artists_by_genre(token, genre_id):
    url = f"https://api.spotify.com/v1/browse/categories/{genre_id}/playlists"
    headers = get_auth_header(token)
    
    result = get(url, headers=headers)
    playlists = json.loads(result.content)["playlists"]["items"]
    
    if not playlists:
        print("No playlists found for this genre.")
        return None
    
    playlist_id = playlists[0]["id"]
    
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    result = get(url, headers=headers)
    tracks = json.loads(result.content)["items"]
    
    if not tracks:
        print("No tracks found for this genre.")
        return None
    
    unique_artists = set()
    for track in tracks:
        artist_id = track["track"]["artists"][0]["id"]
        unique_artists.add(artist_id)
    
    return list(unique_artists)

def get_top_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = get_auth_header(token)
    
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    
    artist_name = json_result.get("name", "Unknown Artist")
    
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    result = get(url, headers=headers)
    top_tracks = json.loads(result.content)["tracks"]
    
    return artist_name, top_tracks

token = get_token()
available_genres = get_available_genres(token)

genre_name_input = input("Enter the name of the genre: ")

token = get_token()
genre_id = search_genre(token, genre_name_input)

if genre_id:
    unique_artists = get_top_artists_by_genre(token, genre_id)

    if unique_artists:
        for artist_id in list(unique_artists)[:15]:
            artist_name, songs = get_top_songs_by_artist(token, artist_id)

            if songs:
                print(f"\nTop songs for artist {artist_name}:")
                for idx, song in enumerate(songs[:3]):  
                    print(f"{idx + 1}. {song['name']}")
