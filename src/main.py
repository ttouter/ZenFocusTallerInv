import customtkinter as ctk
import config
import math
import sys
import os

# Asegurar rutas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.components.breathing_halo import BreathingHalo

class ZenFocusApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Configuración de la Ventana ---
        self.title("ZenFocus")
        self.geometry("450x650")
        self.resizable(False, False)
        self.configure(fg_color=config.COLOR_BACKGROUND)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        # --- Variables de Estado ---
        self.time_left = config.POMODORO_TIME
        self.total_time = config.POMODORO_TIME 
        self.timer_running = False
        self.timer_id = None

        # --- Interfaz ---
        self.crear_widgets()
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

        # 2. Selector
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

    def cambiar_modo(self, valor):
        self.reset_timer()

    def toggle_timer(self):
        if self.timer_running:
            # --- PAUSAR ---
            self.timer_running = False
            self.boton_start.configure(text="Continuar")
            self.halo.stop_breathing()  # <--- Detener animación
            if self.timer_id:
                self.after_cancel(self.timer_id)
        else:
            # --- INICIAR ---
            self.timer_running = True
            self.boton_start.configure(text="Pausar")
            self.halo.start_breathing() # <--- Iniciar animación
            self.contar()

    def contar(self):
        if self.time_left > 0 and self.timer_running:
            self.time_left -= 1
            self.actualizar_reloj()
            self.timer_id = self.after(1000, self.contar)
        elif self.time_left == 0:
            self.timer_running = False
            self.boton_start.configure(text="Iniciar")
            self.halo.stop_breathing() # <--- Detener al finalizar
            
            # Restaurar tiempos
            self.time_left = config.POMODORO_TIME if self.selector_modo.get() == "Enfoque" else config.SHORT_BREAK
            self.total_time = self.time_left
            self.actualizar_reloj()

    def reset_timer(self):
        self.timer_running = False
        self.halo.stop_breathing() # <--- Asegurarnos de detener animación
        
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