import customtkinter as ctk
import config
import math
import sys
import os
import pygame

# Asegurar rutas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.components.breathing_halo import BreathingHalo

class ZenFocusApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Inicializar Pygame Mixer para el audio ---
        pygame.mixer.init()

        # --- Configuración de la Ventana ---
        self.title("ZenFocus")
        self.geometry("450x650")
        self.resizable(False, False)
        self.configure(fg_color=config.COLOR_BACKGROUND)

        # Configuración de la cuadrícula principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        # --- Variables de Estado ---
        self.time_left = config.POMODORO_TIME
        self.total_time = config.POMODORO_TIME 
        self.timer_running = False
        self.timer_id = None
        
        # --- Variables del Menú Lateral ---
        self.menu_abierto = False 
        self.menu_x = 450  # Controla matemáticamente la posición X del menú
        self.sonido_var = ctk.StringVar(value="Sin sonidos") 

        # --- Interfaz ---
        self.crear_widgets()
        self.crear_menu_lateral()
        
        # Inicialización visual
        self.actualizar_reloj()

    def crear_widgets(self):
        # 1. Título
        self.label_titulo = ctk.CTkLabel(
            self, 
            text="ZenFocus", 
            font=("Roboto", 24, "bold"),
            text_color=config.COLOR_PRIMARY
        )
        self.label_titulo.grid(row=0, column=0, pady=(20, 10))

        # Botón para abrir el menú (esquina superior derecha)
        self.btn_abrir_menu = ctk.CTkButton(
            self,
            text="🎵 Sonidos",
            width=90,
            height=30,
            corner_radius=15,
            fg_color="#1e1e1e",
            hover_color="#333333",
            font=("Roboto", 12),
            command=self.toggle_menu
        )
        self.btn_abrir_menu.place(x=340, y=20)

        # 2. Selector de Modo
        self.selector_modo = ctk.CTkSegmentedButton(
            self,
            values=["Enfoque", "Descanso"],
            command=self.cambiar_modo,
            selected_color=config.COLOR_PRIMARY,
            selected_hover_color="#155a8a",
            font=("Roboto", 14)
        )
        self.selector_modo.set("Enfoque")
        self.selector_modo.grid(row=1, column=0, pady=10)

        # 3. COMPONENTE: Breathing Halo
        self.halo = BreathingHalo(self, bg_color=config.COLOR_BACKGROUND)
        self.halo.grid(row=2, column=0, pady=20)

        # 4. Botón Iniciar
        self.boton_start = ctk.CTkButton(
            self,
            text="Iniciar",
            command=self.toggle_timer,
            fg_color=config.COLOR_PRIMARY,
            hover_color="#155a8a",
            width=140,
            height=40,
            corner_radius=20,
            font=("Roboto", 16, "bold")
        )
        self.boton_start.grid(row=3, column=0, pady=10)

        # 5. Botón Reiniciar
        self.boton_reset = ctk.CTkButton(
            self,
            text="Reiniciar",
            command=self.reset_timer,
            fg_color="transparent",
            border_width=2,
            border_color=config.COLOR_ACCENT,
            text_color=config.COLOR_ACCENT,
            hover_color=config.COLOR_BACKGROUND,
            width=140,
            height=40,
            corner_radius=20,
            font=("Roboto", 14)
        )
        self.boton_reset.grid(row=4, column=0, pady=(0, 20))

    def crear_menu_lateral(self):
        # Frame del menú (ancho 220px). Se ubica fuera de la ventana usando self.menu_x
        self.sidebar = ctk.CTkFrame(self, width=220, height=650, corner_radius=0, fg_color="#171717")
        self.sidebar.place(x=self.menu_x, y=0) 

        # Título del menú y botón cerrar
        self.label_sidebar = ctk.CTkLabel(self.sidebar, text="Ambiente", font=("Roboto", 18, "bold"))
        self.label_sidebar.place(x=20, y=20)

        self.btn_cerrar = ctk.CTkButton(
            self.sidebar, text="✖", width=30, height=30, 
            fg_color="transparent", hover_color="#333333", 
            text_color="gray", command=self.toggle_menu
        )
        self.btn_cerrar.place(x=170, y=20)

        # Contenedor scrolleable para los sonidos
        self.scroll_sonidos = ctk.CTkScrollableFrame(self.sidebar, width=180, height=550, fg_color="transparent")
        self.scroll_sonidos.place(x=10, y=70)

        # Opción por defecto: Sin sonido
        rb_ninguno = ctk.CTkRadioButton(
            self.scroll_sonidos, text="Silencio", variable=self.sonido_var, 
            value="Sin sonidos", font=("Roboto", 13),
            command=self.cambiar_sonido_vivo
        )
        rb_ninguno.pack(pady=10, padx=5, anchor="w")

        # Escanear y añadir opciones de audio reales
        try:
            if not os.path.exists(config.SOUNDS_DIR):
                os.makedirs(config.SOUNDS_DIR)
            archivos_audio = [f for f in os.listdir(config.SOUNDS_DIR) if f.endswith(('.mp3', '.wav', '.ogg'))]
            
            for archivo in archivos_audio:
                nombre_limpio = os.path.splitext(archivo)[0].capitalize()
                rb = ctk.CTkRadioButton(
                    self.scroll_sonidos, text=nombre_limpio, variable=self.sonido_var, 
                    value=archivo, font=("Roboto", 13),
                    command=self.cambiar_sonido_vivo
                )
                rb.pack(pady=10, padx=5, anchor="w")
                
        except Exception as e:
            print(f"Error al cargar sonidos: {e}")

    # --- ANIMACIÓN DEL MENÚ LATERAL ---
    def toggle_menu(self):
        # Nos aseguramos de que el menú siempre se dibuje por encima del resto
        self.sidebar.lift()
        
        if self.menu_abierto:
            self.animar_menu(450) # Lo esconde fuera de la ventana
        else:
            self.animar_menu(230) # Lo desliza hacia adentro
        self.menu_abierto = not self.menu_abierto

    def animar_menu(self, target_x):
        step = 15 # Velocidad de animación
        
        if self.menu_x > target_x:
            self.menu_x = max(self.menu_x - step, target_x)
            self.sidebar.place(x=self.menu_x, y=0)
            self.after(10, lambda: self.animar_menu(target_x))
            
        elif self.menu_x < target_x:
            self.menu_x = min(self.menu_x + step, target_x)
            self.sidebar.place(x=self.menu_x, y=0)
            self.after(10, lambda: self.animar_menu(target_x))

    # --- MÉTODOS DE AUDIO ---
    def reproducir_sonido(self):
        sonido_elegido = self.sonido_var.get()
        
        if sonido_elegido != "Sin sonidos":
            archivo_sonido = os.path.join(config.SOUNDS_DIR, sonido_elegido) 
            if os.path.exists(archivo_sonido):
                try:
                    pygame.mixer.music.load(archivo_sonido)
                    pygame.mixer.music.play(-1)
                except Exception as e:
                    print(f"No se pudo reproducir: {e}")

    def detener_sonido(self):
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

    def cambiar_sonido_vivo(self):
        """Permite cambiar el sonido en tiempo real si el temporizador está corriendo"""
        if self.timer_running and self.selector_modo.get() == "Enfoque":
            self.detener_sonido()
            self.reproducir_sonido()

    # --- MÉTODOS DEL TEMPORIZADOR ---
    def cambiar_modo(self, valor):
        self.reset_timer()

    def toggle_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.boton_start.configure(text="Continuar")
            self.halo.stop_breathing()
            self.detener_sonido() 
            if self.timer_id:
                self.after_cancel(self.timer_id)
        else:
            self.timer_running = True
            self.boton_start.configure(text="Pausar")
            self.halo.start_breathing()
            
            if self.selector_modo.get() == "Enfoque":
                self.reproducir_sonido()
                
            self.contar()

    def contar(self):
        if self.time_left > 0 and self.timer_running:
            self.time_left -= 1
            self.actualizar_reloj()
            self.timer_id = self.after(1000, self.contar)
        elif self.time_left == 0:
            self.timer_running = False
            self.boton_start.configure(text="Iniciar")
            self.halo.stop_breathing()
            self.detener_sonido() 
            
            self.time_left = config.POMODORO_TIME if self.selector_modo.get() == "Enfoque" else config.SHORT_BREAK
            self.total_time = self.time_left
            self.actualizar_reloj()

    def reset_timer(self):
        self.timer_running = False
        self.halo.stop_breathing()
        self.detener_sonido() 
        
        if self.timer_id:
            self.after_cancel(self.timer_id)
        
        modo_actual = self.selector_modo.get()
        
        if modo_actual == "Enfoque":
            self.time_left = config.POMODORO_TIME
            nuevo_color = config.COLOR_PRIMARY
            self.boton_start.configure(fg_color=config.COLOR_PRIMARY, hover_color="#155a8a")
            self.selector_modo.configure(selected_color=config.COLOR_PRIMARY, selected_hover_color="#155a8a")
        else:
            self.time_left = config.SHORT_BREAK
            nuevo_color = "#4CAF50"
            self.boton_start.configure(fg_color=nuevo_color, hover_color="#388E3C")
            self.selector_modo.configure(selected_color=nuevo_color, selected_hover_color="#388E3C")
            
        self.total_time = self.time_left
        self.boton_start.configure(text="Iniciar")
        
        self.halo.set_color(nuevo_color)
        self.actualizar_reloj()

    def formato_tiempo(self, segundos):
        m = math.floor(segundos / 60)
        s = segundos % 60
        return f"{m:02d}:{s:02d}"

    def actualizar_reloj(self):
        progreso = self.time_left / self.total_time if self.total_time > 0 else 0
        texto = self.formato_tiempo(self.time_left)
        self.halo.draw(progreso, texto)

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = ZenFocusApp()
    app.mainloop()