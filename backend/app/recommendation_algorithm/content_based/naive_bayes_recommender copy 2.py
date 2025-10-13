from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import logging
import math

from ..config import POSITIVE_RATING_THRESHOLD, NEGATIVE_RATING_THRESHOLD
from .tfidf_processor import TFIDFProcessor


class NaiveBayesRecommender:
    """
    Implementacja Naive Bayes zgodnie z teorią Pazzaniego i Billsusa
    Wzory 8-12 z pracy inżynierskiej
    """

    def __init__(self, model_type: str = "multinomial"):
        self.model_type = model_type  # "multinomial" lub "bernoulli"
        self.model = None
        self.tfidf_processor = TFIDFProcessor()
        self.is_fitted = False
        self.class_labels = None
        self.class_priors = {}  # P(c) - wzór 8
        self.feature_likelihoods = {}  # P(w|c) - wzory 10, 12
        self.vocabulary_size = 0
        self.logger = logging.getLogger(__name__)

    def fit(self, user_ratings: pd.DataFrame) -> None:
        """Trenuje klasyfikator Naive Bayes zgodnie z teorią Pazzaniego i Billsusa"""
        if user_ratings.empty:
            raise ValueError("Brak danych do trenowania")

        descriptions, labels = self._prepare_training_data(user_ratings)

        if len(descriptions) == 0:
            raise ValueError("Brak danych treningowych po filtracji")

        # Sprawdź czy mamy obie klasy (jak w Syskill & Webert)
        unique_labels = set(labels)
        if len(unique_labels) < 2:
            self.logger.warning(f"Tylko jedna klasa w danych: {unique_labels}")
            # Dodaj sztuczną drugą klasę dla stabilności
            if "positive" not in unique_labels:
                descriptions.append("excellent great amazing wonderful")
                labels.append("positive")
            if "negative" not in unique_labels:
                descriptions.append("terrible awful bad horrible")
                labels.append("negative")

        # Tworzenie macierzy TF-IDF (reprezentacja wektorowa)
        tfidf_matrix = self.tfidf_processor.fit_transform(descriptions)
        self.vocabulary_size = len(self.tfidf_processor.feature_names)
        self.class_labels = list(set(labels))

        # Implementacja wzorów z pracy inżynierskiej
        if self.model_type == "multinomial":
            self._train_multinomial_nb(tfidf_matrix, labels)
        else:
            self._train_bernoulli_nb(tfidf_matrix, labels)

        self.is_fitted = True
        self.logger.info(
            f"Naive Bayes ({self.model_type}) wytrenowany na {len(descriptions)} opisach z klasami: {self.class_labels}"
        )

    def _train_multinomial_nb(self, X: np.ndarray, y: List[str]) -> None:
        """
        Model multinomialny - wzory 11, 12 z pracy inżynierskiej
        P(d|c) = ∏(P(w|c)^tf(w,d))
        """
        n_docs = len(y)

        # Oblicz P(c) - prior classes (wzór 8)
        for class_label in self.class_labels:
            class_count = y.count(class_label)
            self.class_priors[class_label] = class_count / n_docs

        # Oblicz P(w|c) dla każdej klasy (wzór 12)
        self.feature_likelihoods = {}

        for class_label in self.class_labels:
            class_indices = [i for i, label in enumerate(y) if label == class_label]
            class_docs = X[class_indices]

            # Suma wszystkich słów w klasie
            total_words_in_class = np.sum(class_docs)

            # P(w|c) = (count(w,c) + 1) / (total_words_in_class + |V|)
            # Laplace smoothing (α = 1)
            word_counts_in_class = np.sum(class_docs, axis=0)
            self.feature_likelihoods[class_label] = (word_counts_in_class + 1) / (
                total_words_in_class + self.vocabulary_size
            )

    def _train_bernoulli_nb(self, X: np.ndarray, y: List[str]) -> None:
        """
        Model Bernoulliego - wzory 9, 10 z pracy inżynierskiej
        P(d|c) = ∏(P(w|c)^x_w * (1-P(w|c))^(1-x_w))
        """
        n_docs = len(y)

        # Oblicz P(c) - prior classes
        for class_label in self.class_labels:
            class_count = y.count(class_label)
            self.class_priors[class_label] = class_count / n_docs

        # Konwertuj na binary (0/1) dla modelu Bernoulliego
        X_binary = (X > 0).astype(int)

        # Oblicz P(w|c) dla każdej klasy (wzór 10)
        self.feature_likelihoods = {}

        for class_label in self.class_labels:
            class_indices = [i for i, label in enumerate(y) if label == class_label]
            class_docs = X_binary[class_indices]
            n_class_docs = len(class_docs)

            # P(w|c) = (N_c(w) + 1) / (N_c + 2)
            # gdzie N_c(w) = liczba dokumentów klasy c zawierających słowo w
            word_presence_in_class = np.sum(class_docs, axis=0)
            self.feature_likelihoods[class_label] = (word_presence_in_class + 1) / (
                n_class_docs + 2
            )

    def predict_with_movie_ids(self, candidates_df: pd.DataFrame) -> Dict[int, float]:
        """Przewiduje preferencje używając reguły Bayesa (wzór 8)"""
        if not self.is_fitted:
            raise ValueError("Model nie został wytrenowany. Użyj najpierw fit()")

        if (
            "description" not in candidates_df.columns
            or "movie_id" not in candidates_df.columns
        ):
            raise ValueError(
                "DataFrame musi zawierać kolumny 'description' i 'movie_id'"
            )

        descriptions = candidates_df["description"].fillna("").tolist()
        movie_ids = candidates_df["movie_id"].tolist()

        if not descriptions:
            return {}

        predictions = {}

        try:
            candidate_tfidf = self.tfidf_processor.transform(descriptions)

            # Konwertuj na binary jeśli model Bernoulliego
            if self.model_type == "bernoulli":
                candidate_tfidf = (candidate_tfidf > 0).astype(int)

            for i, movie_id in enumerate(movie_ids):
                doc_vector = candidate_tfidf[i].toarray()[0]

                # Oblicz P(c|d) dla każdej klasy używając wzoru Bayesa
                class_probabilities = {}

                for class_label in self.class_labels:
                    # P(c|d) ∝ P(c) * P(d|c)
                    log_prob = math.log(self.class_priors[class_label])

                    # Oblicz P(d|c) zgodnie z modelem
                    for j, word_count in enumerate(doc_vector):
                        feature_prob = self.feature_likelihoods[class_label][j]

                        if self.model_type == "multinomial":
                            # P(d|c) = ∏(P(w|c)^tf(w,d))
                            if word_count > 0:
                                log_prob += word_count * math.log(feature_prob)
                        else:
                            # Model Bernoulliego
                            if word_count > 0:
                                log_prob += math.log(feature_prob)
                            else:
                                log_prob += math.log(1 - feature_prob)

                    class_probabilities[class_label] = log_prob

                # Normalizacja do prawdopodobieństw
                max_log_prob = max(class_probabilities.values())
                normalized_probs = {}
                total = 0

                for class_label in self.class_labels:
                    prob = math.exp(class_probabilities[class_label] - max_log_prob)
                    normalized_probs[class_label] = prob
                    total += prob

                # Normalizuj do sumy = 1
                for class_label in normalized_probs:
                    normalized_probs[class_label] /= total

                # Zwróć prawdopodobieństwo klasy pozytywnej
                positive_prob = normalized_probs.get("positive", 0.5)
                predictions[movie_id] = positive_prob

        except Exception as e:
            self.logger.error(f"Błąd w predykcji Naive Bayes: {e}")
            # Fallback
            for movie_id in movie_ids:
                predictions[movie_id] = 0.5

        return predictions

    def _prepare_training_data(
        self, user_ratings: pd.DataFrame
    ) -> Tuple[List[str], List[str]]:
        """Przygotowuje dane treningowe zgodnie z progami klasyfikacji"""
        descriptions = []
        labels = []

        for _, row in user_ratings.iterrows():
            description = str(row.get("description", ""))
            rating = row.get("rating", 0)

            if not description.strip():
                continue

            # Klasyfikacja binarna zgodnie z progami
            if rating >= POSITIVE_RATING_THRESHOLD:
                label = "positive"
            elif rating <= NEGATIVE_RATING_THRESHOLD:
                label = "negative"
            else:
                continue  # Pomijaj neutralne oceny

            descriptions.append(description)
            labels.append(label)

        self.logger.info(f"Przygotowano {len(descriptions)} opisów do trenowania")
        return descriptions, labels

    def get_model_info(self) -> Dict:
        """Zwraca informacje o modelu zgodnie z teorią"""
        if not self.is_fitted:
            return {"error": "Model nie został wytrenowany"}

        info = {
            "algorithm": f"Naive Bayes ({self.model_type} model)",
            "theory": "Pazzani & Billsus content-based filtering",
            "is_fitted": self.is_fitted,
            "classes": self.class_labels,
            "class_priors": self.class_priors,
            "vocabulary_size": self.vocabulary_size,
            "feature_estimation": (
                "Laplace smoothing (α=1)"
                if self.model_type == "multinomial"
                else "Binary smoothing"
            ),
        }

        info.update(self.tfidf_processor.get_vectorizer_info())
        return info

    # Pozostałe metody bez zmian...
    def predict_preferences(
        self, candidate_descriptions: List[str]
    ) -> Dict[int, float]:
        """Backward compatibility"""
        temp_df = pd.DataFrame(
            {
                "movie_id": range(len(candidate_descriptions)),
                "description": candidate_descriptions,
            }
        )
        return self.predict_with_movie_ids(temp_df)

    def get_feature_importance(self, top_n: int = 20) -> Dict[str, Dict[str, float]]:
        """Zwraca najważniejsze słowa dla każdej klasy"""
        if not self.is_fitted:
            return {}

        feature_names = self.tfidf_processor.feature_names
        feature_importance = {}

        for class_name in self.class_labels:
            class_likelihoods = self.feature_likelihoods[class_name]
            word_weights = list(zip(feature_names, class_likelihoods))
            word_weights.sort(key=lambda x: x[1], reverse=True)
            top_words = {word: float(weight) for word, weight in word_weights[:top_n]}
            feature_importance[class_name] = top_words

        return feature_importance

    def analyze_text(self, text: str) -> Dict[str, any]:
        """Analizuje pojedynczy tekst"""
        if not self.is_fitted:
            return {"error": "Model nie został wytrenowany"}

        try:
            temp_df = pd.DataFrame({"movie_id": [0], "description": [text]})
            prediction = self.predict_with_movie_ids(temp_df)[0]

            return {
                "processed_text": self.tfidf_processor.preprocess_text(text),
                "positive_probability": prediction,
                "predicted_class": "positive" if prediction > 0.5 else "negative",
                "model_type": self.model_type,
            }
        except Exception as e:
            return {"error": f"Błąd analizy tekstu: {e}"}

    def retrain_with_feedback(self, new_ratings: pd.DataFrame) -> None:
        """Dopasowuje model na podstawie nowych ocen"""
        if not new_ratings.empty:
            self.fit(new_ratings)
