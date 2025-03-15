# features_window.py
import tkinter as tk
from tkinter import ttk
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from features import compute_volume, compute_ste, compute_zcr, compute_sr, compute_f0


class FeaturesWindow:
    def __init__(self, master, data, fs, frame_size, silence_threshold):
        self.top = tk.Toplevel(master)
        self.top.title("Wykresy cech sygnału")
        self.top.geometry("1200x800")
        self.top.configure(bg="#ffffff")
        self.data = data
        self.fs = fs
        self.frame_size = frame_size
        self.silence_threshold = silence_threshold

        # Oblicz cechy ramkowe
        self.frames, self.times = self.frame_signal(self.data, self.fs, self.frame_size)
        self.volume = np.array([compute_volume(frame) for frame in self.frames])
        self.ste = np.array([compute_ste(frame) for frame in self.frames])
        self.zcr = np.array([compute_zcr(frame) for frame in self.frames])
        self.sr = np.array([compute_sr(frame) for frame in self.frames])
        self.f0 = np.array([compute_f0(frame, self.fs) for frame in self.frames])

        # Utwórz przewijalny obszar na pełnym oknie
        container = ttk.Frame(self.top)
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container, bg="#ffffff")
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Rysujemy duże wykresy cech z opisami
        self.plot_feature(self.times, self.volume, "Volume (RMS)",
                          "Volume określa średnią głośność sygnału, obliczaną jako pierwiastek średniej energii ramki.",
                          row=0, color="#1E88E5")
        self.plot_feature(self.times, self.ste, "Short Time Energy (STE)",
                          "STE to suma kwadratów wartości sygnału w ramce, pomagająca odróżnić fragmenty dźwięczne od bezdźwięcznych.",
                          row=1, color="#43A047")
        self.plot_feature(self.times, self.zcr, "Zero Crossing Rate (ZCR)",
                          "ZCR to liczba przejść sygnału przez zero – miara przydatna w wykrywaniu bezdźwięcznych fragmentów mowy.",
                          row=2, color="#FDD835")
        self.plot_feature(self.times, self.sr, "Silent Ratio (SR)",
                          "SR klasyfikuje ramkę jako ciszę, gdy zarówno volume, jak i ZCR są poniżej ustalonych progów.",
                          row=3, color="#E53935")
        self.plot_feature(self.times, self.f0, "Fundamental Frequency (F0)",
                          "F0 to szacowana częstotliwość tonu podstawowego, wyznaczana metodą autokorelacji.", row=4,
                          color="#8E24AA")

    def frame_signal(self, data, fs, frame_size):
        total_samples = len(data)
        num_frames = int(np.ceil(total_samples / frame_size))
        frames = []
        times = []
        for i in range(num_frames):
            start = i * frame_size
            end = start + frame_size
            frame = data[start:end]
            if len(frame) < frame_size:
                frame = np.pad(frame, (0, frame_size - len(frame)), mode='constant')
            frames.append(frame)
            times.append(start / fs)
        return frames, np.array(times)

    def plot_feature(self, times, feature, title, description, row, color):
        # Ustawiamy wykres na całą szerokość (szerokość w pixelach dobieramy dynamicznie – przykładowo 1100px)
        fig = plt.Figure(figsize=(12, 3), dpi=80)
        ax = fig.add_subplot(111)
        ax.plot(times, feature, color=color, linewidth=1.5)
        ax.set_title(title, fontsize=12)
        ax.set_xlabel("Czas [s]", fontsize=10)
        ax.set_ylabel(title, fontsize=10)
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=row * 2, column=0, padx=10, pady=5, sticky="nsew")

        # Etykieta z opisem cechy
        label = tk.Label(self.scrollable_frame, text=description, font=("Helvetica", 10), bg="#ffffff", wraplength=1100,
                         justify="left")
        label.grid(row=row * 2 + 1, column=0, padx=10, pady=(0, 10), sticky="w")
