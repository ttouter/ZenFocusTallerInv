import customtkinter as ctk
import config
import math
import sys
import os

# Asegurar rutas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.components.breathing_halo import BreathingHalo
from logic.audio_engine import AudioEngine
from logic.notification_engine import NotificationEngine
from ui.components.mixer_panel import MixerPanel

class ZenFocusApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Inicializar Motores ---
        self.audio_engine = AudioEngine()
        self.notification_engine = NotificationEngine()

        # --- Configuración de la Ventana ---
        self.title("ZenFocus")
        self.geometry("450x650")
        self.resizable(False, False)
        self.configure(fg_color=config.COLOR_BACKGROUND)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        # --- Variables de Estado y Ciclos ---
        self.time_left = config.POMODORO_TIME
        self.total_time = config.POMODORO_TIME 
        self.timer_running = False
        self.timer_id = None
        
        self.estado_actual = "Enfoque" 
        self.ciclo_actual = 1
        self.ciclos_totales = 4
        self.modo_vista = "Normal" # Controla la vista actual
        
        # --- Variables del Menú (Responsivo) ---
        self.menu_abierto = False 
        self.ancho_menu = 280
        self.menu_offset_x = 0  # Controla la animación desde el borde derecho
        self.sonido_var = ctk.StringVar(value="Sin sonidos") 

        # --- Interfaz ---
        self.crear_widgets()
        self.crear_menu_lateral()
        
        self.actualizar_etiquetas_estado()
        self.actualizar_reloj()

        ctk.CTkFrame(self.scroll_sonidos, height=2, fg_color=config.COLOR_FRAME).pack(fill="x", pady=(15,10))
        self.mixer_panel = MixerPanel(self.scroll_sonidos, self.audio_engine)
        self.mixer_panel.pack(fill="x", padx=5, pady=5)

        # --- Eventos para Pantalla ---
        self.bind("<ButtonPress-1>", self.iniciar_arrastre)
        self.bind("<B1-Motion>", self.arrastrar)
        self.bind("<Double-Button-1>", self.restaurar_vista_normal)
        self.bind("<Escape>", self.restaurar_desde_escape) # Presionar Esc para salir

    def crear_widgets(self):
        self.label_titulo = ctk.CTkLabel(
            self, text="ZenFocus", font=("Segoe UI Variable", 24, "bold"), text_color=config.COLOR_TEXT_MAIN
        )
        self.label_titulo.grid(row=0, column=0, pady=(20, 0))

        # El botón de ajustes se ancla dinámicamente a la esquina superior derecha
        self.btn_abrir_menu = ctk.CTkButton(
            self, text="⚙️ Ajustes", width=90, height=30, corner_radius=15,
            fg_color=config.COLOR_FRAME, hover_color=config.COLOR_TRACK, text_color=config.COLOR_TEXT_MAIN,
            font=("Segoe UI", 12), command=self.toggle_menu
        )
        self.btn_abrir_menu.place(relx=0.95, y=20, anchor="ne")

        self.frame_info = ctk.CTkFrame(self, fg_color=config.COLOR_FRAME, corner_radius=10)
        self.frame_info.grid(row=1, column=0, pady=10, padx=20, sticky="ew")
        
        self.label_estado = ctk.CTkLabel(self.frame_info, text="", font=("Segoe UI", 14), text_color=config.COLOR_TEXT_MAIN)
        self.label_estado.pack(pady=(10, 0))
        
        self.label_ciclo = ctk.CTkLabel(self.frame_info, text="", font=("Segoe UI", 12), text_color=config.COLOR_TEXT_MUTED)
        self.label_ciclo.pack(pady=(0, 10))

        self.halo = BreathingHalo(
            self, bg_color=config.COLOR_BACKGROUND, progress_color=config.COLOR_PRIMARY, track_color=config.COLOR_TRACK
        )
        self.halo.grid(row=3, column=0, pady=20)

        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.grid(row=4, column=0, pady=10)

        self.boton_start = ctk.CTkButton(
            self.frame_botones, text="▷ Comenzar Ciclo", command=self.toggle_timer,
            fg_color=config.COLOR_FRAME, hover_color=config.COLOR_TRACK, text_color=config.COLOR_TEXT_MAIN,
            border_width=1, border_color=config.COLOR_TRACK, width=150, height=40, corner_radius=8, font=("Segoe UI", 14)
        )
        self.boton_start.pack(side="left", padx=10)

        self.boton_reset = ctk.CTkButton(
            self.frame_botones, text="⟳ Reiniciar", command=self.reset_timer,
            fg_color="transparent", hover_color=config.COLOR_FRAME, text_color=config.COLOR_TEXT_MUTED,
            border_width=1, border_color=config.COLOR_TEXT_MUTED, width=150, height=40, corner_radius=8, font=("Segoe UI", 14)
        )
        self.boton_reset.pack(side="left", padx=10)

    def actualizar_etiquetas_estado(self):
        if self.estado_actual == "Enfoque":
            if self.ciclo_actual >= self.ciclos_totales:
                texto_estado = "ⓘ Estado Actual: Enfoque (Próximo: Descanso Largo)"
            else:
                texto_estado = "ⓘ Estado Actual: Enfoque (Próximo: Descanso)"
            self.halo.set_color(config.COLOR_PRIMARY)
        elif self.estado_actual == "Descanso Largo":
            texto_estado = "ⓘ Estado Actual: Descanso Largo (Próximo: Fin)"
            self.halo.set_color(config.COLOR_ACCENT)
        else:
            texto_estado = "ⓘ Estado Actual: Descanso (Próximo: Enfoque)"
            self.halo.set_color(config.COLOR_ACCENT)
            
        self.label_estado.configure(text=texto_estado)
        self.label_ciclo.configure(text=f"Ciclo {self.ciclo_actual} / {self.ciclos_totales}")

    def crear_menu_lateral(self):
        # El menú se ancla al borde derecho y usa toda la altura (relheight=1.0)
        self.sidebar = ctk.CTkFrame(self, width=self.ancho_menu, corner_radius=0, fg_color=config.COLOR_FRAME)
        self.sidebar.place(relx=1.0, x=self.menu_offset_x, y=0, relheight=1.0) 

        self.label_sidebar = ctk.CTkLabel(self.sidebar, text="Ajustes", font=("Segoe UI", 18, "bold"), text_color=config.COLOR_TEXT_MAIN)
        self.label_sidebar.place(x=20, y=15)

        self.btn_cerrar = ctk.CTkButton(
            self.sidebar, text="✖", width=30, height=30, fg_color="transparent", hover_color=config.COLOR_TRACK, 
            text_color=config.COLOR_TEXT_MUTED, command=self.toggle_menu
        )
        self.btn_cerrar.place(x=self.ancho_menu - 40, y=15)

        self.tabview = ctk.CTkTabview(
            self.sidebar, width=260, fg_color="transparent", 
            segmented_button_selected_color=config.COLOR_PRIMARY,
            segmented_button_selected_hover_color=config.COLOR_PRIMARY_HOVER,
            segmented_button_unselected_color=config.COLOR_BACKGROUND
        )
        self.tabview.place(x=10, y=50, relheight=0.85) # Permite estirarse en pantallas grandes

        self.tabview.add("🎵 Sonidos")
        self.tabview.add("⏱️ Tiempos")
        self.tabview.add("🖥️ Pantalla") 

        # --- PESTAÑA: PANTALLA ---
        tab_pantalla = self.tabview.tab("🖥️ Pantalla")
        ctk.CTkLabel(tab_pantalla, text="Modo de Visualización:", font=("Segoe UI", 13), text_color=config.COLOR_TEXT_MAIN).pack(pady=(20, 10))
        
        self.selector_vista = ctk.CTkSegmentedButton(
            tab_pantalla,
            values=["Normal", "Completa", "Flotante"],
            command=self.cambiar_vista,
            selected_color=config.COLOR_PRIMARY,
            selected_hover_color=config.COLOR_PRIMARY_HOVER,
            unselected_color=config.COLOR_BACKGROUND
        )
        self.selector_vista.set("Normal")
        self.selector_vista.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            tab_pantalla, 
            text="💡 Tip: En el modo flotante, \npuedes arrastrar el reloj a \ncualquier parte. Haz doble \nclic para volver a Normal.", 
            font=("Segoe UI", 12), text_color=config.COLOR_TEXT_MUTED, justify="left"
        ).pack(pady=20, padx=10)

        # --- PESTAÑA: SONIDOS ---
        self.scroll_sonidos = ctk.CTkScrollableFrame(self.tabview.tab("🎵 Sonidos"), fg_color="transparent")
        self.scroll_sonidos.pack(fill="both", expand=True, padx=5, pady=5)
        rb_ninguno = ctk.CTkRadioButton(
            self.scroll_sonidos, text="Silencio", variable=self.sonido_var, value="Sin sonidos", font=("Segoe UI", 13), 
            text_color=config.COLOR_TEXT_MAIN, fg_color=config.COLOR_PRIMARY, command=self.cambiar_sonido_vivo
        )
        rb_ninguno.pack(pady=10, padx=5, anchor="w")

        for sonido in self.audio_engine.obtener_sonidos_disponibles():
            rb = ctk.CTkRadioButton(
                self.scroll_sonidos, text=sonido["nombre_mostrar"], variable=self.sonido_var, value=sonido["archivo"], 
                font=("Segoe UI", 13), text_color=config.COLOR_TEXT_MAIN, fg_color=config.COLOR_PRIMARY, command=self.cambiar_sonido_vivo
            )
            rb.pack(pady=10, padx=5, anchor="w")

        # --- PESTAÑA: TIEMPOS ---
        tab_pomo = self.tabview.tab("⏱️ Tiempos")
        
        ctk.CTkLabel(tab_pomo, text="Modo de Temporizador:", font=("Segoe UI", 13), text_color=config.COLOR_TEXT_MAIN).pack(pady=(10, 5))
        
        self.selector_modo_pomo = ctk.CTkSegmentedButton(
            tab_pomo,
            values=["Normal", "Personalizado"],
            command=self.cambiar_modo_pomodoro,
            selected_color=config.COLOR_PRIMARY,
            selected_hover_color=config.COLOR_PRIMARY_HOVER,
            unselected_color=config.COLOR_BACKGROUND
        )
        self.selector_modo_pomo.set("Normal")
        self.selector_modo_pomo.pack(fill="x", padx=10, pady=5)

        self.frame_pomo_dinamico = ctk.CTkFrame(tab_pomo, fg_color="transparent")
        # No usamos .pack() aquí todavía para que inicie oculto en el modo Normal
        
        self.construir_vista_personalizada()

    def cambiar_modo_pomodoro(self, modo):
        if modo == "Normal":
            # Ocultamos el menú personalizado
            self.frame_pomo_dinamico.pack_forget()
            
            # Restauramos los valores tradicionales por defecto
            config.POMODORO_TIME = 25 * 60
            config.SHORT_BREAK = 5 * 60
            self.ciclos_totales = 4
            
            self.reset_timer()
            if self.modo_vista != "Flotante": 
                self.mostrar_alerta("⏱️ Modo Normal (25/5) activado", config.COLOR_PRIMARY)
                
        elif modo == "Personalizado":
            # Mostramos el menú con los campos para escribir
            self.frame_pomo_dinamico.pack(fill="both", expand=True, pady=10)

    def construir_vista_personalizada(self):
        for widget in self.frame_pomo_dinamico.winfo_children():
            widget.destroy()

        self.var_enfoque = ctk.StringVar(value=str(int(config.POMODORO_TIME / 60)))
        self.var_descanso = ctk.StringVar(value=str(int(config.SHORT_BREAK / 60)))
        self.var_ciclos = ctk.StringVar(value=str(self.ciclos_totales))

        ctk.CTkLabel(self.frame_pomo_dinamico, text="Enfoque (min):", font=("Segoe UI", 13)).pack(anchor="w", padx=10)
        self.entry_enfoque = ctk.CTkEntry(self.frame_pomo_dinamico, fg_color=config.COLOR_BACKGROUND, textvariable=self.var_enfoque)
        self.entry_enfoque.pack(fill="x", padx=10, pady=(0, 15))

        ctk.CTkLabel(self.frame_pomo_dinamico, text="Descanso (min):", font=("Segoe UI", 13)).pack(anchor="w", padx=10)
        self.entry_descanso = ctk.CTkEntry(self.frame_pomo_dinamico, fg_color=config.COLOR_BACKGROUND, textvariable=self.var_descanso)
        self.entry_descanso.pack(fill="x", padx=10, pady=(0, 15))
        
        ctk.CTkLabel(self.frame_pomo_dinamico, text="Ciclos:", font=("Segoe UI", 13)).pack(anchor="w", padx=10)
        self.entry_ciclos = ctk.CTkEntry(self.frame_pomo_dinamico, fg_color=config.COLOR_BACKGROUND, textvariable=self.var_ciclos)
        self.entry_ciclos.pack(fill="x", padx=10, pady=(0, 20))

        ctk.CTkButton(
            self.frame_pomo_dinamico, text="Aplicar Tiempos", command=self.validar_y_aplicar_personalizado,
            fg_color=config.COLOR_PRIMARY, hover_color=config.COLOR_PRIMARY_HOVER
        ).pack(pady=10)

    # --- LÓGICA DE VISTAS (PANTALLA) ---
    def cambiar_vista(self, modo):
        self.modo_vista = modo
        
        # 1. Resetear TODOS los estados previos antes de aplicar el nuevo
        self.state('normal') # <--- ESTA LÍNEA QUITA EL BUG DEL MAXIMIZADO
        self.overrideredirect(False)
        self.attributes("-fullscreen", False)
        self.attributes("-topmost", False)
        self.resizable(True, True) 

        if modo == "Normal":
            self.geometry("450x650")
            self.resizable(False, False) # Volvemos a bloquear el tamaño
            
            # Restaurar visibilidad
            self.label_titulo.grid()
            self.btn_abrir_menu.place(relx=0.95, y=20, anchor="ne")
            self.frame_info.grid()
            self.frame_botones.grid()
            self.halo.grid(row=3, column=0, pady=20, rowspan=1)
            
        elif modo == "Completa":
            # Forzamos maximizado
            self.state('zoomed') 
            
            self.label_titulo.grid()
            self.btn_abrir_menu.place(relx=0.95, y=20, anchor="ne")
            self.frame_info.grid()
            self.frame_botones.grid()
            self.halo.grid(row=3, column=0, pady=20, rowspan=1)
            
            self.mostrar_alerta("💡 Presiona 'Esc' para salir", config.COLOR_FRAME)
            
        elif modo == "Flotante":
            self.overrideredirect(True)
            self.attributes("-topmost", True)
            self.geometry("260x260")
            self.resizable(False, False)
            
            # Ocultar controles
            self.label_titulo.grid_remove()
            self.btn_abrir_menu.place_forget()
            self.frame_info.grid_remove()
            self.frame_botones.grid_remove()
            
            if self.menu_abierto:
                self.toggle_menu()
                
            self.halo.grid(row=0, column=0, pady=0, rowspan=7)
            self.mostrar_alerta("💡 Doble clic para salir", config.COLOR_PRIMARY)

    def iniciar_arrastre(self, event):
        if self.modo_vista == "Flotante":
            self.x = event.x
            self.y = event.y

    def arrastrar(self, event):
        if self.modo_vista == "Flotante":
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.winfo_x() + deltax
            y = self.winfo_y() + deltay
            self.geometry(f"+{x}+{y}")
            
    def restaurar_vista_normal(self, event):
        if self.modo_vista == "Flotante":
            self.selector_vista.set("Normal") 
            self.cambiar_vista("Normal")

    def restaurar_desde_escape(self, event):
        if self.modo_vista == "Completa":
            self.selector_vista.set("Normal")
            self.cambiar_vista("Normal")

    def validar_y_aplicar_personalizado(self):
        try:
            min_enf = int(self.var_enfoque.get())
            min_des = int(self.var_descanso.get())
            ciclos = int(self.var_ciclos.get())
            if min_enf > 0 and min_des > 0 and ciclos > 0:
                config.POMODORO_TIME = min_enf * 60
                config.SHORT_BREAK = min_des * 60
                self.ciclos_totales = ciclos
                self.reset_timer()
                self.toggle_menu() 
                self.mostrar_alerta("✅ Tiempos personalizados aplicados", config.COLOR_PRIMARY)
            else:
                self.mostrar_alerta("❌ Valores deben ser > 0", config.COLOR_FRAME)
        except ValueError:
            self.mostrar_alerta("❌ Ingresa números válidos", config.COLOR_FRAME)

    # --- ANIMACIÓN RESPONSIVA DEL MENÚ ---
    def toggle_menu(self):
        self.sidebar.lift()
        if self.menu_abierto:
            self.animar_menu(0) # Ocultar
        else:
            self.animar_menu(-self.ancho_menu) # Mostrar (-280px)
        self.menu_abierto = not self.menu_abierto

    def animar_menu(self, target_x):
        step = 30 
        if self.menu_offset_x > target_x:
            self.menu_offset_x = max(self.menu_offset_x - step, target_x)
            self.sidebar.place(relx=1.0, x=self.menu_offset_x, y=0, relheight=1.0)
            self.after(10, lambda: self.animar_menu(target_x))
        elif self.menu_offset_x < target_x:
            self.menu_offset_x = min(self.menu_offset_x + step, target_x)
            self.sidebar.place(relx=1.0, x=self.menu_offset_x, y=0, relheight=1.0)
            self.after(10, lambda: self.animar_menu(target_x))

    def reproducir_sonido(self):
        self.audio_engine.reproducir(self.sonido_var.get())

    def detener_sonido(self):
        self.audio_engine.detener()

    def cambiar_sonido_vivo(self):
        if self.timer_running and self.estado_actual == "Enfoque":
            self.detener_sonido()
            self.reproducir_sonido()

    def toggle_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.boton_start.configure(text="▷ Continuar")
            self.halo.stop_breathing()
            self.detener_sonido() 
            self.notification_engine.gestionar_notificaciones(False)
            if self.timer_id:
                self.after_cancel(self.timer_id)
        else:
            self.timer_running = True
            self.boton_start.configure(text="|| Pausar")
            self.halo.start_breathing()
            if self.estado_actual == "Enfoque":
                self.reproducir_sonido()
                self.notification_engine.gestionar_notificaciones(True)
            else:
                self.notification_engine.gestionar_notificaciones(False)
            self.contar()

    def contar(self):
        if self.time_left > 0 and self.timer_running:
            self.time_left -= 1
            self.actualizar_reloj()
            self.timer_id = self.after(1000, self.contar)
        elif self.time_left <= 0:
            self.detener_sonido()
            if self.estado_actual == "Enfoque":
                if self.ciclo_actual >= self.ciclos_totales:
                    # Toca descanso largo al final de los ciclos
                    self.estado_actual = "Descanso Largo"
                    self.time_left = config.LONG_BREAK
                    self.total_time = config.LONG_BREAK
                    self.notification_engine.gestionar_notificaciones(False)
                    if self.modo_vista != "Flotante": self.mostrar_alerta("🎉 ¡4 ciclos! Descanso largo.", config.COLOR_ACCENT)
                else:
                    # Descanso corto normal
                    self.estado_actual = "Descanso"
                    self.time_left = config.SHORT_BREAK
                    self.total_time = config.SHORT_BREAK
                    self.notification_engine.gestionar_notificaciones(False)
                    if self.modo_vista != "Flotante": self.mostrar_alerta("☕ ¡Tiempo de descanso!", config.COLOR_ACCENT)
            
            elif self.estado_actual in ["Descanso", "Descanso Largo"]:
                if self.estado_actual == "Descanso Largo":
                    # Fin de la sesión completa
                    self.timer_running = False
                    self.halo.stop_breathing()
                    self.boton_start.configure(text="▷ Comenzar Ciclo")
                    self.ciclo_actual = 1
                    self.estado_actual = "Enfoque"
                    self.time_left = config.POMODORO_TIME
                    self.total_time = config.POMODORO_TIME
                    if self.modo_vista != "Flotante": self.mostrar_alerta("✅ ¡Sesión completada!", config.COLOR_PRIMARY)
                    self.actualizar_etiquetas_estado()
                    self.actualizar_reloj()
                    return
                else:
                    # Fin de descanso corto, vuelve al enfoque
                    self.estado_actual = "Enfoque"
                    self.time_left = config.POMODORO_TIME
                    self.total_time = config.POMODORO_TIME
                    self.ciclo_actual += 1
                    if self.modo_vista != "Flotante": self.mostrar_alerta("🍅 ¡De vuelta al enfoque!", config.COLOR_PRIMARY)
                    if self.timer_running:
                        self.reproducir_sonido()
                        self.notification_engine.gestionar_notificaciones(True)

            self.actualizar_etiquetas_estado()
            self.actualizar_reloj()
            if self.timer_running:
                self.timer_id = self.after(1000, self.contar)

    def reset_timer(self):
        self.timer_running = False
        self.halo.stop_breathing()
        self.detener_sonido() 
        self.notification_engine.gestionar_notificaciones(False)
        if self.timer_id:
            self.after_cancel(self.timer_id)
        
        self.estado_actual = "Enfoque"
        self.ciclo_actual = 1
        self.time_left = config.POMODORO_TIME
        self.total_time = config.POMODORO_TIME
        self.boton_start.configure(text="▷ Comenzar Ciclo")
        self.actualizar_etiquetas_estado()
        self.actualizar_reloj()

    def formato_tiempo(self, segundos):
        return f"{math.floor(segundos / 60):02d}:{segundos % 60:02d}"

    def actualizar_reloj(self):
        self.halo.draw(self.time_left / self.total_time if self.total_time > 0 else 0, self.formato_tiempo(self.time_left))

    def mostrar_alerta(self, mensaje, color_fondo):
        if hasattr(self, "toast_actual") and self.toast_actual.winfo_exists(): self.toast_actual.destroy()
        self.toast_actual = ctk.CTkLabel(
            self, text=mensaje, fg_color=color_fondo, text_color=config.COLOR_TEXT_MAIN,
            corner_radius=15, font=("Segoe UI", 14, "bold"), width=230, height=40
        )
        self.toast_rely = 1.1 
        self.toast_actual.place(relx=0.5, rely=self.toast_rely, anchor="center")
        self.animar_entrada_toast()

    def animar_entrada_toast(self):
        if hasattr(self, "toast_actual") and self.toast_actual.winfo_exists():
            if self.toast_rely > 0.92:
                self.toast_rely -= 0.015  
                self.toast_actual.place(relx=0.5, rely=self.toast_rely, anchor="center")
                self.after(15, self.animar_entrada_toast)
            else:
                self.after(3000, self.animar_salida_toast)

    def animar_salida_toast(self):
        if hasattr(self, "toast_actual") and self.toast_actual.winfo_exists():
            if self.toast_rely < 1.1:
                self.toast_rely += 0.015  
                self.toast_actual.place(relx=0.5, rely=self.toast_rely, anchor="center")
                self.after(15, self.animar_salida_toast)
            else:
                self.toast_actual.destroy()

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = ZenFocusApp()
    app.mainloop()