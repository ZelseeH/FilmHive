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
    USE_SNOWBALL_STEMMER,
    STEMMER_LANGUAGE,
)


class TFIDFProcessor:
    """
    TF-IDF processor dla opisów filmów

    Features:
    - Custom Polish stemming (suffixes removal)
    - Polish stopwords
    - Bigrams support (1,2)
    - Sublinear TF scaling: 1 + log(tf)
    - L2 normalization

    Based on Pazzani & Billsus (2007) - Wzór 5: normalized tf*idf
    """

    def __init__(
        self,
        use_snowball: bool = USE_SNOWBALL_STEMMER,
        language: str = STEMMER_LANGUAGE,
    ):
        """
        Args:
            use_snowball: Czy używać Snowball stemmer (dla polish: custom stemmer)
            language: Język ('polish' / 'english')
        """
        self.vectorizer = None
        self.feature_names = None
        self.language = language
        self.use_snowball = use_snowball
        self.logger = logging.getLogger(__name__)

        if language == "polish":
            try:
                nltk.data.find("tokenizers/punkt_tab/polish")
                self.logger.info("NLTK punkt_tab polish found")
            except LookupError:
                self.logger.info("Downloading NLTK punkt_tab for Polish...")
                nltk.download("punkt_tab", quiet=True)

        if use_snowball and language == "polish":
            self.logger.warning(
                "SnowballStemmer doesn't support Polish - using custom stemmer"
            )
            self.stemmer = None
        elif use_snowball and language == "english":
            try:
                from nltk.stem.snowball import SnowballStemmer

                self.stemmer = SnowballStemmer("english")
                self.logger.info("Using SnowballStemmer for English")
            except Exception as e:
                self.logger.warning(
                    f"SnowballStemmer init failed: {e} - fallback to no stemming"
                )
                self.stemmer = None
        else:
            self.stemmer = None

        self.logger.info(
            f"TFIDFProcessor initialized: language={language}, "
            f"use_snowball={use_snowball}, stemmer={'custom' if self.stemmer is None else 'snowball'}"
        )

    def preprocess_text(self, text: str) -> str:
        """
        Text preprocessing pipeline:
        1. Lowercase
        2. Remove punctuation (Unicode-safe)
        3. Remove digits
        4. Stemming (custom Polish or Snowball)
        5. Remove short words (<3 chars)

        Args:
            text: Raw text (film description)

        Returns:
            Preprocessed text (space-separated stems)
        """
        if not isinstance(text, str) or not text.strip():
            return ""

        text = text.lower()

        text = re.sub(r"[^\w\sąćęłńóśźżĄĆĘŁŃÓŚŹŻ]", " ", text, flags=re.UNICODE)

        text = re.sub(r"\d+", " ", text)

        text = re.sub(r"\s+", " ", text).strip()

        # 5. Stemming
        words = text.split()
        stemmed_words = []

        for word in words:
            if len(word) <= 2:
                continue

            if self.stemmer:
                stemmed_word = self.stemmer.stem(word)
            elif self.language == "polish":
                stemmed_word = self._simple_polish_stemming(word)
            else:
                stemmed_word = word

            stemmed_words.append(stemmed_word)

        return " ".join(stemmed_words)

    def _simple_polish_stemming(self, word: str) -> str:
        """
        Custom Polish stemmer (suffix stripping)

        Based on common Polish suffixes:
        - Verb endings: -ować, -ywać, -iwać
        - Noun endings: -ość, -nik, -acz, -arz
        - Adjective endings: -owy, -ny, -ski
        - Case endings: -ami, -ach, -ów, -ego

        Example:
        "technologia" → "technolog"
        "wchodzenie" → "wchodz"
        "śpiącego" → "śpi"
        """
        polish_suffixes = [
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
            "owski",
            "ewski",
            "owy",
            "owa",
            "owe",
            "ski",
            "ska",
            "skie",
            "ny",
            "na",
            "ne",
            "owie",
            "ami",
            "ach",
            "ów",
            "em",
            "om",
            "ego",
            "iej",
            "ie",
            "ą",
            "ę",
            "y",
            "a",
            "o",
            "e",
            "ić",
            "ać",
            "eć",
        ]

        for suffix in polish_suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                return word[: -len(suffix)]

        return word

    def fit_transform(self, documents: List[str]) -> np.ndarray:
        """
        Fit TF-IDF vectorizer and transform documents

        Implements Wzór 5 from thesis: normalized tf*idf
        - TF: sublinear (1 + log(freq)) if TFIDF_SUBLINEAR_TF=True
        - IDF: log(N / df) with smoothing
        - Normalization: L2 (Euclidean norm)

        Args:
            documents: List of raw text documents

        Returns:
            Sparse matrix (n_documents, n_features)
        """

        processed_docs = [self.preprocess_text(doc) for doc in documents]
        valid_docs = [doc for doc in processed_docs if doc.strip()]

        if not valid_docs:
            raise ValueError(
                "All documents are empty after preprocessing. "
                "Check if descriptions are valid."
            )

        self.logger.info(
            f"TF-IDF preprocessing: {len(valid_docs)}/{len(documents)} documents valid"
        )

        self.vectorizer = TfidfVectorizer(
            max_features=TFIDF_MAX_FEATURES,
            min_df=TFIDF_MIN_DF,
            max_df=TFIDF_MAX_DF,
            stop_words=self._get_stopwords(),
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
                f"TF-IDF matrix: shape={tfidf_matrix.shape}, "
                f"features={len(self.feature_names)}, "
                f"sparsity={1 - tfidf_matrix.nnz / (tfidf_matrix.shape[0] * tfidf_matrix.shape[1]):.3f}"
            )

            return tfidf_matrix

        except Exception as e:
            self.logger.error(f"TF-IDF fit_transform failed: {e}", exc_info=True)
            raise

    def transform(self, documents: List[str]) -> np.ndarray:
        """
        Transform new documents using fitted vectorizer

        Args:
            documents: List of raw text documents

        Returns:
            Sparse matrix (n_documents, n_features)
        """
        if self.vectorizer is None:
            raise ValueError("Vectorizer not fitted. Call fit_transform() first.")

        processed_docs = [self.preprocess_text(doc) for doc in documents]

        try:
            return self.vectorizer.transform(processed_docs)
        except Exception as e:
            self.logger.error(f"TF-IDF transform failed: {e}", exc_info=True)
            n_features = len(self.feature_names) if self.feature_names else 0
            return np.zeros((len(processed_docs), n_features))

    def get_feature_weights(
        self, document_index: int, tfidf_matrix: np.ndarray, top_n: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Get top N features (words) for a document by TF-IDF weight

        Useful for explainability (why this description is similar?)

        Args:
            document_index: Index of document in tfidf_matrix
            tfidf_matrix: TF-IDF matrix from fit_transform()
            top_n: Number of top features to return

        Returns:
            List[(feature_name, weight)] sorted by weight (descending)
        """
        if self.feature_names is None:
            raise ValueError("Vectorizer not fitted")

        try:
            doc_vector = tfidf_matrix[document_index].toarray()[0]

            word_weights = [
                (word, float(weight))
                for word, weight in zip(self.feature_names, doc_vector)
                if weight > 0
            ]

            word_weights.sort(key=lambda x: x[1], reverse=True)

            return word_weights[:top_n]

        except Exception as e:
            self.logger.error(f"get_feature_weights failed: {e}", exc_info=True)
            return []

    def get_document_similarity(
        self, tfidf_matrix: np.ndarray, doc_index1: int, doc_index2: int
    ) -> float:
        """
        Calculate cosine similarity between two documents

        Args:
            tfidf_matrix: TF-IDF matrix
            doc_index1: Index of first document
            doc_index2: Index of second document

        Returns:
            Cosine similarity [0, 1]
        """
        try:
            from sklearn.metrics.pairwise import cosine_similarity

            similarity = cosine_similarity(
                tfidf_matrix[doc_index1], tfidf_matrix[doc_index2]
            )[0][0]

            return float(similarity)

        except Exception as e:
            self.logger.error(f"get_document_similarity failed: {e}", exc_info=True)
            return 0.0

    def _get_stopwords(self) -> List[str]:
        """
        Get language-specific stopwords

        Returns:
            List of stopwords
        """
        if self.language == "polish":
            return self._get_polish_stopwords()
        elif self.language == "english":
            return self._get_english_stopwords()
        else:
            self.logger.warning(f"Unknown language: {self.language}, no stopwords")
            return []

    def _get_polish_stopwords(self) -> List[str]:
        """
        Polish stopwords (common + film-specific)
        """
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
            "przez",
            "przy",
            "tu",
            "był",
            "była",
            "było",
            "byli",
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
            "thriller",
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
        ]

    def _get_english_stopwords(self) -> List[str]:
        """
        English stopwords (common + film-specific)
        """
        return [
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
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "should",
            "could",
            "may",
            "might",
            "must",
            "can",
            "this",
            "that",
            "these",
            "those",
            "film",
            "movie",
            "story",
            "plot",
            "drama",
            "comedy",
            "character",
            "characters",
            "main",
            "follows",
            "tells",
            "about",
            "shows",
            "depicts",
            "focuses",
            "tries",
            "during",
            "between",
            "together",
            "along",
            "soon",
            "now",
            "life",
            "world",
            "time",
            "place",
            "way",
            "part",
            "end",
            "beginning",
        ]

    def get_top_features_by_class(
        self,
        tfidf_matrix: np.ndarray,
        labels: List[str],
        class_name: str,
        top_n: int = 20,
    ) -> List[Tuple[str, float]]:
        """
        Get top N features for a specific class (e.g., "positive" / "negative")

        Useful for Naive Bayes explainability:
        - Which words are most indicative of positive reviews?
        - Which words are most indicative of negative reviews?

        Args:
            tfidf_matrix: TF-IDF matrix
            labels: List of class labels (same length as tfidf_matrix rows)
            class_name: Target class (e.g., "positive")
            top_n: Number of top features to return

        Returns:
            List[(feature_name, mean_weight)] sorted by mean weight
        """
        if self.feature_names is None:
            return []

        try:
            class_indices = [i for i, label in enumerate(labels) if label == class_name]

            if not class_indices:
                self.logger.warning(f"No documents found for class '{class_name}'")
                return []

            class_matrix = tfidf_matrix[class_indices]
            mean_weights = np.mean(class_matrix.toarray(), axis=0)

            feature_weights = [
                (feature, float(weight))
                for feature, weight in zip(self.feature_names, mean_weights)
                if weight > 0
            ]

            feature_weights.sort(key=lambda x: x[1], reverse=True)

            return feature_weights[:top_n]

        except Exception as e:
            self.logger.error(f"get_top_features_by_class failed: {e}", exc_info=True)
            return []

    def get_vectorizer_info(self) -> Dict:
        """
        Get info about fitted vectorizer (for debugging/logging)

        Returns:
            Dict with vectorizer parameters and statistics
        """
        if self.vectorizer is None:
            return {"error": "Vectorizer not fitted"}

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
                "stop_words_count": len(self._get_stopwords()),
                "language": self.language,
                "stemmer": (
                    "custom_polish"
                    if self.stemmer is None and self.language == "polish"
                    else ("snowball" if self.stemmer else "none")
                ),
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
            self.logger.error(f"get_vectorizer_info failed: {e}", exc_info=True)
            return {"error": str(e)}

    def save_vocabulary(self, filepath: str) -> None:
        """
        Save vocabulary to file (for inspection)

        Args:
            filepath: Output file path (e.g., "tfidf_vocabulary.txt")
        """
        if self.feature_names is None:
            raise ValueError("Vectorizer not fitted")

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                for i, feature in enumerate(self.feature_names):
                    idf = (
                        self.vectorizer.idf_[i]
                        if hasattr(self.vectorizer, "idf_")
                        else 0.0
                    )
                    f.write(f"{feature}\t{idf:.4f}\n")

            self.logger.info(f"Vocabulary saved to {filepath}")

        except Exception as e:
            self.logger.error(f"save_vocabulary failed: {e}", exc_info=True)
