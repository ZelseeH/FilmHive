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
    ADAPTIVE_BASE_COUNTRY_WEIGHT,
    ADAPTIVE_BASE_YEAR_WEIGHT,
    YEAR_MAX_DIFF,
    DURATION_MAX_DIFF,
    DIRECTOR_BONUS,
    ACTOR_BONUS,
    TOP_ACTORS_IN_PATTERN,
    ADAPTIVE_BASE_WEIGHT,
    ADAPTIVE_SCALING_FACTOR,
    MMR_DIVERSITY_FACTOR,
    MMR_UNIQUE_THRESHOLD,
    HYBRID_EXCLUDE_DUPLICATES,
)


class SimilarityMetrics:
    """
    Metryki podobieństwa dla content-based filtering (Pazzani & Billsus)
    Wspiera:
    - Structural similarity (cosine/Jaccard dla genres, actors, directors, country, year)
    - Textual similarity (TF-IDF cosine)
    - Adaptive weighting based on user patterns
    - Hybrid ensemble (KNN + Naive Bayes)
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def cosine_similarity_score(
        self, vector1: np.ndarray, vector2: np.ndarray
    ) -> float:
        """
        Cosine similarity dla high-dimensional vectors
        Używane dla: strukturalne features (binary vectors), TF-IDF vectors
        """
        if vector1.shape != vector2.shape:
            raise ValueError(f"Shape mismatch: {vector1.shape} vs {vector2.shape}")

        # Reshape do 2D jeśli 1D
        vector1 = vector1.reshape(1, -1) if len(vector1.shape) == 1 else vector1
        vector2 = vector2.reshape(1, -1) if len(vector2.shape) == 1 else vector2

        similarity = cosine_similarity(vector1, vector2)[0][0]
        return float(similarity)

    def euclidean_similarity_score(
        self, vector1: np.ndarray, vector2: np.ndarray
    ) -> float:
        """
        Euclidean-based similarity: 1 / (1 + distance)
        Range: [0, 1] (1 = identical, 0 = infinitely far)
        """
        if vector1.shape != vector2.shape:
            raise ValueError(f"Shape mismatch: {vector1.shape} vs {vector2.shape}")

        vector1 = vector1.reshape(1, -1) if len(vector1.shape) == 1 else vector1
        vector2 = vector2.reshape(1, -1) if len(vector2.shape) == 1 else vector2

        distance = euclidean_distances(vector1, vector2)[0][0]
        similarity = 1.0 / (1.0 + distance)
        return float(similarity)

    def jaccard_similarity_score(
        self, set1: Union[set, List], set2: Union[set, List]
    ) -> float:
        """
        Jaccard similarity dla sets: |A ∩ B| / |A ∪ B|
        Używane dla: genres, actors, directors, countries (discrete sets)
        """
        set1 = set(set1) if not isinstance(set1, set) else set1
        set2 = set(set2) if not isinstance(set2, set) else set2

        if len(set1) == 0 and len(set2) == 0:
            return 1.0  # Both empty → identical

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
        Weighted Jaccard (np. boost score jeśli wspólny element jest ważny)
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

    def adaptive_cosine_similarity(
        self,
        vector1: np.ndarray,
        vector2: np.ndarray,
        feature_names: List[str],
        bonuses: Dict[str, float] = None,
    ) -> float:
        """
        Cosine similarity + bonusy za matching features

        Przykład:
        - base_similarity = 0.75
        - matched features: ["director_ChristopherNolan"] → bonus +0.05
        - final = min(1.0, 0.75 + 0.05) = 0.80
        """
        base_sim = self.cosine_similarity_score(vector1, vector2)

        if bonuses is None or not bonuses:
            return base_sim

        v1_nonzero = set(np.where(vector1 > 0)[0])
        v2_nonzero = set(np.where(vector2 > 0)[0])
        overlap = v1_nonzero & v2_nonzero

        total_bonus = 0.0
        for idx in overlap:
            feat = feature_names[idx] if idx < len(feature_names) else None
            if feat and feat in bonuses:
                total_bonus += bonuses[feat]
                self.logger.debug(f"Bonus for {feat}: +{bonuses[feat]:.3f}")

        enhanced_sim = min(1.0, base_sim + total_bonus)

        if total_bonus > 0:
            self.logger.debug(
                f"Adaptive similarity: base={base_sim:.3f}, bonus={total_bonus:.3f}, "
                f"final={enhanced_sim:.3f}"
            )

        return enhanced_sim

    def weighted_similarity(
        self, similarities: Dict[str, float], weights: Dict[str, float]
    ) -> float:
        """
        Ważona średnia podobieństw

        Przykład:
        similarities = {"genres": 0.8, "actors": 0.5, "directors": 0.9}
        weights = {"genres": 0.3, "actors": 0.25, "directors": 0.2}
        → (0.8*0.3 + 0.5*0.25 + 0.9*0.2) / (0.3+0.25+0.2) = 0.733
        """
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
        """
        Adaptive weighted similarity (wagi modyfikowane przez patterns)

        Przykład:
        base_weights = {"genres": 0.3, "directors": 0.2}
        adaptation_factors = {"directors": 0.5}  # User ma pattern na directors
        → adaptive_weights["directors"] = 0.2 * (1 + 0.5) = 0.3 (boost!)
        """
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

    def calculate_movie_similarity(
        self, movie1_features: Dict, movie2_features: Dict
    ) -> Dict[str, float]:
        """
        Multi-attribute similarity między dwoma filmami (metadata-based)

        Zwraca dict z similarity scores dla każdej cechy:
        - genres: Jaccard
        - actors: Jaccard
        - directors: Jaccard
        - country: Jaccard (dodane!)
        - year: normalized diff
        - duration: normalized diff
        """
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

        if "country" in movie1_features and "country" in movie2_features:
            country1 = (
                [movie1_features["country"]] if movie1_features["country"] else []
            )
            country2 = (
                [movie2_features["country"]] if movie2_features["country"] else []
            )
            similarities["country"] = self.jaccard_similarity_score(country1, country2)

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
        """
        Adaptive movie similarity z user-specific weights

        Args:
            movie1_features: Dict z cechami filmu 1
            movie2_features: Dict z cechami filmu 2
            user_preferences: Dict z adaptive weights (z analyze_user_preferences)

        Returns:
            Dict z {"adaptive_total": float, "genres": float, "actors": float, ...}
        """
        base_sim = self.calculate_movie_similarity(movie1_features, movie2_features)

        base_weights = {
            "genres": ADAPTIVE_BASE_GENRE_WEIGHT,
            "actors": ADAPTIVE_BASE_ACTOR_WEIGHT,
            "directors": ADAPTIVE_BASE_DIRECTOR_WEIGHT,
            "country": ADAPTIVE_BASE_COUNTRY_WEIGHT,
            "year": ADAPTIVE_BASE_YEAR_WEIGHT,
        }

        adapt_factors = {}
        for feat, base_w in base_weights.items():
            user_w = user_preferences.get(feat, base_w)
            adapt_factors[feat] = (user_w / base_w - 1.0) if base_w > 0 else 0.0

        adaptive_total = self.adaptive_weighted_similarity(
            base_sim, base_weights, adapt_factors
        )

        return {"adaptive_total": adaptive_total, **base_sim}

    def calculate_user_profile_similarity(
        self,
        user_profile: Dict,
        movie_features: Dict,
        profile_weights: Optional[Dict[str, float]] = None,
    ) -> float:
        """
        Similarity między user profile a movie (Jaccard-based)

        user_profile zawiera:
        - preferred_genres: List[str]
        - preferred_actors: List[str]
        - preferred_directors: List[str]
        - preferred_countries: List[str] (dodane!)
        """
        if profile_weights is None:
            profile_weights = {
                "genres": ADAPTIVE_BASE_GENRE_WEIGHT,
                "actors": ADAPTIVE_BASE_ACTOR_WEIGHT,
                "directors": ADAPTIVE_BASE_DIRECTOR_WEIGHT,
                "country": ADAPTIVE_BASE_COUNTRY_WEIGHT,
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

        if "preferred_countries" in user_profile and "country" in movie_features:
            movie_country = (
                [movie_features["country"]] if movie_features["country"] else []
            )
            similarities["country"] = self.jaccard_similarity_score(
                user_profile["preferred_countries"], movie_country
            )

        return self.weighted_similarity(similarities, profile_weights)

    def combine_algorithm_scores(
        self,
        knn_scores: Dict[int, float],
        nb_scores: Dict[int, float],
        knn_weight: float = ENSEMBLE_KNN_WEIGHT,
        nb_weight: float = ENSEMBLE_NB_WEIGHT,
    ) -> Dict[int, float]:
        """
        Weighted ensemble KNN + Naive Bayes scores

        Args:
            knn_scores: {movie_id: score} z K-NN
            nb_scores: {movie_id: score} z Naive Bayes
            knn_weight: Waga dla KNN (default 0.6)
            nb_weight: Waga dla NB (default 0.4)

        Returns:
            {movie_id: combined_score} (normalized)
        """
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
        """
        Adaptive ensemble: Boost KNN weight jeśli user ma silne patterns

        Logic:
        - Jeśli user_preference_strength > 0.5 (silne patterns)
          → Boost KNN weight (structural features są bardziej reliable)
        - Jeśli user_preference_strength ≤ 0.5 (słabe patterns)
          → Default weights

        Args:
            user_preference_strength: [0,1] siła patterns (0=random, 1=very strong)
        """
        if user_preference_strength > 0.5:
            knn_w = min(0.9, ENSEMBLE_KNN_WEIGHT + user_preference_strength * 0.3)
            nb_w = 1.0 - knn_w
            self.logger.info(
                f"Adaptive ensemble: strong patterns detected ({user_preference_strength:.2f}) "
                f"→ KNN weight boosted to {knn_w:.2f}"
            )
        else:
            knn_w, nb_w = ENSEMBLE_KNN_WEIGHT, ENSEMBLE_NB_WEIGHT

        return self.combine_algorithm_scores(knn_scores, nb_scores, knn_w, nb_w)

    def rank_recommendations(
        self,
        scores: Dict[int, float],
        movies_metadata: pd.DataFrame,
        diversity_factor: float = MMR_DIVERSITY_FACTOR,
        top_k: int = 20,
    ) -> List[Tuple[int, float]]:
        """
        MMR (Maximal Marginal Relevance) ranking z conditional disable

        Logic:
        1. Sort by relevance (base scores)
        2. Check genres diversity w top candidates
        3. Jeśli low diversity (<MMR_UNIQUE_THRESHOLD) → DISABLE MMR (preserve base scores)
        4. Jeśli sufficient diversity → Apply MMR penalty (promote diversity)

        Args:
            scores: {movie_id: relevance_score}
            movies_metadata: DataFrame z metadata (genres, actors, etc.)
            diversity_factor: λ parameter (0=relevance only, 1=diversity only)
            top_k: Number of items to return

        Returns:
            List[(movie_id, final_score)] sorted by final MMR score
        """
        if not scores:
            return []

        ranked_base = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        if diversity_factor <= 0 or movies_metadata.empty:
            return ranked_base[:top_k]

        check_size = min(top_k, len(ranked_base))
        top_ids = [mid for mid, _ in ranked_base[:check_size]]

        genres_in_top = []
        for mid in top_ids:
            movie_info = movies_metadata[movies_metadata["movie_id"] == mid]
            if not movie_info.empty:
                genres = movie_info.iloc[0].get("genres", [])
                if isinstance(genres, list):
                    genres_in_top.extend(genres)

        if len(genres_in_top) > 0:
            unique_genres = len(set(genres_in_top))
            total_genres = len(genres_in_top)
            unique_ratio = unique_genres / total_genres
        else:
            unique_ratio = 1.0

        self.logger.info(
            f"MMR diversity check: {len(set(genres_in_top))} unique genres in top {check_size} "
            f"(ratio={unique_ratio:.2f}, threshold={MMR_UNIQUE_THRESHOLD})"
        )

        if unique_ratio < MMR_UNIQUE_THRESHOLD:
            self.logger.warning(
                f"Low diversity ({unique_ratio:.2f} < {MMR_UNIQUE_THRESHOLD}) "
                f"→ DISABLE MMR (preserve base ranking)"
            )
            return ranked_base[:top_k]

        self.logger.info(f"MMR enabled (λ={diversity_factor:.2f})")

        features_dict = {}
        for _, row in movies_metadata.iterrows():
            mid = row["movie_id"]
            features_dict[mid] = row.get("genres", [])

        final_ranking = []
        remaining = dict(ranked_base)

        if remaining:
            best_item = max(remaining.items(), key=lambda x: x[1])
            final_ranking.append(best_item)
            selected_ids = {best_item[0]}
            del remaining[best_item[0]]

        while remaining and len(final_ranking) < top_k:
            best_score = -np.inf
            best_item = None

            for mid, relevance in remaining.items():

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

    def _normalize_scores(self, scores: Dict[int, float]) -> Dict[int, float]:
        """
        Min-max normalization to [0, 1]

        Jeśli wszystkie scores są identyczne → return 0.5 dla wszystkich
        """
        if not scores:
            return {}

        vals = list(scores.values())
        min_s, max_s = min(vals), max(vals)

        if max_s == min_s:

            return {mid: 0.5 for mid in scores}

        return {mid: (s - min_s) / (max_s - min_s) for mid, s in scores.items()}

    def get_similarity_stats(self, similarities: List[float]) -> Dict[str, float]:
        """
        Statystyki dla listy similarity scores (dla debugging)
        """
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
        """
        Report dla explainability (dlaczego user dostał te rekomendacje?)

        Returns:
            Dict z:
            - base_similarities: {genres: 0.8, actors: 0.5, ...}
            - adaptive_weights: {genres: 0.35, actors: 0.25, ...}
            - weighted_score: float
            - adaptation_summary: {strongest_feature: "genres", ...}
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

    def analyze_preference_patterns(self, user_ratings: List[Dict]) -> Dict[str, float]:
        """
        DEPRECATED: Ta funkcja powinna być w DataPreprocessor.analyze_user_preferences

        Zachowane dla backward compatibility
        """
        self.logger.warning(
            "analyze_preference_patterns() is deprecated. "
            "Use DataPreprocessor.analyze_user_preferences() instead."
        )

        if not user_ratings:
            return {
                "genres": ADAPTIVE_BASE_GENRE_WEIGHT,
                "actors": ADAPTIVE_BASE_ACTOR_WEIGHT,
                "directors": ADAPTIVE_BASE_DIRECTOR_WEIGHT,
                "country": ADAPTIVE_BASE_COUNTRY_WEIGHT,
                "year": ADAPTIVE_BASE_YEAR_WEIGHT,
            }

        high_rated = [
            r for r in user_ratings if r.get("rating", 0) >= POSITIVE_RATING_THRESHOLD
        ]

        if len(high_rated) < 2:
            return {
                "genres": ADAPTIVE_BASE_GENRE_WEIGHT,
                "actors": ADAPTIVE_BASE_ACTOR_WEIGHT,
                "directors": ADAPTIVE_BASE_DIRECTOR_WEIGHT,
                "country": ADAPTIVE_BASE_COUNTRY_WEIGHT,
                "year": ADAPTIVE_BASE_YEAR_WEIGHT,
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
                "country": ADAPTIVE_BASE_COUNTRY_WEIGHT,
                "year": ADAPTIVE_BASE_YEAR_WEIGHT,
            }

        return {
            "genres": ADAPTIVE_BASE_WEIGHT
            + (genre_strength / total_strength) * ADAPTIVE_SCALING_FACTOR,
            "actors": ADAPTIVE_BASE_WEIGHT
            + (actor_strength / total_strength) * ADAPTIVE_SCALING_FACTOR,
            "directors": ADAPTIVE_BASE_WEIGHT
            + (director_strength / total_strength) * ADAPTIVE_SCALING_FACTOR,
            "country": ADAPTIVE_BASE_COUNTRY_WEIGHT,
            "year": ADAPTIVE_BASE_YEAR_WEIGHT,
        }
