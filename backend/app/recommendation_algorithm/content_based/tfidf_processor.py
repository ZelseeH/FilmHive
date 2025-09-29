from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np
import re
from typing import List, Dict, Tuple, Optional
import logging

from ..config import TFIDF_MAX_FEATURES, TFIDF_MIN_DF, TFIDF_MAX_DF


class TFIDFProcessor:
    def __init__(self):
        self.vectorizer = None
        self.feature_names = None
        self.logger = logging.getLogger(__name__)

    def preprocess_text(self, text: str) -> str:
        """Preprocessing tekstu - stemming i normalizacja"""
        if not isinstance(text, str) or not text.strip():
            return ""

        # Konwersja do małych liter
        text = text.lower()

        # Lepsze czyszczenie znaków specjalnych - zachowaj polskie znaki
        text = re.sub(
            r"[^\w\s]", " ", text
        )  # Usuń znaki specjalne ale zachowaj Unicode

        # Usuń liczby (często nieistotne w opisach filmów)
        text = re.sub(r"\d+", " ", text)

        # Usunięcie nadmiarowych spacji
        text = re.sub(r"\s+", " ", text).strip()

        # Podstawowy stemming dla języka polskiego
        text = self._simple_polish_stemming(text)

        return text

    def _simple_polish_stemming(self, text: str) -> str:
        """Ulepszone stemming dla języka polskiego"""
        words = text.split()
        stemmed_words = []

        # Rozszerzone reguły stemmingu dla polskiego (posortowane od najdłuższych)
        polish_endings = [
            "owanie",
            "anie",
            "enie",
            "owanie",
            "iwanie",
            "ywanie",  # Gerund
            "ności",
            "ość",
            "ość",
            "nik",
            "acz",
            "arz",
            "arz",  # Nouns
            "acji",
            "cji",
            "owy",
            "owa",
            "owe",
            "ny",
            "na",
            "ne",  # Adjectives
            "owie",
            "ami",
            "ach",
            "em",
            "ie",
            "ów",
            "y",
            "a",
            "ę",
            "ą",
            "o",
            "e",  # Cases
        ]

        for word in words:
            if len(word) <= 3:  # Krótkie słowa zostawiamy bez zmian
                stemmed_words.append(word)
                continue

            stemmed_word = word
            # Próbuj od najdłuższych końcówek
            for ending in sorted(polish_endings, key=len, reverse=True):
                if word.endswith(ending) and len(word) > len(ending) + 2:
                    stemmed_word = word[: -len(ending)]
                    break

            stemmed_words.append(stemmed_word)

        return " ".join(stemmed_words)

    def fit_transform(self, documents: List[str]) -> np.ndarray:
        """Trenuje TF-IDF vectorizer i transformuje dokumenty"""
        # Preprocessing wszystkich dokumentów
        processed_docs = [self.preprocess_text(doc) for doc in documents]

        # Usuń puste dokumenty i zachowaj mapowanie
        valid_docs = []
        for i, doc in enumerate(processed_docs):
            if doc.strip():
                valid_docs.append(doc)

        if not valid_docs:
            raise ValueError("Brak dokumentów do przetworzenia po preprocessing")

        self.logger.info(
            f"TF-IDF: Przetwarzam {len(valid_docs)} dokumentów z {len(documents)} oryginalnych"
        )

        # Inicjalizuj i trenuj vectorizer z lepszymi parametrami
        self.vectorizer = TfidfVectorizer(
            max_features=TFIDF_MAX_FEATURES,
            min_df=TFIDF_MIN_DF,
            max_df=TFIDF_MAX_DF,
            stop_words=self._get_polish_stopwords(),
            ngram_range=(1, 2),  # Unigramy i bigramy
            lowercase=False,  # Już zrobione w preprocessing
            sublinear_tf=True,  # Zmniejsza wpływ bardzo częstych słów
            norm="l2",  # L2 normalization
            smooth_idf=True,  # Smooth IDF weights
        )

        # Transform dokumentów
        try:
            tfidf_matrix = self.vectorizer.fit_transform(valid_docs)
            self.feature_names = self.vectorizer.get_feature_names_out()

            self.logger.info(
                f"TF-IDF: Utworzono macierz {tfidf_matrix.shape} z {len(self.feature_names)} cechami"
            )
            return tfidf_matrix

        except Exception as e:
            self.logger.error(f"Błąd podczas TF-IDF fit_transform: {e}")
            raise

    def transform(self, documents: List[str]) -> np.ndarray:
        """Transformuje nowe dokumenty używając wytrenowanego vectorizera"""
        if self.vectorizer is None:
            raise ValueError(
                "Vectorizer nie został wytrenowany. Użyj najpierw fit_transform()"
            )

        # Preprocessing dokumentów
        processed_docs = [self.preprocess_text(doc) for doc in documents]

        try:
            return self.vectorizer.transform(processed_docs)
        except Exception as e:
            self.logger.error(f"Błąd podczas TF-IDF transform: {e}")
            # Fallback - zwróć macierz zer
            return np.zeros((len(processed_docs), len(self.feature_names)))

    def get_feature_weights(
        self, document_index: int, tfidf_matrix: np.ndarray, top_n: int = 10
    ) -> List[Tuple[str, float]]:
        """Pobiera top N słów z najwyższymi wagami TF-IDF dla dokumentu"""
        if self.feature_names is None:
            raise ValueError("Brak nazw cech. Użyj najpierw fit_transform()")

        try:
            # Pobierz wektor dla dokumentu
            doc_vector = tfidf_matrix[document_index].toarray()[0]

            # Utwórz pary (słowo, waga) i posortuj
            word_weights = list(zip(self.feature_names, doc_vector))
            word_weights = [
                (word, weight) for word, weight in word_weights if weight > 0
            ]
            word_weights.sort(key=lambda x: x[1], reverse=True)

            return word_weights[:top_n]
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania feature weights: {e}")
            return []

    def get_document_similarity(
        self, tfidf_matrix: np.ndarray, doc_index1: int, doc_index2: int
    ) -> float:
        """Oblicza podobieństwo kosinusowe między dwoma dokumentami"""
        try:
            from sklearn.metrics.pairwise import cosine_similarity

            doc1_vector = tfidf_matrix[doc_index1]
            doc2_vector = tfidf_matrix[doc_index2]

            similarity = cosine_similarity(doc1_vector, doc2_vector)[0][0]
            return similarity
        except Exception as e:
            self.logger.error(f"Błąd podczas obliczania podobieństwa: {e}")
            return 0.0

    def _get_polish_stopwords(self) -> List[str]:
        """Zwraca rozszerzoną listę polskich stop words dla filmów"""
        return [
            # Podstawowe polskie stop words
            "a",
            "aby",
            "ale",
            "am",
            "ani",
            "być",
            "ci",
            "co",
            "czy",
            "dla",
            "do",
            "go",
            "i",
            "ich",
            "ja",
            "jak",
            "jako",
            "je",
            "jego",
            "jej",
            "już",
            "ma",
            "może",
            "na",
            "nad",
            "nie",
            "o",
            "od",
            "po",
            "pod",
            "są",
            "się",
            "tak",
            "te",
            "to",
            "w",
            "we",
            "więc",
            "z",
            "za",
            "że",
            "albo",
            "bardzo",
            "bez",
            "bo",
            "gdy",
            "gdzie",
            "oraz",
            "także",
            "tylko",
            "lub",
            "jeden",
            "jedna",
            "jedno",
            # Filmowe stop words (często pojawiają się ale nie niosą znaczenia)
            "film",
            "filmy",
            "filmu",
            "filmie",
            "filmów",
            "filmach",
            "historia",
            "opowieść",
            "fabuła",
            "akcja",
            "dramat",
            "komedia",
            "główny",
            "główna",
            "główne",
            "bohater",
            "bohaterka",
            "bohaterowie",
            "opowiada",
            "przedstawia",
            "pokazuje",
            "koncentruje",
            "próbuje",
            "podczas",
            "między",
            "razem",
            "wraz",
            "wkrótce",
            "właśnie",
            "teraz",
            "życie",
            "świat",
            "czas",
            "miejsce",
            "sposób",
            "część",
            "koniec",
            "początek",
            # Częste angielskie słowa które mogą się pojawić
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
        ]

    def get_top_features_by_class(
        self,
        tfidf_matrix: np.ndarray,
        labels: List[str],
        class_name: str,
        top_n: int = 20,
    ) -> List[Tuple[str, float]]:
        """Zwraca najważniejsze cechy dla danej klasy (pozytywne/negatywne)"""
        if self.feature_names is None:
            return []

        try:
            # Znajdź dokumenty należące do danej klasy
            class_indices = [i for i, label in enumerate(labels) if label == class_name]

            if not class_indices:
                return []

            # Oblicz średnie wagi TF-IDF dla klasy
            class_matrix = tfidf_matrix[class_indices]
            mean_weights = np.mean(class_matrix.toarray(), axis=0)

            # Utwórz pary (cecha, waga)
            feature_weights = list(zip(self.feature_names, mean_weights))
            feature_weights = [
                (feat, weight) for feat, weight in feature_weights if weight > 0
            ]
            feature_weights.sort(key=lambda x: x[1], reverse=True)

            return feature_weights[:top_n]

        except Exception as e:
            self.logger.error(f"Błąd podczas analizy cech klasy: {e}")
            return []

    def get_vectorizer_info(self) -> Dict:
        """Zwraca rozszerzone informacje o wytrenowanym vectorizerze"""
        if self.vectorizer is None:
            return {"error": "Vectorizer nie został wytrenowany"}

        try:
            info = {
                "vocabulary_size": len(self.vectorizer.vocabulary_),
                "feature_count": (
                    len(self.feature_names) if self.feature_names is not None else 0
                ),
                "max_features": TFIDF_MAX_FEATURES,
                "min_df": TFIDF_MIN_DF,
                "max_df": TFIDF_MAX_DF,
                "ngram_range": self.vectorizer.ngram_range,
                "sublinear_tf": self.vectorizer.sublinear_tf,
                "norm": self.vectorizer.norm,
                "stop_words_count": len(self._get_polish_stopwords()),
            }

            # Dodaj statystyki IDF jeśli dostępne
            if hasattr(self.vectorizer, "idf_"):
                info.update(
                    {
                        "min_idf": float(np.min(self.vectorizer.idf_)),
                        "max_idf": float(np.max(self.vectorizer.idf_)),
                        "mean_idf": float(np.mean(self.vectorizer.idf_)),
                    }
                )

            return info

        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania info vectorizera: {e}")
            return {"error": str(e)}
