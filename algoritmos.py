import requests
import random
import pandas as pd
import os
import base64
import networkx as nx

# Variables de autenticación de Spotify
client_id = '82c9ff8e123b4112bbd706a75fac9c3f'
client_secret = '121b746c23184e6b8af94a2ab00e7202'

# Obtener Access Token
def get_spotify_token():
    # Codificar credenciales en Base64
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode()).decode()

    # Configurar la solicitud para obtener el token
    token_url = "https://accounts.spotify.com/api/token"
    token_data = {"grant_type": "client_credentials"}
    token_headers = {
        "Authorization": f"Basic {client_creds_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Solicitar el token de acceso
    response = requests.post(token_url, data=token_data, headers=token_headers)

    # Verificar si la respuesta contiene el token
    if response.status_code == 200:
        token_info = response.json()
        if "access_token" in token_info:
            return token_info["access_token"]
        else:
            print("Error: No se encontró el 'access_token' en la respuesta.")
            print("Respuesta completa:", token_info)
            return None
    else:
        print(f"Error al obtener el token de Spotify: {response.status_code}")
        print("Mensaje de error:", response.text)
        return None

# Obtener imagen del album a partir del spotify_track_id
def get_album_image(track_id, token):
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    track_info = response.json()
    # Obtener la URL de la imagen
    album_image_url = track_info['album']['images'][0]['url']
    return album_image_url

# Seleccionar una cancion aleatoria y obtener su imagen
def get_random_song_and_image():
    # Leer archivo csv
    csv_path = os.path.join('assets', 'data_clean.csv')
    data = pd.read_csv(csv_path)

    # Seleccionar una cancion aleatoria 
    random_song = data.sample(1).iloc[0]
    track_id = random_song['spotify_track_id']
    song_title = random_song['Song']
    performer = random_song['Performer']
    trackurl = random_song['spotify_track_preview_url']
    index1 = random_song['index']

    # Obtener imagen del album
    token = get_spotify_token()
    album_image_url = get_album_image(track_id, token)
    
    return {
        'title': song_title,
        'performer': performer,
        'image_url': album_image_url,
        'track_url': trackurl,
        'index': index1
    }

def CreateSongGrafo(index):
    # Leer el archivo CSV
    csv_path = os.path.join('assets', 'data_clean.csv')
    df = pd.read_csv(csv_path)
    
    # Verificar si el índice existe en el dataset
    if index not in df['index'].values:
        return "Index not found"
    
    # Obtener la cancion base
    song = df[df['index'] == index].iloc[0]
    
    # Crear un grafo vacio
    G = nx.Graph()
    
    # Agregar el nodo base al grafo
    G.add_node(index, **song.to_dict())
    
    # Recorrer todas las canciones del dataset
    for _, row in df.iterrows():
        if row['index'] == index:
            continue
        
        # Inicializar el puntaje
        score = 100
        
        # Comparar spotify_genre
        if song['spotify_genre'] == row['spotify_genre']:
            score -= 5
        
        # Comparar Performer
        if song['Performer'] == row['Performer']:
            score -= 20
        
        # Comparar tempo 
        if abs(song['tempo'] - row['tempo']) < 30:
            score -= 5 + (30 - abs(song['tempo'] - row['tempo']))
        
        # Comparar danceability 
        if abs(song['danceability'] - row['danceability']) < 0.3:
            score -= 5 + (10 - abs(song['danceability'] - row['danceability']) * 10)
        
        # Comparar spotify_track_album
        if song['spotify_track_album'] == row['spotify_track_album']:
            score -= 20
        
        # Si el puntaje es menor a 100, agregar el nodo y la arista al grafo
        if score < 100:
            G.add_node(row['index'], **row.to_dict())
            G.add_edge(index, row['index'], weight=score)
    
    return G

def SongNode(index):
    # Leer el archivo csv
    csv_path = os.path.join('assets', 'data_clean.csv')
    df = pd.read_csv(csv_path)
    
    # Buscar la fila del index
    song_data = df[df['index'] == index]
    
    if song_data.empty:
        return "Error. Index no se encuentra"
    
    # Extraer la información solicitada
    spotify_genre = song_data['spotify_genre'].values[0]
    performer = song_data['Performer'].values[0]
    tempo = song_data['tempo'].values[0]
    danceability = song_data['danceability'].values[0]
    spotify_track_album = song_data['spotify_track_album'].values[0]
    
    # Retornar la informacion como diccionario
    return {
        'spotify_genre': spotify_genre,
        'Performer': performer,
        'Tempo': tempo,
        'Danceability': danceability,
        'spotify_track_album': spotify_track_album
    }