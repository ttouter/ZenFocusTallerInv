import customtkinter as ctk
import config

class MixerPanel(ctk.CTkFrame):
    """
    Panel de mezcla que incluye control de volumen y botón de mute.
    """
    def __init__(self, master, audio_engine, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.audio_engine = audio_engine
        self.volumen_previo = 0.5  # Guardará el nivel de volumen antes de silenciar
        self.muteado = False

        # --- Contenedor superior (Título y Botón) ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 5))

        self.label_volumen = ctk.CTkLabel(
            self.header_frame, 
            text="🔊 Volumen", 
            font=("Roboto", 13, "bold"),
            text_color=config.COLOR_TEXT_MAIN
        )
        self.label_volumen.pack(side="left")

        # Botón Mute
        self.btn_mute = ctk.CTkButton(
            self.header_frame,
            text="🔇 Mute",
            width=60,
            height=24,
            corner_radius=12,
            fg_color=config.COLOR_FRAME,
            hover_color=config.COLOR_PRIMARY_HOVER,
            font=("Roboto", 11),
            command=self.alternar_mute
        )
        self.btn_mute.pack(side="right")

        # --- Slider de Volumen ---
        self.slider = ctk.CTkSlider(
            self, 
            from_=0.0, 
            to=1.0, 
            command=self.cambiar_volumen,
            progress_color=config.COLOR_PRIMARY,
            button_color=config.COLOR_PRIMARY_HOVER,
            button_hover_color=config.COLOR_TEXT_MAIN
        )
        self.slider.set(0.5)  # Inicia al 50%
        self.slider.pack(fill="x", pady=5)
        
        # Aplicamos el volumen inicial al motor
        self.audio_engine.ajustar_volumen(0.5)

    def cambiar_volumen(self, valor):
        """Se ejecuta cada vez que el usuario mueve la barra de volumen."""
        # Si el usuario mueve el slider mientras está muteado, se desmutea automáticamente
        if self.muteado and valor > 0:
            self.muteado = False
            self.btn_mute.configure(text="🔇 Mute", fg_color=config.COLOR_FRAME)
        
        # Si no está muteado, actualizamos la memoria del volumen previo
        if not self.muteado:
            self.volumen_previo = valor
            
        self.audio_engine.ajustar_volumen(valor)

    def alternar_mute(self):
        """Activa o desactiva el modo silencio recordando el nivel previo."""
        if self.muteado:
            # Desmutear: Restaurar volumen guardado
            self.muteado = False
            self.btn_mute.configure(text="🔇 Mute", fg_color=config.COLOR_FRAME)
            self.slider.set(self.volumen_previo)
            self.audio_engine.ajustar_volumen(self.volumen_previo)
        else:
            # Mutear: Guardar volumen actual y bajar a 0
            self.muteado = True
            self.btn_mute.configure(text="🔊 Sonar", fg_color=config.COLOR_PRIMARY)
            self.slider.set(0.0)
            self.audio_engine.ajustar_volumen(0.0)