import numpy as np

class BaseAudioProcessor:
    """
    Klasa bazowa z podstawową metodą do detekcji ciszy.
    """
    def detect_silence(self, data, fs, frame_size, silence_threshold):
        """
        Zwraca listę krotek (start_idx, end_idx) z przedziałami zdetekowanej ciszy.
        """
        total_samples = len(data)
        frame_step = frame_size
        silence_regions = []
        in_silence = False
        start_silence = 0
        for i in range(0, total_samples, frame_step):
            frame = data[i:i+frame_step]
            if len(frame) == 0:
                continue
            rms = np.sqrt(np.mean(frame**2))
            if rms < silence_threshold:
                if not in_silence:
                    in_silence = True
                    start_silence = i
            else:
                if in_silence:
                    silence_regions.append((start_silence, i))
                    in_silence = False
        if in_silence:
            silence_regions.append((start_silence, total_samples))
        return silence_regions


class VoicedAudioProcessor(BaseAudioProcessor):
    """
    Klasa rozszerzona o detekcję fragmentów dźwięcznych / bezdźwięcznych.
    Dla uproszczenia przyjmujemy:
    - RMS > vol_threshold => potencjalnie dźwięczny
    - Zero Crossing Rate < zcr_threshold => potwierdzenie dźwięczności
    itp.
    """
    def detect_voiced_unvoiced(self, data, fs, frame_size, vol_threshold=0.02, zcr_threshold=0.3):
        """
        Zwraca listę krotek (start_idx, end_idx, is_voiced)
        - is_voiced = True, jeśli fragment dźwięczny
        - is_voiced = False, jeśli bezdźwięczny
        """
        total_samples = len(data)
        frame_step = frame_size
        results = []
        # Będziemy spinać w ciągi: dźwięczny/dźwięczny/dźwięczny... i tak dalej
        current_state = None
        start_idx = 0

        for i in range(0, total_samples, frame_step):
            frame = data[i:i+frame_step]
            if len(frame) == 0:
                continue
            rms = np.sqrt(np.mean(frame**2))
            zero_crosses = np.count_nonzero(np.diff(np.sign(frame)))
            zcr = zero_crosses / len(frame) if len(frame) != 0 else 0

            # Prosty warunek: wystarczająco głośno i zcr < próg => dźwięczny
            is_voiced = (rms > vol_threshold and zcr < zcr_threshold)

            if current_state is None:
                # Pierwszy fragment
                current_state = is_voiced
                start_idx = i
            elif is_voiced != current_state:
                # Zmiana stanu z dźwięczny->bezdźwięczny lub odwrotnie
                results.append((start_idx, i, current_state))
                current_state = is_voiced
                start_idx = i

        # Ostatni fragment
        if current_state is not None:
            results.append((start_idx, total_samples, current_state))

        return results
