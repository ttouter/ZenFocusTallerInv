import os

# Rutas absolutas para evitar errores al compilar
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

# --- Paleta de Colores Formal (Estilo Académico / Universitario) ---
# Tonos sobrios que reducen la fatiga visual y transmiten seriedad
COLOR_BACKGROUND = "#1E262C"    # Fondo principal (Azul grisáceo muy oscuro)
COLOR_FRAME = "#2A3439"         # Fondo para menús y paneles (Azul grisáceo oscuro)

COLOR_PRIMARY = "#3949AB"       # Índigo formal (Modo Enfoque)
COLOR_PRIMARY_HOVER = "#283593" # Índigo oscuro para interacción

COLOR_ACCENT = "#00897B"        # Verde azulado mate / Teal (Modo Descanso)
COLOR_ACCENT_HOVER = "#00695C"  # Verde azulado oscuro para interacción

COLOR_TEXT_MAIN = "#F5F5F5"     # Blanco ahumado para alta legibilidad
COLOR_TEXT_MUTED = "#B0BEC5"    # Gris azulado para textos secundarios e información
COLOR_TRACK = "#2A3439"         # Color del riel inactivo del temporizador

# Configuración de Tiempos (en segundos)
POMODORO_TIME = 25 * 60
SHORT_BREAK = 5 * 60
LONG_BREAK = 15 * 60