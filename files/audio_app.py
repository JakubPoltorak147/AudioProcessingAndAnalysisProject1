import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import sounddevice as sd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Patch
from scipy.io import wavfile
import threading
import time
import os
import sys
from scipy.io.wavfile import WavFileWarning
import warnings

from design import ColorScheme, configure_style
from audio_processing import VoicedAudioProcessor
from features_window import FeaturesWindow

warnings.simplefilter("ignore", WavFileWarning)


class AudioApp:
    def __init__(self, master):
        self.master = master

        # --- Konfigurujemy styl ---
        self.style = ttk.Style()
        configure_style(self.style)

        # Klasa do przetwarzania audio
        self.processor = VoicedAudioProcessor()

        self.master.title("Aplikacja Audio - Pastelowa Edycja")
        self.master.geometry("900x700")

        # Zmienne audio
        self.fs = None
        self.data = None
        self.total_samples = 0
        self.time_array = None
        self.current_index = 0
        self.filename = ""

        # Flag sterujących odtwarzaniem
        self.playing = False
        self.paused = False
        self.play_thread = None

        # Parametry analizy
        self.silence_threshold = 0.001
        self.frame_size = 256

        # Zmienna do wyboru trybu podświetlania
        self.highlight_mode = tk.StringVar(value="silence")  # domyślnie "silence"

        # Główna ramka
        self.main_frame = ttk.Frame(self.master, style="App.TFrame")
        self.main_frame.pack(fill="both", expand=True)

        self.create_widgets()

    def create_widgets(self):
        # --- Górny panel z przyciskami ---
        self.top_frame = ttk.Frame(self.main_frame, style="Controls.TFrame")
        self.top_frame.pack(side="top", fill="x", padx=10, pady=10)

        self.load_button = ttk.Button(
            self.top_frame,
            text="Wczytaj plik WAV",
            command=self.load_file
        )
        self.load_button.grid(row=0, column=0, padx=5, pady=5)

        self.play_button = ttk.Button(
            self.top_frame,
            text="Odtwórz",
            command=self.play_audio,
            state="disabled"
        )
        self.play_button.grid(row=0, column=1, padx=5, pady=5)

        # Odtwarzanie od początku
        self.play_from_start_button = ttk.Button(
            self.top_frame,
            text="Odtwórz od początku",
            command=self.play_from_start,
            state="disabled"
        )
        self.play_from_start_button.grid(row=0, column=2, padx=5, pady=5)

        self.pause_button = ttk.Button(
            self.top_frame,
            text="Pauza",
            command=self.toggle_pause,
            state="disabled"
        )
        self.pause_button.grid(row=0, column=3, padx=5, pady=5)

        self.features_button = ttk.Button(
            self.top_frame,
            text="Wykresy cech",
            command=self.open_features_window,
            state="disabled"
        )
        self.features_button.grid(row=0, column=4, padx=5, pady=5)

        self.close_button = ttk.Button(
            self.top_frame,
            text="Zamknij",
            command=self.on_close
        )
        self.close_button.grid(row=0, column=5, padx=5, pady=5)

        # --- Sekcja info: nazwa pliku, czas, tryb ---
        info_frame = ttk.Frame(self.main_frame, style="App.TFrame")
        info_frame.pack(side="top", fill="x", padx=10, pady=(0,5))

        self.file_label = ttk.Label(
            info_frame,
            text="Brak wczytanego pliku",
            style="TitleLabel.TLabel"
        )
        self.file_label.pack(side="top", anchor="w")

        self.time_label = ttk.Label(
            info_frame,
            text="Czas: 00:00"
        )
        self.time_label.pack(side="top", anchor="w", pady=5)

        # Etykieta z aktualnym trybem
        self.highlight_label = ttk.Label(
            info_frame,
            text="Aktualnie pokazujemy: CISZĘ"
        )
        self.highlight_label.pack(side="top", anchor="w", pady=5)

        # Suwak (inicjalizowany po wczytaniu pliku)
        self.slider = None

        # Tekst z parametrami
        self.frame_params_text = tk.StringVar()
        self.params_label = ttk.Label(
            info_frame,
            textvariable=self.frame_params_text,
            justify="left"
        )
        self.params_label.pack(side="top", anchor="w", pady=5)

        # --- Opcje wyboru trybu podświetlania ---
        mode_frame = ttk.Frame(self.main_frame, style="Controls.TFrame")
        mode_frame.pack(side="top", fill="x", padx=10, pady=5)

        ttk.Label(
            mode_frame,
            text="Tryb podświetlania:",
            style="TitleLabel.TLabel"
        ).pack(side="left", padx=(5,10))

        rb_silence = ttk.Radiobutton(
            mode_frame,
            text="Cisza",
            variable=self.highlight_mode,
            value="silence",
            command=self.update_highlight_mode
        )
        rb_silence.pack(side="left", padx=5)

        rb_voiced = ttk.Radiobutton(
            mode_frame,
            text="Dźwięczne/Bezdźwięczne",
            variable=self.highlight_mode,
            value="voiced_unvoiced",
            command=self.update_highlight_mode
        )
        rb_voiced.pack(side="left", padx=5)

        # --- Ramka z wykresem audio ---
        plot_frame = ttk.LabelFrame(
            self.main_frame,
            text="Przebieg czasowy sygnału",
            style="App.TFrame"
        )
        plot_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def update_highlight_mode(self):
        """Wywoływane przy zmianie radio buttonów."""
        mode = self.highlight_mode.get()
        if mode == "silence":
            self.highlight_label.config(text="Aktualnie pokazujemy: CISZĘ")
        else:
            self.highlight_label.config(text="Aktualnie pokazujemy: DŹWIĘCZNE / BEZDŹWIĘCZNE")

        # Przerysuj wykres w nowym trybie
        if self.data is not None:
            self.draw_main_plot()

    def load_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        if not filepath:
            return

        self.filename = filepath
        base_name = os.path.basename(filepath)
        self.file_label.config(text=f"Plik: {base_name}")

        self.fs, self.data = wavfile.read(filepath)
        if len(self.data.shape) > 1:
            self.data = self.data[:, 0]
        # Normalizacja 16-bit
        if self.data.dtype == np.int16:
            self.data = self.data.astype(np.float32) / np.iinfo(np.int16).max

        self.total_samples = len(self.data)
        duration = self.total_samples / self.fs if self.fs else 0.001
        self.time_array = np.linspace(0, duration, self.total_samples)
        self.current_index = 0

        self.draw_main_plot()
        self.calculate_and_display_frame_params()

        if not self.slider:
            self.slider = ttk.Scale(
                self.main_frame,
                from_=0, to=max(duration, 0.001),
                orient="horizontal",
                command=self.on_slider_move,
                length=600
            )
            self.slider.pack(pady=5)
        else:
            self.slider.config(to=duration)
            self.slider.set(0)

        # Aktywacja przycisków
        self.play_button.state(["!disabled"])
        self.pause_button.state(["!disabled"])
        self.features_button.state(["!disabled"])
        self.play_from_start_button.state(["!disabled"])

    def draw_main_plot(self):
        """Rysuje przebieg czasowy i zaznacza wg trybu highlight_mode."""
        self.ax.clear()
        self.ax.set_title("Przebieg czasowy sygnału", fontsize=11, color=ColorScheme.ACCENT)
        self.ax.set_xlabel("Czas [s]", fontsize=9)
        self.ax.set_ylabel("Amplituda", fontsize=9)
        self.ax.plot(self.time_array, self.data, linewidth=0.8, color=ColorScheme.WAVEFORM_COLOR)

        # Tworzymy legend patches – zależnie od trybu
        legend_patches = []
        mode = self.highlight_mode.get()

        if mode == "silence":
            # Zaznaczamy tylko ciszę
            silence_regions = self.processor.detect_silence(
                self.data, self.fs, self.frame_size, self.silence_threshold
            )
            for (start_idx, end_idx) in silence_regions:
                start_t = start_idx / self.fs
                end_t = end_idx / self.fs
                self.ax.axvspan(start_t, end_t, color=ColorScheme.SILENCE_COLOR, alpha=0.6)

            # Patch do legendy
            silence_patch = Patch(facecolor=ColorScheme.SILENCE_COLOR, alpha=0.6, label="Cisza")
            legend_patches.append(silence_patch)

        else:
            # Zaznaczamy dźwięczne/bezdźwięczne
            vu_regions = self.processor.detect_voiced_unvoiced(self.data, self.fs, self.frame_size)
            for (start_idx, end_idx, is_voiced) in vu_regions:
                start_t = start_idx / self.fs
                end_t = end_idx / self.fs
                if is_voiced:
                    self.ax.axvspan(start_t, end_t, color=ColorScheme.VOICED_COLOR, alpha=0.3)
                else:
                    self.ax.axvspan(start_t, end_t, color=ColorScheme.UNVOICED_COLOR, alpha=0.3)

            # Patche do legendy
            voiced_patch = Patch(facecolor=ColorScheme.VOICED_COLOR, alpha=0.3, label="Dźwięczne")
            unvoiced_patch = Patch(facecolor=ColorScheme.UNVOICED_COLOR, alpha=0.3, label="Bezdźwięczne")
            legend_patches.extend([voiced_patch, unvoiced_patch])

        # Linia aktualnej pozycji
        self.line = self.ax.axvline(x=0, color="#004D40", linewidth=2)

        # Dodajemy legendę (jeśli cokolwiek zaznaczamy)
        if legend_patches:
            self.ax.legend(handles=legend_patches, loc="upper right", fontsize=8)

        self.canvas.draw()

    def on_slider_move(self, value):
        if not self.playing:
            new_index = int(float(value) * self.fs) if self.fs else 0
            self.current_index = new_index
            if self.line:
                self.line.set_xdata([float(value), float(value)])
                self.canvas.draw()
            self.update_time_label(float(value))

    def update_time_label(self, current_time):
        minutes = int(current_time // 60)
        seconds = int(current_time % 60)
        self.time_label.config(text=f"Czas: {minutes:02d}:{seconds:02d}")

    def calculate_and_display_frame_params(self):
        frame_step = self.frame_size
        rms_values = []
        zcr_values = []
        for i in range(0, self.total_samples, frame_step):
            frame = self.data[i:i+frame_step]
            if len(frame) == 0:
                continue
            rms = np.sqrt(np.mean(frame**2))
            rms_values.append(rms)
            zero_crosses = np.count_nonzero(np.diff(np.sign(frame)))
            zcr = zero_crosses / len(frame) if len(frame) != 0 else 0
            zcr_values.append(zcr)
        avg_rms = np.mean(rms_values) if rms_values else 0
        avg_zcr = np.mean(zcr_values) if zcr_values else 0

        text = (
            f"Parametry nagrania (ramkowe):\n"
            f"  • Średni RMS (Volume): {avg_rms:.6f}\n"
            f"  • Średnie ZCR: {avg_zcr:.6f}\n"
            f"(Próg ciszy: {self.silence_threshold})"
        )
        self.frame_params_text.set(text)

    def play_audio(self):
        if self.data is None:
            return
        if self.current_index >= self.total_samples:
            self.current_index = 0
            if self.slider:
                self.slider.set(0)
            if self.line:
                self.line.set_xdata([0, 0])
                self.canvas.draw()

        self.playing = True
        self.paused = False
        self.play_thread = threading.Thread(target=self._play, daemon=True)
        self.play_thread.start()

    def play_from_start(self):
        """Ustawia indeks na 0 i wywołuje play."""
        self.current_index = 0
        if self.slider:
            self.slider.set(0)
        if self.line:
            self.line.set_xdata([0, 0])
            self.canvas.draw()
        self.play_audio()

    def stop_audio(self):
        self.playing = False
        sd.stop()

    def toggle_pause(self):
        if not self.playing:
            return
        if self.paused:
            self.pause_button.config(text="Pauza")
            self.paused = False
            self.play_audio()
        else:
            self.pause_button.config(text="Wznów")
            self.paused = True
            sd.stop()

    def _play(self):
        remaining_data = self.data[self.current_index:]
        if len(remaining_data) == 0:
            return
        sd.play(remaining_data, self.fs)
        start_time = time.time()
        local_start_index = self.current_index

        while (self.playing and not self.paused and
               self.current_index < self.total_samples and sd.get_stream().active):
            elapsed = time.time() - start_time
            new_index = local_start_index + int(elapsed * self.fs)
            if new_index >= self.total_samples:
                new_index = self.total_samples
                self.playing = False
            self.current_index = new_index

            current_time = self.current_index / self.fs if self.fs else 0.0
            if self.line is not None:
                self.line.set_xdata([current_time, current_time])

            self.master.after(0, self.slider.set, current_time)
            self.master.after(0, self.update_time_label, current_time)
            self.canvas.draw_idle()
            time.sleep(0.02)

        sd.stop()
        if self.current_index >= self.total_samples:
            self.current_index = self.total_samples
            if len(self.time_array) > 0:
                final_time = self.time_array[-1]
            else:
                final_time = 0.0
            self.master.after(0, self.slider.set, final_time)
            self.master.after(0, self.update_time_label, final_time)
            if self.line is not None:
                self.line.set_xdata([final_time, final_time])
                self.canvas.draw_idle()

        self.playing = False
        self.pause_button.config(text="Pauza")

    def open_features_window(self):
        if self.data is None:
            messagebox.showwarning("Brak danych", "Najpierw wczytaj plik WAV!")
            return
        FeaturesWindow(self.master, self.data, self.fs, self.frame_size, self.silence_threshold)

    def on_close(self):
        self.stop_audio()
        self.playing = False
        self.paused = True
        if self.play_thread is not None and self.play_thread.is_alive():
            self.play_thread.join(timeout=1)
        self.master.destroy()
        sys.exit(0)
