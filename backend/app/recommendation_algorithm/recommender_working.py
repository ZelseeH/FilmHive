from sqlalchemy.orm import Session
import pandas as pd
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
import traceback
import nltk

from .config import (
    MIN_USER_RATINGS,
    NUM_RECOMMENDATIONS,
    KNN_TOP_K,
    NB_TOP_K,
    ENSEMBLE_KNN_WEIGHT,
    ENSEMBLE_NB_WEIGHT,
    MAX_CANDIDATES,
    RECENT_RATINGS_LIMIT,
    POSITIVE_RATING_THRESHOLD,
    COLD_START_STRATEGY,
)
from .utils.data_preprocessor import DataPreprocessor
from .content_based.knn_recommender import KNNRecommender
from .content_based.naive_bayes_recommender import NaiveBayesRecommender
from .content_based.tfidf_processor import TFIDFProcessor
from .utils.similarity_metrics import SimilarityMetrics
from app.models.recommendation import Recommendation
from app.models.rating import Rating


class MovieRecommender:
    """
    ADAPTACYJNY HYBRYDOWY SYSTEM REKOMENDACYJNY
    Łączy k-NN (strukturalne) + Naive Bayes (tekstowe) z adaptive weights
    FIX: NO MMR (simple weighted sum dla varied scores, no zeros)
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self.preprocessor = DataPreprocessor(db_session)
        self.knn_recommender = KNNRecommender()
        self.nb_recommender = NaiveBayesRecommender(model_type="multinomial")
        self.tfidf_processor = TFIDFProcessor()
        self.similarity_metrics = SimilarityMetrics()

        # NLTK punkt_tab
        try:
            nltk.data.find("tokenizers/punkt_tab/polish")
        except LookupError:
            try:
                nltk.download("punkt_tab", quiet=True)
            except Exception as e:
                logging.getLogger(__name__).warning(f"NLTK download failed: {e}")

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def generate_recommendations(self, user_id: int) -> Dict[str, any]:
        """
        GŁÓWNA METODA z ADAPTIVE WEIGHTS (NO MMR – simple weighted hybrid)
        1. Analizuje wzorce → adaptive weights
        2. k-NN (strukturalne) + NB (tekstowe) → predict ALL candidates
        3. Adaptive weighted sum (boost structural jeśli strong patterns)
        4. Sort by score → top N (varied, no zeros)
        """
        try:
            actual_ratings_count = (
                self.db.query(Rating).filter(Rating.user_id == user_id).count()
            )
            self.logger.info(
                f"User {user_id} ma {actual_ratings_count} ocen (analizujemy ostatnie {RECENT_RATINGS_LIMIT})"
            )

            # Kwalifikacja
            if not self.preprocessor.check_user_eligibility(user_id):
                return {
                    "success": False,
                    "message": f"Użytkownik musi mieć co najmniej {MIN_USER_RATINGS} ocen (ma: {actual_ratings_count})",
                    "recommendations": [],
                }

            # 1. Profil + kandydaci
            user_ratings = self.preprocessor.get_user_ratings(user_id)
            candidate_movies = self.preprocessor.get_candidate_movies(user_id)

            self.logger.info(
                f"Profil: {len(user_ratings)} ocen; Kandydaci: {len(candidate_movies)} filmów"
            )

            if candidate_movies.empty:
                return {
                    "success": False,
                    "message": "Brak kandydatów",
                    "recommendations": [],
                }

            # 2. Wzorce preferencji (adaptive weights)
            preference_patterns = self.preprocessor.analyze_user_preferences(
                user_ratings
            )
            preference_strength = (
                max(preference_patterns.values()) if preference_patterns else 0.0
            )
            self.logger.info(
                f"Wzorce: {preference_patterns}, max_strength={preference_strength:.2f}"
            )

            # 3. k-NN (strukturalne) – predict ALL candidates
            knn_scores = self._get_adaptive_structural_recommendations(
                user_ratings, candidate_movies
            )

            # 4. NB (tekstowe) – predict ALL candidates
            nb_scores = self._get_textual_recommendations(
                user_ratings, candidate_movies
            )

            # 5. Adaptive weighted hybrid (simple sum, NO MMR)
            final_scores = self._combine_adaptive_hybrid(
                knn_scores, nb_scores, preference_strength, candidate_movies
            )

            # 6. Top N (sort by score)
            top_recommendations = self._select_top_recommendations(
                final_scores, candidate_movies
            )

            # 7. Zapis
            self._save_recommendations(user_id, top_recommendations)

            self.logger.info(
                f"Adaptive hybrid (NO MMR): {len(knn_scores)} KNN + {len(nb_scores)} NB → {len(top_recommendations)} recs"
            )

            return {
                "success": True,
                "message": f"Adaptive hybrid (NO MMR) – varied scores, no zeros",
                "recommendations": top_recommendations,
                "algorithm_info": {
                    "approach": "Adaptive Pazzani & Billsus hybrid (weighted sum, NO MMR)",
                    "adaptive_weights": preference_patterns,
                    "knn_weight": ENSEMBLE_KNN_WEIGHT,
                    "nb_weight": ENSEMBLE_NB_WEIGHT,
                    "preference_strength": preference_strength,
                    "diversity": "NO MMR – simple weighted sum for varied scores",
                },
            }

        except Exception as e:
            self.logger.error(f"Błąd generate: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Błąd: {str(e)}",
                "recommendations": [],
            }

    def _get_adaptive_structural_recommendations(
        self, user_ratings: pd.DataFrame, candidate_movies: pd.DataFrame
    ) -> Dict[int, float]:
        """k-NN z adaptive wagami – predict ALL candidates (normalize [0,1])"""
        try:
            self.logger.info(f"k-NN adaptive: {len(user_ratings)} ocen")

            # Features z adaptive weights
            structural_rated = self.preprocessor.prepare_structural_features(
                user_ratings, user_ratings
            )
            structural_candidates = self.preprocessor.prepare_structural_features(
                candidate_movies, user_ratings
            )

            # Align
            rated_aligned, candidates_aligned = self.preprocessor.align_features(
                structural_rated, structural_candidates
            )

            # Fit + predict ALL candidates
            user_ratings_for_fit = user_ratings[["movie_id", "rating"]].copy()
            self.knn_recommender.fit(rated_aligned, user_ratings_for_fit)
            knn_scores = self.knn_recommender.predict_ratings(
                candidates_aligned, user_ratings_for_fit
            )

            if not knn_scores:
                self.logger.warning("KNN empty scores")
                return {}

            # Normalize [1,10] → [0,1] (jak w starym)
            normalized_knn = {}
            for movie_id, rating in knn_scores.items():
                normalized_score = (rating - 1.0) / 9.0
                normalized_knn[movie_id] = max(0.0, min(1.0, normalized_score))

            avg = (
                sum(normalized_knn.values()) / len(normalized_knn)
                if normalized_knn
                else 0
            )
            std = self.similarity_metrics.get_similarity_stats(
                list(normalized_knn.values())
            )["std"]
            self.logger.info(
                f"k-NN: {len(normalized_knn)} predictions, avg={avg:.3f}, std={std:.3f}"
            )

            return normalized_knn

        except Exception as e:
            self.logger.error(f"Błąd k-NN: {str(e)}", exc_info=True)
            return {}

    def _get_textual_recommendations(
        self, user_ratings: pd.DataFrame, candidate_movies: pd.DataFrame
    ) -> Dict[int, float]:
        """NB (tekstowe) – predict ALL candidates"""
        try:
            self.logger.info(f"NB textual: {len(user_ratings)} ocen")

            # Pobierz opisy
            all_movie_ids = list(
                set(
                    user_ratings["movie_id"].tolist()
                    + candidate_movies["movie_id"].tolist()
                )
            )
            descriptions_df = self.preprocessor.get_movie_descriptions(all_movie_ids)

            self.logger.info(f"Pobrano {len(descriptions_df)} opisów dla NB")

            # Fit (graceful fallback 0.5 jeśli not fitted)
            self.nb_recommender.fit(descriptions_df, user_ratings)

            # Predict
            if "description" not in candidate_movies.columns:
                candidate_movies = candidate_movies.merge(
                    descriptions_df[["movie_id", "description"]],
                    on="movie_id",
                    how="left",
                ).fillna({"description": ""})

            nb_scores = self.nb_recommender.predict_with_movie_ids(candidate_movies)

            if not nb_scores:
                self.logger.warning("NB empty scores")
                return {}

            avg = sum(nb_scores.values()) / len(nb_scores) if nb_scores else 0
            std = self.similarity_metrics.get_similarity_stats(
                list(nb_scores.values())
            )["std"]
            self.logger.info(
                f"NB: {len(nb_scores)} predictions, avg={avg:.3f}, std={std:.3f}"
            )

            return nb_scores

        except Exception as e:
            self.logger.error(f"Błąd NB: {str(e)}", exc_info=True)
            return {}

    def _combine_adaptive_hybrid(
        self,
        knn_scores: Dict[int, float],
        nb_scores: Dict[int, float],
        preference_strength: float,
        candidate_movies: pd.DataFrame,
    ) -> Dict[int, float]:
        """
        Adaptive weighted hybrid (NO MMR – simple sum)
        Boost KNN jeśli preference_strength > 0.5 (jak w starym)
        """
        all_movie_ids = set(knn_scores.keys()) | set(nb_scores.keys())

        if not all_movie_ids:
            self.logger.warning("Empty union (KNN + NB both failed)")
            return {}

        # Adaptive weights (boost structural jeśli strong patterns)
        if preference_strength > 0.5:
            adaptive_knn_weight = min(0.9, ENSEMBLE_KNN_WEIGHT + 0.2)
            adaptive_nb_weight = 1.0 - adaptive_knn_weight
            self.logger.info(
                f"Strong patterns (>{preference_strength:.2f}) – boost KNN: {adaptive_knn_weight:.2f}"
            )
        else:
            adaptive_knn_weight = ENSEMBLE_KNN_WEIGHT
            adaptive_nb_weight = ENSEMBLE_NB_WEIGHT

        # Weighted sum (all candidates)
        combined = {}
        for movie_id in all_movie_ids:
            knn_score = knn_scores.get(movie_id, 0.0)
            nb_score = nb_scores.get(movie_id, 0.0)
            combined[movie_id] = (
                adaptive_knn_weight * knn_score + adaptive_nb_weight * nb_score
            )

        avg = sum(combined.values()) / len(combined) if combined else 0
        std = self.similarity_metrics.get_similarity_stats(list(combined.values()))[
            "std"
        ]
        self.logger.info(
            f"Adaptive hybrid: {len(combined)} scores, avg={avg:.3f}, std={std:.3f}"
        )

        # Debug top 5
        if combined:
            top_5 = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:5]
            self.logger.info(f"Top 5 hybrid: {top_5}")

        return combined

    def _select_top_recommendations(
        self, scores: Dict[int, float], candidate_movies: pd.DataFrame
    ) -> List[Dict]:
        """Top N (sort by score, NO MMR)"""
        if not scores:
            self.logger.warning("Empty scores – fallback popular")
            return self._fallback_popular_recommendations(candidate_movies)

        # Simple sort (NO MMR)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Serialize top N
        top_recs = []
        for movie_id, score in ranked[:NUM_RECOMMENDATIONS]:
            try:
                movie_info = candidate_movies[
                    candidate_movies["movie_id"] == movie_id
                ].iloc[0]
                top_recs.append(
                    {
                        "movie_id": int(movie_id),
                        "title": movie_info["title"],
                        "score": float(score),
                        "description": movie_info.get("description", ""),
                        "algorithm": "adaptive_hybrid_no_mmr",
                        "adaptation_info": "Adaptive weights (NO MMR) – simple weighted sum",
                    }
                )
            except Exception as e:
                self.logger.error(f"Error serializing movie {movie_id}: {e}")
                continue

        # Stats
        if top_recs:
            top_scores = [rec["score"] for rec in top_recs]
            stats = self.similarity_metrics.get_similarity_stats(top_scores)
            self.logger.info(
                f"Top recs: avg={stats['mean']:.3f}, std={stats['std']:.3f}"
            )

        return top_recs

    def _fallback_popular_recommendations(
        self, candidate_movies: pd.DataFrame
    ) -> List[Dict]:
        """Fallback popular (varied scores 1.0 → 0.5)"""
        self.logger.info("Fallback popular: varied scores")

        if "avg_rating" in candidate_movies.columns:
            popular = candidate_movies.sort_values(
                "avg_rating", ascending=False, na_position="last"
            ).head(NUM_RECOMMENDATIONS)
        else:
            popular = candidate_movies.sample(
                min(NUM_RECOMMENDATIONS, len(candidate_movies))
            )

        recs = []
        for i, (_, row) in enumerate(popular.iterrows()):
            score = 1.0 - (i / NUM_RECOMMENDATIONS) * 0.5
            recs.append(
                {
                    "movie_id": int(row["movie_id"]),
                    "title": row["title"],
                    "score": float(score),
                    "description": row.get("description", ""),
                    "algorithm": "fallback_popular",
                    "adaptation_info": "Popular rank",
                }
            )

        return recs

    def _save_recommendations(self, user_id: int, recommendations: List[Dict]):
        """Zapis do DB"""
        try:
            deleted = (
                self.db.query(Recommendation)
                .filter(Recommendation.user_id == user_id)
                .delete()
            )

            for rec in recommendations:
                recommendation = Recommendation(
                    user_id=user_id,
                    movie_id=int(rec["movie_id"]),
                    score=float(rec["score"]),
                    created_at=datetime.utcnow(),
                )
                self.db.add(recommendation)

            self.db.commit()
            self.logger.info(
                f"Zapisano {len(recommendations)} recs (usunięto {deleted})"
            )

        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Błąd zapisu: {str(e)}")
            raise

    def get_recommendation_explanation(
        self, user_id: int, movie_id: int
    ) -> Dict[str, any]:
        """Wyjaśnienie"""
        try:
            user_ratings = self.preprocessor.get_user_ratings(user_id)
            patterns = self.preprocessor.analyze_user_preferences(user_ratings)
            return {
                "user_id": user_id,
                "movie_id": movie_id,
                "explanation": "Adaptive hybrid: k-NN (structural) + NB (textual), NO MMR",
                "structural_similarity": f"KNN z adaptive weights: {patterns}",
                "textual_similarity": "NB P(positive) na tf*idf",
                "adaptation_info": f"Preference strength: {max(patterns.values()):.2f}",
                "algorithm": "Adaptive Pazzani & Billsus hybrid (NO MMR)",
            }
        except Exception as e:
            return {"error": f"Błąd: {str(e)}"}

    def analyze_user_preference_trends(self, user_id: int) -> Dict[str, any]:
        """Analiza trends"""
        try:
            user_ratings = self.preprocessor.get_user_ratings(user_id)
            patterns = self.preprocessor.analyze_user_preferences(user_ratings)

            max_w = max(patterns.values()) if patterns else 0
            dominant = max(patterns, key=patterns.get) if patterns else "none"

            user_type = f"Specjalista ({dominant})" if max_w > 0.6 else "Wszechstronny"
            adaptation = f"Boost {dominant}" if max_w > 0.5 else "Równomierne"

            return {
                "user_id": user_id,
                "user_type": user_type,
                "preference_weights": patterns,
                "adaptation_strategy": adaptation,
                "dominant_feature": dominant,
                "specialization_level": float(max_w),
            }
        except Exception as e:
            return {"error": f"Błąd: {str(e)}"}

    def get_system_info(self) -> Dict[str, any]:
        """Info"""
        return {
            "algorithm": "Adaptive Hybrid Content-Based (NO MMR)",
            "theory_base": "Pazzani & Billsus + adaptive weighting",
            "innovation": "Dynamic weights based on preference patterns, NO MMR for varied scores",
            "components": {
                "structural": "k-NN cosine z adaptive weights (genres/actors/directors)",
                "textual": "NB multinomial na tf*idf",
                "hybrid": "Adaptive weighted sum (boost structural jeśli preference_strength > 0.5)",
                "adaptation": f"Patterns z high ratings (>= {POSITIVE_RATING_THRESHOLD})",
            },
            "fallback": "Popular by avg_rating (varied 1.0 → 0.5)",
            "weights": {
                "base_knn": ENSEMBLE_KNN_WEIGHT,
                "base_nb": ENSEMBLE_NB_WEIGHT,
                "adaptation": "Boost structural jeśli preference_strength > 0.5",
            },
        }
