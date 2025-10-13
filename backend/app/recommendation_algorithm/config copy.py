# Minimalne wymagania użytkownika
MIN_USER_RATINGS = 5

# Liczba rekomendacji do zwrócenia
NUM_RECOMMENDATIONS = 20  # Całkowita liczba; suma top-K z algorytmów

# Progi ocen
POSITIVE_RATING_THRESHOLD = 7.0  # oceny 7+ traktowane jako pozytywne
NEGATIVE_RATING_THRESHOLD = 4.0  # oceny poniżej 4 jako negatywne

# Parametry dla k-NN
KNN_NEIGHBORS = 10
KNN_METRIC = "cosine"
DIRECTOR_BONUS = 0.8  # Bonus za match reżysera w hybrydowym podobieństwie
DEFAULT_RATING = 3.0  # Domyślna ocena przy braku podobieństw
MIN_SIMILARITY_THRESHOLD = 0.1  # Minimalne podobieństwo dla bonusu reżysera
KNN_TOP_K = 7  # Liczba top rekomendacji z KNN (strukturalne)

# Parametry dla TF-IDF
TFIDF_MAX_FEATURES = 5000
TFIDF_MIN_DF = 2  # słowo musi wystąpić w co najmniej 2 dokumentach
TFIDF_MAX_DF = 0.8  # słowo nie może wystąpić w więcej niż 80% dokumentów
TFIDF_NGRAM_RANGE = (1, 2)  # Zakres n-gramów (unigramy i bigramy)
TFIDF_SUBLINEAR_TF = True  # Sublinear scaling dla tf (zmniejsza wpływ częstych słów)

# Parametry dla Naive Bayes
NB_ALPHA = 1.0  # Parametr wygładzania Laplace'a
NB_MODEL_TYPE = "multinomial"  # Domyślny model NB (multinomialny lub bernoulli)
NB_TOP_K = 3  # Liczba top rekomendacji z NB (tekstowe)

# Wagi dla kombinowania algorytmów (używane tylko jeśli wrócimy do weighted sum)
STRUCTURAL_WEIGHT = 0.7  # waga dla k-NN (dane strukturalne)
TEXTUAL_WEIGHT = 0.3  # waga dla Naive Bayes (opisy)

# Parametry algorytmu Rocchio (na przyszłość)
ROCCHIO_ALPHA = 1.0  # waga dotychczasowego profilu
ROCCHIO_BETA = 0.75  # waga dokumentów istotnych
ROCCHIO_GAMMA = 0.15  # waga dokumentów nieistotnych

# Parametry dla klasyfikatorów liniowych (na przyszłość, z teorii)
ETA = 0.01  # Współczynnik uczenia dla Widrow-Hoffa
SVM_C = 1.0  # Parametr regularyzacji dla SVM

# Parametry hybrydy i ogólne
HYBRID_THRESHOLD = 0.5  # Próg decyzyjny dla predykcji (np. P(positive) > 0.5)
COLD_START_STRATEGY = "popular"  # Strategia dla cold start (np. polecaj popularne)
MAX_CANDIDATES = 100  # Maksymalna liczba kandydatów do predykcji (efektywność)
LOG_LEVEL = "INFO"  # Poziom loggingu (DEBUG, INFO, WARNING, ERROR)

# Parametry bazy danych
BATCH_SIZE = 1000  # rozmiar batcha przy przetwarzaniu dużych zbiorów
RECENT_RATINGS_LIMIT = 10  # Liczba ostatnich ocen do analizy

# Parametry adaptacyjne (dla wag wzorców użytkownika w DataPreprocessor i SimilarityMetrics)
ADAPTIVE_BASE_WEIGHT = (
    0.1  # Minimalna waga bazowa dla każdej kategorii (genres/actors/directors)
)
ADAPTIVE_SCALING_FACTOR = 0.7  # Skalowanie siły wzorców (max powtórzeń w high ratings)
ADAPTIVE_GENRE_WEIGHT = 0.25  # Fallback waga dla gatunków
ADAPTIVE_ACTOR_WEIGHT = 0.40  # Fallback waga dla aktorów
ADAPTIVE_DIRECTOR_WEIGHT = 0.35  # Fallback waga dla reżyserów (bonus dla patterns)
ADAPTIVE_BASE_GENRE_WEIGHT = 0.3  # Bazowa waga dla adaptive movie sim (genres)
ADAPTIVE_BASE_ACTOR_WEIGHT = 0.3  # Bazowa waga dla adaptive movie sim (actors)
ADAPTIVE_BASE_DIRECTOR_WEIGHT = 0.25  # Bazowa waga dla adaptive movie sim (directors)

# Parametry similarity (dla metryk w SimilarityMetrics, sekcja 3.1 teorii)
ENSEMBLE_KNN_WEIGHT = (
    0.6  # Waga KNN w hybrydzie (strukturalne; blisko STRUCTURAL_WEIGHT)
)
ENSEMBLE_NB_WEIGHT = 0.4  # Waga NB w hybrydzie (tekstowe; blisko TEXTUAL_WEIGHT)
YEAR_MAX_DIFF = (
    20  # Maks różnica lat dla normalizacji year similarity (np. 1 - diff/20)
)
DURATION_MAX_DIFF = 180  # Maks różnica minut dla duration similarity (np. 1 - diff/180)
ACTOR_BONUS = 0.05  # Bonus za match aktora w adaptive cosine (mniejszy niż director)
TOP_ACTORS_IN_PATTERN = (
    3  # Liczba top aktorów do liczenia w analyze_preference_patterns
)
TOP_ENTITIES = 50  # Top N actors/directors w prepare_structural_features (one-hot)
