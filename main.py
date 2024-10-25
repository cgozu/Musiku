from PyQt5.QtWidgets import QApplication
import sys
from gui import TuneMatchApp
import algoritmos  # Importar los algoritmos

def run_app():
    app = QApplication(sys.argv)
    window = TuneMatchApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_app()
