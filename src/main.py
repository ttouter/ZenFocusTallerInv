import customtkinter as ctk
import sys
import os

# Asegurar rutas correctas para las importaciones modulares
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import ZenFocusApp

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = ZenFocusApp()
    app.mainloop()