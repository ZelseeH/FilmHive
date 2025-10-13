import numpy as np
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from scipy.spatial.distance import jaccard
from typing import Dict, List, Tuple, Optional, Union
import pandas as pd


class SimilarityMetrics:
    """
    Klasa zawierająca różne metryki podobieństwa
    Rozszerzona o adaptacyjne funkcje dla systemów rekomendacyjnych
    """

    def __init__(self):
        pass

    def cosine_similarity_score(
        self, vector1: np.ndarray, vector2: np.ndarray
    ) -> float:
        """Oblicza podobieństwo kosinusowe między dwoma wektorami"""
        if vector1.shape != vector2.shape:
            raise ValueError("Wektory muszą mieć te same wymiary")

        # Reshape do 2D jeśli potrzeba
        if len(vector1.shape) == 1:
            vector1 = vector1.reshape(1, -1)
        if len(vector2.shape) == 1:
            vector2 = vector2.reshape(1, -1)

        similarity = cosine_similarity(vector1, vector2)[0][0]
        return float(similarity)

    def adaptive_cosine_similarity(
        self,
        vector1: np.ndarray,
        vector2: np.ndarray,
        feature_bonuses: Optional[Dict[str, float]] = None,
    ) -> float:
        """
        NOWE: Adaptacyjne podobieństwo kosinusowe z bonusami za konkretne cechy
        Przydatne dla analizy podobieństw z uwzględnieniem wzorców użytkownika
        """
        base_similarity = self.cosine_similarity_score(vector1, vector2)

        if feature_bonuses is None:
            return base_similarity

        # Dodaj bonusy za specific matches (np. ten sam reżyser)
        total_bonus = sum(feature_bonuses.values())
        enhanced_similarity = min(1.0, base_similarity + total_bonus)

        return enhanced_similarity

    def euclidean_similarity_score(
        self, vector1: np.ndarray, vector2: np.ndarray
    ) -> float:
        """Oblicza podobieństwo na podstawie odległości euklidesowej"""
        if vector1.shape != vector2.shape:
            raise ValueError("Wektory muszą mieć te same wymiary")

        # Reshape do 2D jeśli potrzeba
        if len(vector1.shape) == 1:
            vector1 = vector1.reshape(1, -1)
        if len(vector2.shape) == 1:
            vector2 = vector2.reshape(1, -1)

        distance = euclidean_distances(vector1, vector2)[0][0]

        # Konwertuj dystans na podobieństwo (im mniejszy dystans, tym większe podobieństwo)
        similarity = 1.0 / (1.0 + distance)
        return float(similarity)

    def jaccard_similarity_score(self, set1: set, set2: set) -> float:
        """Oblicza podobieństwo Jaccard'a dla zbiorów (np. gatunki, aktorzy)"""
        if not isinstance(set1, set):
            set1 = set(set1)
        if not isinstance(set2, set):
            set2 = set(set2)

        if len(set1) == 0 and len(set2) == 0:
            return 1.0

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        if union == 0:
            return 0.0

        return float(intersection / union)

    def weighted_jaccard_similarity(
        self, set1: set, set2: set, element_weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        NOWE: Ważone podobieństwo Jaccard'a
        Przydatne gdy niektóre elementy są ważniejsze (np. główni aktorzy vs drugoplanowi)
        """
        if not isinstance(set1, set):
            set1 = set(set1)
        if not isinstance(set2, set):
            set2 = set(set2)

        if len(set1) == 0 and len(set2) == 0:
            return 1.0

        if element_weights is None:
            return self.jaccard_similarity_score(set1, set2)

        # Oblicz ważoną intersection i union
        intersection = set1.intersection(set2)
        union = set1.union(set2)

        weighted_intersection = sum(
            element_weights.get(elem, 1.0) for elem in intersection
        )
        weighted_union = sum(element_weights.get(elem, 1.0) for elem in union)

        if weighted_union == 0:
            return 0.0

        return float(weighted_intersection / weighted_union)

    def weighted_similarity(
        self, similarities: Dict[str, float], weights: Dict[str, float]
    ) -> float:
        """Oblicza ważoną kombinację podobieństw"""
        if not similarities or not weights:
            return 0.0

        weighted_sum = 0.0
        weight_sum = 0.0

        for metric_name, similarity in similarities.items():
            weight = weights.get(metric_name, 0.0)
            weighted_sum += similarity * weight
            weight_sum += weight

        if weight_sum == 0:
            return 0.0

        return weighted_sum / weight_sum

    def adaptive_weighted_similarity(
        self,
        similarities: Dict[str, float],
        base_weights: Dict[str, float],
        adaptation_factor: Dict[str, float],
    ) -> float:
        """
        NOWE: Adaptacyjnie ważone podobieństwo na podstawie wzorców użytkownika
        adaptation_factor określa jak bardzo zwiększyć/zmniejszyć poszczególne wagi
        """
        if not similarities or not base_weights:
            return 0.0

        # Oblicz adaptacyjne wagi
        adaptive_weights = {}
        for metric_name, base_weight in base_weights.items():
            adaptation = adaptation_factor.get(metric_name, 0.0)
            adaptive_weight = base_weight * (1.0 + adaptation)
            adaptive_weights[metric_name] = max(0.0, adaptive_weight)

        # Normalizuj wagi do sumy = 1.0
        total_weight = sum(adaptive_weights.values())
        if total_weight > 0:
            adaptive_weights = {
                k: v / total_weight for k, v in adaptive_weights.items()
            }

        return self.weighted_similarity(similarities, adaptive_weights)

    def combine_algorithm_scores(
        self,
        knn_scores: Dict[int, float],
        nb_scores: Dict[int, float],
        knn_weight: float = 0.6,
        nb_weight: float = 0.4,
    ) -> Dict[int, float]:
        """Kombinuje wyniki z k-NN i Naive Bayes"""
        combined_scores = {}

        # Normalizuj scores do zakresu [0, 1]
        knn_normalized = self._normalize_scores(knn_scores)
        nb_normalized = self._normalize_scores(nb_scores)

        # Pobierz wszystkie movie_id
        all_movie_ids = set(knn_normalized.keys()) | set(nb_normalized.keys())

        for movie_id in all_movie_ids:
            knn_score = knn_normalized.get(movie_id, 0.0)
            nb_score = nb_normalized.get(movie_id, 0.0)

            # Ważona kombinacja
            combined_score = knn_weight * knn_score + nb_weight * nb_score
            combined_scores[movie_id] = combined_score

        return combined_scores

    def adaptive_algorithm_combination(
        self,
        knn_scores: Dict[int, float],
        nb_scores: Dict[int, float],
        user_preference_strength: float = 0.0,
    ) -> Dict[int, float]:
        """
        NOWE: Adaptacyjna kombinacja algorytmów na podstawie siły wzorców użytkownika
        user_preference_strength: 0.0-1.0, gdzie 1.0 = silne wzorce strukturalne
        """
        # Adaptacyjne wagi na podstawie siły wzorców
        if user_preference_strength > 0.5:
            # Silne wzorce -> zwiększ wagę k-NN (strukturalnego)
            knn_weight = min(0.9, 0.6 + user_preference_strength * 0.3)
            nb_weight = 1.0 - knn_weight
        else:
            # Słabe wzorce -> standardowe wagi
            knn_weight = 0.6
            nb_weight = 0.4

        return self.combine_algorithm_scores(
            knn_scores, nb_scores, knn_weight, nb_weight
        )

    def calculate_movie_similarity(
        self, movie1_features: Dict, movie2_features: Dict
    ) -> Dict[str, float]:
        """Oblicza wielowymiarowe podobieństwo między filmami"""
        similarities = {}

        # Podobieństwo gatunków (Jaccard)
        if "genres" in movie1_features and "genres" in movie2_features:
            genres1 = set(movie1_features["genres"])
            genres2 = set(movie2_features["genres"])
            similarities["genres"] = self.jaccard_similarity_score(genres1, genres2)

        # Podobieństwo aktorów (Jaccard)
        if "actors" in movie1_features and "actors" in movie2_features:
            actors1 = set(movie1_features["actors"])
            actors2 = set(movie2_features["actors"])
            similarities["actors"] = self.jaccard_similarity_score(actors1, actors2)

        # Podobieństwo reżyserów (Jaccard) - KLUCZOWE dla adaptacji!
        if "directors" in movie1_features and "directors" in movie2_features:
            directors1 = set(movie1_features["directors"])
            directors2 = set(movie2_features["directors"])
            similarities["directors"] = self.jaccard_similarity_score(
                directors1, directors2
            )

        # Podobieństwo roku (na podstawie różnicy)
        if "release_year" in movie1_features and "release_year" in movie2_features:
            year_diff = abs(
                movie1_features["release_year"] - movie2_features["release_year"]
            )
            # Im mniejsza różnica, tym większe podobieństwo (max 20 lat różnicy)
            year_similarity = max(0.0, 1.0 - (year_diff / 20.0))
            similarities["year"] = year_similarity

        # Podobieństwo czasu trwania
        if (
            "duration_minutes" in movie1_features
            and "duration_minutes" in movie2_features
        ):
            duration_diff = abs(
                movie1_features["duration_minutes"]
                - movie2_features["duration_minutes"]
            )
            # Normalizuj różnicę (max 180 minut różnicy)
            duration_similarity = max(0.0, 1.0 - (duration_diff / 180.0))
            similarities["duration"] = duration_similarity

        return similarities

    def calculate_adaptive_movie_similarity(
        self,
        movie1_features: Dict,
        movie2_features: Dict,
        user_preferences: Dict[str, float],
    ) -> Dict[str, float]:
        """
        NOWE: Oblicza podobieństwo filmów z uwzględnieniem preferencji użytkownika
        user_preferences: wagi dla różnych cech (genres, actors, directors, etc.)
        """
        base_similarities = self.calculate_movie_similarity(
            movie1_features, movie2_features
        )

        # Zastosuj adaptacyjne wagi
        base_weights = {
            "genres": 0.3,
            "actors": 0.3,
            "directors": 0.25,
            "year": 0.1,
            "duration": 0.05,
        }

        # Oblicz adaptation factors na podstawie preferencji użytkownika
        adaptation_factors = {}
        for feature, base_weight in base_weights.items():
            user_pref = user_preferences.get(feature, base_weight)
            # Im wyższa preferencja użytkownika, tym większy adaptation factor
            adaptation_factors[feature] = (user_pref - base_weight) / base_weight

        adaptive_similarity = self.adaptive_weighted_similarity(
            base_similarities, base_weights, adaptation_factors
        )

        return {"adaptive_total": adaptive_similarity, **base_similarities}

    def _normalize_scores(self, scores: Dict[int, float]) -> Dict[int, float]:
        """Normalizuje scores do zakresu [0, 1]"""
        if not scores:
            return {}

        score_values = list(scores.values())
        min_score = min(score_values)
        max_score = max(score_values)

        if max_score == min_score:
            # Wszystkie scores są takie same
            return {movie_id: 0.5 for movie_id in scores.keys()}

        normalized = {}
        for movie_id, score in scores.items():
            normalized_score = (score - min_score) / (max_score - min_score)
            normalized[movie_id] = normalized_score

        return normalized

    def calculate_user_profile_similarity(
        self,
        user_profile: Dict,
        movie_features: Dict,
        profile_weights: Optional[Dict[str, float]] = None,
    ) -> float:
        """Oblicza podobieństwo między profilem użytkownika a filmem"""
        if profile_weights is None:
            profile_weights = {
                "genres": 0.4,
                "actors": 0.3,
                "directors": 0.2,
                "other": 0.1,
            }

        similarities = {}

        # Porównaj preferencje gatunkowe
        if "preferred_genres" in user_profile and "genres" in movie_features:
            user_genres = set(user_profile["preferred_genres"])
            movie_genres = set(movie_features["genres"])
            similarities["genres"] = self.jaccard_similarity_score(
                user_genres, movie_genres
            )

        # Porównaj preferencje aktorskie
        if "preferred_actors" in user_profile and "actors" in movie_features:
            user_actors = set(user_profile["preferred_actors"])
            movie_actors = set(movie_features["actors"])
            similarities["actors"] = self.jaccard_similarity_score(
                user_actors, movie_actors
            )

        # Porównaj preferencje reżyserskie
        if "preferred_directors" in user_profile and "directors" in movie_features:
            user_directors = set(user_profile["preferred_directors"])
            movie_directors = set(movie_features["directors"])
            similarities["directors"] = self.jaccard_similarity_score(
                user_directors, movie_directors
            )

        # Oblicz ważoną kombinację
        return self.weighted_similarity(similarities, profile_weights)

    def analyze_preference_patterns(self, user_ratings: List[Dict]) -> Dict[str, float]:
        """
        NOWE: Analizuje wzorce preferencji użytkownika na podstawie ocen
        Zwraca siłę preferencji dla różnych cech
        """
        if not user_ratings:
            return {"genres": 0.33, "actors": 0.33, "directors": 0.34}

        high_rated = [
            rating for rating in user_ratings if rating.get("rating", 0) >= 8.0
        ]

        if len(high_rated) < 2:
            return {"genres": 0.33, "actors": 0.33, "directors": 0.34}

        # Zlicz powtórzenia w wysokich ocenach
        genre_counts = {}
        actor_counts = {}
        director_counts = {}

        for rating in high_rated:
            # Zlicz gatunki
            for genre in rating.get("genres", []):
                genre_counts[genre] = genre_counts.get(genre, 0) + 1

            # Zlicz aktorów (top 3)
            for actor in rating.get("actors", [])[:3]:
                actor_counts[actor] = actor_counts.get(actor, 0) + 1

            # Zlicz reżyserów
            for director in rating.get("directors", []):
                director_counts[director] = director_counts.get(director, 0) + 1

        # Oblicz siłę wzorców
        genre_strength = max(genre_counts.values()) if genre_counts else 0
        actor_strength = max(actor_counts.values()) if actor_counts else 0
        director_strength = max(director_counts.values()) if director_counts else 0

        total_strength = genre_strength + actor_strength + director_strength

        if total_strength == 0:
            return {"genres": 0.33, "actors": 0.33, "directors": 0.34}

        # Oblicz adaptacyjne wagi
        return {
            "genres": 0.1 + (genre_strength / total_strength) * 0.7,
            "actors": 0.1 + (actor_strength / total_strength) * 0.7,
            "directors": 0.1 + (director_strength / total_strength) * 0.7,
        }

    def rank_recommendations(
        self,
        scores: Dict[int, float],
        movies_metadata: pd.DataFrame,
        diversity_factor: float = 0.1,
    ) -> List[Tuple[int, float]]:
        """Rankuje rekomendacje z opcjonalnym uwzględnieniem różnorodności"""
        if not scores:
            return []

        # Sortuj według score
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        if diversity_factor <= 0 or movies_metadata.empty:
            return ranked

        # Implementuj MMR (Maximal Marginal Relevance) dla różnorodności
        final_ranking = []
        remaining_items = dict(ranked)

        # Wybierz pierwszy element (najwyższy score)
        if remaining_items:
            best_item = max(remaining_items.items(), key=lambda x: x[1])
            final_ranking.append(best_item)
            del remaining_items[best_item[0]]

        # Dla pozostałych elementów uwzględnij różnorodność
        while remaining_items and len(final_ranking) < len(ranked):
            best_score = -float("inf")
            best_item = None

            for movie_id, relevance_score in remaining_items.items():
                # Oblicz średnie podobieństwo do już wybranych filmów
                diversity_penalty = 0.0
                if final_ranking:
                    similarities = []
                    for selected_movie_id, _ in final_ranking:
                        # Tu można dodać obliczanie podobieństwa między filmami
                        # Na razie używamy uproszczonej wersji
                        similarity = 0.5  # Placeholder
                        similarities.append(similarity)

                    diversity_penalty = np.mean(similarities)

                # MMR score = λ * relevance - (1-λ) * similarity
                mmr_score = (
                    1 - diversity_factor
                ) * relevance_score - diversity_factor * diversity_penalty

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_item = (movie_id, relevance_score)  # Zachowaj oryginalny score

            if best_item:
                final_ranking.append(best_item)
                del remaining_items[best_item[0]]

        return final_ranking

    def get_similarity_stats(self, similarities: List[float]) -> Dict[str, float]:
        """Oblicza statystyki podobieństwa"""
        if not similarities:
            return {}

        similarities_array = np.array(similarities)

        return {
            "mean": float(np.mean(similarities_array)),
            "median": float(np.median(similarities_array)),
            "std": float(np.std(similarities_array)),
            "min": float(np.min(similarities_array)),
            "max": float(np.max(similarities_array)),
            "count": len(similarities),
        }

    def get_adaptive_similarity_report(
        self, base_similarities: Dict[str, float], adaptive_weights: Dict[str, float]
    ) -> Dict[str, any]:
        """
        NOWE: Generuje raport z adaptacyjnych podobieństw
        Przydatne do debugowania i explainability
        """
        return {
            "base_similarities": base_similarities,
            "adaptive_weights": adaptive_weights,
            "weighted_score": self.weighted_similarity(
                base_similarities, adaptive_weights
            ),
            "adaptation_summary": {
                "strongest_feature": max(
                    adaptive_weights.keys(), key=adaptive_weights.get
                ),
                "weight_distribution": adaptive_weights,
                "total_features": len(base_similarities),
            },
        }
