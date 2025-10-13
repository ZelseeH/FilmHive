from sqlalchemy.orm import Session
import pandas as pd
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
import traceback

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
from app.models.rating import Rating  # Dla count


class MovieRecommender:
    """
    ADAPTACYJNY HYBRYDOWY SYSTEM REKOMENDACYJNY
    Zgodny z teorią Pazzaniego i Billsusa + adaptacyjne ważenie
    Łączy k-NN (dane strukturalne, top-K=7) z Naive Bayes (dane tekstowe, top-K=3)
    NOWOŚĆ: Top-K selection + MMR dla varied scores (no flat top-10)
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self.preprocessor = DataPreprocessor(db_session)
        self.knn_recommender = KNNRecommender()
        self.nb_recommender = NaiveBayesRecommender(model_type="multinomial")
        self.tfidf_processor = TFIDFProcessor()
        self.similarity_metrics = SimilarityMetrics()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def generate_recommendations(self, user_id: int) -> Dict[str, any]:
        """
        GŁÓWNA METODA z ADAPTACYJNYM WAŻENIEM I TOP-K SELECTION
        1. Analizuje wzorce (top high ratings)
        2. Top-7 KNN (strukturalne) + top-3 NB (tekstowe)
        3. Hybrid na union (≤10), MMR rank dla diversity/variance
        4. Pad do NUM_RECOMMENDATIONS z candidates jeśli potrzeba
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

            # 1. Profil + kandydaci (pre-filter popular dla efficiency)
            user_ratings = self.preprocessor.get_user_ratings(user_id)
            candidate_movies = self.preprocessor.get_candidate_movies(
                user_id
            )  # Zakładam .order_by(popular).limit(MAX_CANDIDATES) w impl

            self.logger.info(
                f"Profil: {len(user_ratings)} ocen; Kandydaci: {len(candidate_movies)} filmów"
            )

            if candidate_movies.empty:
                return {
                    "success": False,
                    "message": "Brak kandydatów",
                    "recommendations": [],
                }

            # 2. Wzorce preferencji (strength dla adaptive)
            preference_patterns = self.preprocessor.analyze_user_preferences(
                user_ratings
            )
            preference_strength = (
                max(preference_patterns.values()) if preference_patterns else 0.0
            )
            self.logger.info(
                f"Wzorce: {preference_patterns}, max_strength={preference_strength:.2f}"
            )

            # 3. Top-K strukturalne (KNN)
            knn_top_scores = self._get_adaptive_structural_recommendations(
                user_ratings, candidate_movies
            )

            # 4. Top-K tekstowe (NB)
            nb_top_scores = self._get_textual_recommendations(
                user_ratings, candidate_movies
            )

            # 5. Hybrid na top-K union + MMR rank
            final_scores = self._combine_hybrid_top_k(
                knn_top_scores, nb_top_scores, preference_strength, candidate_movies
            )

            # 6. Top N z MMR (diversity dla varied scores)
            top_recommendations = self._select_top_recommendations(
                final_scores, candidate_movies
            )

            # 7. Zapis
            self._save_recommendations(user_id, top_recommendations)

            self.logger.info(
                f"Hybrydowy top-K: {len(knn_top_scores)} KNN + {len(nb_top_scores)} NB → {len(top_recommendations)} recs"
            )

            return {
                "success": True,
                "message": f"Adaptacyjne top-K hybrid (KNN={KNN_TOP_K}, NB={NB_TOP_K}) z MMR diversity",
                "recommendations": top_recommendations,
                "algorithm_info": {
                    "approach": "Adaptive Pazzani & Billsus hybrid (top-K selection + MMR)",
                    "adaptive_weights": preference_patterns,
                    "knn_weight": ENSEMBLE_KNN_WEIGHT,
                    "nb_weight": ENSEMBLE_NB_WEIGHT,
                    "preference_strength": preference_strength,
                    "top_k_info": f"KNN top-{KNN_TOP_K}, NB top-{NB_TOP_K}",
                    "diversity": "MMR applied for score variance",
                },
            }

        except Exception as e:
            self.logger.error(f"Błąd hybrydy: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "message": f"Błąd: {str(e)}",
                "recommendations": [],
            }

    def _get_adaptive_structural_recommendations(
        self, user_ratings: pd.DataFrame, candidate_movies: pd.DataFrame
    ) -> Dict[int, float]:
        """
        Top-K KNN z adaptive wagami (strukturalne features, sekcja 3.1)
        Predict all → top KNN_TOP_K (varied via min-max norm)
        """
        try:
            self.logger.info(f"k-NN adaptive: {len(user_ratings)} ocen")

            # Features z adaptive weights (user_ratings dla patterns)
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

            # Fit + predict (weighted avg ratings * cosine)
            self.knn_recommender.fit(
                rated_aligned, user_ratings["rating"].values
            )  # Pass ratings
            knn_scores = self.knn_recommender.predict_ratings(candidates_aligned)

            # Min-max norm dla variance [0,1]
            normalized_knn = self.similarity_metrics._normalize_scores(knn_scores)

            # Top-K selection (sorted, varied highs)
            top_k_items = sorted(
                normalized_knn.items(), key=lambda x: x[1], reverse=True
            )[:KNN_TOP_K]
            top_knn_scores = {mid: score for mid, score in top_k_items}

            avg = (
                sum(top_knn_scores.values()) / len(top_knn_scores)
                if top_knn_scores
                else 0
            )
            std = self.similarity_metrics.get_similarity_stats(
                list(top_knn_scores.values())
            )["std"]
            self.logger.info(f"k-NN top-{KNN_TOP_K}: avg={avg:.3f}, std={std:.3f}")

            return top_knn_scores

        except Exception as e:
            self.logger.error(f"Błąd k-NN: {str(e)}")
            return {}

    def _get_textual_recommendations(
        self, user_ratings: pd.DataFrame, candidate_movies: pd.DataFrame
    ) -> Dict[int, float]:
        """
        Top-K NB (tekstowe tf*idf, sekcja 2.3.5)
        Predict P(positive) all → top NB_TOP_K
        """
        try:
            self.logger.info(f"NB textual: {len(user_ratings)} ocen")

            # Fit na descriptions (positive/negative z threshold)
            self.nb_recommender.fit(user_ratings)  # Zakładam classify positive/negative
            nb_scores = self.nb_recommender.predict_with_movie_ids(
                candidate_movies
            )  # Dict[mid: P(positive)]

            # Min-max norm (choć P already [0,1], dla consistency)
            normalized_nb = self.similarity_metrics._normalize_scores(nb_scores)

            # Top-K (varied probs)
            top_k_items = sorted(
                normalized_nb.items(), key=lambda x: x[1], reverse=True
            )[:NB_TOP_K]
            top_nb_scores = {mid: score for mid, score in top_k_items}

            avg = (
                sum(top_nb_scores.values()) / len(top_nb_scores) if top_nb_scores else 0
            )
            std = self.similarity_metrics.get_similarity_stats(
                list(top_nb_scores.values())
            )["std"]
            self.logger.info(f"NB top-{NB_TOP_K}: avg={avg:.3f}, std={std:.3f}")

            return top_nb_scores

        except Exception as e:
            self.logger.error(f"Błąd NB: {str(e)}")
            return {}

    def _combine_hybrid_top_k(
        self,
        knn_top_scores: Dict[int, float],
        nb_top_scores: Dict[int, float],
        preference_strength: float,
        candidate_movies: pd.DataFrame,
    ) -> Dict[int, float]:
        """
        Adaptive hybrid na top-K union (≤10, sekcja 5)
        Użyj SimilarityMetrics.adaptive_algorithm_combination dla boost
        Rozszerz do all candidates jeśli <10, z MMR prep
        """
        union_ids = set(knn_top_scores) | set(nb_top_scores)
        self.logger.info(f"Hybrid union top-K: {len(union_ids)} filmów")

        if not union_ids:
            return {}

        # Adaptive weights (boost KNN jeśli strong patterns)
        combined_top = self.similarity_metrics.adaptive_algorithm_combination(
            knn_top_scores, nb_top_scores, preference_strength
        )

        # Rozszerz do candidates (jeśli < NUM_RECOMMENDATIONS/2, rank all z low scores)
        all_candidates_scores = {mid: 0.0 for mid in candidate_movies["movie_id"]}
        for mid, score in combined_top.items():
            all_candidates_scores[mid] = score

        # Fallback dla missing: Low base (0.2) jeśli cold_start popular
        if COLD_START_STRATEGY == "popular" and len(combined_top) < 5:
            # Zakładam candidates sorted by avg_rating desc; boost top non-top-K
            for i, mid in enumerate(
                candidate_movies["movie_id"][:10]
            ):  # Top 10 popular
                if mid not in combined_top:
                    all_candidates_scores[mid] = 0.2 + (i * 0.01)  # Varied low

        # MMR prep: Return all dla rank_recommendations (diversity na candidates)
        self.logger.info(
            f"Hybrid scores: {len(all_candidates_scores)}, top std={self.similarity_metrics.get_similarity_stats(list(combined_top.values()))['std']:.3f}"
        )
        return all_candidates_scores

    def _select_top_recommendations(
        self, scores: Dict[int, float], candidate_movies: pd.DataFrame
    ) -> List[Dict]:
        """Top N z MMR rank (diversity dla no flat; sekcja 7)"""
        if not scores:
            self.logger.warning("Brak scores - fallback popular/random")
            # Fallback: Top popular
            popular = (
                candidate_movies.sort_values("avg_rating", ascending=False).head(
                    NUM_RECOMMENDATIONS
                )
                if "avg_rating" in candidate_movies
                else candidate_movies.sample(NUM_RECOMMENDATIONS)
            )
            return [
                {
                    "movie_id": int(row["movie_id"]),
                    "title": row["title"],
                    "score": 0.5,
                    "description": row.get("description", ""),
                    "algorithm": COLD_START_STRATEGY,
                }
                for _, row in popular.iterrows()
            ]

        # MMR rank dla variance/diversity (użyj features z candidates)
        ranked = self.similarity_metrics.rank_recommendations(
            scores, candidate_movies, diversity_factor=0.1
        )

        # Top N
        top_recs = []
        for movie_id, score in ranked[:NUM_RECOMMENDATIONS]:
            movie_info = candidate_movies[
                candidate_movies["movie_id"] == movie_id
            ].iloc[0]
            top_recs.append(
                {
                    "movie_id": int(movie_id),
                    "title": movie_info["title"],
                    "score": float(score),
                    "description": movie_info.get("description", ""),
                    "algorithm": "adaptive_hybrid_top_k_mmr",
                    "adaptation_info": "Top-K selection + MMR for score diversity",
                }
            )

        # Stats dla log (variance)
        top_scores = [rec["score"] for rec in top_recs]
        stats = self.similarity_metrics.get_similarity_stats(top_scores)
        self.logger.info(f"Top recs: avg={stats['mean']:.3f}, std={stats['std']:.3f}")

        return top_recs

    def _save_recommendations(self, user_id: int, recommendations: List[Dict]):
        """Zapis do DB"""
        try:
            # Delete old
            deleted = (
                self.db.query(Recommendation)
                .filter(Recommendation.user_id == user_id)
                .delete()
            )

            # Add new
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
        """Wyjaśnienie z patterns"""
        try:
            user_ratings = self.preprocessor.get_user_ratings(user_id)
            patterns = self.preprocessor.analyze_user_preferences(user_ratings)
            return {
                "user_id": user_id,
                "movie_id": movie_id,
                "explanation": "Top-K hybrid k-NN (strukturalne) + NB (tekstowe) z MMR",
                "structural_similarity": "Top-7 KNN z adaptive weights (genres/actors/directors)",
                "textual_similarity": "Top-3 NB P(positive) na tf*idf",
                "adaptation_info": f"Wzorce: {patterns}",
                "algorithm": "Adaptive Pazzani & Billsus top-K + MMR",
            }
        except Exception as e:
            return {"error": f"Błąd: {str(e)}"}

    def analyze_user_preference_trends(self, user_id: int) -> Dict[str, any]:
        """Analiza trends (użyj preprocessor)"""
        try:
            user_ratings = self.preprocessor.get_user_ratings(user_id)
            patterns = self.preprocessor.analyze_user_preferences(user_ratings)

            max_w = max(patterns.values())
            dominant = max(patterns, key=patterns.get)

            user_type = f"Specjalista ({dominant})" if max_w > 0.6 else "Wszechstronny"
            adaptation = f"Boost {dominant}" if max_w > 0.5 else "Równomierne"

            return {
                "user_id": user_id,
                "user_type": user_type,
                "preference_weights": patterns,
                "adaptation_strategy": adaptation,
                "dominant_feature": dominant,
                "specialization_level": max_w,
            }
        except Exception as e:
            return {"error": f"Błąd: {str(e)}"}

    def get_system_info(self) -> Dict[str, any]:
        """Info o systemie"""
        return {
            "algorithm": "Adaptive Hybrid Top-K Content-Based + MMR",
            "theory_base": "Pazzani & Billsus (1997) + dynamic weighting",
            "innovation": "Top-K selection (7 KNN + 3 NB) + MMR for variance/diversity",
            "components": {
                "structural": f"k-NN cosine top-{KNN_TOP_K} z adaptive weights",
                "textual": f"NB multinomial top-{NB_TOP_K} na tf*idf",
                "hybrid": "Adaptive weighted sum na union + MMR rank",
                "adaptation": "Patterns z high ratings (>= {POSITIVE_RATING_THRESHOLD})",
            },
            "data_representation": "Semi-structured (adaptive structural + tf*idf)",
            "weights": {
                "base_knn": ENSEMBLE_KNN_WEIGHT,
                "base_nb": ENSEMBLE_NB_WEIGHT,
                "adaptation": "Boost structural jeśli preference_strength > 0.5",
            },
            "features": {
                "genres/actors/directors": "One-hot top-{TOP_ENTITIES} z adaptive weights",
                "descriptions": "tf*idf (max_features={TFIDF_MAX_FEATURES})",
                "threshold": f"High ratings >= {POSITIVE_RATING_THRESHOLD}",
            },
        }
