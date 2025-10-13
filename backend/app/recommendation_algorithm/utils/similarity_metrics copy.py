import numpy as np
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from scipy.spatial.distance import jaccard
from typing import Dict, List, Tuple, Optional, Union
import pandas as pd
from collections import Counter

from ..config import (
    POSITIVE_RATING_THRESHOLD,  # 7.0 dla patterns
    ENSEMBLE_KNN_WEIGHT,
    ENSEMBLE_NB_WEIGHT,  # 0.6, 0.4
    ADAPTIVE_BASE_GENRE_WEIGHT,
    ADAPTIVE_BASE_ACTOR_WEIGHT,
    ADAPTIVE_BASE_DIRECTOR_WEIGHT,  # 0.3, 0.3, 0.25
    YEAR_MAX_DIFF,
    DURATION_MAX_DIFF,  # 20, 180
    DIRECTOR_BONUS,
    ACTOR_BONUS,  # 0.1, 0.05 (dla adaptive cosine)
    TOP_ACTORS_IN_PATTERN,  # 3
    ADAPTIVE_BASE_WEIGHT,
    ADAPTIVE_SCALING_FACTOR,  # 0.1, 0.7 (jak w DataPreprocessor)
)


class SimilarityMetrics:
    """
    Klasa z metrykami podobieństwa dla content-based recsys (Pazzani & Billsus).
    Wspiera hybrydę strukturalną (cosine/Jaccard) + tekstową (TF-IDF cosine).
    """

    def __init__(self):
        pass

    def cosine_similarity_score(
        self, vector1: np.ndarray, vector2: np.ndarray
    ) -> float:
        """Cosine similarity dla high-dim vectors (strukturalne/TF-IDF, sekcja 3.1)"""
        if vector1.shape != vector2.shape:
            raise ValueError("Wektory muszą mieć te same wymiary")

        # Reshape do 2D
        vector1 = vector1.reshape(1, -1) if len(vector1.shape) == 1 else vector1
        vector2 = vector2.reshape(1, -1) if len(vector2.shape) == 1 else vector2

        similarity = cosine_similarity(vector1, vector2)[0][0]
        return float(similarity)

    def adaptive_cosine_similarity(
        self,
        vector1: np.ndarray,
        vector2: np.ndarray,
        feature_names: List[str],
        bonuses: Dict[str, float] = None,  # np. {"director_Nolan": 0.1}
    ) -> float:
        """
        Adaptive cosine z bonusami za matching features (user patterns, sekcja 4).
        Bonusy tylko dla overlapping non-zero.
        """
        base_sim = self.cosine_similarity_score(vector1, vector2)

        if bonuses is None:
            return base_sim

        # Znajdź overlapping features z bonusami (np. shared director)
        v1_nonzero = set(np.where(vector1 > 0)[0])
        v2_nonzero = set(np.where(vector2 > 0)[0])
        overlap = v1_nonzero & v2_nonzero
        total_bonus = 0.0
        for idx in overlap:
            feat = feature_names[idx] if idx < len(feature_names) else None
            if feat and feat in bonuses:
                total_bonus += bonuses[feat]

        enhanced_sim = min(1.0, base_sim + total_bonus)
        return enhanced_sim

    def euclidean_similarity_score(
        self, vector1: np.ndarray, vector2: np.ndarray
    ) -> float:
        """Euclidean-based similarity (1/(1+dist)) dla low-dim (year/duration)"""
        if vector1.shape != vector2.shape:
            raise ValueError("Wektory muszą mieć te same wymiary")

        vector1 = vector1.reshape(1, -1) if len(vector1.shape) == 1 else vector1
        vector2 = vector2.reshape(1, -1) if len(vector2.shape) == 1 else vector2

        distance = euclidean_distances(vector1, vector2)[0][0]
        similarity = 1.0 / (1.0 + distance)
        return float(similarity)

    def jaccard_similarity_score(
        self, set1: Union[set, List], set2: Union[set, List]
    ) -> float:
        """Jaccard dla sets (genres/actors/directors, sekcja 3.1)"""
        set1 = set(set1) if not isinstance(set1, set) else set1
        set2 = set(set2) if not isinstance(set2, set) else set2

        if len(set1) == 0 and len(set2) == 0:
            return 1.0

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return float(intersection / union) if union > 0 else 0.0

    def weighted_jaccard_similarity(
        self,
        set1: Union[set, List],
        set2: Union[set, List],
        element_weights: Optional[Dict[str, float]] = None,
    ) -> float:
        """
        Weighted Jaccard (ważone intersection/union, np. lead actor 2x).
        """
        set1 = set(set1) if not isinstance(set1, set) else set1
        set2 = set(set2) if not isinstance(set2, set) else set2

        if len(set1) == 0 and len(set2) == 0:
            return 1.0

        if element_weights is None:
            return self.jaccard_similarity_score(set1, set2)

        intersection = set1.intersection(set2)
        union = set1.union(set2)

        weighted_inter = sum(element_weights.get(elem, 1.0) for elem in intersection)
        weighted_union = sum(element_weights.get(elem, 1.0) for elem in union)

        return float(weighted_inter / weighted_union) if weighted_union > 0 else 0.0

    def weighted_similarity(
        self, similarities: Dict[str, float], weights: Dict[str, float]
    ) -> float:
        """Ważona średnia podobieństw (multi-attribute, sekcja 5)"""
        if not similarities or not weights:
            return 0.0

        weighted_sum = sum(sim * weights.get(k, 0.0) for k, sim in similarities.items())
        weight_sum = sum(weights.values())
        return weighted_sum / weight_sum if weight_sum > 0 else 0.0

    def adaptive_weighted_similarity(
        self,
        similarities: Dict[str, float],
        base_weights: Dict[str, float],
        adaptation_factors: Dict[str, float],  # (user_pref - base)/base lub config
    ) -> float:
        """
        Adaptive weighted (dynamic weights z patterns, sekcja 4.3).
        """
        if not similarities or not base_weights:
            return 0.0

        adaptive_weights = {}
        for k, base_w in base_weights.items():
            adapt = adaptation_factors.get(k, 0.0)
            adaptive_w = base_w * (1.0 + adapt)  # Positive boost; cap negative?
            adaptive_weights[k] = max(0.0, adaptive_w)

        total_w = sum(adaptive_weights.values())
        if total_w > 0:
            adaptive_weights = {k: v / total_w for k, v in adaptive_weights.items()}

        return self.weighted_similarity(similarities, adaptive_weights)

    def combine_algorithm_scores(
        self,
        knn_scores: Dict[int, float],  # High = similar (cosine)
        nb_scores: Dict[int, float],  # High = P(positive)
        knn_weight: float = ENSEMBLE_KNN_WEIGHT,
        nb_weight: float = ENSEMBLE_NB_WEIGHT,
    ) -> Dict[int, float]:
        """Ensemble KNN (strukturalne) + NB (tekstowe, sekcja 5)"""
        knn_norm = self._normalize_scores(knn_scores)
        nb_norm = self._normalize_scores(nb_scores)

        all_ids = set(knn_norm) | set(nb_norm)
        combined = {}
        for mid in all_ids:
            combined[mid] = knn_weight * knn_norm.get(
                mid, 0.0
            ) + nb_weight * nb_norm.get(mid, 0.0)
        return combined

    def adaptive_algorithm_combination(
        self,
        knn_scores: Dict[int, float],
        nb_scores: Dict[int, float],
        user_preference_strength: float = 0.0,  # 0-1 z analyze_patterns (max strength)
    ) -> Dict[int, float]:
        """
        Adaptive ensemble: Boost KNN jeśli silne patterns strukturalne.
        """
        if user_preference_strength > 0.5:
            knn_w = min(0.9, ENSEMBLE_KNN_WEIGHT + user_preference_strength * 0.3)
            nb_w = 1.0 - knn_w
        else:
            knn_w, nb_w = ENSEMBLE_KNN_WEIGHT, ENSEMBLE_NB_WEIGHT

        return self.combine_algorithm_scores(knn_scores, nb_scores, knn_w, nb_w)

    def calculate_movie_similarity(
        self, movie1_features: Dict, movie2_features: Dict
    ) -> Dict[str, float]:
        """Multi-attribute sim (Jaccard sets + normalized diff numerycznych, sekcja 3.1)"""
        similarities = {}

        # Jaccard genres
        if "genres" in movie1_features and "genres" in movie2_features:
            similarities["genres"] = self.jaccard_similarity_score(
                movie1_features["genres"], movie2_features["genres"]
            )

        # Jaccard actors
        if "actors" in movie1_features and "actors" in movie2_features:
            similarities["actors"] = self.jaccard_similarity_score(
                movie1_features["actors"], movie2_features["actors"]
            )

        # Jaccard directors (key dla patterns)
        if "directors" in movie1_features and "directors" in movie2_features:
            similarities["directors"] = self.jaccard_similarity_score(
                movie1_features["directors"], movie2_features["directors"]
            )

        # Year diff (normalized na dataset max)
        if "release_year" in movie1_features and "release_year" in movie2_features:
            year_diff = abs(
                movie1_features["release_year"] - movie2_features["release_year"]
            )
            similarities["year"] = max(0.0, 1.0 - (year_diff / YEAR_MAX_DIFF))

        # Duration diff
        if (
            "duration_minutes" in movie1_features
            and "duration_minutes" in movie2_features
        ):
            dur_diff = abs(
                movie1_features["duration_minutes"]
                - movie2_features["duration_minutes"]
            )
            similarities["duration"] = max(0.0, 1.0 - (dur_diff / DURATION_MAX_DIFF))

        return similarities

    def calculate_adaptive_movie_similarity(
        self,
        movie1_features: Dict,
        movie2_features: Dict,
        user_preferences: Dict[str, float],  # z DataPreprocessor: {"directors": 0.5}
    ) -> Dict[str, float]:
        """
        Adaptive movie sim z user weights (sekcja 4.3).
        Adaptation: (user_w / base_w - 1) dla positive boost.
        """
        base_sim = self.calculate_movie_similarity(movie1_features, movie2_features)

        base_weights = {
            "genres": ADAPTIVE_BASE_GENRE_WEIGHT,
            "actors": ADAPTIVE_BASE_ACTOR_WEIGHT,
            "directors": ADAPTIVE_BASE_DIRECTOR_WEIGHT,
            "year": 0.1,
            "duration": 0.05,
        }

        # Adaptation factors: positive jeśli user_pref > base
        adapt_factors = {}
        for feat, base_w in base_weights.items():
            user_w = user_preferences.get(feat, base_w)
            adapt_factors[feat] = (
                (user_w / base_w - 1.0) if base_w > 0 else 0.0
            )  # Avoid div0

        adaptive_total = self.adaptive_weighted_similarity(
            base_sim, base_weights, adapt_factors
        )

        return {"adaptive_total": adaptive_total, **base_sim}

    def _normalize_scores(self, scores: Dict[int, float]) -> Dict[int, float]:
        """Min-max norm do [0,1] (dla ensemble różnych skal)"""
        if not scores:
            return {}

        vals = list(scores.values())
        min_s, max_s = min(vals), max(vals)

        if max_s == min_s:
            return {mid: 0.5 for mid in scores}

        return {mid: (s - min_s) / (max_s - min_s) for mid, s in scores.items()}

    def calculate_user_profile_similarity(
        self,
        user_profile: Dict,  # {"preferred_directors": ["Nolan"]}
        movie_features: Dict,
        profile_weights: Optional[Dict[str, float]] = None,
    ) -> float:
        """Sim profilu user-movie (Jaccard na preferred sets, sekcja 4)"""
        if profile_weights is None:
            profile_weights = {
                "genres": 0.4,
                "actors": 0.3,
                "directors": 0.2,
                "other": 0.1,
            }

        similarities = {}

        # Genres
        if "preferred_genres" in user_profile and "genres" in movie_features:
            similarities["genres"] = self.jaccard_similarity_score(
                user_profile["preferred_genres"], movie_features["genres"]
            )

        # Actors
        if "preferred_actors" in user_profile and "actors" in movie_features:
            similarities["actors"] = self.jaccard_similarity_score(
                user_profile["preferred_actors"], movie_features["actors"]
            )

        # Directors
        if "preferred_directors" in user_profile and "directors" in movie_features:
            similarities["directors"] = self.jaccard_similarity_score(
                user_profile["preferred_directors"], movie_features["directors"]
            )

        return self.weighted_similarity(similarities, profile_weights)

    def analyze_preference_patterns(self, user_ratings: List[Dict]) -> Dict[str, float]:
        """
        Analiza patterns w high ratings (>= POSITIVE_THRESHOLD) dla wag (sekcja 4).
        Używa Counter; max strength do proportional weights.
        """
        if not user_ratings:
            return {
                "genres": ADAPTIVE_BASE_GENRE_WEIGHT,
                "actors": ADAPTIVE_BASE_ACTOR_WEIGHT,
                "directors": ADAPTIVE_BASE_DIRECTOR_WEIGHT,
            }

        high_rated = [
            r for r in user_ratings if r.get("rating", 0) >= POSITIVE_RATING_THRESHOLD
        ]

        if len(high_rated) < 2:
            return {
                "genres": ADAPTIVE_BASE_GENRE_WEIGHT,
                "actors": ADAPTIVE_BASE_ACTOR_WEIGHT,
                "directors": ADAPTIVE_BASE_DIRECTOR_WEIGHT,
            }

        # Counter dla efektywności
        genre_counts = Counter()
        actor_counts = Counter()
        director_counts = Counter()

        for rating in high_rated:
            genre_counts.update(rating.get("genres", []))
            actor_counts.update(rating.get("actors", [])[:TOP_ACTORS_IN_PATTERN])
            director_counts.update(rating.get("directors", []))

        genre_strength = max(genre_counts.values()) if genre_counts else 0
        actor_strength = max(actor_counts.values()) if actor_counts else 0
        director_strength = max(director_counts.values()) if director_counts else 0

        total_strength = genre_strength + actor_strength + director_strength

        if total_strength == 0:
            return {
                "genres": ADAPTIVE_BASE_GENRE_WEIGHT,
                "actors": ADAPTIVE_BASE_ACTOR_WEIGHT,
                "directors": ADAPTIVE_BASE_DIRECTOR_WEIGHT,
            }

        # Proportional weights (jak DataPreprocessor)
        return {
            "genres": ADAPTIVE_BASE_WEIGHT
            + (genre_strength / total_strength) * ADAPTIVE_SCALING_FACTOR,
            "actors": ADAPTIVE_BASE_WEIGHT
            + (actor_strength / total_strength) * ADAPTIVE_SCALING_FACTOR,
            "directors": ADAPTIVE_BASE_WEIGHT
            + (director_strength / total_strength) * ADAPTIVE_SCALING_FACTOR,
        }

    def rank_recommendations(
        self,
        scores: Dict[int, float],
        movies_metadata: pd.DataFrame,  # Potrzebne do sim (movie_id -> features)
        diversity_factor: float = 0.1,
    ) -> List[Tuple[int, float]]:
        """
        Ranking z MMR dla diversity (sekcja 7: post-processing).
        Pełna: Używa calculate_movie_similarity do avg sim.
        """
        if not scores:
            return []

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        if diversity_factor <= 0 or movies_metadata.empty:
            return ranked

        # MMR: Zbuduj features dict z metadata
        features_dict = {}
        for _, row in movies_metadata.iterrows():
            mid = row["movie_id"]
            features_dict[mid] = {
                "genres": row.get("genres", []),
                "actors": row.get("actors", []),
                "directors": row.get("directors", []),
                "release_year": row.get("release_year", 0),
                "duration_minutes": row.get("duration_minutes", 0),
            }

        final_ranking = []
        remaining = dict(ranked)

        # Pierwszy: max relevance
        if remaining:
            best_item = max(remaining.items(), key=lambda x: x[1])
            final_ranking.append(best_item)
            selected_ids = {best_item[0]}
            del remaining[best_item[0]]

        # Pozostałe: MMR loop
        while remaining and len(final_ranking) < len(ranked):
            best_score = -np.inf
            best_item = None

            for mid, relevance in remaining.items():
                # Avg sim do selected
                sims = []
                for sel_mid in selected_ids:
                    if mid in features_dict and sel_mid in features_dict:
                        movie_sim = self.calculate_movie_similarity(
                            features_dict[mid], features_dict[sel_mid]
                        )
                        # Weighted avg sim (simple mean features)
                        avg_sim = (
                            np.mean(list(movie_sim.values())) if movie_sim else 0.0
                        )
                        sims.append(avg_sim)
                avg_sim = np.mean(sims) if sims else 0.0

                # MMR: (1-λ)*relevance - λ*sim
                mmr = (1 - diversity_factor) * relevance - diversity_factor * avg_sim

                if mmr > best_score:
                    best_score = mmr
                    best_item = (mid, relevance)  # Zachowaj original score

            if best_item:
                final_ranking.append(best_item)
                selected_ids.add(best_item[0])
                del remaining[best_item[0]]

        return final_ranking

    def get_similarity_stats(self, similarities: List[float]) -> Dict[str, float]:
        """Statystyki podobieństw (debug)"""
        if not similarities:
            return {}

        arr = np.array(similarities)
        return {
            "mean": float(np.mean(arr)),
            "median": float(np.median(arr)),
            "std": float(np.std(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "count": len(similarities),
        }

    def get_adaptive_similarity_report(
        self, base_similarities: Dict[str, float], adaptive_weights: Dict[str, float]
    ) -> Dict[str, any]:
        """
        Raport adaptive sim (explainability, sekcja 6).
        """
        weighted = self.weighted_similarity(base_similarities, adaptive_weights)
        strongest = (
            max(adaptive_weights, key=adaptive_weights.get)
            if adaptive_weights
            else None
        )

        return {
            "base_similarities": base_similarities,
            "adaptive_weights": adaptive_weights,
            "weighted_score": weighted,
            "adaptation_summary": {
                "strongest_feature": strongest,
                "weight_distribution": adaptive_weights,
                "total_features": len(base_similarities),
            },
        }
