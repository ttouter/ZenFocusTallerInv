import customtkinter as ctk
import math

class BreathingHalo(ctk.CTkCanvas):
    def __init__(self, master, width=300, height=300, bg_color=None, progress_color="#3949AB", track_color="#2A3439", **kwargs):
        # Si bg_color es None, usamos el gris oscuro formal por defecto
        self.bg_hex = bg_color if bg_color else "#1E262C"
        
        super().__init__(master, width=width, height=height, bg=self.bg_hex, highlightthickness=0, **kwargs)
        
        self.width = width
        self.height = height
        self.progress_color = progress_color
        self.track_color = track_color
        
        # --- Configuración de Animación (Ondas) ---
        self.is_breathing = False
        self.phase = 0  
        self.speed = 0.02
        
        # --- Dimensiones ---
        self.padding = 40  
        self.stroke_width = 15
        self.base_coords = (self.padding, self.padding, self.width-self.padding, self.height-self.padding)
        
        # Geometría para las tapas redondeadas
        self.center_x = self.width / 2
        self.center_y = self.height / 2
        self.radius = (self.width - 2 * self.padding) / 2
        
        # --- CAPAS DE DIBUJO ---
        
        # 1. Las Ondas (Ripples)
        self.ripples = []
        for _ in range(3):
            r_id = self.create_oval(self.base_coords, outline=self.bg_hex, width=2)
            self.ripples.append(r_id)
            
        # 2. El Riel de Fondo (Track estático)
        self.track_ring = self.create_oval(self.base_coords, outline=self.track_color, width=self.stroke_width)
        
        # 3. El Arco de Progreso
        self.progress_arc = self.create_arc(
            self.base_coords, 
            start=90, 
            extent=360, 
            outline=self.progress_color, 
            width=self.stroke_width, 
            style="arc"
        )
        
        # 4. Tapas Redondeadas
        cap_radius = self.stroke_width / 2
        start_x = self.center_x
        start_y = self.center_y - self.radius
        
        self.start_cap = self.create_oval(
            start_x - cap_radius, start_y - cap_radius,
            start_x + cap_radius, start_y + cap_radius,
            fill=self.progress_color, outline=self.progress_color
        )
        
        self.end_cap = self.create_oval(
            start_x - cap_radius, start_y - cap_radius,
            start_x + cap_radius, start_y + cap_radius,
            fill=self.progress_color, outline=self.progress_color
        )
        
        # 5. Texto Central (Ahumado claro)
        self.text_id = self.create_text(self.center_x, self.center_y, text="00:00", fill="#F5F5F5", font=("Roboto", 60, "bold"))

    def set_color(self, color):
        self.progress_color = color
        self.itemconfig(self.progress_arc, outline=color)
        self.itemconfig(self.start_cap, fill=color, outline=color)
        self.itemconfig(self.end_cap, fill=color, outline=color)

    def draw(self, progress, text):
        progress = max(0, min(1, progress))
        angle = 360 * progress
        
        if progress <= 0:
            self.itemconfig(self.progress_arc, state="hidden")
            self.itemconfig(self.start_cap, state="hidden")
            self.itemconfig(self.end_cap, state="hidden")
        else:
            self.itemconfig(self.progress_arc, state="normal", extent=angle)
            self.itemconfig(self.start_cap, state="normal")
            self.itemconfig(self.end_cap, state="normal")
            
            theta_deg = 90 + angle
            theta_rad = math.radians(theta_deg)
            
            end_x = self.center_x + self.radius * math.cos(theta_rad)
            end_y = self.center_y - self.radius * math.sin(theta_rad)
            
            r = self.stroke_width / 2
            self.coords(self.end_cap, end_x - r, end_y - r, end_x + r, end_y + r)

        self.itemconfig(self.text_id, text=text)

    def start_breathing(self):
        if not self.is_breathing:
            self.is_breathing = True
            self.animate_ripples()

    def stop_breathing(self):
        self.is_breathing = False
        for r_id in self.ripples:
            self.itemconfig(r_id, outline=self.bg_hex)

    def animate_ripples(self):
        if not self.is_breathing:
            return

        self.phase += self.speed
        offsets = [0, 0.33, 0.66] 
        
        for i, r_id in enumerate(self.ripples):
            local_p = (self.phase + offsets[i]) % 1.0
            
            expansion = local_p * 30 
            current_padding = self.padding - expansion
            
            new_coords = (
                current_padding, 
                current_padding, 
                self.width - current_padding, 
                self.height - current_padding
            )
            self.coords(r_id, new_coords)
            
            fade_color = self.interpolate_color(self.progress_color, self.bg_hex, local_p)
            self.itemconfig(r_id, outline=fade_color)

        self.after(30, self.animate_ripples)

    def interpolate_color(self, color_a, color_b, t):
        t = max(0, min(1, t))
        
        def hex_to_rgb(h):
            h = h.lstrip('#')
            if len(h) == 3: h = ''.join([c*2 for c in h])
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

        try:
            c1 = hex_to_rgb(color_a)
            c2 = hex_to_rgb(color_b)
            
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return color_a