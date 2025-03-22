import tkinter as tk
from tkinter import ttk

class ColorScheme:
    """
    Klasa z kolorami używanymi w aplikacji.
    Można dowolnie zmienić paletę – tutaj pastelowe zielenie i akcenty.
    """
    MAIN_BG = "#E8F5E9"    # Jasne zielonkawe tło (light pastel green)
    FRAME_BG = "#C8E6C9"   # Trochę ciemniejsza zieleń
    ACCENT = "#43A047"     # Mocny zielony akcent
    WAVEFORM_COLOR = "#1B5E20"   # Ciemniejsza zieleń do rysowania sygnału
    SILENCE_COLOR = "#FFECB3"    # Jasny żółty do zaznaczania ciszy
    VOICED_COLOR = "#B3E5FC"     # Jasny niebieski do zaznaczania fragmentów dźwięcznych
    UNVOICED_COLOR = "#FFCDD2"   # Jasny różowy do zaznaczania fragmentów bezdźwięcznych

def configure_style(style: ttk.Style):
    """Konfiguruje style ttk korzystając z klasy ColorScheme."""
    style.theme_use("clam")
    style.configure("App.TFrame", background=ColorScheme.MAIN_BG)
    style.configure("Controls.TFrame", background=ColorScheme.FRAME_BG)
    style.configure("TLabel",
                    background=ColorScheme.MAIN_BG,
                    font=("Helvetica", 10))
    style.configure("TitleLabel.TLabel",
                    background=ColorScheme.MAIN_BG,
                    font=("Helvetica", 11, "bold"),
                    foreground=ColorScheme.ACCENT)

    style.configure("TButton",
                    font=("Helvetica", 9, "bold"),
                    padding=5)
    style.map("TButton",
              foreground=[("active", "#212121"), ("disabled", "#999999")],
              background=[("active", "#A5D6A7"), ("!active", "#81C784")])  # pastelowe zielenie
