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
    NB_RECOMMENDATIONS,
    TRAINING_POSITIVE_LIMIT,
    TRAINING_NEGATIVE_LIMIT,
    USE_SNOWBALL_STEMMER,
    STEMMER_LANGUAGE,
)
from ..content_based.tfidf_processor import TFIDFProcessor


class NaiveBayesRecommender:
    """
    Naive Bayes Text Classifier dla opisów filmów
    Based on Pazzani & Billsus (2007) - wzory 8-12

    Trains on positive descriptions (liked) vs negative descriptions (disliked)
    Predicts P(positive | description) for candidates
    """

    def __init__(self, model_type: str = NB_MODEL_TYPE):
        """
        Args:
            model_type: "multinomial" or "bernoulli"
        """
        self.model_type = model_type

        try:
            nltk.data.find("tokenizers/punkt_tab/polish")
        except LookupError:
            try:
                nltk.download("punkt_tab", quiet=True)
            except Exception as e:
                logging.getLogger(__name__).warning(
                    f"NLTK punkt_tab download failed: {e}"
                )

        self.tfidf_processor = TFIDFProcessor(
            use_snowball=USE_SNOWBALL_STEMMER, language=STEMMER_LANGUAGE
        )

        self.is_fitted = False
        self.class_labels = ["positive", "negative"]
        self.class_priors = {}
        self.feature_likelihoods = {}
        self.vocabulary_size = 0
        self.logger = logging.getLogger(__name__)

    def fit(
        self, positive_descriptions: pd.DataFrame, negative_descriptions: pd.DataFrame
    ) -> None:
        """
        Train Naive Bayes on positive vs negative descriptions

        Args:
            positive_descriptions: DataFrame z ['movie_id', 'description'] dla polubionych (≥6)
            negative_descriptions: DataFrame z ['movie_id', 'description'] dla nielobionych (≤4)
        """
        self.logger.info(
            f"=== NaiveBayes.fit START: positive={len(positive_descriptions)}, "
            f"negative={len(negative_descriptions)} ==="
        )

        # Validation
        if positive_descriptions.empty and negative_descriptions.empty:
            self.logger.warning(
                "Both positive and negative descriptions are empty - NB not fitted"
            )
            self.is_fitted = False
            return

        for df, name in [
            (positive_descriptions, "positive"),
            (negative_descriptions, "negative"),
        ]:
            if not df.empty and ("description" not in df.columns):
                self.logger.error(f"{name}_descriptions missing 'description' column")
                self.is_fitted = False
                return

        try:
            descriptions, labels = self._prepare_training_data(
                positive_descriptions, negative_descriptions
            )

            if len(descriptions) == 0:
                self.logger.warning(
                    "No valid descriptions after preprocessing - NB not fitted"
                )
                self.is_fitted = False
                return

            unique_labels = set(labels)
            if len(unique_labels) < 2:
                self.logger.warning(
                    f"Only one class present: {unique_labels}. "
                    f"Adding synthetic sample for missing class."
                )
                if "positive" not in unique_labels:
                    descriptions.append(
                        "excellent great amazing wonderful fantastic masterpiece"
                    )
                    labels.append("positive")
                if "negative" not in unique_labels:
                    descriptions.append(
                        "terrible awful bad horrible boring disappointing waste"
                    )
                    labels.append("negative")

            tfidf_matrix = self.tfidf_processor.fit_transform(descriptions)
            self.vocabulary_size = len(self.tfidf_processor.feature_names)

            y = np.array(labels)

            if self.model_type == "multinomial":
                self._train_multinomial_nb(tfidf_matrix, y)
            elif self.model_type == "bernoulli":
                self._train_bernoulli_nb(tfidf_matrix, y)
            else:
                raise ValueError(f"Unknown model_type: {self.model_type}")

            self.is_fitted = True

            pos_count = np.sum(y == "positive")
            neg_count = np.sum(y == "negative")
            self.logger.info(
                f"NaiveBayes ({self.model_type}, α={NB_ALPHA}) fitted: "
                f"positive={pos_count}, negative={neg_count}, vocab={self.vocabulary_size}"
            )

        except Exception as e:
            self.logger.error(f"NaiveBayes.fit failed: {e}", exc_info=True)
            self.is_fitted = False
            self.logger.warning("NB fit failed - fallback P=0.5")

    def _prepare_training_data(
        self, positive_descriptions: pd.DataFrame, negative_descriptions: pd.DataFrame
    ) -> Tuple[List[str], List[str]]:
        """
        Prepare training data: filter empty descriptions + assign labels

        Returns:
            descriptions: List[str] - valid descriptions
            labels: List[str] - corresponding labels ("positive"/"negative")
        """
        descriptions = []
        labels = []

        if not positive_descriptions.empty:
            for _, row in positive_descriptions.iterrows():
                desc = str(row.get("description", "")).strip()

                if len(desc) >= 10:
                    descriptions.append(desc)
                    labels.append("positive")

        if not negative_descriptions.empty:
            for _, row in negative_descriptions.iterrows():
                desc = str(row.get("description", "")).strip()

                if len(desc) >= 10:
                    descriptions.append(desc)
                    labels.append("negative")

        self.logger.info(
            f"Prepared {len(descriptions)} training samples: "
            f"positive={labels.count('positive')}, negative={labels.count('negative')}"
        )

        return descriptions, labels

    def _train_multinomial_nb(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Train Multinomial Naive Bayes

        P(word | class) = (count(word, class) + α) / (total_words_class + α * vocab_size)
        """
        n_docs = len(y)

        for class_label in self.class_labels:
            self.class_priors[class_label] = np.sum(y == class_label) / n_docs

        self.feature_likelihoods = {}
        for class_label in self.class_labels:
            class_mask = y == class_label
            class_docs = X[class_mask]

            total_words_c = np.sum(class_docs)
            word_counts_c = np.sum(class_docs, axis=0)

            likelihoods = (word_counts_c + NB_ALPHA) / (
                total_words_c + NB_ALPHA * self.vocabulary_size
            )

            if isinstance(likelihoods, np.matrix):
                likelihoods = np.asarray(likelihoods).flatten()
            elif len(likelihoods.shape) > 1:
                likelihoods = likelihoods.flatten()

            self.feature_likelihoods[class_label] = likelihoods

            self.logger.debug(
                f"Trained {class_label}: prior={self.class_priors[class_label]:.3f}, "
                f"likelihoods shape={likelihoods.shape}"
            )

    def _train_bernoulli_nb(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Train Bernoulli Naive Bayes (binary presence/absence)

        P(word | class) = (presence_count + α) / (n_docs_class + 2α)
        """
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

            likelihoods = (presence_c + NB_ALPHA) / (n_docs_c + 2 * NB_ALPHA)

            if isinstance(likelihoods, np.matrix):
                likelihoods = np.asarray(likelihoods).flatten()
            elif len(likelihoods.shape) > 1:
                likelihoods = likelihoods.flatten()

            self.feature_likelihoods[class_label] = likelihoods

            self.logger.debug(
                f"Trained {class_label}: prior={self.class_priors[class_label]:.3f}, "
                f"likelihoods shape={likelihoods.shape}"
            )

    def predict_with_movie_ids(self, candidates_df: pd.DataFrame) -> Dict[int, float]:
        """
        Predict P(positive | description) dla candidates

        Args:
            candidates_df: DataFrame z ['movie_id', 'description']

        Returns:
            Dict {movie_id: P(positive)} gdzie P(positive) ∈ [0, 1]
        """
        if not self.is_fitted:
            self.logger.warning(
                "NaiveBayes not fitted - returning default P=0.5 for all"
            )
            if "movie_id" not in candidates_df.columns:
                return {}
            return {mid: 0.5 for mid in candidates_df["movie_id"].tolist()}

        required_cols = ["movie_id", "description"]
        if not all(col in candidates_df.columns for col in required_cols):
            self.logger.error(f"candidates_df missing columns: {required_cols}")
            return {}

        descriptions = candidates_df["description"].fillna("").tolist()
        movie_ids = candidates_df["movie_id"].tolist()

        if not descriptions:
            return {}

        predictions = {}
        try:
            candidate_tfidf = self.tfidf_processor.transform(descriptions)

            self.logger.debug(
                f"Transformed {len(descriptions)} descriptions to TF-IDF: "
                f"shape={candidate_tfidf.shape}"
            )

            if self.model_type == "bernoulli":
                candidate_tfidf = (candidate_tfidf > 0).astype(int)

            for i, movie_id in enumerate(movie_ids):
                doc_vector = candidate_tfidf[i].toarray().flatten()

                class_log_probs = {}
                for class_label in self.class_labels:
                    log_prob = math.log(self.class_priors[class_label])

                    for j, tf_idf_weight in enumerate(doc_vector):
                        p_w_c = self.feature_likelihoods[class_label][j]

                        if self.model_type == "multinomial":
                            if tf_idf_weight > 0:
                                log_prob += tf_idf_weight * math.log(p_w_c)
                        else:
                            if tf_idf_weight > 0:
                                log_prob += math.log(p_w_c)
                            else:
                                log_prob += math.log(1 - p_w_c)

                    class_log_probs[class_label] = log_prob

                max_log = max(class_log_probs.values())
                exp_probs = {
                    k: math.exp(v - max_log) for k, v in class_log_probs.items()
                }
                total = sum(exp_probs.values())
                norm_probs = {k: v / total for k, v in exp_probs.items()}

                predictions[movie_id] = norm_probs.get("positive", 0.5)

            if predictions:
                top_preds = sorted(
                    predictions.items(), key=lambda x: x[1], reverse=True
                )[:5]
                self.logger.info(
                    f"NaiveBayes top 5 P(positive): {[(mid, f'{p:.3f}') for mid, p in top_preds]}"
                )

        except Exception as e:
            self.logger.error(f"NaiveBayes.predict failed: {e}", exc_info=True)
            predictions = {mid: 0.5 for mid in movie_ids}

        return predictions

    def recommend(
        self,
        positive_descriptions: pd.DataFrame,
        negative_descriptions: pd.DataFrame,
        candidate_descriptions: pd.DataFrame,
        top_k: int = NB_RECOMMENDATIONS,
    ) -> List[Tuple[int, float]]:
        """
        Full pipeline: fit + predict + rank

        Args:
            positive_descriptions: DataFrame z opisami polubionych filmów
            negative_descriptions: DataFrame z opisami nielobionych filmów
            candidate_descriptions: DataFrame z opisami kandydatów
            top_k: Liczba rekomendacji do zwrócenia (default 7)

        Returns:
            List[(movie_id, P(positive))] sorted by P(positive) descending
        """
        self.fit(positive_descriptions, negative_descriptions)

        if not self.is_fitted:
            self.logger.warning(
                "NaiveBayes not fitted - returning empty recommendations"
            )
            return []

        predictions = self.predict_with_movie_ids(candidate_descriptions)

        if not predictions:
            self.logger.warning("NaiveBayes: No predictions generated")
            return []

        ranked = sorted(predictions.items(), key=lambda x: x[1], reverse=True)

        top_recommendations = ranked[:top_k]

        self.logger.info(
            f"NaiveBayes recommendations: returning top {len(top_recommendations)} "
            f"(requested {top_k})"
        )

        return top_recommendations

    def get_model_info(self) -> Dict:
        """Debug info o modelu"""
        if not self.is_fitted:
            return {"error": "NaiveBayes not fitted", "is_fitted": False}

        info = {
            "algorithm": f"Naive Bayes ({self.model_type})",
            "theory": "Pazzani & Billsus (2007) - equations 8-12",
            "is_fitted": True,
            "classes": self.class_labels,
            "priors": {k: float(v) for k, v in self.class_priors.items()},
            "vocabulary_size": self.vocabulary_size,
            "alpha": NB_ALPHA,
            "min_description_length": 10,
        }

        tfidf_info = self.tfidf_processor.get_vectorizer_info()
        info.update(tfidf_info)

        return info

    def predict_preferences(
        self, candidate_descriptions: List[str]
    ) -> Dict[int, float]:
        """
        Helper: predict for list of descriptions (bez movie_id)
        """
        temp_df = pd.DataFrame(
            {
                "movie_id": range(len(candidate_descriptions)),
                "description": candidate_descriptions,
            }
        )
        return self.predict_with_movie_ids(temp_df)

    def get_feature_importance(
        self, top_n: int = 20
    ) -> Dict[str, List[Tuple[str, float]]]:
        """
        Get top N most important features (words) for each class
        """
        if not self.is_fitted:
            return {}

        feature_names = self.tfidf_processor.feature_names
        importance = {}

        for class_name in self.class_labels:
            likelihoods = self.feature_likelihoods[class_name]

            word_likelihood_pairs = list(zip(feature_names, likelihoods))
            word_likelihood_pairs.sort(key=lambda x: x[1], reverse=True)

            importance[class_name] = [
                (word, float(likelihood))
                for word, likelihood in word_likelihood_pairs[:top_n]
            ]

        return importance

    def analyze_text(self, text: str) -> Dict[str, any]:
        """
        Analyze single text (for debugging/explainability)
        """
        if not self.is_fitted:
            return {"error": "NaiveBayes not fitted"}

        try:
            temp_df = pd.DataFrame({"movie_id": [0], "description": [text]})

            pred = self.predict_with_movie_ids(temp_df)[0]

            processed = self.tfidf_processor.preprocess_text(text)

            return {
                "original_text": text[:100] + "..." if len(text) > 100 else text,
                "processed_text": processed,
                "positive_prob": float(pred),
                "predicted_class": "positive" if pred > 0.5 else "negative",
                "confidence": abs(pred - 0.5) * 2,
                "model_type": self.model_type,
            }

        except Exception as e:
            self.logger.error(f"analyze_text failed: {e}", exc_info=True)
            return {"error": str(e)}

    def retrain_with_feedback(
        self, positive_descriptions: pd.DataFrame, negative_descriptions: pd.DataFrame
    ) -> None:
        """
        Retrain model with new feedback data
        """
        if not positive_descriptions.empty or not negative_descriptions.empty:
            self.tfidf_processor = TFIDFProcessor(
                use_snowball=USE_SNOWBALL_STEMMER, language=STEMMER_LANGUAGE
            )

            self.fit(positive_descriptions, negative_descriptions)
            self.logger.info("NaiveBayes retrained with feedback")
