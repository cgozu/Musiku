import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QStackedWidget
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import requests
from algoritmos import get_random_song_and_image

# Pantalla de inicio
class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Título "TUNE MATCH" centrado
        self.title_label = QLabel("MUSIKU", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 24, QFont.Bold))

        # Botón "Ingresar"
        self.enter_button = QPushButton("Ingresar", self)
        self.enter_button.setFont(QFont("Arial", 14))
        self.enter_button.clicked.connect(self.on_enter_clicked)

        # Layout de la pantalla de inicio
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.enter_button)
        self.setLayout(layout)

    def on_enter_clicked(self):
        # Cambiar a la pantalla de la canción aleatoria
        self.parentWidget().setCurrentIndex(1)

# Pantalla de información de la canción
class SongPage(QWidget):
    def __init__(self, player, parent=None):
        super().__init__(parent)

        # Almacenar el reproductor multimedia
        self.player = player

        # Etiqueta de título
        self.song_title = QLabel("Canción aleatoria", self)
        self.song_title.setAlignment(Qt.AlignCenter)
        self.song_title.setFont(QFont("Arial", 20, QFont.Bold))

        # Etiquetas para mostrar canción, artista y álbum
        self.song_label = QLabel("", self)
        self.song_label.setAlignment(Qt.AlignCenter)
        self.artist_label = QLabel("", self)
        self.artist_label.setAlignment(Qt.AlignCenter)
        self.album_image_label = QLabel(self)
        self.album_image_label.setAlignment(Qt.AlignCenter)

        # Botón "Volver"
        self.back_button = QPushButton("Volver", self)
        self.back_button.setFont(QFont("Arial", 12))
        self.back_button.clicked.connect(self.on_back_clicked)

        # Botón de reproducción/pausa
        self.play_pause_button = QPushButton("▶", self)
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.is_playing = False  # Para llevar el estado de reproducción

        # Layout de la pantalla de canción
        layout = QVBoxLayout()
        layout.addWidget(self.song_title)
        layout.addWidget(self.song_label)
        layout.addWidget(self.artist_label)
        layout.addWidget(self.album_image_label)
        layout.addWidget(self.play_pause_button)
        layout.addWidget(self.back_button)
        self.setLayout(layout)

    def display_random_song(self):
        # Obtener canción aleatoria e información del álbum
        song_info = get_random_song_and_image()

        # Mostrar título y artista
        self.song_label.setText(f"Canción: {song_info['title']}")
        self.artist_label.setText(f"Artista: {song_info['performer']}")

        # Descargar y mostrar la imagen del álbum
        image_data = requests.get(song_info['image_url']).content
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        self.album_image_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio))

        # Configurar URL de vista previa en el reproductor
        self.player.setMedia(QMediaContent(QUrl(song_info['track_url'])))

        # Reproducir la canción automáticamente al cargar una nueva
        self.player.play()
        self.play_pause_button.setText("⏸")  # Cambiar el botón a pausa
        self.is_playing = True

    def toggle_play_pause(self):
        # Alternar entre reproducir y pausar
        if self.is_playing:
            self.player.pause()
            self.play_pause_button.setText("▶")
        else:
            self.player.play()
            self.play_pause_button.setText("⏸")
        self.is_playing = not self.is_playing

    def on_back_clicked(self):
        # Detener la reproducción cuando regresa a la pantalla principal
        self.player.stop()
        self.is_playing = False
        self.play_pause_button.setText("▶")
        # Volver a la pantalla de inicio
        self.parentWidget().setCurrentIndex(0)

# Clase principal para la aplicación
class TuneMatchApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TuneMatch")
        self.setGeometry(100, 100, 300, 500)  # Medidas para simular una interfaz móvil

        # Crear el reproductor multimedia
        self.player = QMediaPlayer()

        # Crear las pantallas y añadirlas al QStackedWidget
        self.home_page = HomePage(self)
        self.song_page = SongPage(self.player, self)

        self.addWidget(self.home_page)
        self.addWidget(self.song_page)

        # Configurar el botón de "Ingresar" para mostrar la pantalla de la canción aleatoria
        self.home_page.enter_button.clicked.connect(self.song_page.display_random_song)

# Inicializar la aplicación
app = QApplication(sys.argv)
window = TuneMatchApp()
window.show()
sys.exit(app.exec_())
