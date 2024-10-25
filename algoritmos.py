import requests
import random
import pandas as pd
import os
import base64

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

# Obtener imagen del álbum a partir del spotify_track_id
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

# Seleccionar una canción aleatoria y obtener su imagen
def get_random_song_and_image():
    # Leer archivo CSV
    csv_path = os.path.join('assets', 'data_clean.csv')
    data = pd.read_csv(csv_path)

    # Seleccionar una canción aleatoria
    random_song = data.sample(1).iloc[0]
    track_id = random_song['spotify_track_id']
    song_title = random_song['Song']
    performer = random_song['Performer']

    # Obtener imagen del álbum
    token = get_spotify_token()
    album_image_url = get_album_image(track_id, token)
    
    return {
        'title': song_title,
        'performer': performer,
        'image_url': album_image_url
    }
