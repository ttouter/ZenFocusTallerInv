import json
import os
from datetime import date, timedelta

class GamificationEngine:
    """
    Motor de gamificación para ZenFocus.
    Se encarga de rastrear el tiempo de concentración, otorgar puntos de experiencia (XP),
    y gestionar el nivel del usuario para mantener la motivación.
    """
    
    def __init__(self, save_file="user_progress.json"):
        self.save_file = save_file
        self.stats = {
            "level": 1,
            "current_xp": 0,
            "total_focus_minutes": 0,
            "sessions_completed": 0,
            "achievements": [],
            "streak_count": 0,          # Días de racha actual
            "last_active_date": None,   # Última fecha activa
            "active_days": []           # Lista de fechas activas ('YYYY-MM-DD')
        }
        self.load_progress()

    def add_focus_session(self, minutes_focused):
        """
        Registra una sesión de concentración terminada y otorga recompensas.
        """
        self.stats["sessions_completed"] += 1
        self.stats["total_focus_minutes"] += minutes_focused
        
        # Calcular XP ganada
        xp_gained = int(minutes_focused * 10)
        self.stats["current_xp"] += xp_gained
        
        # --- LÓGICA DE RACHAS ---
        today = date.today().isoformat()
        racha_actualizada = False
        
        # Si hoy no se ha registrado actividad, actualizar racha
        if today not in self.stats["active_days"]:
            self.stats["active_days"].append(today)
            
            if self.stats["last_active_date"]:
                last_date = date.fromisoformat(self.stats["last_active_date"])
                
                # Si la última actividad fue exactamente ayer, aumentar racha
                if date.today() - last_date == timedelta(days=1):
                    self.stats["streak_count"] += 1
                # Si pasó más de un día, la racha se reinicia a 1
                elif date.today() - last_date > timedelta(days=1):
                    self.stats["streak_count"] = 1
            else:
                # Primera vez que usa la app
                self.stats["streak_count"] = 1
                
            self.stats["last_active_date"] = today
            racha_actualizada = True
        # -------------------------------
        
        leveled_up = self._check_level_up()
        
        # Guardar el progreso automáticamente
        self.save_progress()
        
        # ¡AQUÍ ESTÁ LA CORRECCIÓN! Devolvemos 3 valores en lugar de 2
        return xp_gained, leveled_up, racha_actualizada

    def _check_level_up(self):
        """
        Verifica si la XP actual supera el límite necesario para el siguiente nivel.
        """
        # Fórmula simple: Cada nivel requiere (Nivel actual * 100) XP
        xp_needed_for_next_level = self.stats["level"] * 100
        
        if self.stats["current_xp"] >= xp_needed_for_next_level:
            self.stats["current_xp"] -= xp_needed_for_next_level
            self.stats["level"] += 1
            return True
            
        return False

    def get_progress_percentage(self):
        """Devuelve el porcentaje de progreso hacia el siguiente nivel."""
        xp_needed = self.stats["level"] * 100
        return (self.stats["current_xp"] / xp_needed) * 100

    def get_stats(self):
        """Devuelve las estadísticas actuales del usuario."""
        return self.stats

    def save_progress(self):
        """Guarda el progreso en un archivo JSON local."""
        try:
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=4)
        except Exception as e:
            print(f"Error guardando el progreso: {e}")

    def load_progress(self):
        """Carga el progreso desde el archivo JSON si existe."""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    for key in self.stats.keys():
                        if key in saved_data:
                            self.stats[key] = saved_data[key]
            except Exception as e:
                print(f"Error cargando el progreso: {e}")