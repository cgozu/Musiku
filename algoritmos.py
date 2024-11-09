import requests
import random
import pandas as pd
import os
import base64
import networkx as nx
import heapq

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

def dijkstra(graph, start):
    # Inicializar las distancias y el heap
    distances = {node: float('infinity') for node in graph.nodes}
    distances[start] = 0
    priority_queue = [(0, start)]
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        if current_distance > distances[current_node]:
            continue
        
        for neighbor, attributes in graph[current_node].items():
            distance = current_distance + attributes['weight']
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))
    
    return distances

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
def get_random_song(graph=None, start_index=None):
    csv_path = os.path.join('assets', 'data_clean.csv')
    data = pd.read_csv(csv_path)

    if graph is None:
        # Seleccionar una canción aleatoria del dataset
        random_song = data.sample(1).iloc[0]
    else:
        # Encontrar la canción con la distancia más corta desde start_index usando Dijkstra
        shortest_paths = dijkstra(graph, start_index)
        # Excluir el nodo de inicio y ordenar por distancia
        sorted_paths = sorted(shortest_paths.items(), key=lambda x: x[1])
        # Seleccionar la canción con la distancia más corta
        closest_song_index = sorted_paths[1][0]  # El primer elemento es el nodo de inicio, así que tomamos el segundo
        random_song = data[data['index'] == closest_song_index].iloc[0]

    track_id = random_song['spotify_track_id']
    song_title = random_song['Song']
    performer = random_song['Performer']
    track_url = random_song['spotify_track_preview_url']
    index1 = random_song['index']

    # Obtener imagen del álbum
    token = get_spotify_token()
    album_image_url = get_album_image(track_id, token)

    return {
        'index': index1,
        'title': song_title,
        'performer': performer,
        'track_url': track_url,
        'image_url': album_image_url
    }

def CreateSongGrafo(index):
    # Leer el archivo CSV
    csv_path = os.path.join('assets', 'data_clean.csv')
    df = pd.read_csv(csv_path)
    
    # Verificar si el índice existe en el dataset
    if index not in df['index'].values:
        return "Index not found"
    
    # Obtener la canción base
    song = df[df['index'] == index].iloc[0]
    print("ESTA ES LA CANCION XDXDXDXd:" ,song)
    # Crear un grafo vacío
    G = nx.Graph()
    
    
    # Agregar el nodo base al grafo
    G.add_node(index, **song.to_dict())
    
    # Recorrer todas las canciones del dataset
    for _, row in df.iterrows():
        generosparecidos = 0
        if row['index'] == index:
            continue
        
        # Inicializar el puntaje
        score = 100
        
        song_genres = song['spotify_genre'].split(',')
        row_genres = row['spotify_genre'].split(',')
        for genre in song_genres:
            if genre in row_genres:
                score -= 5
                generosparecidos += 1

        # Comparar Performer
        if row['Performer'] in song['Performer'] or song['Performer'] in row['Performer']:
            score -= 10
            print("Si, es igual, mismo performer")
    
        # Comparar spotify_track_album
        if song['spotify_track_album'] == row['spotify_track_album']:
            score -= 15
            print("Si, es igual, mismo album GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        
        # Si el puntaje es menor a 100, agregar el nodo y la arista al grafo
        if score <= 95:
            print("Generos parecidos: ", generosparecidos)
            G.add_node(row['index'], **row.to_dict())
            G.add_edge(index, row['index'], weight=score)
            print(f"Canción: {row['Song']} - Valor de la arista: {score}")
    
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