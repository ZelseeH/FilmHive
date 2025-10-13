from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import logging
import math
import nltk

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
    FIX: Dynamic threshold adjustment jeśli 0 samples (user ratings boundary)
    """

    def __init__(self, model_type: str = NB_MODEL_TYPE):
        self.model_type = model_type

        # NLTK punkt_tab dla polskiego
        try:
            nltk.data.find("tokenizers/punkt_tab/polish")
        except LookupError:
            try:
                nltk.download("punkt_tab", quiet=True)
            except Exception as e:
                logging.getLogger(__name__).warning(
                    f"NLTK punkt_tab download failed: {e}"
                )

        self.tfidf_processor = TFIDFProcessor(use_snowball=True)
        self.is_fitted = False
        self.class_labels = None
        self.class_priors = {}
        self.feature_likelihoods = {}
        self.vocabulary_size = 0
        self.logger = logging.getLogger(__name__)

        self.proba_positive = 0.5
        self.proba_negative = 0.5

    def fit(self, descriptions_df: pd.DataFrame, user_ratings: pd.DataFrame) -> None:
        """
        Fit: merge po movie_id, train na TF-IDF + labels
        FIX: Dynamic threshold adjustment jeśli 0 samples
        """
        self.logger.info(
            f"=== NB.fit START: descriptions={len(descriptions_df)}, ratings={len(user_ratings)} ==="
        )

        # NLTK diagnostics
        try:
            nltk.data.find("tokenizers/punkt_tab/polish")
            self.logger.info(f"NLTK punkt_tab polish OK")
        except Exception as e:
            self.logger.warning(f"NLTK check failed: {e}")

        # Validation
        if descriptions_df.empty or user_ratings.empty:
            self.logger.warning("Empty input data – NB not fitted (fallback P=0.5)")
            self.is_fitted = False
            return

        if (
            "movie_id" not in descriptions_df.columns
            or "description" not in descriptions_df.columns
        ):
            self.logger.error("descriptions_df missing 'movie_id' or 'description'")
            self.is_fitted = False
            return

        if (
            "movie_id" not in user_ratings.columns
            or "rating" not in user_ratings.columns
        ):
            self.logger.error("user_ratings missing 'movie_id' or 'rating'")
            self.is_fitted = False
            return

        try:
            # Merge po movie_id
            merged_data = pd.merge(
                user_ratings,
                descriptions_df[["movie_id", "description"]],
                on="movie_id",
                how="inner",
            )

            self.logger.info(
                f"Merged data: {len(merged_data)} rows (from {len(user_ratings)} ratings, {len(descriptions_df)} descriptions)"
            )

            if merged_data.empty:
                self.logger.warning(
                    "No movie_id matches – NB not fitted (fallback P=0.5)"
                )
                self.is_fitted = False
                return

            # DEBUG: Log user ratings distribution (check boundary issue)
            ratings_values = merged_data["rating"].tolist()
            self.logger.info(f"User ratings distribution: {ratings_values}")
            self.logger.info(
                f"Ratings stats: min={min(ratings_values):.1f}, max={max(ratings_values):.1f}, mean={np.mean(ratings_values):.2f}"
            )

            # FIX: Try prepare with config thresholds first
            descriptions, labels = self._prepare_training_data(
                merged_data,
                pos_threshold=POSITIVE_RATING_THRESHOLD,
                neg_threshold=NEGATIVE_RATING_THRESHOLD,
            )

            # FIX: Jeśli 0 samples (all neutral), try dynamic adjust
            if len(descriptions) == 0:
                self.logger.warning(
                    f"0 samples with thresholds (pos>={POSITIVE_RATING_THRESHOLD}, neg<={NEGATIVE_RATING_THRESHOLD})"
                )
                self.logger.info(
                    "FIX: Trying dynamic threshold adjustment (split at median/mean)"
                )

                # Calculate median/mean for dynamic split
                median_rating = np.median(ratings_values)
                mean_rating = np.mean(ratings_values)
                self.logger.info(
                    f"Median rating: {median_rating:.2f}, Mean: {mean_rating:.2f}"
                )

                # Strategy 1: Split at median (>=median positive, <median negative)
                descriptions, labels = self._prepare_training_data(
                    merged_data,
                    pos_threshold=median_rating,
                    neg_threshold=median_rating,
                )

                if len(descriptions) == 0:
                    # Strategy 2: Split at mean
                    self.logger.warning(
                        f"Still 0 samples with median split – trying mean ({mean_rating:.2f})"
                    )
                    descriptions, labels = self._prepare_training_data(
                        merged_data,
                        pos_threshold=mean_rating,
                        neg_threshold=mean_rating,
                    )

                if len(descriptions) == 0:
                    # Strategy 3: Ultra-liberal (>=5.0 positive, <5.0 negative)
                    self.logger.warning(
                        "Still 0 samples – trying ultra-liberal (5.0 split)"
                    )
                    descriptions, labels = self._prepare_training_data(
                        merged_data, pos_threshold=5.0, neg_threshold=5.0
                    )

            if len(descriptions) == 0:
                self.logger.warning(
                    "Brak danych po wszystkich próbach – NB not fitted (fallback P=0.5)"
                )
                self.is_fitted = False
                return

            # Stabilność: dodaj synthetic samples jeśli tylko 1 klasa
            unique_labels = set(labels)
            if len(unique_labels) < 2:
                self.logger.warning(
                    f"Only {unique_labels} class – adding synthetic samples"
                )
                if "positive" not in unique_labels:
                    descriptions.append(
                        "excellent great amazing wonderful sci-fi adventure"
                    )
                    labels.append("positive")
                if "negative" not in unique_labels:
                    descriptions.append(
                        "terrible awful bad horrible boring disappointing"
                    )
                    labels.append("negative")

            # TF-IDF fit
            tfidf_matrix = self.tfidf_processor.fit_transform(descriptions)
            self.vocabulary_size = len(self.tfidf_processor.feature_names)
            self.class_labels = sorted(set(labels))

            y = np.array(labels)

            # Train Naive Bayes
            if self.model_type == "multinomial":
                self._train_multinomial_nb(tfidf_matrix, y)
            else:
                self._train_bernoulli_nb(tfidf_matrix, y)

            self.is_fitted = True

            # Log balance
            pos_count = np.sum(y == "positive")
            neg_count = np.sum(y == "negative")
            self.logger.info(
                f"NB ({self.model_type}, α={NB_ALPHA}) fitted on {len(descriptions)} docs: "
                f"positive={pos_count}, negative={neg_count}, vocab={self.vocabulary_size}"
            )

        except Exception as e:
            self.logger.error(f"Error in NB fit: {e}", exc_info=True)
            self.is_fitted = False
            self.logger.warning("NB fit failed – fallback P=0.5")

    def _train_multinomial_nb(self, X: np.ndarray, y: np.ndarray) -> None:
        """Multinomial NB"""
        n_docs = len(y)

        for class_label in self.class_labels:
            self.class_priors[class_label] = np.sum(y == class_label) / n_docs

        self.feature_likelihoods = {}
        for class_label in self.class_labels:
            class_mask = y == class_label
            class_docs = X[class_mask]
            total_words_c = np.sum(class_docs)
            word_counts_c = np.sum(class_docs, axis=0)
            self.feature_likelihoods[class_label] = (word_counts_c + NB_ALPHA) / (
                total_words_c + NB_ALPHA * self.vocabulary_size
            )

    def _train_bernoulli_nb(self, X: np.ndarray, y: np.ndarray) -> None:
        """Bernoulli NB"""
        n_docs = len(y)

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
                n_docs_c + 2 * NB_ALPHA
            )

    def predict_with_movie_ids(self, candidates_df: pd.DataFrame) -> Dict[int, float]:
        """Predykcja P(positive|d) (fallback 0.5 jeśli not fitted)"""
        if not self.is_fitted:
            self.logger.warning("NB not fitted – returning default P=0.5 for all")
            if "movie_id" not in candidates_df.columns:
                return {}
            return {mid: 0.5 for mid in candidates_df["movie_id"].tolist()}

        required_cols = ["movie_id", "description"]
        if not all(col in candidates_df.columns for col in required_cols):
            self.logger.error(f"candidates_df missing: {required_cols}")
            return {}

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
                    log_prob = math.log(self.class_priors[class_label])

                    for j, count in enumerate(doc_vector):
                        p_w_c = self.feature_likelihoods[class_label][j]

                        if self.model_type == "multinomial":
                            if count > 0:
                                log_prob += count * math.log(p_w_c)
                        else:
                            if count > 0:
                                log_prob += math.log(p_w_c)
                            else:
                                log_prob += math.log(1 - p_w_c)

                    class_log_probs[class_label] = log_prob

                # Softmax normalization
                max_log = max(class_log_probs.values())
                exp_probs = {
                    k: math.exp(v - max_log) for k, v in class_log_probs.items()
                }
                total = sum(exp_probs.values())
                norm_probs = {k: v / total for k, v in exp_probs.items()}

                predictions[movie_id] = norm_probs.get("positive", 0.5)

        except Exception as e:
            self.logger.error(f"Predict error: {e}", exc_info=True)
            for mid in movie_ids:
                predictions[mid] = 0.5

        return predictions

    def _prepare_training_data(
        self,
        data_df: pd.DataFrame,
        pos_threshold: float = None,
        neg_threshold: float = None,
    ) -> Tuple[List[str], List[str]]:
        """
        Binarna labels z dynamic thresholds
        FIX: Accept custom thresholds (dla dynamic adjustment)
        """
        if pos_threshold is None:
            pos_threshold = POSITIVE_RATING_THRESHOLD
        if neg_threshold is None:
            neg_threshold = NEGATIVE_RATING_THRESHOLD

        descriptions = []
        labels = []

        for _, row in data_df.iterrows():
            desc = str(row.get("description", "")).strip()
            if not desc or len(desc) < 10:
                continue

            rating = row.get("rating", 0)
            if rating >= pos_threshold:
                labels.append("positive")
                descriptions.append(desc)
            elif rating < neg_threshold:  # FIX: Strict < (nie <=, dla median split)
                labels.append("negative")
                descriptions.append(desc)

        self.logger.info(
            f"Prepared {len(descriptions)} samples (pos>={pos_threshold:.1f}, neg<{neg_threshold:.1f}): "
            f"positive={labels.count('positive')}, negative={labels.count('negative')}"
        )
        return descriptions, labels

    def get_model_info(self) -> Dict:
        """Model info"""
        if not self.is_fitted:
            return {"error": "NB nie fitted", "is_fitted": False}

        info = {
            "algorithm": f"Naive Bayes ({self.model_type})",
            "theory": "Pazzani & Billsus (wz. 8-12)",
            "is_fitted": True,
            "classes": self.class_labels,
            "priors": {k: float(v) for k, v in self.class_priors.items()},
            "vocab_size": self.vocabulary_size,
            "alpha": NB_ALPHA,
        }
        info.update(self.tfidf_processor.get_vectorizer_info())
        return info

    def predict_preferences(
        self, candidate_descriptions: List[str]
    ) -> Dict[int, float]:
        """Helper: predict for list"""
        temp_df = pd.DataFrame(
            {
                "movie_id": range(len(candidate_descriptions)),
                "description": candidate_descriptions,
            }
        )
        return self.predict_with_movie_ids(temp_df)

    def get_feature_importance(self, top_n: int = 20) -> Dict[str, Dict[str, float]]:
        """Top N features per class"""
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
        """Analyze text (debug)"""
        if not self.is_fitted:
            return {"error": "NB nie fitted"}

        try:
            temp_df = pd.DataFrame({"movie_id": [0], "description": [text]})
            pred = list(self.predict_with_movie_ids(temp_df).values())[0]
            return {
                "processed": self.tfidf_processor.preprocess_text(text),
                "positive_prob": float(pred),
                "class": "positive" if pred > 0.5 else "negative",
                "model": self.model_type,
            }
        except Exception as e:
            return {"error": str(e)}

    def retrain_with_feedback(
        self, descriptions_df: pd.DataFrame, new_ratings: pd.DataFrame
    ) -> None:
        """Retrain z feedback"""
        if not new_ratings.empty:
            self.tfidf_processor = TFIDFProcessor(use_snowball=True)
            self.fit(descriptions_df, new_ratings)
            self.logger.info("NB retrained")
