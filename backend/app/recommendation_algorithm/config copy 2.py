# Minimalne wymagania użytkownika
MIN_USER_RATINGS = 5

# Liczba rekomendacji do zwrócenia
NUM_RECOMMENDATIONS = 20

# Progi ocen
POSITIVE_RATING_THRESHOLD = 7.0  # oceny 7+ traktowane jako pozytywne
NEGATIVE_RATING_THRESHOLD = 4.0  # oceny poniżej 4 jako negatywne

# Parametry dla k-NN
KNN_NEIGHBORS = 10
KNN_METRIC = "cosine"

# Parametry dla TF-IDF
TFIDF_MAX_FEATURES = 5000
TFIDF_MIN_DF = 2  # słowo musi wystąpić w co najmniej 2 dokumentach
TFIDF_MAX_DF = 0.8  # słowo nie może wystąpić w więcej niż 80% dokumentów

# Wagi dla kombinowania algorytmów
STRUCTURAL_WEIGHT = 0.7  # waga dla k-NN (dane strukturalne)
TEXTUAL_WEIGHT = 0.3  # waga dla Naive Bayes (opisy)

# Parametry algorytmu Rocchio (na przyszłość)
ROCCHIO_ALPHA = 1.0  # waga dotychczasowego profilu
ROCCHIO_BETA = 0.75  # waga dokumentów istotnych
ROCCHIO_GAMMA = 0.15  # waga dokumentów nieistotnych

# Parametry bazy danych
BATCH_SIZE = 1000  # rozmiar batcha przy przetwarzaniu dużych zbiorów

RECENT_RATINGS_LIMIT = 20  # Liczba ostatnich ocen do analizy
