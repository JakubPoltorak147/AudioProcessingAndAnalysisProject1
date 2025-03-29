# Aplikacja Audio — Analiza i Przetwarzanie Dźwięku

Niniejsze repozytorium zawiera aplikację napisaną w Pythonie, służącą do wczytywania, odtwarzania oraz podstawowej analizy sygnałów dźwiękowych w formacie `.wav`. Aplikacja zapewnia graficzny interfejs użytkownika (GUI) wykorzystujący bibliotekę **Tkinter**.

## 📂 Struktura projektu
```
AudioProcessingAndAnalysisProject1/
├── audio_files/
│   └── ... (opcjonalnie pliki .wav używane w projekcie)
├── files/
│   ├── main.py                 # Główny punkt startowy aplikacji
│   ├── audio_app.py            # Moduł z klasą AudioApp (GUI, odtwarzanie, wykres przebiegu)
│   ├── audio_processing.py     # Klasy do przetwarzania audio (np. detekcja ciszy, dźwięczności)
│   ├── design.py               # Klasy i funkcje definiujące styl, kolory w GUI
│   ├── features.py             # Funkcje obliczające cechy sygnału (RMS, ZCR, STE, F0, itp.)
│   ├── features_window.py      # Moduł z klasą FeaturesWindow do wyświetlania wykresów cech
├── AiPD_dokumentacja_Jakub_Poltorak.pdf  # Dokumentacja projektu
├── .gitignore
├── README.md                   # Niniejszy plik (informacje o uruchamianiu i strukturze)
└── requirements.txt            # Lista zależności (pip)

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
   - Fragmenty _ciszy_ (kolor pomarańczowo-różowy),  
   - Fragmenty _dźwięczne_ (kolor zielony) oraz _bezdźwięczne_ (kolor różowy).

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
   ```
2.  **Stworzenie i aktywacja wirtualnego środowiska (opcjonalnie, zalecane):**
   ```bash
   python -m venv .venv
   # Linux / macOS
   source .venv/bin/activate
   # Windows
   .venv\Scripts\activate
   ```

3. **Instalacja zależnych pakietów:**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Uruchamianie aplikacji
1. **Przejdź do folderu z plikiem `main.py`:**
   ```bash
   cd files
   ```
2. **Uruchom aplikację:**
   ```bash
   python main.py
   ```

# Aplikacja GUI

Po uruchomieniu aplikacji pojawi się główne okno GUI, w którym można:

- **Wczytać plik WAV** (przycisk: "Wczytaj plik WAV")
- **Odtwarzać, pauzować i zatrzymywać dźwięk**
- **Analizować cechy sygnału** (przycisk: "Wykresy cech")
- **Zamknąć aplikację**

---

## 📑 Dokumentacja

Plik `AiPD_dokumentacja_Jakub_Poltorak.pdf` zawiera rozszerzoną dokumentację opisującą szczegółowo:

- Architekturę aplikacji
- Opis poszczególnych modułów i funkcji
- Przykłady użycia i analizy

---

## 🤝 Wkład

Projekt opracowany przez **JakubPoltorak147**.  
Wszelkie uwagi, sugestie i poprawki mile widziane w formie Issues lub Pull Requests.

Miłej pracy! 🚀

