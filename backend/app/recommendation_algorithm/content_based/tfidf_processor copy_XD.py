from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np
import re
from typing import List, Dict, Tuple, Optional
import logging
import nltk


from ..config import (
    TFIDF_MAX_FEATURES,
    TFIDF_MIN_DF,
    TFIDF_MAX_DF,
    TFIDF_NGRAM_RANGE,
    TFIDF_SUBLINEAR_TF,
)


class TFIDFProcessor:
    def __init__(self, use_snowball: bool = False):
        self.vectorizer = None
        self.feature_names = None
        self.logger = logging.getLogger(__name__)

        try:
            nltk.data.find("tokenizers/punkt_tab/polish")
            self.logger.info("NLTK punkt_tab polish found")
        except LookupError:
            self.logger.info("Downloading NLTK punkt_tab...")
            nltk.download("punkt_tab", quiet=True)

        if use_snowball:
            self.logger.warning(
                "SnowballStemmer nie wspiera języka 'polish' - używam custom stemmera"
            )

        self.stemmer = None
        self.logger.info("Używam custom polish stemmera (_simple_polish_stemming)")

    def preprocess_text(self, text: str) -> str:
        """Preprocessing tekstu - stemming i normalizacja (Unicode-safe dla PL/EN)"""
        if not isinstance(text, str) or not text.strip():
            return ""

        text = text.lower()

        text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)

        text = re.sub(r"\d+", " ", text)

        text = re.sub(r"\s+", " ", text).strip()

        words = text.split()
        stemmed_words = []
        for word in words:
            if len(word) <= 2:
                stemmed_words.append(word)
                continue
            stemmed_word = self._simple_polish_stemming(word)
            stemmed_words.append(stemmed_word)

        return " ".join(stemmed_words)

    def _simple_polish_stemming(self, word: str) -> str:
        """Custom stemming dla polskiego (ulepszone endings)"""
        polish_endings = [
            "owanie",
            "iwanie",
            "ywanie",
            "ności",
            "ość",
            "acja",
            "cja",
            "enie",
            "anie",
            "nik",
            "acz",
            "arz",
            "owy",
            "owa",
            "owe",
            "ny",
            "na",
            "ne",
            "owie",
            "ami",
            "ach",
            "em",
            "ie",
            "ów",
            "ego",
            "y",
            "a",
            "ę",
            "ą",
            "o",
            "e",
            "ić",
            "ia",
        ]
        for ending in sorted(polish_endings, key=len, reverse=True):
            if word.endswith(ending) and len(word) > len(ending) + 2:
                return word[: -len(ending)]
        return word

    def fit_transform(self, documents: List[str]) -> np.ndarray:
        """Trenuje TF-IDF (wzór 5: tf*idf z normalizacją)"""
        processed_docs = [self.preprocess_text(doc) for doc in documents]

        # Filtruj puste
        valid_docs = [doc for doc in processed_docs if doc.strip()]
        if not valid_docs:
            raise ValueError("Brak dokumentów po preprocessing")

        self.logger.info(f"TF-IDF: {len(valid_docs)}/{len(documents)} docs gotowe")

        self.vectorizer = TfidfVectorizer(
            max_features=TFIDF_MAX_FEATURES,
            min_df=TFIDF_MIN_DF,
            max_df=TFIDF_MAX_DF,
            stop_words=self._get_polish_stopwords(),
            ngram_range=TFIDF_NGRAM_RANGE,
            lowercase=False,
            sublinear_tf=TFIDF_SUBLINEAR_TF,
            norm="l2",
            smooth_idf=True,
            analyzer="word",
        )

        try:
            tfidf_matrix = self.vectorizer.fit_transform(valid_docs)
            self.feature_names = self.vectorizer.get_feature_names_out()
            self.logger.info(
                f"TF-IDF matrix: {tfidf_matrix.shape}, {len(self.feature_names)} features"
            )
            return tfidf_matrix
        except Exception as e:
            self.logger.error(f"TF-IDF fit_transform error: {e}")
            raise

    def transform(self, documents: List[str]) -> np.ndarray:
        """Transform nowych docs"""
        if self.vectorizer is None:
            raise ValueError("Fit najpierw fit_transform")
        processed_docs = [self.preprocess_text(doc) for doc in documents]
        try:
            return self.vectorizer.transform(processed_docs)
        except Exception as e:
            self.logger.error(f"TF-IDF transform error: {e}")
            return np.zeros((len(processed_docs), len(self.feature_names)))  # Fallback

    def get_feature_weights(
        self, document_index: int, tfidf_matrix: np.ndarray, top_n: int = 10
    ) -> List[Tuple[str, float]]:
        if self.feature_names is None:
            raise ValueError("Fit najpierw")
        try:
            doc_vector = tfidf_matrix[document_index].toarray()[0]
            word_weights = [
                (w, float(v)) for w, v in zip(self.feature_names, doc_vector) if v > 0
            ]
            word_weights.sort(key=lambda x: x[1], reverse=True)
            return word_weights[:top_n]
        except Exception as e:
            self.logger.error(f"Feature weights error: {e}")
            return []

    def get_document_similarity(
        self, tfidf_matrix: np.ndarray, doc_index1: int, doc_index2: int
    ) -> float:
        try:
            from sklearn.metrics.pairwise import cosine_similarity

            return cosine_similarity(
                tfidf_matrix[doc_index1], tfidf_matrix[doc_index2]
            )[0][0]
        except Exception as e:
            self.logger.error(f"Similarity error: {e}")
            return 0.0

    def _get_polish_stopwords(self) -> List[str]:
        return [
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
        if self.feature_names is None:
            return []
        try:
            class_indices = [i for i, label in enumerate(labels) if label == class_name]
            if not class_indices:
                return []
            class_matrix = tfidf_matrix[class_indices]
            mean_weights = np.mean(class_matrix.toarray(), axis=0)
            feature_weights = [
                (f, float(w)) for f, w in zip(self.feature_names, mean_weights) if w > 0
            ]
            feature_weights.sort(key=lambda x: x[1], reverse=True)
            return feature_weights[:top_n]
        except Exception as e:
            self.logger.error(f"Top features error: {e}")
            return []

    def get_vectorizer_info(self) -> Dict:
        if self.vectorizer is None:
            return {"error": "Nie wytrenowany"}
        try:
            info = {
                "vocabulary_size": len(self.vectorizer.vocabulary_),
                "feature_count": len(self.feature_names) if self.feature_names else 0,
                "max_features": TFIDF_MAX_FEATURES,
                "min_df": TFIDF_MIN_DF,
                "max_df": TFIDF_MAX_DF,
                "ngram_range": TFIDF_NGRAM_RANGE,
                "sublinear_tf": TFIDF_SUBLINEAR_TF,
                "norm": self.vectorizer.norm,
                "stop_words_count": len(self._get_polish_stopwords()),
                "stemmer": "Custom Polish Stemmer",
            }
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
            self.logger.error(f"Vectorizer info error: {e}")
            return {"error": str(e)}
