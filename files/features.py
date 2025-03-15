# features.py
import numpy as np

def compute_volume(frame):
    """Volume – pierwiastek średniej energii sygnału w ramce."""
    return np.sqrt(np.mean(frame**2))

def compute_ste(frame):
    """Short Time Energy (STE) – suma kwadratów wartości sygnału w ramce, podzielona przez długość ramki."""
    return np.sum(frame**2) / len(frame)

def compute_zcr(frame):
    """Zero Crossing Rate (ZCR) – liczba przejść sygnału przez zero, znormalizowana przez długość ramki."""
    zero_crossings = np.count_nonzero(np.diff(np.sign(frame)))
    return zero_crossings / len(frame)

def compute_sr(frame, vol_threshold=0.01, zcr_threshold=0.1):
    """
    Silent Ratio (SR) – ramka jest klasyfikowana jako cisza, jeśli zarówno volume jak i ZCR
    są poniżej zadanych progów. Zwraca 1 (cisza) lub 0.
    """
    vol = compute_volume(frame)
    zcr = compute_zcr(frame)
    return 1 if (vol < vol_threshold and zcr < zcr_threshold) else 0

def compute_f0(frame, fs, fmin=50, fmax=500):
    """
    Fundamental Frequency (F0) – estymacja częstotliwości tonu podstawowego przy użyciu autokorelacji.
    Zwraca F0 w Hz lub 0, jeśli nie znaleziono wyraźnego piku.
    """
    frame = frame - np.mean(frame)
    corr = np.correlate(frame, frame, mode='full')
    corr = corr[len(corr)//2:]
    d = np.diff(corr)
    start = np.nonzero(d > 0)[0]
    if len(start) == 0:
        return 0
    lag = start[0]
    f0 = fs / lag if lag != 0 else 0
    if f0 < fmin or f0 > fmax:
        return 0
    return f0
