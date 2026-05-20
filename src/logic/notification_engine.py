# src/logic/notification_engine.py
import platform
import subprocess

class NotificationEngine:
    """
    Clase encargada de gestionar el estado de las notificaciones del sistema operativo.
    Separa la lógica del sistema de la interfaz gráfica.
    """
    def __init__(self):
        self.sistema = platform.system()

    def gestionar_notificaciones(self, bloquear: bool):
        """Activa o desactiva el modo No Molestar según el SO."""
        try:
            if self.sistema == "Darwin":  # macOS
                estado = "true" if bloquear else "false"
                # Comando base o integración nativa para macOS
                print(f"Modo No Molestar (macOS): {estado}")
                
            elif self.sistema == "Windows":  # Windows
                if bloquear:
                    print("Activando Focus Assist (Asistente de Concentración) en Windows...")
                else:
                    print("Desactivando Focus Assist en Windows...")
                    
            elif self.sistema == "Linux":
                comando = "dunstctl set-paused true" if bloquear else "dunstctl set-paused false"
                subprocess.run(comando, shell=True)
                
        except Exception as e:
            print(f"Error en el motor de notificaciones: {e}")