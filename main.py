from PyQt5.QtWidgets import QApplication
import sys
from gui import TuneMatchApp
import algoritmos  # Importar los algoritmos

# Inicializar la aplicación
app = QApplication(sys.argv)
app.setStyleSheet("""
    QLabel, QPushButton, QLineEdit {
        color: #FFFFFF;
    }
""")
window = TuneMatchApp()
window.show()
sys.exit(app.exec_())