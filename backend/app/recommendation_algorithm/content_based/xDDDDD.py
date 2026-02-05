from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import logging

from ..config import (
    KNN_NEIGHBORS,
    KNN_METRIC,
    DIRECTOR_BONUS,
    ACTOR_BONUS,
    MIN_SIMILARITY_THRESHOLD,
    KNN_RECOMMENDATIONS,
    POSITIVE_RATING_THRESHOLD,
)


class KNNRecommender:
    """
    Content-Based K-NN Recommender (Pazzani & Billsus approach)

    Logic:
    1. Build user profile = average vector of positive-rated movies
    2. Apply adaptive weights (boost genres/actors/directors with patterns)
    3. Compute weighted cosine similarity between user profile and candidates
    4. Return top K candidates by similarity score

    WAŻNE: To NIE jest collaborative filtering k-NN!
    Nie szukamy k najbliższych sąsiadów w rated movies.
    Zamiast tego: porównujemy każdego candidate z user profile.
    """

    def __init__(self):
        self.user_profile = None
        self.adaptive_weights = None
        self.feature_names = None
        self.logger = logging.getLogger(__name__)

    def fit(
        self,
        positive_ratings: pd.DataFrame,
        positive_features: pd.DataFrame,
        adaptive_weights: Dict[str, float],
    ) -> None:
        """
        Build user profile z pozytywnych ocen

        Args:
            positive_ratings: DataFrame z pozytywnymi ocenami (≥6)
            positive_features: DataFrame z cechami pozytywnie ocenionych filmów
            adaptive_weights: Dict z adaptive weights {genres: 0.35, actors: 0.25, ...}
        """
        if positive_features.empty:
            raise ValueError("Brak pozytywnych filmów do budowy profilu")

        if "movie_id" not in positive_features.columns:
            raise ValueError("positive_features brak kolumny 'movie_id'")

        features_only = positive_features.drop("movie_id", axis=1)

        if features_only.empty:
            raise ValueError("Brak cech po usunięciu movie_id")

        self.feature_names = features_only.columns.tolist()
        features_matrix = features_only.values.astype(float)

        self.user_profile = np.mean(features_matrix, axis=0)
        self.adaptive_weights = adaptive_weights

        non_zero_features = np.count_nonzero(self.user_profile)
        self.logger.info(
            f"User profile built: {len(positive_ratings)} positive movies, "
            f"{len(self.feature_names)} features ({non_zero_features} non-zero)"
        )

        self.logger.info(
            f"Adaptive weights: genres={adaptive_weights.get('genres', 0):.3f}, "
            f"actors={adaptive_weights.get('actors', 0):.3f}, "
            f"directors={adaptive_weights.get('directors', 0):.3f}, "
            f"country={adaptive_weights.get('country', 0):.3f}, "
            f"year={adaptive_weights.get('year', 0):.3f}"
        )

    def predict(self, candidate_features: pd.DataFrame) -> Dict[int, float]:
        """
        Compute similarity scores między user profile a candidates

        Args:
            candidate_features: DataFrame z cechami candidate movies

        Returns:
            Dict {movie_id: similarity_score} gdzie score ∈ [0, 1]
        """
        if self.user_profile is None:
            raise ValueError("Model nie został wytrenowany. Wywołaj fit() najpierw.")

        if candidate_features.empty:
            self.logger.warning("Brak kandydatów do predict")
            return {}

        if "movie_id" not in candidate_features.columns:
            raise ValueError("candidate_features brak kolumny 'movie_id'")

        try:

            candidate_movie_ids = candidate_features["movie_id"].values
            features_only = candidate_features.drop("movie_id", axis=1)

            if list(features_only.columns) != self.feature_names:
                raise ValueError("Feature columns mismatch with fitted model")

            features_matrix = features_only.values.astype(float)

            weighted_user_profile = self._apply_adaptive_weights(
                self.user_profile.reshape(1, -1)
            )[0]

            weighted_candidate_features = self._apply_adaptive_weights(features_matrix)

            similarities = cosine_similarity(
                weighted_user_profile.reshape(1, -1), weighted_candidate_features
            )[0]

            predictions = {
                movie_id: max(0.0, float(sim))
                for movie_id, sim in zip(candidate_movie_ids, similarities)
            }

            top_preds = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[
                :5
            ]
            self.logger.info(
                f"K-NN top 5 similarities: {[(mid, f'{s:.3f}') for mid, s in top_preds]}"
            )

            return predictions

        except Exception as e:
            self.logger.error(f"K-NN predict error: {e}", exc_info=True)
            return {}

    def _apply_adaptive_weights(self, features_matrix: np.ndarray) -> np.ndarray:
        """
        Apply adaptive weights do feature vectors

        Logic:
        - Multiply each feature column by its adaptive weight
        - genres columns × genres_weight
        - actors columns × actors_weight
        - directors columns × directors_weight
        - country columns × country_weight
        - year column × year_weight

        Args:
            features_matrix: (n_samples, n_features) numpy array

        Returns:
            Weighted features matrix (same shape)
        """
        weighted_matrix = features_matrix.copy()

        for i, feature_name in enumerate(self.feature_names):
            if feature_name.startswith("genre_"):
                weight = self.adaptive_weights.get("genres", 1.0)
            elif feature_name.startswith("actor_"):
                weight = self.adaptive_weights.get("actors", 1.0)
            elif feature_name.startswith("director_"):
                weight = self.adaptive_weights.get("directors", 1.0)
            elif feature_name.startswith("country_"):
                weight = self.adaptive_weights.get("country", 1.0)
            elif feature_name == "release_year_normalized":
                weight = self.adaptive_weights.get("year", 1.0)
            elif feature_name == "duration_normalized":
                weight = 0.5
            else:
                weight = 1.0

            weighted_matrix[:, i] *= weight

        return weighted_matrix

    def recommend(
        self,
        positive_ratings: pd.DataFrame,
        positive_features: pd.DataFrame,
        candidate_features: pd.DataFrame,
        adaptive_weights: Dict[str, float],
        top_k: int = KNN_RECOMMENDATIONS,
    ) -> List[Tuple[int, float]]:
        """
        Pełny pipeline: fit + predict + rank

        Args:
            positive_ratings: DataFrame z pozytywnymi ocenami (≥6)
            positive_features: DataFrame z cechami pozytywnie ocenionych filmów
            candidate_features: DataFrame z cechami kandydatów
            adaptive_weights: Dict z adaptive weights
            top_k: Liczba rekomendacji do zwrócenia (default 7)

        Returns:
            List[(movie_id, similarity_score)] sorted by score (descending)
        """
        self.fit(positive_ratings, positive_features, adaptive_weights)

        predictions = self.predict(candidate_features)

        if not predictions:
            self.logger.warning("K-NN: No predictions generated")
            return []

        ranked = sorted(predictions.items(), key=lambda x: x[1], reverse=True)

        top_recommendations = ranked[:top_k]

        self.logger.info(
            f"K-NN recommendations: returning top {len(top_recommendations)} "
            f"(requested {top_k})"
        )

        return top_recommendations

    def get_model_info(self) -> Dict:
        """Debug info o modelu"""
        if self.user_profile is None:
            return {"error": "Model nie został wytrenowany"}

        return {
            "algorithm": "Content-Based K-NN (Pazzani & Billsus)",
            "profile_size": len(self.user_profile),
            "non_zero_features": int(np.count_nonzero(self.user_profile)),
            "feature_count": len(self.feature_names),
            "adaptive_weights": self.adaptive_weights,
            "similarity_metric": "weighted_cosine",
            "min_threshold": MIN_SIMILARITY_THRESHOLD,
        }

    def explain_recommendation(
        self, movie_id: int, candidate_features: pd.DataFrame
    ) -> Dict:
        """
        Explain dlaczego movie został rekomendowany

        Returns:
            Dict z top matching features i ich contributions
        """
        if self.user_profile is None:
            return {"error": "Model nie został wytrenowany"}

        movie_row = candidate_features[candidate_features["movie_id"] == movie_id]

        if movie_row.empty:
            return {"error": f"Movie {movie_id} not found in candidates"}

        movie_features = movie_row.drop("movie_id", axis=1).values[0]

        weighted_profile = self._apply_adaptive_weights(
            self.user_profile.reshape(1, -1)
        )[0]

        weighted_movie = self._apply_adaptive_weights(movie_features.reshape(1, -1))[0]

        contributions = weighted_profile * weighted_movie

        top_indices = np.argsort(contributions)[::-1][:10]

        top_features = [
            {
                "feature": self.feature_names[i],
                "contribution": float(contributions[i]),
                "user_profile_value": float(weighted_profile[i]),
                "movie_value": float(weighted_movie[i]),
            }
            for i in top_indices
            if contributions[i] > 0
        ]

        return {
            "movie_id": movie_id,
            "top_features": top_features,
            "total_similarity": float(np.sum(contributions)),
        }
