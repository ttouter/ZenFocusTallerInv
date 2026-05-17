import os

# Rutas absolutas para evitar errores al compilar
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

# Colores del Tema
COLOR_PRIMARY = "#1f6aa5"
COLOR_ACCENT = "#D32F2F"
COLOR_BACKGROUND = "#242424"

# Configuración de Tiempos (en segundos)
POMODORO_TIME = 25 * 60
SHORT_BREAK = 5 * 60