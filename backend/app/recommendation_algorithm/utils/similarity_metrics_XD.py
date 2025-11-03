import numpy as np
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from scipy.spatial.distance import jaccard
from typing import Dict, List, Tuple, Optional, Union
import pandas as pd
from collections import Counter
import logging

from ..config import (
    POSITIVE_RATING_THRESHOLD,
    ENSEMBLE_KNN_WEIGHT,
    ENSEMBLE_NB_WEIGHT,
    ADAPTIVE_BASE_GENRE_WEIGHT,
    ADAPTIVE_BASE_ACTOR_WEIGHT,
    ADAPTIVE_BASE_DIRECTOR_WEIGHT,
    YEAR_MAX_DIFF,
    DURATION_MAX_DIFF,
    DIRECTOR_BONUS,
    ACTOR_BONUS,
    TOP_ACTORS_IN_PATTERN,
    ADAPTIVE_BASE_WEIGHT,
    ADAPTIVE_SCALING_FACTOR,
)


class SimilarityMetrics:
    """
    Klasa z metrykami podobieństwa dla content-based recsys (Pazzani & Billsus).
    Wspiera hybrydę strukturalną (cosine/Jaccard) + tekstową (TF-IDF cosine).
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def cosine_similarity_score(
        self, vector1: np.ndarray, vector2: np.ndarray
    ) -> float:
        """Cosine similarity dla high-dim vectors (strukturalne/TF-IDF)"""
        if vector1.shape != vector2.shape:
            raise ValueError("Wektory muszą mieć te same wymiary")

        vector1 = vector1.reshape(1, -1) if len(vector1.shape) == 1 else vector1
        vector2 = vector2.reshape(1, -1) if len(vector2.shape) == 1 else vector2

        similarity = cosine_similarity(vector1, vector2)[0][0]
        return float(similarity)

    def adaptive_cosine_similarity(
        self,
        vector1: np.ndarray,
        vector2: np.ndarray,
        feature_names: List[str],
        bonuses: Dict[str, float] = None,
    ) -> float:
        """Adaptive cosine z bonusami za matching features (user patterns)"""
        base_sim = self.cosine_similarity_score(vector1, vector2)

        if bonuses is None:
            return base_sim

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
        """Euclidean-based similarity (1/(1+dist))"""
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
        """Jaccard dla sets (genres/actors/directors)"""
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
        """Weighted Jaccard"""
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
        """Ważona średnia podobieństw"""
        if not similarities or not weights:
            return 0.0

        weighted_sum = sum(sim * weights.get(k, 0.0) for k, sim in similarities.items())
        weight_sum = sum(weights.values())
        return weighted_sum / weight_sum if weight_sum > 0 else 0.0

    def adaptive_weighted_similarity(
        self,
        similarities: Dict[str, float],
        base_weights: Dict[str, float],
        adaptation_factors: Dict[str, float],
    ) -> float:
        """Adaptive weighted (dynamic weights z patterns)"""
        if not similarities or not base_weights:
            return 0.0

        adaptive_weights = {}
        for k, base_w in base_weights.items():
            adapt = adaptation_factors.get(k, 0.0)
            adaptive_w = base_w * (1.0 + adapt)
            adaptive_weights[k] = max(0.0, adaptive_w)

        total_w = sum(adaptive_weights.values())
        if total_w > 0:
            adaptive_weights = {k: v / total_w for k, v in adaptive_weights.items()}

        return self.weighted_similarity(similarities, adaptive_weights)

    def combine_algorithm_scores(
        self,
        knn_scores: Dict[int, float],
        nb_scores: Dict[int, float],
        knn_weight: float = ENSEMBLE_KNN_WEIGHT,
        nb_weight: float = ENSEMBLE_NB_WEIGHT,
    ) -> Dict[int, float]:
        """Ensemble KNN + NB"""
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
        user_preference_strength: float = 0.0,
    ) -> Dict[int, float]:
        """Adaptive ensemble: Boost KNN jeśli silne patterns"""
        if user_preference_strength > 0.5:
            knn_w = min(0.9, ENSEMBLE_KNN_WEIGHT + user_preference_strength * 0.3)
            nb_w = 1.0 - knn_w
        else:
            knn_w, nb_w = ENSEMBLE_KNN_WEIGHT, ENSEMBLE_NB_WEIGHT

        return self.combine_algorithm_scores(knn_scores, nb_scores, knn_w, nb_w)

    def calculate_movie_similarity(
        self, movie1_features: Dict, movie2_features: Dict
    ) -> Dict[str, float]:
        """Multi-attribute sim (Jaccard + normalized diff)"""
        similarities = {}

        if "genres" in movie1_features and "genres" in movie2_features:
            similarities["genres"] = self.jaccard_similarity_score(
                movie1_features["genres"], movie2_features["genres"]
            )

        if "actors" in movie1_features and "actors" in movie2_features:
            similarities["actors"] = self.jaccard_similarity_score(
                movie1_features["actors"], movie2_features["actors"]
            )

        if "directors" in movie1_features and "directors" in movie2_features:
            similarities["directors"] = self.jaccard_similarity_score(
                movie1_features["directors"], movie2_features["directors"]
            )

        if "release_year" in movie1_features and "release_year" in movie2_features:
            year_diff = abs(
                movie1_features["release_year"] - movie2_features["release_year"]
            )
            similarities["year"] = max(0.0, 1.0 - (year_diff / YEAR_MAX_DIFF))

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
        user_preferences: Dict[str, float],
    ) -> Dict[str, float]:
        """Adaptive movie sim z user weights"""
        base_sim = self.calculate_movie_similarity(movie1_features, movie2_features)

        base_weights = {
            "genres": ADAPTIVE_BASE_GENRE_WEIGHT,
            "actors": ADAPTIVE_BASE_ACTOR_WEIGHT,
            "directors": ADAPTIVE_BASE_DIRECTOR_WEIGHT,
            "year": 0.1,
            "duration": 0.05,
        }

        adapt_factors = {}
        for feat, base_w in base_weights.items():
            user_w = user_preferences.get(feat, base_w)
            adapt_factors[feat] = (user_w / base_w - 1.0) if base_w > 0 else 0.0

        adaptive_total = self.adaptive_weighted_similarity(
            base_sim, base_weights, adapt_factors
        )

        return {"adaptive_total": adaptive_total, **base_sim}

    def _normalize_scores(self, scores: Dict[int, float]) -> Dict[int, float]:
        """Min-max norm [0,1]"""
        if not scores:
            return {}

        vals = list(scores.values())
        min_s, max_s = min(vals), max(vals)

        if max_s == min_s:
            return {mid: 0.5 for mid in scores}

        return {mid: (s - min_s) / (max_s - min_s) for mid, s in scores.items()}

    def calculate_user_profile_similarity(
        self,
        user_profile: Dict,
        movie_features: Dict,
        profile_weights: Optional[Dict[str, float]] = None,
    ) -> float:
        """Sim profilu user-movie (Jaccard)"""
        if profile_weights is None:
            profile_weights = {
                "genres": 0.4,
                "actors": 0.3,
                "directors": 0.2,
                "other": 0.1,
            }

        similarities = {}

        if "preferred_genres" in user_profile and "genres" in movie_features:
            similarities["genres"] = self.jaccard_similarity_score(
                user_profile["preferred_genres"], movie_features["genres"]
            )

        if "preferred_actors" in user_profile and "actors" in movie_features:
            similarities["actors"] = self.jaccard_similarity_score(
                user_profile["preferred_actors"], movie_features["actors"]
            )

        if "preferred_directors" in user_profile and "directors" in movie_features:
            similarities["directors"] = self.jaccard_similarity_score(
                user_profile["preferred_directors"], movie_features["directors"]
            )

        return self.weighted_similarity(similarities, profile_weights)

    def analyze_preference_patterns(self, user_ratings: List[Dict]) -> Dict[str, float]:
        """Analiza patterns w high ratings"""
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
        movies_metadata: pd.DataFrame,
        diversity_factor: float = 0.1,
    ) -> List[Tuple[int, float]]:
        """
        FIX: MMR diversity z CONDITIONAL DISABLE jeśli genres overlap wysoki
        Disable jeśli <30% unique genres w top 20 (all same → no penalty, preserve scores)
        """
        if not scores:
            return []

        # Sort by base score (dla check diversity)
        ranked_base = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        if diversity_factor <= 0 or movies_metadata.empty:
            return ranked_base

        # FIX: Check genres diversity w top 20 candidates
        top_20_ids = [mid for mid, _ in ranked_base[:20]]
        genres_in_top = []
        for mid in top_20_ids:
            movie_info = movies_metadata[movies_metadata["movie_id"] == mid]
            if not movie_info.empty:
                genres = movie_info.iloc[0].get("genres", [])
                if isinstance(genres, list):
                    genres_in_top.extend(genres)

        # Calculate unique ratio
        if len(genres_in_top) > 0:
            unique_genres = len(set(genres_in_top))
            total_genres = len(genres_in_top)
            unique_ratio = unique_genres / total_genres
        else:
            unique_ratio = 1.0  # No genres data → assume diverse

        self.logger.info(
            f"MMR diversity check: {len(set(genres_in_top)) if len(genres_in_top)>0 else 0} unique genres in top 20 (ratio={unique_ratio:.2f})"
        )

        # FIX: Disable MMR jeśli low diversity (<30% unique)
        if unique_ratio < 0.3:
            self.logger.warning(
                f"Low genres diversity ({unique_ratio:.2f}) – DISABLE MMR (preserve base scores, no penalty)"
            )
            return ranked_base

        # Apply MMR (reduced λ=diversity_factor, default 0.1)
        self.logger.info(
            f"MMR diversity ON (ratio={unique_ratio:.2f}, λ={diversity_factor})"
        )

        # Build features dict (genres only dla fast similarity)
        features_dict = {}
        for _, row in movies_metadata.iterrows():
            mid = row["movie_id"]
            features_dict[mid] = row.get("genres", [])

        final_ranking = []
        remaining = dict(ranked_base)

        # First item: max relevance (no penalty)
        if remaining:
            best_item = max(remaining.items(), key=lambda x: x[1])
            final_ranking.append(best_item)
            selected_ids = {best_item[0]}
            del remaining[best_item[0]]

        # MMR iteration
        while remaining and len(final_ranking) < 20:
            best_score = -np.inf
            best_item = None

            for mid, relevance in remaining.items():
                # Max sim to selected (Jaccard genres)
                max_sim = 0.0
                for sel_mid in selected_ids:
                    if mid in features_dict and sel_mid in features_dict:
                        sim = self.jaccard_similarity_score(
                            features_dict[mid], features_dict[sel_mid]
                        )
                        max_sim = max(max_sim, sim)

                mmr_score = relevance - diversity_factor * max_sim

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_item = (mid, relevance) 

            if best_item:
                final_ranking.append((best_item[0], best_score))
                selected_ids.add(best_item[0])
                del remaining[best_item[0]]

        final_ranking = [(mid, max(0.0, score)) for mid, score in final_ranking]

        return final_ranking

    def get_similarity_stats(self, similarities: List[float]) -> Dict[str, float]:
        """Statystyki podobieństw"""
        if not similarities:
            return {
                "mean": 0.0,
                "median": 0.0,
                "std": 0.0,
                "min": 0.0,
                "max": 0.0,
                "count": 0,
            }

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
        """Raport adaptive sim (explainability)"""
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
