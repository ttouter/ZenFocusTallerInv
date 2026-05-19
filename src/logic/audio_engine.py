import os
import pygame
import config

class AudioEngine:
    """
    Clase encargada de gestionar la reproducción de sonidos ambientales.
    Separa la lógica de audio de la interfaz gráfica.
    """
    def __init__(self):
        # Inicializa Pygame Mixer de forma segura
        if not pygame.mixer.get_init():
            pygame.mixer.init()

    def obtener_sonidos_disponibles(self):
        """
        Escanea el directorio de sonidos y devuelve una lista de diccionarios
        con el nombre del archivo y un nombre formateado para la interfaz de usuario.
        """
        sonidos = []
        
        # Crear el directorio si no existe, previniendo errores
        if not os.path.exists(config.SOUNDS_DIR):
            try:
                os.makedirs(config.SOUNDS_DIR)
            except Exception as e:
                print(f"Error al crear el directorio de sonidos: {e}")
                return sonidos

        # Buscar archivos con extensiones de audio compatibles
        try:
            archivos_audio = [f for f in os.listdir(config.SOUNDS_DIR) if f.endswith(('.mp3', '.wav', '.ogg'))]
            
            for archivo in archivos_audio:
                # Generar un nombre limpio: quitar guiones y capitalizar
                nombre_limpio = os.path.splitext(archivo)[0].replace("-", " ").capitalize()
                sonidos.append({
                    "archivo": archivo,
                    "nombre_mostrar": nombre_limpio
                })
        except Exception as e:
            print(f"Error al leer los archivos de sonido: {e}")
            
        return sonidos

    def reproducir(self, nombre_archivo):
        """
        Reproduce un archivo de sonido en bucle infinito.
        """
        if nombre_archivo == "Sin sonidos" or not nombre_archivo:
            self.detener()
            return

        ruta_completa = os.path.join(config.SOUNDS_DIR, nombre_archivo)
        
        if os.path.exists(ruta_completa):
            try:
                pygame.mixer.music.load(ruta_completa)
                pygame.mixer.music.play(-1)  # -1 indica reproducción en bucle infinito
            except Exception as e:
                print(f"Error en el motor de audio al reproducir '{nombre_archivo}': {e}")
        else:
            print(f"No se encontró el archivo de sonido: {ruta_completa}")

    def detener(self):
        """
        Detiene la música si hay algo reproduciéndose actualmente.
        """
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

    def ajustar_volumen(self, volumen):
        """
        (Funcionalidad extra) Permite ajustar el volumen.
        :param volumen: Flotante entre 0.0 y 1.0
        """
        if pygame.mixer.get_init():
            # Asegura que el valor esté entre 0.0 y 1.0 para evitar errores en Pygame
            volumen_seguro = max(0.0, min(1.0, float(volumen)))
            pygame.mixer.music.set_volume(volumen_seguro)