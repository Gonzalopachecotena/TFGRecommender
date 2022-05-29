import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import os
import sys
import requests
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from collections import defaultdict
from scipy.spatial.distance import cdist
import difflib

def getAPIrequest(auth_token, url):
	# Función para realizar peticiones GET a la API de Spotify.
    response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
    return response

def postAPIrequest(auth_token, url, data):
	#  Función para realizar peticiones POST a la API de Spotify.
    response = requests.post(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
    )
    return response

def getLastPlayedSongs(numOfTracks):
	# Función para obtener las últimas canciones reproducidas por el usuario.
    url = f"https://api.spotify.com/v1/me/player/recently-played?limit={numOfTracks}"
    response = getAPIrequest(auth_token, url)
    response_json = response.json()
    songs = []
    try:
        for song in response_json["items"]:
            songs.append(song)
    except KeyError:
        print("Tu token de acceso a Spotify ha expirado.")
        print("Por favor, obtenga uno nuevo o pruebe otra vez.")
        sys.exit(1)
    return songs

def get_song_info(song_list):
	#  Función para obtener el nombre y el año de publicación de las pistas de canciones. 
    seeds = []
    for item in range(len(song_list)):
        song = {'name': song_list[item]['track']['name'], 'artists': str([song_list[item]['track']['artists'][0]['name']]) }
        seeds.append(song)
    return seeds

def get_song_data(song, song_data):    
	#  Obtiene los datos de una canción específica. La canción adopta la forma de un diccionario con 
    #  pares clave-valor para el nombre y el año de lanzamiento.
    try:
        song_info = song_data[(song_data['name'] == song['name']) 
                            & (song_data['artists'] == song['artists'])].iloc[0]
        return song_info
    except IndexError:
        return None

def get_mean_vector(song_list, song_data):
    # Obtiene el vector medio de una lista de canciones.
    song_vectors = []
    for song in song_list:
        song_info = get_song_data(song, song_data)
        if song_info is None:
            print('Cuidado: {} no existe en la base de datos'.format(song['name']))
            continue
        song_vector = song_info[number_cols].values
        song_vectors.append(song_vector)  
    song_matrix = np.array(list(song_vectors))
    return np.mean(song_matrix, axis=0)

def flatten_dict_list(dict_list):
    # Función de utilidad para "flatering" una lista de diccionarios.
    flattened_dict = defaultdict()
    for key in dict_list[0].keys():
        flattened_dict[key] = []
    for dictionary in dict_list:
        for key, value in dictionary.items():
            flattened_dict[key].append(value)
    return flattened_dict

def recommend_songs(song_list, song_data, n_songs=12):
	# Recomienda canciones basándose en una lista de canciones anteriores que el usuario ha escuchado.
    metadata_cols = ['name', 'year', 'artists', 'id']

    song_dict = flatten_dict_list(song_list)
    song_center = get_mean_vector(song_list, song_data)
    scaler = song_cluster_pipeline.steps[0][1]
    scaled_data = scaler.transform(song_data[number_cols])
    scaled_song_center = scaler.transform(song_center.reshape(1, -1))
    distances = cdist(scaled_song_center, scaled_data, 'cosine')
    index = list(np.argsort(distances)[:, :n_songs][0])
    
    rec_songs = song_data.iloc[index]
    rec_songs = rec_songs[~rec_songs['name'].isin(song_dict['name'])]
    return rec_songs[metadata_cols].to_dict(orient='records')[1:]

def createPlaylist(name, user_id):
	#  Esta función crea una lista de reproducción para el usuario con el nombre y la descripción dadas.
    data = json.dumps({
            "name": name,
            "description": "Playlist creada con un modelo de recomendaciones!",
            "public": True
        })
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    response = postAPIrequest(auth_token, url, data)
    response_json = response.json()
    playlist_id = response_json["id"]
    return playlist_id


def searchForTrack(track):
    # Esta función hace coincidir el id de una canción con su URI en Spotify.
    # Los URIs son necesarios para añadir canciones a una lista de reproducción.
    url = f"https://api.spotify.com/v1/tracks/{track['id']}"
    response = getAPIrequest(auth_token, url)
    response_json = response.json()
    track_uri = response_json["uri"]
    return track_uri

def addSongsToPlaylist(playlist_id, tracks):
	# Esta función encuentra los URI de todas las canciones recomendadas y las añade a la lista de reproducción. 
    track_uris = [searchForTrack(track) for track in tracks]
    data = json.dumps(track_uris)
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    response = postAPIrequest(auth_token, url, data)
    response_json = response.json()
    return response_json

# Inicializar variables
auth_token = "BQBwtOWwVmqvQm1U31dVuwQj4BtpwD5sDDHMxZxZvGOSct6eADtYLcfno1j12LVDKpxHWmr_ijlTU5-Et-XyPMZFNtlzqip-eqHofTw5MZKgU0Rk2aMIRtMY8md9h0TnOZuSPuw9qBxebBazgUyvQEgCK8mVAElygKuHEZI0KJREUvGZqn-r8qMDT1sPtQ0MdS8Pobo2CTcO_0UeQmrKYtt-Cw"
user_id = "gonzalopacheco38"
if auth_token is None: 
	print("Authorization Token está vacio. Por favor, reinicie la aplicación después de configurar el token.")

# Recuperar las canciones reproducidas recientemente por el usuario
num = int(input("¿Cuántas pistas le gustaría visualizar? "))
lastPlayed = getLastPlayedSongs(num)
print(f"\nEstas son las últimas {num} canciones que has escuchado en Spotify:")
for index, track in enumerate(lastPlayed):
    print(f"\n {index+1}: {track['track']['name']}, {track['track']['artists'][0]['name']} ({track['track']['album']['release_date'][:4]})")
print("\n")

# Permitir al usuario elegir las canciones a partir de las cuales hacer las recomendaciones
ref_tracks = input("\nIntroduzca una lista de hasta 5 pistas separadas por espacios que se utilizarán como pistas iniciales: ") # introduzca los números separados por espacios de la pista") 
ref_tracks = ref_tracks.split()
seed_tracks = [lastPlayed[int(i)-1] for i in ref_tracks]
print("\n")

# Construyendo el cluster de K-Means
song_data = pd.read_csv('./data/data.csv')
song_cluster_pipeline = Pipeline([('scaler', StandardScaler()), 
                                  ('kmeans', KMeans(n_clusters=20, 
                                   verbose=2))],verbose=True)
X = song_data.select_dtypes(np.number)
number_cols = list(X.columns)
song_cluster_pipeline.fit(X)
song_cluster_labels = song_cluster_pipeline.predict(X)
song_data['cluster_label'] = song_cluster_labels
print("\n")
print("\n")

# Realizando recomendaciones
recommended = recommend_songs(get_song_info(seed_tracks), song_data)

# Crear Playlist
playlist_name = input("Introduce el nombre de la playlist: ")
playlist_description = "Playlist creada con un modelo de recomendaciones!"
success = addSongsToPlaylist(createPlaylist(playlist_name, user_id), recommended)
print("\n")
print("\n")
if success: print("Playlist creada correctamente.Por favor, comprueba tu cuenta de Spotify")
print("\n")
print("\n")
