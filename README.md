# Aplikacja Audio — Przetwarzanie i Analiza Dźwięku

Niniejsze repozytorium zawiera aplikację napisaną w Pythonie, służącą do wczytywania, odtwarzania oraz podstawowej analizy sygnałów dźwiękowych w formacie `.wav`. Aplikacja zapewnia graficzny interfejs użytkownika (GUI) wykorzystujący bibliotekę **Tkinter**.

## 📂 Struktura projektu
```
/AudioProcessingAndAnalysisProject1/
 │── audio_files/
 │   │── ... (opcjonalnie pliki .wav używane w projekcie)
 │── files/
 │   │── audio_app.py # Moduł z klasą AudioApp (GUI, odtwarzanie, wykres przebiegu)
 │   │── audio_processing.py  # Klasy do przetwarzania audio (np. detekcja ciszy, dźwięczności)
 │   │── design.py # Klasy i funkcje definiujące styl, kolory w GUI
 │   │── features.py # Funkcje obliczające cechy sygnału (RMS, ZCR, STE, F0, itp.)
 │   │── features_window.py # Moduł z klasą FeaturesWindow do wyświetlania wykresów cech
 │   │── main.py # Główny punkt startowy aplikacji
 │── .gitignore
 │── README.md
 │── requirements.txt
```

## 💡 Opis aplikacji

Aplikacja umożliwia:

1. **Wczytywanie pliku `.wav`:**  
   Użytkownik może wybrać dowolny plik dźwiękowy w formacie WAV z dysku.

2. **Odtwarzanie sygnału:**  
   Dostępne są przyciski **Odtwórz**, **Odtwórz od początku** oraz **Pauza/Wznów**.  
   Aplikacja wizualizuje aktualną pozycję w sygnale (pionowa linia na wykresie).

3. **Wizualizacja przebiegu:**  
   Na głównym wykresie przedstawiany jest czasowy przebieg amplitudy sygnału.  
   Opcjonalnie, można zaznaczać:
   - Fragmenty _ciszy_ (kolor żółty),  
   - Fragmenty _dźwięczne_ (kolor niebieski) oraz _bezdźwięczne_ (kolor różowy).

4. **Analiza cech sygnału (Wykresy cech):**  
   Aplikacja pozwala otworzyć dodatkowe okno (**Wykresy cech**) z wykresami:
   - Volume (RMS), STE, ZCR, SR (Silent Ratio), F0 (Autocorrelation), F0 (AMDF).  
   Istnieje możliwość wyboru, które cechy mają zostać narysowane.

5. **Parametry statystyczne:**  
   W górnym panelu wyświetlane są podstawowe statystyki *RMS* i *ZCR* obliczone w dziedzinie ramki.

Dodatkowo w folderze **audio_files** można umieścić własne pliki WAV do testowania.

## 🔧 Instalacja i konfiguracja

1. **Klonowanie repozytorium:**

   ```bash
   git clone https://github.com/JakubPoltorak147/AudioProcessingAndAnalysisProject1.git
   cd AudioProcessingAndAnalysisProject1
