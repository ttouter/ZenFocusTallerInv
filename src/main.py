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
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

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
            text_color=config.COLOR_TEXT_MAIN
        )
        self.label_titulo.grid(row=0, column=0, pady=(20, 0))

        # Botón para abrir el menú (esquina superior derecha)
        self.btn_abrir_menu = ctk.CTkButton(
            self,
            text="⚙️ Ajustes",
            width=90,
            height=30,
            corner_radius=15,
            fg_color=config.COLOR_FRAME,
            hover_color=config.COLOR_PRIMARY_HOVER,
            text_color=config.COLOR_TEXT_MAIN,
            font=("Roboto", 12),
            command=self.toggle_menu
        )
        self.btn_abrir_menu.place(x=340, y=20)

        # Etiqueta de Modo Actual
        self.label_tipo_reloj = ctk.CTkLabel(
            self,
            text="Modo: Tradicional",
            font=("Roboto", 12),
            text_color=config.COLOR_TEXT_MUTED
        )
        self.label_tipo_reloj.grid(row=1, column=0, pady=(0, 10))

        # 2. Selector de Modo
        self.selector_modo = ctk.CTkSegmentedButton(
            self,
            values=["Enfoque", "Descanso"],
            command=self.cambiar_modo,
            selected_color=config.COLOR_PRIMARY,
            selected_hover_color=config.COLOR_PRIMARY_HOVER,
            unselected_color=config.COLOR_FRAME,
            unselected_hover_color=config.COLOR_BACKGROUND,
            font=("Roboto", 14)
        )
        self.selector_modo.set("Enfoque")
        self.selector_modo.grid(row=2, column=0, pady=10)

        # 3. COMPONENTE: Breathing Halo
        self.halo = BreathingHalo(
            self, 
            bg_color=config.COLOR_BACKGROUND,
            progress_color=config.COLOR_PRIMARY,
            track_color=config.COLOR_TRACK
        )
        self.halo.grid(row=3, column=0, pady=20)

        # 4. Botón Iniciar
        self.boton_start = ctk.CTkButton(
            self,
            text="Iniciar",
            command=self.toggle_timer,
            fg_color=config.COLOR_PRIMARY,
            hover_color=config.COLOR_PRIMARY_HOVER,
            text_color=config.COLOR_TEXT_MAIN,
            width=140,
            height=40,
            corner_radius=20,
            font=("Roboto", 16, "bold")
        )
        self.boton_start.grid(row=4, column=0, pady=10)

        # 5. Botón Reiniciar
        self.boton_reset = ctk.CTkButton(
            self,
            text="Reiniciar",
            command=self.reset_timer,
            fg_color="transparent",
            border_width=2,
            border_color=config.COLOR_TEXT_MUTED,
            text_color=config.COLOR_TEXT_MUTED,
            hover_color=config.COLOR_FRAME,
            width=140,
            height=40,
            corner_radius=20,
            font=("Roboto", 14)
        )
        self.boton_reset.grid(row=5, column=0, pady=(0, 20))

    def crear_menu_lateral(self):
        self.ancho_menu = 280
        self.sidebar = ctk.CTkFrame(self, width=self.ancho_menu, height=650, corner_radius=0, fg_color=config.COLOR_FRAME)
        self.sidebar.place(x=self.menu_x, y=0) 

        # Título y botón cerrar
        self.label_sidebar = ctk.CTkLabel(self.sidebar, text="Ajustes", font=("Roboto", 18, "bold"), text_color=config.COLOR_TEXT_MAIN)
        self.label_sidebar.place(x=20, y=15)

        self.btn_cerrar = ctk.CTkButton(
            self.sidebar, text="✖", width=30, height=30, 
            fg_color="transparent", hover_color=config.COLOR_BACKGROUND, 
            text_color=config.COLOR_TEXT_MUTED, command=self.toggle_menu
        )
        self.btn_cerrar.place(x=self.ancho_menu - 40, y=15)

        # --- SISTEMA DE PESTAÑAS ---
        self.tabview = ctk.CTkTabview(
            self.sidebar, width=260, height=580, 
            fg_color="transparent", 
            segmented_button_selected_color=config.COLOR_PRIMARY,
            segmented_button_selected_hover_color=config.COLOR_PRIMARY_HOVER
        )
        self.tabview.place(x=10, y=50)

        self.tabview.add("🎵 Sonidos")
        self.tabview.add("⏱️ Pomodoro")

        # --- PESTAÑA: SONIDOS ---
        self.scroll_sonidos = ctk.CTkScrollableFrame(self.tabview.tab("🎵 Sonidos"), fg_color="transparent")
        self.scroll_sonidos.pack(fill="both", expand=True, padx=5, pady=5)

        rb_ninguno = ctk.CTkRadioButton(
            self.scroll_sonidos, text="Silencio", variable=self.sonido_var, 
            value="Sin sonidos", font=("Roboto", 13), 
            text_color=config.COLOR_TEXT_MAIN, fg_color=config.COLOR_PRIMARY,
            command=self.cambiar_sonido_vivo
        )
        rb_ninguno.pack(pady=10, padx=5, anchor="w")

        # Carga dinámica de audios
        try:
            if not os.path.exists(config.SOUNDS_DIR):
                os.makedirs(config.SOUNDS_DIR)
            archivos_audio = [f for f in os.listdir(config.SOUNDS_DIR) if f.endswith(('.mp3', '.wav', '.ogg'))]
            
            for archivo in archivos_audio:
                nombre_limpio = os.path.splitext(archivo)[0].replace("-", " ").capitalize()
                rb = ctk.CTkRadioButton(
                    self.scroll_sonidos, text=nombre_limpio, variable=self.sonido_var, 
                    value=archivo, font=("Roboto", 13), 
                    text_color=config.COLOR_TEXT_MAIN, fg_color=config.COLOR_PRIMARY,
                    command=self.cambiar_sonido_vivo
                )
                rb.pack(pady=10, padx=5, anchor="w")
        except Exception as e:
            print(f"Error al cargar sonidos: {e}")

        # --- PESTAÑA: POMODORO ---
        tab_pomo = self.tabview.tab("⏱️ Pomodoro")
        
        self.selector_tipo_pomo = ctk.CTkSegmentedButton(
            tab_pomo,
            values=["Tradicional", "Personalizado"],
            command=self.cambiar_vista_pomodoro,
            selected_color=config.COLOR_PRIMARY,
            selected_hover_color=config.COLOR_PRIMARY_HOVER,
            unselected_color=config.COLOR_BACKGROUND
        )
        self.selector_tipo_pomo.set("Tradicional")
        self.selector_tipo_pomo.pack(fill="x", pady=(10, 20), padx=5)

        # Contenedor dinámico para la vista elegida
        self.frame_pomo_dinamico = ctk.CTkFrame(tab_pomo, fg_color="transparent")
        self.frame_pomo_dinamico.pack(fill="both", expand=True)

        self.construir_vista_tradicional()

    def construir_vista_tradicional(self):
        for widget in self.frame_pomo_dinamico.winfo_children():
            widget.destroy()
            
        lbl_info = ctk.CTkLabel(
            self.frame_pomo_dinamico, 
            text="El método clásico para máxima\nproductividad apoyado por la ciencia.", 
            text_color=config.COLOR_TEXT_MUTED, font=("Roboto", 12)
        )
        lbl_info.pack(pady=(0, 20))

        ctk.CTkLabel(self.frame_pomo_dinamico, text="🍅 Enfoque: 25 minutos", font=("Roboto", 14, "bold"), text_color=config.COLOR_TEXT_MAIN).pack(pady=5)
        ctk.CTkLabel(self.frame_pomo_dinamico, text="☕ Descanso: 5 minutos", font=("Roboto", 14, "bold"), text_color=config.COLOR_TEXT_MAIN).pack(pady=5)

        btn_aplicar = ctk.CTkButton(
            self.frame_pomo_dinamico, text="Aplicar Tradicional", 
            command=lambda: self.aplicar_tiempos(25, 5, "Tradicional"),
            fg_color=config.COLOR_PRIMARY, hover_color=config.COLOR_PRIMARY_HOVER
        )
        btn_aplicar.pack(pady=30)

    def construir_vista_personalizada(self):
        for widget in self.frame_pomo_dinamico.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.frame_pomo_dinamico, text="Minutos de Enfoque:", font=("Roboto", 13), text_color=config.COLOR_TEXT_MAIN).pack(anchor="w", padx=10)
        self.entry_enfoque = ctk.CTkEntry(self.frame_pomo_dinamico, placeholder_text="Ej: 45", fg_color=config.COLOR_BACKGROUND, border_color=config.COLOR_TEXT_MUTED)
        self.entry_enfoque.pack(fill="x", padx=10, pady=(0, 15))

        ctk.CTkLabel(self.frame_pomo_dinamico, text="Minutos de Descanso:", font=("Roboto", 13), text_color=config.COLOR_TEXT_MAIN).pack(anchor="w", padx=10)
        self.entry_descanso = ctk.CTkEntry(self.frame_pomo_dinamico, placeholder_text="Ej: 10", fg_color=config.COLOR_BACKGROUND, border_color=config.COLOR_TEXT_MUTED)
        self.entry_descanso.pack(fill="x", padx=10, pady=(0, 20))

        btn_guardar = ctk.CTkButton(
            self.frame_pomo_dinamico, text="Guardar y Aplicar", 
            command=self.validar_y_aplicar_personalizado,
            fg_color=config.COLOR_PRIMARY, hover_color=config.COLOR_PRIMARY_HOVER
        )
        btn_guardar.pack(pady=10)

    def cambiar_vista_pomodoro(self, seleccion):
        if seleccion == "Tradicional":
            self.construir_vista_tradicional()
        else:
            self.construir_vista_personalizada()

    def validar_y_aplicar_personalizado(self):
        try:
            min_enfoque = int(self.entry_enfoque.get())
            min_descanso = int(self.entry_descanso.get())
            
            if min_enfoque > 0 and min_descanso > 0:
                self.aplicar_tiempos(min_enfoque, min_descanso, "Personalizado")
            else:
                print("Los valores deben ser mayores a 0")
        except ValueError:
            print("Por favor, ingresa números válidos")

    def aplicar_tiempos(self, min_enfoque, min_descanso, tipo_reloj):
        config.POMODORO_TIME = min_enfoque * 60
        config.SHORT_BREAK = min_descanso * 60
        self.label_tipo_reloj.configure(text=f"Modo: {tipo_reloj}")
        self.reset_timer()
        self.toggle_menu() 

    # --- ANIMACIÓN DEL MENÚ LATERAL ---
    def toggle_menu(self):
        self.sidebar.lift()
        if self.menu_abierto:
            self.animar_menu(450)
        else:
            self.animar_menu(170)
        self.menu_abierto = not self.menu_abierto

    def animar_menu(self, target_x):
        step = 15 
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
            hover_color = config.COLOR_PRIMARY_HOVER
            self.selector_modo.configure(selected_color=nuevo_color, selected_hover_color=hover_color)
        else:
            self.time_left = config.SHORT_BREAK
            nuevo_color = config.COLOR_ACCENT
            hover_color = config.COLOR_ACCENT_HOVER
            self.selector_modo.configure(selected_color=nuevo_color, selected_hover_color=hover_color)
            
        self.total_time = self.time_left
        self.boton_start.configure(text="Iniciar", fg_color=nuevo_color, hover_color=hover_color)
        self.boton_reset.configure(border_color=nuevo_color, text_color=nuevo_color)
        
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
    ctk.set_appearance_mode("Dark") # Obligamos el modo oscuro formal
    app = ZenFocusApp()
    app.mainloop()