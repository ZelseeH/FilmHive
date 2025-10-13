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
        self.director_indices = None  # Indeksy kolumn reżyserów dla bonusu
        self.user_ratings = None
        self.nbrs = None  # NearestNeighbors model
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

        # Zapisz indeksy kolumn reżyserów dla bonusu
        self.director_indices = [
            i for i, col in enumerate(self.feature_names) if col.startswith("director_")
        ]

        # Trenuj NearestNeighbors
        self.nbrs = NearestNeighbors(
            n_neighbors=min(KNN_NEIGHBORS, len(self.fitted_features)),
            metric=KNN_METRIC,
            algorithm="auto",
        ).fit(self.fitted_features)

        all_columns = self.feature_names
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
                col_idx = self.feature_names.index(col)
                nolan_movies = self.movie_ids[self.fitted_features[:, col_idx] > 0]
                self.logger.info(f"DEBUG k-NN FIT: {col} ma filmy: {nolan_movies}")

        self.logger.info(f"DEBUG k-NN FIT: Trenuje na filmach: {self.movie_ids}")
        self.logger.info(
            f"k-NN wytrenowany na {len(self.fitted_features)} filmach z {self.fitted_features.shape[1]} cechami "
            f"(NearestNeighbors z {KNN_METRIC} metryką)"
        )

    def predict_ratings(
        self, candidate_features: pd.DataFrame, user_ratings: pd.DataFrame
    ) -> Dict[int, float]:
        """Przewiduje oceny używając NearestNeighbors + hybrid similarity: exact director match bonus"""
        if self.fitted_features is None or self.nbrs is None:
            raise ValueError("Model nie został wytrenowany. Użyj najpierw fit()")

        predictions = {}
        candidate_movie_ids = candidate_features["movie_id"].values
        candidate_features_only = candidate_features.drop("movie_id", axis=1)
        candidate_features_matrix = candidate_features_only.values.astype(float)

        # Sprawdź cechy reżyserów w kandydatach (dla debugu)
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

        # Oblicz base predictions dla wszystkich kandydatów
        base_predictions = {}
        top_predictions = []

        for i, candidate_movie_id in enumerate(candidate_movie_ids):
            candidate_vector = candidate_features_matrix[i : i + 1]

            # Znajdź k nearest neighbors (dla cosine, distance = 1 - sim)
            distances, indices = self.nbrs.kneighbors(
                candidate_vector, n_neighbors=KNN_NEIGHBORS, return_distance=True
            )
            base_similarities = 1 - distances[0]  # Konwersja distance na similarity

            # Aplikuj bonus za director match
            adjusted_similarities = self._apply_director_bonus(
                base_similarities, indices[0], candidate_vector
            )

            # Oblicz przewidywaną ocenę tylko na ważonych sąsiadach po bonusie
            predicted_rating = self._calculate_weighted_average(
                indices[0], adjusted_similarities, user_ratings
            )

            base_predictions[candidate_movie_id] = {
                "rating": predicted_rating,
                "max_base_sim": max(base_similarities),
            }

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
                    f"DEBUG: Film Nolana {candidate_movie_id} dostał base score: {predicted_rating:.3f}"
                )

            top_predictions.append(
                (candidate_movie_id, predicted_rating, max(base_similarities))
            )

        # Nowa logika: Identyfikuj frequent director z recent ratings i boostuj jeden kandydata
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

        top_predictions = [
            (mid, predictions[mid], base_predictions[mid]["max_base_sim"])
            for mid in candidate_movie_ids
        ]
        top_predictions.sort(key=lambda x: x[1], reverse=True)
        self.logger.info(
            f"DEBUG k-NN PREDICT: Top 10 predykcji (po boostach): {top_predictions[:10]}"
        )

        return predictions

    def _identify_frequent_director(self, user_ratings: pd.DataFrame) -> Optional[str]:
        """Identyfikuje najczęściej powtarzającego się reżysera w ostatnich RECENT_RATINGS_LIMIT ocenach (min 3 filmy)"""
        recent_ratings = user_ratings.head(
            RECENT_RATINGS_LIMIT
        )  # Zakładając sortowane po dacie (malejąco)
        if len(recent_ratings) < 3:
            self.logger.info(
                f"DEBUG: Za mało recent ratings ({len(recent_ratings)} < 3), brak boostu dla repeated director"
            )
            return None

        # Mapuj movie_id na director (używając self.fitted_features; załóż, że user_ratings ma movie_id w fitted)
        director_counts = {}
        for _, rating_row in recent_ratings.iterrows():
            movie_id = rating_row["movie_id"]
            movie_idx = np.where(self.movie_ids == movie_id)[0]
            if len(movie_idx) > 0:
                movie_features = self.fitted_features[movie_idx[0]]
                for dir_idx in self.director_indices:
                    if movie_features[dir_idx] > 0:
                        director_col = self.feature_names[
                            dir_idx
                        ]  # np. 'director_nolan'
                        director_name = director_col.replace(
                            "director_", ""
                        )  # np. 'nolan'
                        director_counts[director_name] = (
                            director_counts.get(director_name, 0) + 1
                        )
                        break

        if not director_counts:
            return None

        # Znajdź director z max count >=3
        max_count = max(director_counts.values())
        if max_count < 3:
            self.logger.info(
                f"DEBUG: Żaden director nie powtarza się >=3 razy w recent {RECENT_RATINGS_LIMIT} ratings"
            )
            return None

        frequent_director = max(director_counts, key=director_counts.get)
        self.logger.info(
            f"DEBUG: Frequent director '{frequent_director}' pojawia się {max_count} razy w recent ratings - boost aktywny"
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
        """Boostuje co najwyżej jeden inny film frequent directora o 2.0 w score, wybierając ten z najwyższym base_sim"""
        # Znajdź kandydatów z frequent_director (wyklucz ocenione)
        candidates_with_director = []
        for i, candidate_movie_id in enumerate(candidate_movie_ids):
            # Sprawdź jeśli ma director (kolumna 'director_{frequent_director}')
            dir_col_idx = None
            for j, col in enumerate(self.feature_names):
                if col == f"director_{frequent_director}":
                    dir_col_idx = j
                    break
            if (
                dir_col_idx is not None
                and candidate_features_matrix[i, dir_col_idx] > 0
            ):
                # Wyklucz jeśli już oceniony
                if candidate_movie_id not in user_ratings["movie_id"].values:
                    base_sim = base_predictions[candidate_movie_id]["max_base_sim"]
                    candidates_with_director.append((candidate_movie_id, base_sim, i))

        if not candidates_with_director:
            self.logger.info(
                f"DEBUG: Brak innych filmów dla frequent director '{frequent_director}' wśród kandydatów"
            )
            return

        # Wybierz jeden z najwyższym base_sim
        candidates_with_director.sort(key=lambda x: x[1], reverse=True)
        boosted_movie_id = candidates_with_director[0][0]
        boost_value = 2.0  # Stały boost, aby podnieść wysoko w top
        predictions[boosted_movie_id] += boost_value

        self.logger.info(
            f"DEBUG: Boost {boost_value} dla filmu {boosted_movie_id} (frequent director '{frequent_director}', base_sim {candidates_with_director[0][1]:.3f})"
        )

    def _apply_director_bonus(
        self,
        base_similarities: np.ndarray,
        neighbor_indices: np.ndarray,
        candidate_vector: np.ndarray,
    ) -> np.ndarray:
        """Aplikuje bonus za exact director match tylko jeśli base_sim >= MIN_SIMILARITY_THRESHOLD"""
        adjusted_similarities = base_similarities.copy()

        for j, (sim, idx) in enumerate(zip(base_similarities, neighbor_indices)):
            if sim < MIN_SIMILARITY_THRESHOLD:
                continue  # Pomijaj słabe podobieństwa, bez bonusu

            has_same_director = False
            neighbor_vector = self.fitted_features[idx]

            # Sprawdź match z reżyserem kandydata
            for dir_idx in self.director_indices:
                if candidate_vector[0, dir_idx] > 0 and neighbor_vector[dir_idx] > 0:
                    has_same_director = True
                    break

            if has_same_director:
                adjusted_similarities[j] += DIRECTOR_BONUS  # Addytywny bonus
                self.logger.info(
                    f"DEBUG: Director match bonus dla sąsiada {self.movie_ids[idx]} -> adjusted sim: {adjusted_similarities[j]:.3f}"
                )

        return adjusted_similarities

    def _calculate_weighted_average(
        self, indices: np.ndarray, similarities: np.ndarray, user_ratings: pd.DataFrame
    ) -> float:
        """Klasyczne k-NN: średnia ważona podobieństwem, pomijając sim < MIN_SIMILARITY_THRESHOLD"""
        weighted_sum = 0.0
        similarity_sum = 0.0

        for idx, similarity in zip(indices, similarities):
            if similarity < MIN_SIMILARITY_THRESHOLD:  # Filtruj po adjusted sim
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
            return DEFAULT_RATING  # Użyj z config

        return max(1.0, min(10.0, weighted_sum / similarity_sum))

    def get_similar_movies(
        self, movie_features: pd.DataFrame, target_movie_id: int, n_similar: int = 5
    ) -> List[Tuple[int, float]]:
        """Znajdź podobne filmy używając NearestNeighbors + hybrid similarity"""
        if self.fitted_features is None or self.nbrs is None:
            raise ValueError("Model nie został wytrenowany")

        target_index = None
        for i, movie_id in enumerate(self.movie_ids):
            if movie_id == target_movie_id:
                target_index = i
                break

        if target_index is None:
            return []

        target_vector = self.fitted_features[target_index : target_index + 1]

        # Znajdź k nearest (w tym siebie)
        distances, indices = self.nbrs.kneighbors(
            target_vector, n_neighbors=n_similar + 1, return_distance=True
        )
        base_similarities = 1 - distances[0]

        # Aplikuj bonus (choć dla target vs training, bonus dla matchy z sobą jest trivial)
        adjusted_similarities = self._apply_director_bonus(
            base_similarities, indices[0], target_vector
        )

        # Wyklucz siebie i posortuj
        similar_indices = []
        for j, idx in enumerate(indices[0]):
            if idx != target_index:
                similarity_score = adjusted_similarities[j]
                if similarity_score >= MIN_SIMILARITY_THRESHOLD:
                    similar_indices.append((self.movie_ids[idx], similarity_score))

        similar_movies = sorted(similar_indices, key=lambda x: x[1], reverse=True)[
            :n_similar
        ]

        return similar_movies

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
            "algorithm": f"k-NN NearestNeighbors ({KNN_METRIC} + director match bonus {DIRECTOR_BONUS} + repeated director boost)",
            "n_training_items": len(self.movie_ids),
            "n_features": self.fitted_features.shape[1],
            "similarity_metric": f"{KNN_METRIC} z bonusem {DIRECTOR_BONUS} za reżysera (min threshold {MIN_SIMILARITY_THRESHOLD})",
            "default_rating": DEFAULT_RATING,
            "recent_ratings_limit": RECENT_RATINGS_LIMIT,
        }
