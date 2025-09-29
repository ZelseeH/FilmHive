from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import logging

from ..config import KNN_NEIGHBORS, KNN_METRIC


class KNNRecommender:
    def __init__(self):
        self.fitted_features = None
        self.movie_ids = None
        self.feature_names = None
        self.user_ratings = None
        self.logger = logging.getLogger(__name__)

    def fit(self, features_matrix: pd.DataFrame, user_ratings: pd.DataFrame) -> None:
        """Trenuje model k-NN na cechach strukturalnych ocenionych filmów"""
        if features_matrix.empty or user_ratings.empty:
            raise ValueError("Brak danych do trenowania")

        self.movie_ids = features_matrix["movie_id"].values
        features_only = features_matrix.drop("movie_id", axis=1)
        self.feature_names = features_only.columns.tolist()
        self.fitted_features = features_only.values.astype(float)
        self.user_ratings = user_ratings

        all_columns = features_only.columns.tolist()
        director_columns = [col for col in all_columns if col.startswith("director_")]
        genre_columns = [col for col in all_columns if col.startswith("genre_")]
        actor_columns = [col for col in all_columns if col.startswith("actor_")]

        self.logger.info(f"DEBUG k-NN FIT: Wszystkich cech: {len(all_columns)}")
        self.logger.info(f"DEBUG k-NN FIT: Cech reżyserów: {len(director_columns)}")
        self.logger.info(f"DEBUG k-NN FIT: Cech gatunków: {len(genre_columns)}")
        self.logger.info(f"DEBUG k-NN FIT: Cech aktorów: {len(actor_columns)}")

        nolan_columns = [
            col
            for col in director_columns
            if "nolan" in col.lower() or "christopher" in col.lower()
        ]
        self.logger.info(f"DEBUG k-NN FIT: Cechy Nolana: {nolan_columns}")

        if nolan_columns:
            for col in nolan_columns:
                col_idx = features_only.columns.get_loc(col)
                nolan_movies = self.movie_ids[self.fitted_features[:, col_idx] > 0]
                self.logger.info(f"DEBUG k-NN FIT: {col} ma filmy: {nolan_movies}")

        self.logger.info(f"DEBUG k-NN FIT: Trenuje na filmach: {self.movie_ids}")
        self.logger.info(
            f"k-NN wytrenowany na {len(self.fitted_features)} filmach z {self.fitted_features.shape[1]} cechami"
        )

    def predict_ratings(
        self, candidate_features: pd.DataFrame, user_ratings: pd.DataFrame
    ) -> Dict[int, float]:
        """Przewiduje oceny używając hybrid similarity: exact director match + cosine"""
        if self.fitted_features is None:
            raise ValueError("Model nie został wytrenowany. Użyj najpierw fit()")

        predictions = {}
        candidate_movie_ids = candidate_features["movie_id"].values
        candidate_features_only = candidate_features.drop("movie_id", axis=1)
        candidate_features_matrix = candidate_features_only.values.astype(float)

        director_columns = [
            col
            for col in candidate_features_only.columns
            if col.startswith("director_")
        ]
        nolan_columns = [
            col
            for col in director_columns
            if "nolan" in col.lower() or "christopher" in col.lower()
        ]

        self.logger.info(f"DEBUG k-NN PREDICT: Kandydatów: {len(candidate_movie_ids)}")
        self.logger.info(
            f"DEBUG k-NN PREDICT: Cechy reżyserów kandydatów: {len(director_columns)}"
        )
        self.logger.info(
            f"DEBUG k-NN PREDICT: Cechy Nolana kandydatów: {nolan_columns}"
        )

        if nolan_columns:
            for col in nolan_columns:
                col_idx = candidate_features_only.columns.get_loc(col)
                nolan_candidates = candidate_movie_ids[
                    candidate_features_matrix[:, col_idx] > 0
                ]
                if len(nolan_candidates) > 0:
                    self.logger.info(
                        f"DEBUG k-NN PREDICT: {col} - kandydaci: {nolan_candidates}"
                    )

        top_predictions = []

        for i, candidate_movie_id in enumerate(candidate_movie_ids):
            candidate_vector = candidate_features_matrix[i : i + 1]

            # HYBRID SIMILARITY: cosine + director match bonus
            similarities = self._hybrid_similarity(
                candidate_vector, self.fitted_features, candidate_features_only.columns
            )

            # Znajdź k najbliższych sąsiadów
            k = min(KNN_NEIGHBORS, len(similarities))
            nearest_indices = np.argsort(similarities)[-k:]
            nearest_similarities = similarities[nearest_indices]

            # Oblicz przewidywaną ocenę
            predicted_rating = self._calculate_weighted_average(
                nearest_indices, nearest_similarities, user_ratings
            )

            predictions[candidate_movie_id] = predicted_rating

            # Debug dla filmów Nolana
            if nolan_columns and any(
                candidate_features_matrix[
                    i, candidate_features_only.columns.get_loc(col)
                ]
                > 0
                for col in nolan_columns
            ):
                self.logger.info(
                    f"DEBUG: Film Nolana {candidate_movie_id} dostał score: {predicted_rating:.3f}"
                )

            top_predictions.append(
                (candidate_movie_id, predicted_rating, max(similarities))
            )

        top_predictions.sort(key=lambda x: x[1], reverse=True)
        self.logger.info(
            f"DEBUG k-NN PREDICT: Top 10 predykcji: {top_predictions[:10]}"
        )

        return predictions

    def _hybrid_similarity(
        self, candidate_vector: np.ndarray, training_features: np.ndarray, feature_names
    ) -> np.ndarray:
        """Hybrid: exact director match + cosine similarity"""

        # Standardowe cosine similarity
        similarities = cosine_similarity(candidate_vector, training_features)[0]

        # Znajdź indeksy kolumn reżyserów
        director_indices = [
            i for i, col in enumerate(feature_names) if col.startswith("director_")
        ]

        # Bonus za exact director match
        for i, sim in enumerate(similarities):
            has_same_director = False

            # Sprawdź czy ma tego samego reżysera
            for dir_idx in director_indices:
                if (
                    candidate_vector[0, dir_idx] > 0
                    and training_features[i, dir_idx] > 0
                ):
                    has_same_director = True
                    break

            if has_same_director:
                similarities[i] += 0.8  # MASSIVE BONUS for same director
                self.logger.info(
                    f"DEBUG: Director match bonus for training movie {self.movie_ids[i]} -> similarity: {similarities[i]:.3f}"
                )

        return similarities

    def _calculate_weighted_average(
        self, indices: np.ndarray, similarities: np.ndarray, user_ratings: pd.DataFrame
    ) -> float:
        """Klasyczne k-NN: średnia ważona podobieństwem"""
        weighted_sum = 0.0
        similarity_sum = 0.0

        for idx, similarity in zip(indices, similarities):
            if similarity <= 0:  # Pomijaj ujemne podobieństwa
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
            return 3.0  # Default low rating

        return max(1.0, min(10.0, weighted_sum / similarity_sum))

    def get_similar_movies(
        self, movie_features: pd.DataFrame, target_movie_id: int, n_similar: int = 5
    ) -> List[Tuple[int, float]]:
        """Znajdź podobne filmy używając hybrid similarity"""
        if self.fitted_features is None:
            raise ValueError("Model nie został wytrenowany")

        target_index = None
        for i, movie_id in enumerate(self.movie_ids):
            if movie_id == target_movie_id:
                target_index = i
                break

        if target_index is None:
            return []

        target_vector = self.fitted_features[target_index : target_index + 1]
        similarities = self._hybrid_similarity(
            target_vector, self.fitted_features, self.feature_names
        )

        # Znajdź n najbardziej podobnych (bez samego siebie)
        similar_indices = np.argsort(similarities)[-n_similar - 1 : -1]
        similar_movies = []

        for idx in similar_indices:
            if idx != target_index:
                similarity_score = similarities[idx]
                similar_movie_id = self.movie_ids[idx]
                similar_movies.append((similar_movie_id, similarity_score))

        return sorted(similar_movies, key=lambda x: x[1], reverse=True)

    def get_feature_importance(self, feature_names: List[str]) -> Dict[str, float]:
        """Analizuje ważność cech w modelu"""
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
        """Zwraca informacje o modelu"""
        if self.fitted_features is None:
            return {"error": "Model nie został wytrenowany"}

        return {
            "algorithm": "Hybrid k-NN (cosine + director match bonus)",
            "n_training_items": len(self.movie_ids),
            "n_features": self.fitted_features.shape[1],
            "similarity_metric": "cosine + director bonus",
        }
