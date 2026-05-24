import customtkinter as ctk
import config
from datetime import date, timedelta

class StreakWindow(ctk.CTkToplevel):
    def __init__(self, master, gamification_engine):
        super().__init__(master)
        self.gamification = gamification_engine
        
        # --- Configuración de la Ventana Secundaria ---
        self.title("Tu Racha")
        self.geometry("380x400")
        self.resizable(False, False)
        self.configure(fg_color=config.COLOR_BACKGROUND)
        
        # Esto hace que la ventana se comporte como un "diálogo" sobre la principal
        self.transient(master)
        self.grab_set()

        self.construir_interfaz()

    def construir_interfaz(self):
        # Obtener los datos del motor de gamificación
        stats = self.gamification.get_stats()
        racha_actual = stats.get("streak_count", 0)
        
        # --- Título ---
        ctk.CTkLabel(
            self, text="Racha de Concentración", 
            font=("Segoe UI Variable", 20, "bold"), text_color=config.COLOR_TEXT_MAIN
        ).pack(pady=(30, 10))
        
        # --- Contador de fuego ---
        frame_contador = ctk.CTkFrame(self, fg_color="transparent")
        frame_contador.pack(pady=10)
        
        ctk.CTkLabel(frame_contador, text="🔥", font=("Segoe UI", 55)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(frame_contador, text=str(racha_actual), font=("Segoe UI", 65, "bold"), text_color=config.COLOR_PRIMARY).pack(side="left")
        ctk.CTkLabel(frame_contador, text=" días", font=("Segoe UI", 20), text_color=config.COLOR_TEXT_MUTED).pack(side="left", align="bottom", pady=(35, 0))
        
        # --- Separador ---
        ctk.CTkFrame(self, height=2, fg_color=config.COLOR_FRAME).pack(fill="x", padx=40, pady=25)
        
        # --- Calendario Semanal ---
        ctk.CTkLabel(
            self, text="Tu actividad de los últimos 7 días:", 
            font=("Segoe UI", 14), text_color=config.COLOR_TEXT_MAIN
        ).pack(pady=(0, 15))
        
        frame_semana = ctk.CTkFrame(self, fg_color="transparent")
        frame_semana.pack(pady=5)
        
        today = date.today()
        active_days = stats.get("active_days", [])
        dias_semana = ["L", "M", "X", "J", "V", "S", "D"]
        
        # Dibujar los 7 círculos (de izquierda a derecha)
        for i in range(6, -1, -1):
            dia_fecha = today - timedelta(days=i)
            dia_str = dia_fecha.isoformat()
            dia_nombre = dias_semana[dia_fecha.weekday()]
            
            # Verificar si este día hubo actividad
            dia_activo = dia_str in active_days
            color_fondo = config.COLOR_PRIMARY if dia_activo else config.COLOR_TRACK
            color_texto = config.COLOR_BACKGROUND if dia_activo else config.COLOR_TEXT_MUTED
            
            # Crear un círculo simulado con un Frame
            frame_dia = ctk.CTkFrame(frame_semana, width=38, height=38, corner_radius=19, fg_color=color_fondo)
            frame_dia.pack(side="left", padx=4)
            frame_dia.pack_propagate(False) 
            
            lbl_dia = ctk.CTkLabel(frame_dia, text=dia_nombre, font=("Segoe UI", 14, "bold"), text_color=color_texto)
            lbl_dia.place(relx=0.5, rely=0.5, anchor="center")

        # --- Botón de cerrar ---
        ctk.CTkButton(
            self, text="¡A seguir así!", command=self.destroy,
            fg_color=config.COLOR_PRIMARY, hover_color=config.COLOR_PRIMARY_HOVER, 
            text_color=config.COLOR_BACKGROUND, font=("Segoe UI", 14, "bold")
        ).pack(side="bottom", pady=30)