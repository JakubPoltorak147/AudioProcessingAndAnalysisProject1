# audio_app.py
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import sounddevice as sd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.io import wavfile
import threading
import time
import warnings
import os
import sys
from scipy.io.wavfile import WavFileWarning
from features_window import FeaturesWindow

# Ignorujemy ostrzeżenia dotyczące pliku WAV
warnings.simplefilter("ignore", WavFileWarning)

class AudioApp:
    def __init__(self, master):
        self.master = master
        # Ustawienia stylu – przykładowe kolory i czcionki
        self.master.configure(bg="#f0f0f0")
        self.default_font = ("Helvetica", 10)

        # Zmienne audio
        self.fs = None              # Częstotliwość próbkowania
        self.data = None            # Dane audio
        self.total_samples = 0
        self.time_array = None      # Oś czasu
        self.current_index = 0      # Aktualny indeks odtwarzania
        self.filename = ""          # Pełna ścieżka do aktualnie wczytanego pliku

        # Flag sterujących odtwarzaniem
        self.playing = False
        self.paused = False
        self.play_thread = None

        # Parametry analizy
        self.silence_threshold = 0.001  # Próg detekcji ciszy
        self.frame_size = 1024          # Rozmiar ramki

        # Elementy GUI
        self.create_widgets()

    def create_widgets(self):
        top_frame = tk.Frame(self.master, bg="#f0f0f0")
        top_frame.pack(pady=10)

        self.load_button = tk.Button(top_frame, text="Wczytaj plik WAV", command=self.load_file,
                                     font=self.default_font, bg="#4CAF50", fg="white", width=18)
        self.load_button.grid(row=0, column=0, padx=5)

        self.play_button = tk.Button(top_frame, text="Odtwórz", command=self.play_audio,
                                     state="disabled", font=self.default_font, bg="#2196F3", fg="white", width=10)
        self.play_button.grid(row=0, column=1, padx=5)

        self.pause_button = tk.Button(top_frame, text="Pauza", command=self.toggle_pause,
                                      state="disabled", font=self.default_font, bg="#FF9800", fg="white", width=10)
        self.pause_button.grid(row=0, column=2, padx=5)

        self.features_button = tk.Button(top_frame, text="Wykresy cech", command=self.open_features_window,
                                         state="disabled", font=self.default_font, bg="#9C27B0", fg="white", width=12)
        self.features_button.grid(row=0, column=3, padx=5)

        self.close_button = tk.Button(top_frame, text="Zamknij", command=self.on_close,
                                      font=self.default_font, bg="#f44336", fg="white", width=10)
        self.close_button.grid(row=0, column=4, padx=5)

        # Etykieta z nazwą pliku
        self.file_label = tk.Label(self.master, text="Brak wczytanego pliku", font=self.default_font, bg="#f0f0f0")
        self.file_label.pack(pady=5)

        # Etykieta czasu
        self.time_label = tk.Label(self.master, text="Czas: 00:00", font=self.default_font, bg="#f0f0f0")
        self.time_label.pack(pady=5)

        # Suwak – zostanie utworzony przy wczytaniu pliku
        self.slider = None

        # Label z parametrami
        self.frame_params_text = tk.StringVar()
        self.params_label = tk.Label(self.master, textvariable=self.frame_params_text,
                                     justify="left", font=self.default_font, bg="#f0f0f0")
        self.params_label.pack(pady=5)

        # Wykres z sygnałem audio
        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def load_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        if not filepath:
            return

        self.filename = filepath
        # Aktualizacja etykiety z nazwą pliku (wyświetlamy tylko nazwę pliku)
        self.file_label.config(text=f"Plik: {os.path.basename(filepath)}")

        self.fs, self.data = wavfile.read(filepath)
        # Jeśli plik jest stereo – wybieramy jeden kanał
        if len(self.data.shape) > 1:
            self.data = self.data[:, 0]
        # Normalizacja, jeśli int16
        if self.data.dtype == np.int16:
            self.data = self.data.astype(np.float32) / np.iinfo(np.int16).max

        self.total_samples = len(self.data)
        duration = self.total_samples / self.fs
        self.time_array = np.linspace(0, duration, self.total_samples)
        self.current_index = 0

        # Rysowanie wykresu
        self.ax.clear()
        self.ax.set_title("Przebieg czasowy sygnału", fontsize=12)
        self.ax.set_xlabel("Czas [s]", fontsize=10)
        self.ax.set_ylabel("Amplituda", fontsize=10)
        self.ax.plot(self.time_array, self.data, label="Sygnał audio", linewidth=0.8, color="#1565C0")
        # Dodajemy poziomą linię na poziomie 0.0
        self.ax.axhline(y=0.0, color="black", linestyle="--", linewidth=1)

        # Detekcja ciszy i zaznaczenie regionów
        silence_regions = self.detect_silence()
        for (start_idx, end_idx) in silence_regions:
            start_time = start_idx / self.fs
            end_time = end_idx / self.fs
            self.ax.axvspan(start_time, end_time, color="#EF5350", alpha=0.3)

        # Linia pokazująca aktualną pozycję odtwarzania
        self.line = self.ax.axvline(x=0, color="#388E3C", linewidth=2)
        self.canvas.draw()

        # Obliczenie i wyświetlenie parametrów ramki
        self.calculate_and_display_frame_params()

        # Utworzenie suwaka (jeśli nie został jeszcze utworzony)
        if self.slider is None:
            self.slider = tk.Scale(self.master, from_=0, to=duration, orient="horizontal", resolution=0.01,
                                   length=600, font=self.default_font, troughcolor="#e0e0e0")
            self.slider.pack(pady=5)
            self.slider.bind("<ButtonRelease-1>", self.slider_released)
        else:
            self.slider.config(to=duration)
            self.slider.set(0)

        # Odblokowanie przycisków
        self.play_button.config(state="normal")
        self.pause_button.config(state="normal")
        self.features_button.config(state="normal")

    def slider_released(self, event):
        new_time = self.slider.get()
        self.current_index = int(new_time * self.fs)
        if self.line is not None:
            self.line.set_xdata([new_time, new_time])
            self.canvas.draw()
        self.update_time_label(new_time)
        if self.playing:
            self.stop_audio()
            self.play_audio()

    def update_time_label(self, current_time):
        minutes = int(current_time // 60)
        seconds = int(current_time % 60)
        self.time_label.config(text=f"Czas: {minutes:02d}:{seconds:02d}")

    def detect_silence(self):
        silence_regions = []
        frame_step = self.frame_size
        in_silence = False
        start_silence = 0
        for i in range(0, self.total_samples, frame_step):
            frame = self.data[i:i+frame_step]
            rms = np.sqrt(np.mean(frame**2))
            if rms < self.silence_threshold:
                if not in_silence:
                    in_silence = True
                    start_silence = i
            else:
                if in_silence:
                    silence_regions.append((start_silence, i))
                    in_silence = False
        if in_silence:
            silence_regions.append((start_silence, self.total_samples))
        return silence_regions

    def calculate_and_display_frame_params(self):
        frame_step = self.frame_size
        rms_values = []
        zcr_values = []
        for i in range(0, self.total_samples, frame_step):
            frame = self.data[i:i+frame_step]
            rms = np.sqrt(np.mean(frame**2))
            rms_values.append(rms)
            zero_crosses = np.count_nonzero(np.diff(np.sign(frame)))
            zcr = zero_crosses / len(frame)
            zcr_values.append(zcr)
        avg_rms = np.mean(rms_values)
        avg_zcr = np.mean(zcr_values)
        text = (f"Parametry nagrania na poziomie ramek:\n"
                f"  • Średni RMS (Volume): {avg_rms:.6f}\n"
                f"  • Średnie ZCR: {avg_zcr:.6f}\n"
                f"(Próg ciszy: {self.silence_threshold})")
        self.frame_params_text.set(text)

    def play_audio(self):
        if self.data is None:
            return
        # Jeśli odtwarzanie zakończyło się, resetujemy indeks i suwak
        if self.current_index >= self.total_samples:
            self.current_index = 0
            self.slider.set(0)
            if self.line is not None:
                self.line.set_xdata([0, 0])
                self.canvas.draw()
        self.playing = True
        self.paused = False
        self.play_thread = threading.Thread(target=self._play, daemon=True)
        self.play_thread.start()

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
            self.pause_button.config(text="Resume")
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
            current_time = self.current_index / self.fs
            if self.line is not None:
                self.line.set_xdata([current_time, current_time])
            self.master.after(0, self.slider.set, current_time)
            self.master.after(0, self.update_time_label, current_time)
            self.canvas.draw_idle()
            time.sleep(0.02)
        sd.stop()
        if self.current_index >= self.total_samples:
            self.current_index = self.total_samples
            final_time = self.time_array[-1]
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
        # Zatrzymaj odtwarzanie i dołącz wątek, jeśli działa
        self.stop_audio()
        self.playing = False
        self.paused = True
        if self.play_thread is not None and self.play_thread.is_alive():
            self.play_thread.join(timeout=1)
        self.master.destroy()
        sys.exit(0)
