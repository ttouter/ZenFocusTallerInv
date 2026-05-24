import json
import os

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
            "achievements": []
        }
        self.load_progress()

    def add_focus_session(self, minutes_focused):
        """
        Registra una sesión de concentración terminada y otorga recompensas.
        """
        self.stats["sessions_completed"] += 1
        self.stats["total_focus_minutes"] += minutes_focused
        
        # Calcular XP ganada (ejemplo: 10 XP por cada minuto de concentración)
        xp_gained = int(minutes_focused * 10)
        self.stats["current_xp"] += xp_gained
        
        # Verificar si el usuario subió de nivel
        leveled_up = self._check_level_up()
        
        # Guardar el progreso automáticamente
        self.save_progress()
        
        return xp_gained, leveled_up

    def _check_level_up(self):
        """
        Verifica si la XP actual supera el límite necesario para el siguiente nivel.
        Retorna True si subió de nivel, False de lo contrario.
        """
        # Fórmula simple: Cada nivel requiere (Nivel actual * 100) XP
        xp_needed_for_next_level = self.stats["level"] * 100
        
        if self.stats["current_xp"] >= xp_needed_for_next_level:
            self.stats["current_xp"] -= xp_needed_for_next_level
            self.stats["level"] += 1
            return True
            
        return False

    def get_progress_percentage(self):
        """
        Devuelve el porcentaje de progreso hacia el siguiente nivel (útil para la UI).
        """
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
                    # Actualizamos solo las claves que existen para evitar errores con versiones viejas
                    for key in self.stats.keys():
                        if key in saved_data:
                            self.stats[key] = saved_data[key]
            except Exception as e:
                print(f"Error cargando el progreso: {e}")