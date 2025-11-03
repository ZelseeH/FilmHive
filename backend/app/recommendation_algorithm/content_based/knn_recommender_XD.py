from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import logging

from ..config import (
    KNN_NEIGHBORS,
    KNN_METRIC,
    DIRECTOR_BONUS,
    DEFAULT_RATING,
    MIN_SIMILARITY_THRESHOLD,
    RECENT_RATINGS_LIMIT,
)


class KNNRecommender:
    def __init__(self):
        self.fitted_features = None
        self.movie_ids = None
        self.feature_names = None
        self.director_indices = None
        self.user_ratings = None
        self.nbrs = None
        self.logger = logging.getLogger(__name__)

    def fit(self, features_matrix: pd.DataFrame, user_ratings: pd.DataFrame) -> None:
        """Trenuje model k-NN na cechach strukturalnych ocenionych filmów"""
        # Safety: Check empty before conversion
        if features_matrix.empty or user_ratings.empty:
            raise ValueError("Brak danych do trenowania KNN")

        if "movie_id" not in features_matrix.columns:
            raise ValueError("features_matrix brak kolumny 'movie_id'")

        self.movie_ids = features_matrix["movie_id"].values
        features_only = features_matrix.drop("movie_id", axis=1)

        if features_only.empty or len(features_only.columns) == 0:
            raise ValueError("Brak cech po usunięciu movie_id")

        self.feature_names = features_only.columns.tolist()
        self.fitted_features = features_only.values.astype(float)
        self.user_ratings = user_ratings

        # Zapisz indeksy kolumn reżyserów dla bonusu
        self.director_indices = [
            i for i, col in enumerate(self.feature_names) if col.startswith("director_")
        ]

        # Trenuj NearestNeighbors
        n_neighbors = min(KNN_NEIGHBORS, len(self.fitted_features))
        if n_neighbors < 1:
            raise ValueError(
                f"Za mało danych do trenowania KNN (fitted: {len(self.fitted_features)})"
            )

        self.nbrs = NearestNeighbors(
            n_neighbors=n_neighbors,
            metric=KNN_METRIC,
            algorithm="auto",
        ).fit(self.fitted_features)

        # Debug info (reduce excessive logs)
        director_columns = [
            col for col in self.feature_names if col.startswith("director_")
        ]
        genre_columns = [col for col in self.feature_names if col.startswith("genre_")]
        actor_columns = [col for col in self.feature_names if col.startswith("actor_")]

        self.logger.info(
            f"k-NN fitted: {len(self.fitted_features)} movies, {self.fitted_features.shape[1]} features"
        )
        self.logger.info(
            f"Features breakdown: {len(genre_columns)} genres, {len(actor_columns)} actors, {len(director_columns)} directors"
        )
        self.logger.info(f"k-NN neighbors: {n_neighbors}, metric: {KNN_METRIC}")

    def predict_ratings(
        self, candidate_features: pd.DataFrame, user_ratings: pd.DataFrame
    ) -> Dict[int, float]:
        """Przewiduje oceny używając NearestNeighbors + hybrid similarity"""
        if self.fitted_features is None or self.nbrs is None:
            raise ValueError("Model KNN nie został wytrenowany. Użyj najpierw fit()")

        if candidate_features.empty:
            self.logger.warning("Brak kandydatów do predict_ratings KNN")
            return {}

        if "movie_id" not in candidate_features.columns:
            raise ValueError("candidate_features brak kolumny 'movie_id'")

        try:
            predictions = {}
            candidate_movie_ids = candidate_features["movie_id"].values
            candidate_features_only = candidate_features.drop("movie_id", axis=1)

            # Safety: Check alignment features (candidate vs fitted)
            if list(candidate_features_only.columns) != self.feature_names:
                self.logger.error(
                    "Feature mismatch between candidates and fitted model"
                )
                raise ValueError("Feature columns do not match fitted model")

            candidate_features_matrix = candidate_features_only.values.astype(float)

            # Base predictions
            base_predictions = {}

            for i, candidate_movie_id in enumerate(candidate_movie_ids):
                candidate_vector = candidate_features_matrix[i : i + 1]

                # Znajdź k nearest neighbors
                try:
                    distances, indices = self.nbrs.kneighbors(
                        candidate_vector,
                        n_neighbors=min(KNN_NEIGHBORS, len(self.fitted_features)),
                        return_distance=True,
                    )
                except Exception as e:
                    self.logger.error(
                        f"KNN kneighbors error for movie {candidate_movie_id}: {e}"
                    )
                    predictions[candidate_movie_id] = DEFAULT_RATING
                    continue

                base_similarities = 1 - distances[0]  # Cosine: sim = 1 - dist

                # Aplikuj bonus za director match
                adjusted_similarities = self._apply_director_bonus(
                    base_similarities, indices[0], candidate_vector
                )

                # Oblicz przewidywaną ocenę (weighted average)
                predicted_rating = self._calculate_weighted_average(
                    indices[0], adjusted_similarities, user_ratings
                )

                base_predictions[candidate_movie_id] = {
                    "rating": predicted_rating,
                    "max_base_sim": float(max(base_similarities)),
                }

                predictions[candidate_movie_id] = predicted_rating

            # Boost dla frequent director (opcjonalny)
            frequent_director = self._identify_frequent_director(user_ratings)
            if frequent_director:
                self._boost_repeated_director(
                    predictions,
                    base_predictions,
                    candidate_features_matrix,
                    candidate_movie_ids,
                    frequent_director,
                    user_ratings,
                )

            # Log top predictions (reduce debug spam)
            top_predictions = sorted(
                predictions.items(), key=lambda x: x[1], reverse=True
            )[:5]
            self.logger.info(f"k-NN top 5 predictions: {top_predictions}")

            return predictions

        except Exception as e:
            self.logger.error(f"Błąd w predict_ratings KNN: {e}", exc_info=True)
            # Fallback: Return default ratings (nie crash)
            return {
                mid: DEFAULT_RATING for mid in candidate_features["movie_id"].values
            }

    def _identify_frequent_director(self, user_ratings: pd.DataFrame) -> Optional[str]:
        """Identyfikuje frequent director w recent ratings (min 3 filmy)"""
        if len(user_ratings) < 3:
            return None

        # Assume user_ratings sorted by date desc (jeśli nie, sort w DataProcessor przed)
        recent_ratings = user_ratings.head(RECENT_RATINGS_LIMIT)

        director_counts = {}
        for _, rating_row in recent_ratings.iterrows():
            movie_id = rating_row["movie_id"]
            movie_idx = np.where(self.movie_ids == movie_id)[0]
            if len(movie_idx) > 0:
                movie_features = self.fitted_features[movie_idx[0]]
                for dir_idx in self.director_indices:
                    if movie_features[dir_idx] > 0:
                        director_col = self.feature_names[dir_idx]  # 'director_nolan'
                        director_name = director_col.replace("director_", "")
                        director_counts[director_name] = (
                            director_counts.get(director_name, 0) + 1
                        )
                        break  # Only first director per movie

        if not director_counts:
            return None

        max_count = max(director_counts.values())
        if max_count < 3:
            return None

        frequent_director = max(director_counts, key=director_counts.get)
        self.logger.info(
            f"Frequent director '{frequent_director}' appears {max_count}x in recent ratings"
        )
        return frequent_director

    def _boost_repeated_director(
        self,
        predictions: Dict[int, float],
        base_predictions: Dict,
        candidate_features_matrix: np.ndarray,
        candidate_movie_ids: np.ndarray,
        frequent_director: str,
        user_ratings: pd.DataFrame,
    ) -> None:
        """Boostuje top film frequent directora o 2.0 (wybór po base_sim)"""
        dir_col_name = f"director_{frequent_director}"
        if dir_col_name not in self.feature_names:
            self.logger.warning(f"Director column '{dir_col_name}' not in features")
            return

        dir_col_idx = self.feature_names.index(dir_col_name)

        candidates_with_director = []
        for i, candidate_movie_id in enumerate(candidate_movie_ids):
            if candidate_features_matrix[i, dir_col_idx] > 0:
                # Wyklucz ocenione
                if candidate_movie_id not in user_ratings["movie_id"].values:
                    base_sim = base_predictions.get(candidate_movie_id, {}).get(
                        "max_base_sim", 0.0
                    )
                    candidates_with_director.append((candidate_movie_id, base_sim))

        if not candidates_with_director:
            return

        # Wybierz top 1 po base_sim
        candidates_with_director.sort(key=lambda x: x[1], reverse=True)
        boosted_movie_id = candidates_with_director[0][0]
        boost_value = 2.0
        predictions[boosted_movie_id] = (
            predictions.get(boosted_movie_id, DEFAULT_RATING) + boost_value
        )

        self.logger.info(
            f"Boosted movie {boosted_movie_id} (+{boost_value}) for frequent director '{frequent_director}'"
        )

    def _apply_director_bonus(
        self,
        base_similarities: np.ndarray,
        neighbor_indices: np.ndarray,
        candidate_vector: np.ndarray,
    ) -> np.ndarray:
        """Aplikuje bonus za director match jeśli base_sim >= MIN_SIMILARITY_THRESHOLD"""
        adjusted_similarities = base_similarities.copy()

        for j, (sim, idx) in enumerate(zip(base_similarities, neighbor_indices)):
            if sim < MIN_SIMILARITY_THRESHOLD:
                continue

            neighbor_vector = self.fitted_features[idx]

            # Check director match
            has_same_director = False
            for dir_idx in self.director_indices:
                if candidate_vector[0, dir_idx] > 0 and neighbor_vector[dir_idx] > 0:
                    has_same_director = True
                    break

            if has_same_director:
                adjusted_similarities[j] += DIRECTOR_BONUS  # Additive bonus
                # Reduce log spam (tylko dla debug)
                # self.logger.debug(f"Director match bonus for neighbor {self.movie_ids[idx]}")

        return adjusted_similarities

    def _calculate_weighted_average(
        self, indices: np.ndarray, similarities: np.ndarray, user_ratings: pd.DataFrame
    ) -> float:
        """Weighted average k-NN (pomijaj sim < MIN_SIMILARITY_THRESHOLD)"""
        weighted_sum = 0.0
        similarity_sum = 0.0

        for idx, similarity in zip(indices, similarities):
            if similarity < MIN_SIMILARITY_THRESHOLD:
                continue

            neighbor_movie_id = self.movie_ids[idx]
            neighbor_ratings = user_ratings[
                user_ratings["movie_id"] == neighbor_movie_id
            ]["rating"].values

            if len(neighbor_ratings) > 0:
                rating = neighbor_ratings[0]
                weighted_sum += similarity * rating
                similarity_sum += similarity

        if similarity_sum == 0:
            return DEFAULT_RATING

        # Clamp [1, 10]
        return max(1.0, min(10.0, weighted_sum / similarity_sum))

    def get_similar_movies(
        self, movie_features: pd.DataFrame, target_movie_id: int, n_similar: int = 5
    ) -> List[Tuple[int, float]]:
        """Znajdź podobne filmy (dla explain/UI)"""
        if self.fitted_features is None or self.nbrs is None:
            return []

        target_index = None
        for i, movie_id in enumerate(self.movie_ids):
            if movie_id == target_movie_id:
                target_index = i
                break

        if target_index is None:
            return []

        target_vector = self.fitted_features[target_index : target_index + 1]

        try:
            distances, indices = self.nbrs.kneighbors(
                target_vector,
                n_neighbors=min(n_similar + 1, len(self.fitted_features)),
                return_distance=True,
            )
            base_similarities = 1 - distances[0]

            adjusted_similarities = self._apply_director_bonus(
                base_similarities, indices[0], target_vector
            )

            similar_indices = []
            for j, idx in enumerate(indices[0]):
                if idx != target_index:
                    similarity_score = adjusted_similarities[j]
                    if similarity_score >= MIN_SIMILARITY_THRESHOLD:
                        similar_indices.append(
                            (self.movie_ids[idx], float(similarity_score))
                        )

            similar_movies = sorted(similar_indices, key=lambda x: x[1], reverse=True)[
                :n_similar
            ]
            return similar_movies

        except Exception as e:
            self.logger.error(f"Error in get_similar_movies: {e}")
            return []

    def get_feature_importance(self, feature_names: List[str]) -> Dict[str, float]:
        """Analizuje ważność cech (variance-based)"""
        if self.fitted_features is None:
            return {}

        feature_variances = np.var(self.fitted_features, axis=0)
        importance_dict = {}

        for i, feature_name in enumerate(feature_names):
            if i < len(feature_variances):
                importance_dict[feature_name] = float(feature_variances[i])

        total_importance = sum(importance_dict.values())
        if total_importance > 0:
            importance_dict = {
                k: v / total_importance for k, v in importance_dict.items()
            }

        return importance_dict

    def get_model_info(self) -> Dict:
        """Zwraca info o modelu KNN"""
        if self.fitted_features is None:
            return {"error": "Model nie został wytrenowany"}

        return {
            "algorithm": f"k-NN NearestNeighbors ({KNN_METRIC} + director bonus {DIRECTOR_BONUS} + frequent director boost)",
            "n_training_items": len(self.movie_ids),
            "n_features": self.fitted_features.shape[1],
            "similarity_metric": f"{KNN_METRIC} (cosine) z bonusem {DIRECTOR_BONUS} za reżysera (min threshold {MIN_SIMILARITY_THRESHOLD})",
            "default_rating": DEFAULT_RATING,
            "recent_ratings_limit": RECENT_RATINGS_LIMIT,
            "knn_neighbors": KNN_NEIGHBORS,
        }
