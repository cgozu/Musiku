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
#
def bellman_ford(graph, start):
    # Inicializar las distancias y los predecesores
    distances = {node: float('infinity') for node in graph.nodes}
    distances[start] = 0
    predecessors = {node: None for node in graph.nodes}
    
    # Relajar todas las aristas V-1 veces
    for _ in range(len(graph.nodes) - 1):
        for node in graph.nodes:
            for neighbor, attributes in graph[node].items():
                weight = attributes['weight']
                if distances[node] + weight < distances[neighbor]:
                    distances[neighbor] = distances[node] + weight
                    predecessors[neighbor] = node
    
    # Verificar la existencia de ciclos negativos
    for node in graph.nodes:
        for neighbor, attributes in graph[node].items():
            weight = attributes['weight']
            if distances[node] + weight < distances[neighbor]:
                print("El grafo contiene un ciclo negativo (osea hay una similitud muy fuerte)")
                #return None, None Si los queremos
    
    return distances, predecessors

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

def get_top_3_similar_songs(graph, start_index):
    # bellman Ford
    distances, _ = bellman_ford(graph, start_index)

    # ordenar las canciones por distancia
    sorted_distances = sorted(distances.items(), key=lambda x: x[1])
    # obtener indices de las 3 cancion mas cercanas
    top_3_songs_indices = [index for index, _ in sorted_distances[1:4]]
    print("Desde algoritmos:", top_3_songs_indices)
    return top_3_songs_indices

    # dijkstra 
    # distances = dijkstra(graph, start_index)
    # ordenar las canciones por distancia
    # sorted_distances = sorted(distances.items(), key=lambda x: x[1])
    # obtener indices de las 3 cancion mas cercanas
    # top_3_songs_indices = [index for index, _ in sorted_distances[1:4]]
    # print("Desde algoritmos:", top_3_songs_indices)
    # return top_3_songs_indices

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
def get_random_song(graph=None):
    csv_path = os.path.join('assets', 'data_clean.csv')
    data = pd.read_csv(csv_path)

    if graph is None:
        # Seleccionar una canción aleatoria del dataset
        random_song = data.sample(1).iloc[0]
    else:
        # Seleccionar una canción aleatoria del grafo
        random_node = random.choice(list(graph.nodes))
        random_song = data[data['index'] == random_node].iloc[0]

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

def UpdateSongGrafo(previous_index, new_index, graph, min_score):
    # Leer el archivo CSV
    csv_path = os.path.join('assets', 'data_clean.csv')
    df = pd.read_csv(csv_path)
    
    # Verificar si los índices existen en el dataset
    if previous_index not in df['index'].values or new_index not in df['index'].values:
        return "Index not found"
    
    # Obtener la canción base (nuevo nodo)
    new_song = df[df['index'] == new_index].iloc[0]
    
    # Transferir las conexiones del nodo anterior al nuevo nodo
    for neighbor in list(graph.neighbors(previous_index)):
        if neighbor == new_index:
            continue
        weight = graph[previous_index][neighbor]['weight']
        graph.add_edge(new_index, neighbor, weight=weight)
    
    # Eliminar el nodo anterior del grafo
    graph.remove_node(previous_index)
    
    # Recorrer todos los nodos existentes en el grafo para actualizar las conexiones del nuevo nodo
    for node in list(graph.nodes):
        if node == new_index:
            continue
        
        row = df[df['index'] == node].iloc[0]
        
        # Inicializar el puntaje
        score = 100
        
        # Comparar spotify_genre
        new_song_genres = new_song['spotify_genre'].split(',')
        row_genres = row['spotify_genre'].split(',')
        for genre in new_song_genres:
            if genre in row_genres:
                score -= 5
        
        # Comparar Performer
        if row['Performer'] in new_song['Performer'] or new_song['Performer'] in row['Performer']:
            score -= 10
        
        # Comparar tempo (consideramos similar si la diferencia es menor a 30)
        if abs(new_song['tempo'] - row['tempo']) < 30:
            score -= 5 + (30 - abs(new_song['tempo'] - row['tempo']))
        
        # Comparar danceability (consideramos similar si la diferencia es menor a 0.3)
        if abs(new_song['danceability'] - row['danceability']) < 0.3:
            score -= 5 + (10 - abs(new_song['danceability'] - row['danceability']) * 10)
        
        # Comparar spotify_track_album
        if new_song['spotify_track_album'] == row['spotify_track_album']:
            score -= 15
        
        # Si el puntaje es menor a 100, actualizar la arista en el grafo
        if score < min_score:
            graph.add_edge(new_index, node, weight=score)
        else:
            # Eliminar nodos con puntaje de 100
            graph.remove_node(node)
    
    return graph


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
            #print("Si, es igual, mismo performer")
    
        # Comparar spotify_track_album
        if song['spotify_track_album'] == row['spotify_track_album']:
            score -= 15
            #print("Si, es igual, mismo album GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        
        # Si el puntaje es menor a 100, agregar el nodo y la arista al grafo
        if score < 100:
            #print("Generos parecidos: ", generosparecidos)
            G.add_node(row['index'], **row.to_dict())
            G.add_edge(index, row['index'], weight=score)
            #print(f"Canción: {row['Song']} - Valor de la arista: {score}")
    
    return G

import os
import pandas as pd

def SongNode(index):
    # Leer el archivo CSV
    csv_path = os.path.join('assets', 'data_clean.csv')
    df = pd.read_csv(csv_path)
    print("Este es el index:", index)
    # Buscar la fila correspondiente al índice
    song_data = df[df['index'] == index]
    
    if song_data.empty:
        print("VACIOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        return {}
    
    # Extraer la información solicitada
    spotify_genre = song_data['spotify_genre'].values[0]
    performer = song_data['Performer'].values[0]
    tempo = song_data['tempo'].values[0]
    danceability = song_data['danceability'].values[0]
    spotify_track_album = song_data['spotify_track_album'].values[0]
    title = song_data['Song'].values[0]
    track_url = song_data['spotify_track_preview_url'].values[0]
    image_url = get_album_image(song_data['spotify_track_id'].values[0], get_spotify_token())
    
    # Retornar la información en un diccionario
    return {
        'index': index,
        'spotify_genre': spotify_genre,
        'performer': performer,
        'tempo': tempo,
        'danceability': danceability,
        'spotify_track_album': spotify_track_album,
        'title': title,
        'track_url': track_url,
        'image_url': image_url
    }

print(SongNode(1))