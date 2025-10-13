from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import logging
import math

from ..config import (
    POSITIVE_RATING_THRESHOLD,
    NEGATIVE_RATING_THRESHOLD,
    NB_MODEL_TYPE,
    NB_ALPHA,
)
from .tfidf_processor import TFIDFProcessor


class NaiveBayesRecommender:
    """
    Naive Bayes wg Pazzaniego i Billsusa (wzory 8-12: P(c|d) = P(c) * P(d|c) / P(d))
    Binarna klasyfikacja tekstu (opisy filmów) na positive/negative.
    """

    def __init__(self, model_type: str = NB_MODEL_TYPE):
        self.model_type = model_type
        self.tfidf_processor = TFIDFProcessor(use_snowball=True)  # Default Snowball
        self.is_fitted = False
        self.class_labels = None
        self.class_priors = {}  # P(c) wz. 8
        self.feature_likelihoods = {}  # P(w|c) wz. 10/12
        self.vocabulary_size = 0
        self.logger = logging.getLogger(__name__)

    def fit(self, descriptions_df: pd.DataFrame, user_ratings: pd.DataFrame) -> None:
        """Fit: merge po movie_id, train na TF-IDF (wz. 5) + labels"""
        if descriptions_df.empty or user_ratings.empty:
            raise ValueError("Brak danych")

        if (
            "movie_id" not in descriptions_df.columns
            or "description" not in descriptions_df.columns
        ):
            raise ValueError("descriptions_df brak 'movie_id'/'description'")
        if (
            "movie_id" not in user_ratings.columns
            or "rating" not in user_ratings.columns
        ):
            raise ValueError("user_ratings brak 'movie_id'/'rating'")

        # Merge po movie_id
        merged_data = pd.merge(
            user_ratings,
            descriptions_df[["movie_id", "description"]],
            on="movie_id",
            how="inner",
        )
        if merged_data.empty:
            raise ValueError("Brak dopasowań movie_id")

        descriptions, labels = self._prepare_training_data(merged_data)

        if len(descriptions) == 0:
            raise ValueError("Brak danych po filtracji")

        # Stabilność: dodaj klasy jeśli brak (jak Syskill & Webert [20])
        unique_labels = set(labels)
        if len(unique_labels) < 2:
            self.logger.warning(f"Tylko {unique_labels}; dodaj sztuczną klasę")
            if "positive" not in unique_labels:
                descriptions.append("excellent great amazing sci-fi dream")
                labels.append("positive")
            if "negative" not in unique_labels:
                descriptions.append("terrible awful bad horror")
                labels.append("negative")

        tfidf_matrix = self.tfidf_processor.fit_transform(descriptions)
        self.vocabulary_size = len(self.tfidf_processor.feature_names)
        self.class_labels = sorted(set(labels))  # ['negative', 'positive']

        y = np.array(labels)
        if self.model_type == "multinomial":
            self._train_multinomial_nb(tfidf_matrix, y)
        else:
            self._train_bernoulli_nb(tfidf_matrix, y)

        self.is_fitted = True
        self.logger.info(
            f"NB ({self.model_type}, α={NB_ALPHA}) fitted na {len(descriptions)} docs, classes: {self.class_labels}"
        )

    def _train_multinomial_nb(self, X: np.ndarray, y: np.ndarray) -> None:
        """Multinomial: wz. 11-12, P(w|c) = (count_w_c + α) / (total_c + α|V|), P(d|c) = ∏ P(w|c)^{tf}"""
        n_docs = len(y)

        # P(c) = count_c / n_docs (wz. 8)
        for class_label in self.class_labels:
            self.class_priors[class_label] = np.sum(y == class_label) / n_docs

        self.feature_likelihoods = {}
        for class_label in self.class_labels:
            class_mask = y == class_label
            class_docs = X[class_mask]
            total_words_c = np.sum(class_docs)  # Suma tf w klasie
            word_counts_c = np.sum(class_docs, axis=0)
            self.feature_likelihoods[class_label] = (word_counts_c + NB_ALPHA) / (
                total_words_c + NB_ALPHA * self.vocabulary_size
            )

    def _train_bernoulli_nb(self, X: np.ndarray, y: np.ndarray) -> None:
        """Bernoulli: wz. 9-10, P(w|c) = (presence_c + α) / (n_docs_c + 2α), P(d|c) = ∏ [P^x * (1-P)^{1-x}]"""
        n_docs = len(y)

        # P(c)
        for class_label in self.class_labels:
            self.class_priors[class_label] = np.sum(y == class_label) / n_docs

        X_binary = (X > 0).astype(int)
        self.feature_likelihoods = {}
        for class_label in self.class_labels:
            class_mask = y == class_label
            class_docs = X_binary[class_mask]
            n_docs_c = np.sum(class_mask)
            presence_c = np.sum(class_docs, axis=0)
            self.feature_likelihoods[class_label] = (presence_c + NB_ALPHA) / (
                n_docs_c + 2 * NB_ALPHA  # Dla binary features
            )

    def predict_with_movie_ids(self, candidates_df: pd.DataFrame) -> Dict[int, float]:
        """Predykcja P(positive|d) dla movie_id (użyj w ensemble dla top NB_TOP_K >0.5)"""
        if not self.is_fitted:
            raise ValueError("Fit najpierw")

        required_cols = ["movie_id", "description"]
        if not all(col in candidates_df.columns for col in required_cols):
            raise ValueError(f"Brak kolumn: {required_cols}")

        descriptions = candidates_df["description"].fillna("").tolist()
        movie_ids = candidates_df["movie_id"].tolist()

        if not descriptions:
            return {}

        predictions = {}
        try:
            candidate_tfidf = self.tfidf_processor.transform(descriptions)

            if self.model_type == "bernoulli":
                candidate_tfidf = (candidate_tfidf > 0).astype(int)

            for i, movie_id in enumerate(movie_ids):
                doc_vector = candidate_tfidf[i].toarray().flatten()

                class_log_probs = {}
                for class_label in self.class_labels:
                    log_prob = math.log(self.class_priors[class_label])  # log P(c)

                    for j, count in enumerate(doc_vector):
                        p_w_c = self.feature_likelihoods[class_label][j]

                        if self.model_type == "multinomial":
                            if count > 0:
                                log_prob += count * math.log(
                                    p_w_c
                                )  # log ∏ P^{tf} (wz. 11)
                        else:
                            # Bernoulli: log [P^x * (1-P)^{1-x}] (wz. 9)
                            if count > 0:
                                log_prob += math.log(p_w_c)
                            else:
                                log_prob += math.log(1 - p_w_c)

                    class_log_probs[class_label] = log_prob

                # Normalizacja softmax
                max_log = max(class_log_probs.values())
                exp_probs = {
                    k: math.exp(v - max_log) for k, v in class_log_probs.items()
                }
                total = sum(exp_probs.values())
                norm_probs = {k: v / total for k, v in exp_probs.items()}

                predictions[movie_id] = norm_probs.get("positive", 0.5)  # P(positive)

        except Exception as e:
            self.logger.error(f"Predict error: {e}")
            for mid in movie_ids:  # Fallback
                predictions[mid] = 0.5

        return predictions

    def _prepare_training_data(
        self, data_df: pd.DataFrame
    ) -> Tuple[List[str], List[str]]:
        """Binarna labels: positive >=7, negative <=4 (pomij neutralne)"""
        descriptions = []
        labels = []
        for _, row in data_df.iterrows():
            desc = str(row.get("description", "")).strip()
            if not desc:
                continue
            rating = row.get("rating", 0)
            if rating >= POSITIVE_RATING_THRESHOLD:
                labels.append("positive")
            elif rating <= NEGATIVE_RATING_THRESHOLD:
                labels.append("negative")
            else:
                continue  # Neutralne pomiń
            descriptions.append(desc)
        self.logger.info(f"Prepared {len(descriptions)} samples")
        return descriptions, labels

    def get_model_info(self) -> Dict:
        if not self.is_fitted:
            return {"error": "Nie fitted"}
        info = {
            "algorithm": f"Naive Bayes ({self.model_type})",
            "theory": "Pazzani & Billsus (wz. 8-12)",
            "is_fitted": True,
            "classes": self.class_labels,
            "priors": self.class_priors,
            "vocab_size": self.vocabulary_size,
            "alpha": NB_ALPHA,
            "estimation": f"Laplace α={NB_ALPHA} (multinomial wz.12 / Bernoulli wz.10)",
        }
        info.update(self.tfidf_processor.get_vectorizer_info())
        return info

    # Pozostałe (predict_preferences, get_feature_importance, analyze_text, retrain_with_feedback)
    def predict_preferences(
        self, candidate_descriptions: List[str]
    ) -> Dict[int, float]:
        temp_df = pd.DataFrame(
            {
                "movie_id": range(len(candidate_descriptions)),
                "description": candidate_descriptions,
            }
        )
        return self.predict_with_movie_ids(temp_df)

    def get_feature_importance(self, top_n: int = 20) -> Dict[str, Dict[str, float]]:
        if not self.is_fitted:
            return {}
        feature_names = self.tfidf_processor.feature_names
        importance = {}
        for class_name in self.class_labels:
            likelihoods = self.feature_likelihoods[class_name]
            weights = sorted(
                zip(feature_names, likelihoods), key=lambda x: x[1], reverse=True
            )[:top_n]
            importance[class_name] = {w: float(l) for w, l in weights}
        return importance

    def analyze_text(self, text: str) -> Dict[str, any]:
        if not self.is_fitted:
            return {"error": "Nie fitted"}
        try:
            temp_df = pd.DataFrame({"movie_id": [0], "description": [text]})
            pred = list(self.predict_with_movie_ids(temp_df).values())[0]
            return {
                "processed": self.tfidf_processor.preprocess_text(text),
                "positive_prob": pred,
                "class": "positive" if pred > 0.5 else "negative",
                "model": self.model_type,
            }
        except Exception as e:
            return {"error": str(e)}

    def retrain_with_feedback(
        self, descriptions_df: pd.DataFrame, new_ratings: pd.DataFrame
    ) -> None:
        """Retrain (relevance feedback, reset TF-IDF jeśli nowe docs)"""
        if not new_ratings.empty:
            self.tfidf_processor = TFIDFProcessor(use_snowball=True)  # Reset
            self.fit(descriptions_df, new_ratings)
            self.logger.info("Retrained z feedback")
