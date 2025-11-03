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

    def __init__(self, db_session: Session):
        self.db = db_session
        self.preprocessor = DataPreprocessor(db_session)
        self.knn_recommender = KNNRecommender()
        self.nb_recommender = NaiveBayesRecommender(model_type="multinomial")
        self.tfidf_processor = TFIDFProcessor()
        self.similarity_metrics = SimilarityMetrics()

        # Store scores
        self._knn_scores = {}
        self._nb_scores = {}
        self._last_preference_strength = 0.0

        # NLTK
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
        try:
            actual_ratings_count = (
                self.db.query(Rating).filter(Rating.user_id == user_id).count()
            )
            self.logger.info(
                f"User {user_id} ma {actual_ratings_count} ocen (analizujemy ostatnie {RECENT_RATINGS_LIMIT})"
            )

            if not self.preprocessor.check_user_eligibility(user_id):
                return {
                    "success": False,
                    "message": f"Użytkownik musi mieć co najmniej {MIN_USER_RATINGS} ocen (ma: {actual_ratings_count})",
                    "recommendations": {"top_knn": [], "top_nb": [], "top_hybrid": []},
                }

            user_ratings = self.preprocessor.get_user_ratings(user_id)
            candidate_movies = self.preprocessor.get_candidate_movies(user_id)

            self.logger.info(
                f"Profil: {len(user_ratings)} ocen; Kandydaci: {len(candidate_movies)} filmów"
            )

            if candidate_movies.empty:
                return {
                    "success": False,
                    "message": "Brak kandydatów",
                    "recommendations": {"top_knn": [], "top_nb": [], "top_hybrid": []},
                }

            preference_patterns = self.preprocessor.analyze_user_preferences(
                user_ratings
            )
            preference_strength = (
                max(preference_patterns.values()) if preference_patterns else 0.0
            )
            self.logger.info(
                f"Wzorce: {preference_patterns}, max_strength={preference_strength:.2f}"
            )

            # Get KNN + NB scores
            self._knn_scores = self._get_adaptive_structural_recommendations(
                user_ratings, candidate_movies
            )
            self._nb_scores = self._get_textual_recommendations(
                user_ratings, candidate_movies
            )

            # Hybrid scores
            hybrid_scores = self._combine_adaptive_hybrid(
                self._knn_scores, self._nb_scores, preference_strength, candidate_movies
            )

            # Select TOP 5 KNN + TOP 5 NB + TOP 10 Hybrid (ZAWSZE 20 unique)
            top_recommendations = self._select_top_recommendations_multi(
                self._knn_scores, self._nb_scores, hybrid_scores, candidate_movies
            )

            # Save all 20 unique
            self._save_recommendations_multi(user_id, top_recommendations)

            self.logger.info(
                f"Generated: {len(top_recommendations['top_knn'])} KNN + "
                f"{len(top_recommendations['top_nb'])} NB + "
                f"{len(top_recommendations['top_hybrid'])} Hybrid"
            )

            return {
                "success": True,
                "message": f"TOP 5 KNN + TOP 5 NB + TOP 10 Hybrid (20 recs total)",
                "recommendations": top_recommendations,
                "algorithm_info": {
                    "approach": "Multi-section: KNN (structural) + NB (textual) + Hybrid (combined)",
                    "adaptive_weights": preference_patterns,
                    "knn_weight": ENSEMBLE_KNN_WEIGHT,
                    "nb_weight": ENSEMBLE_NB_WEIGHT,
                    "preference_strength": preference_strength,
                    "sections": {
                        "top_knn": "TOP 5 structural similarity (genres/directors/actors)",
                        "top_nb": "TOP 5 textual similarity (description keywords)",
                        "top_hybrid": "TOP 10 combined (weighted sum KNN + NB)",
                    },
                },
            }

        except Exception as e:
            self.logger.error(f"Błąd generate: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Błąd: {str(e)}",
                "recommendations": {"top_knn": [], "top_nb": [], "top_hybrid": []},
            }

    def _get_adaptive_structural_recommendations(
        self, user_ratings: pd.DataFrame, candidate_movies: pd.DataFrame
    ) -> Dict[int, float]:
        """k-NN z adaptive wagami"""
        try:
            self.logger.info(f"k-NN adaptive: {len(user_ratings)} ocen")

            structural_rated = self.preprocessor.prepare_structural_features(
                user_ratings, user_ratings
            )
            structural_candidates = self.preprocessor.prepare_structural_features(
                candidate_movies, user_ratings
            )

            rated_aligned, candidates_aligned = self.preprocessor.align_features(
                structural_rated, structural_candidates
            )

            user_ratings_for_fit = user_ratings[["movie_id", "rating"]].copy()
            self.knn_recommender.fit(rated_aligned, user_ratings_for_fit)
            knn_scores = self.knn_recommender.predict_ratings(
                candidates_aligned, user_ratings_for_fit
            )

            if not knn_scores:
                self.logger.warning("KNN empty scores")
                return {}

            # Normalize [1,10] → [0,1]
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
        """NB (tekstowe)"""
        try:
            self.logger.info(f"NB textual: {len(user_ratings)} ocen")

            all_movie_ids = list(
                set(
                    user_ratings["movie_id"].tolist()
                    + candidate_movies["movie_id"].tolist()
                )
            )
            descriptions_df = self.preprocessor.get_movie_descriptions(all_movie_ids)

            self.logger.info(f"Pobrano {len(descriptions_df)} opisów dla NB")

            user_ratings_for_nb = user_ratings[["movie_id", "rating"]].copy()
            self.nb_recommender.fit(descriptions_df, user_ratings_for_nb)

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
        """Adaptive weighted hybrid"""
        all_movie_ids = set(knn_scores.keys()) | set(nb_scores.keys())

        if not all_movie_ids:
            self.logger.warning("Empty union")
            return {}

        # Adaptive weights
        if preference_strength > 0.5:
            adaptive_knn_weight = min(0.9, ENSEMBLE_KNN_WEIGHT + 0.2)
            adaptive_nb_weight = 1.0 - adaptive_knn_weight
            self.logger.info(
                f"Strong patterns ({preference_strength:.2f}) – boost KNN: {adaptive_knn_weight:.2f}"
            )
        else:
            adaptive_knn_weight = ENSEMBLE_KNN_WEIGHT
            adaptive_nb_weight = ENSEMBLE_NB_WEIGHT

        self._last_preference_strength = preference_strength

        # Weighted sum
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

        return combined

    def _select_top_recommendations_multi(
        self,
        knn_scores: Dict[int, float],
        nb_scores: Dict[int, float],
        hybrid_scores: Dict[int, float],
        candidate_movies: pd.DataFrame,
    ) -> Dict[str, List[Dict]]:
        """
        Returns 3 sections (ZAWSZE 20 unique total):
        - top_knn: TOP 5 KNN
        - top_nb: TOP 5 NB
        - top_hybrid: TOP 10 Hybrid (skip duplicates, extend to 10 unique)
        """

        # Track used movie_ids
        used_ids = set()

        # ═══════════════════════════════════════════════
        # TOP 5 KNN (structural)
        # ═══════════════════════════════════════════════
        top_knn_items = sorted(knn_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        top_knn = []
        for movie_id, score in top_knn_items:
            try:
                movie_info = candidate_movies[
                    candidate_movies["movie_id"] == movie_id
                ].iloc[0]
                top_knn.append(
                    {
                        "movie_id": int(movie_id),
                        "title": movie_info["title"],
                        "score": float(score),
                        "description": movie_info.get("description", ""),
                        "algorithm": "knn_structural",
                        "source": "TOP 5 KNN (structural similarity)",
                    }
                )
                used_ids.add(movie_id)
            except Exception as e:
                self.logger.error(f"Error serializing KNN movie {movie_id}: {e}")
                continue

        # ═══════════════════════════════════════════════
        # TOP 5 NB (textual)
        # ═══════════════════════════════════════════════
        top_nb_items = sorted(nb_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        top_nb = []
        for movie_id, score in top_nb_items:
            try:
                movie_info = candidate_movies[
                    candidate_movies["movie_id"] == movie_id
                ].iloc[0]
                top_nb.append(
                    {
                        "movie_id": int(movie_id),
                        "title": movie_info["title"],
                        "score": float(score),
                        "description": movie_info.get("description", ""),
                        "algorithm": "nb_textual",
                        "source": "TOP 5 NB (textual similarity)",
                    }
                )
                used_ids.add(movie_id)
            except Exception as e:
                self.logger.error(f"Error serializing NB movie {movie_id}: {e}")
                continue

        # ═══════════════════════════════════════════════
        # TOP 10 Hybrid (combined + MMR + no duplicates)
        # ═══════════════════════════════════════════════
        preference_strength = self._last_preference_strength

        # Optional MMR
        if preference_strength < 0.6:
            self.logger.info(
                f"Weak patterns ({preference_strength:.2f}) – adding MMR diversity (λ=0.03)"
            )
            try:
                ranked_hybrid = self.similarity_metrics.rank_recommendations(
                    hybrid_scores, candidate_movies, diversity_factor=0.03
                )
            except Exception as e:
                self.logger.error(f"MMR error: {e} – fallback sorted")
                ranked_hybrid = sorted(
                    hybrid_scores.items(), key=lambda x: x[1], reverse=True
                )
        else:
            self.logger.info(f"Strong patterns ({preference_strength:.2f}) – NO MMR")
            ranked_hybrid = sorted(
                hybrid_scores.items(), key=lambda x: x[1], reverse=True
            )

        # Collect TOP 10 unique (skip duplicates z KNN/NB)
        top_hybrid = []
        hybrid_target = 10
        duplicates_skipped = 0

        for movie_id, score in ranked_hybrid:
            # Skip jeśli już użyty w KNN/NB
            if movie_id in used_ids:
                duplicates_skipped += 1
                continue

            try:
                movie_info = candidate_movies[
                    candidate_movies["movie_id"] == movie_id
                ].iloc[0]

                # Get breakdown
                knn_s = knn_scores.get(movie_id, 0.0)
                nb_s = nb_scores.get(movie_id, 0.0)

                top_hybrid.append(
                    {
                        "movie_id": int(movie_id),
                        "title": movie_info["title"],
                        "score": float(score),
                        "description": movie_info.get("description", ""),
                        "algorithm": "hybrid_adaptive",
                        "source": "TOP 10 Hybrid (KNN + NB combined)",
                        "breakdown": {
                            "knn_score": float(knn_s),
                            "nb_score": float(nb_s),
                            "hybrid_formula": f"{ENSEMBLE_KNN_WEIGHT:.1f}*KNN + {ENSEMBLE_NB_WEIGHT:.1f}*NB",
                        },
                    }
                )
                used_ids.add(movie_id)

                # Stop gdy mamy 10 unique
                if len(top_hybrid) >= hybrid_target:
                    break

            except Exception as e:
                self.logger.error(f"Error serializing Hybrid movie {movie_id}: {e}")
                continue

        # Stats
        self.logger.info(
            f"TOP 5 KNN: avg={sum(r['score'] for r in top_knn)/len(top_knn) if top_knn else 0:.3f}"
        )
        self.logger.info(
            f"TOP 5 NB: avg={sum(r['score'] for r in top_nb)/len(top_nb) if top_nb else 0:.3f}"
        )
        self.logger.info(
            f"TOP 10 Hybrid: avg={sum(r['score'] for r in top_hybrid)/len(top_hybrid) if top_hybrid else 0:.3f}"
        )
        self.logger.info(
            f"Total unique: {len(used_ids)} (skipped {duplicates_skipped} duplicates in Hybrid)"
        )

        return {
            "top_knn": top_knn,
            "top_nb": top_nb,
            "top_hybrid": top_hybrid,
        }

    def _save_recommendations_multi(
        self, user_id: int, recommendations: Dict[str, List[Dict]]
    ):
        """
        Save all unique recommendations (FINAL deduplication check)
        Priority: KNN > NB > Hybrid (jeśli overlap)
        """
        try:
            # Delete old
            deleted = (
                self.db.query(Recommendation)
                .filter(Recommendation.user_id == user_id)
                .delete()
            )

            # Collect all unique (with final deduplication)
            all_recs = []
            seen_ids = set()

            # Priority 1: KNN
            for rec in recommendations["top_knn"]:
                if rec["movie_id"] not in seen_ids:
                    all_recs.append(rec)
                    seen_ids.add(rec["movie_id"])
                else:
                    self.logger.warning(
                        f"Duplicate in KNN: movie_id={rec['movie_id']} (skipping)"
                    )

            # Priority 2: NB
            for rec in recommendations["top_nb"]:
                if rec["movie_id"] not in seen_ids:
                    all_recs.append(rec)
                    seen_ids.add(rec["movie_id"])
                else:
                    self.logger.warning(
                        f"Duplicate in NB: movie_id={rec['movie_id']} (skipping)"
                    )

            # Priority 3: Hybrid
            for rec in recommendations["top_hybrid"]:
                if rec["movie_id"] not in seen_ids:
                    all_recs.append(rec)
                    seen_ids.add(rec["movie_id"])
                else:
                    self.logger.warning(
                        f"Duplicate in Hybrid: movie_id={rec['movie_id']} (skipping)"
                    )

            # Save to DB
            for rec in all_recs:
                recommendation = Recommendation(
                    user_id=user_id,
                    movie_id=int(rec["movie_id"]),
                    score=float(rec["score"]),
                    created_at=datetime.utcnow(),
                )
                self.db.add(recommendation)

            self.db.commit()
            self.logger.info(
                f"Zapisano {len(all_recs)} unique recs (usunięto {deleted})"
            )

        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Błąd zapisu: {str(e)}")
            raise

    def _fallback_popular_recommendations(
        self, candidate_movies: pd.DataFrame
    ) -> Dict[str, List[Dict]]:
        """Fallback popular (all sections)"""
        self.logger.info("Fallback popular")

        if "avg_rating" in candidate_movies.columns:
            popular = candidate_movies.sort_values(
                "avg_rating", ascending=False, na_position="last"
            ).head(20)
        else:
            popular = candidate_movies.sample(min(20, len(candidate_movies)))

        # Split into 3 sections (5+5+10)
        top_knn = []
        top_nb = []
        top_hybrid = []

        for i, (_, row) in enumerate(popular.iterrows()):
            score = 1.0 - (i / 20) * 0.5
            rec = {
                "movie_id": int(row["movie_id"]),
                "title": row["title"],
                "score": float(score),
                "description": row.get("description", ""),
                "algorithm": "fallback_popular",
            }

            if i < 5:
                top_knn.append({**rec, "source": "TOP 5 KNN (fallback popular)"})
            elif i < 10:
                top_nb.append({**rec, "source": "TOP 5 NB (fallback popular)"})
            else:
                top_hybrid.append({**rec, "source": "TOP 10 Hybrid (fallback popular)"})

        return {
            "top_knn": top_knn,
            "top_nb": top_nb,
            "top_hybrid": top_hybrid,
        }

    def get_recommendation_explanation(
        self, user_id: int, movie_id: int
    ) -> Dict[str, any]:
        try:
            user_ratings = self.preprocessor.get_user_ratings(user_id)
            patterns = self.preprocessor.analyze_user_preferences(user_ratings)
            return {
                "user_id": user_id,
                "movie_id": movie_id,
                "explanation": "Multi-section: KNN (structural) + NB (textual) + Hybrid (combined)",
                "structural_similarity": f"KNN z adaptive weights: {patterns}",
                "textual_similarity": "NB P(positive) na tf*idf",
                "adaptation_info": f"Preference strength: {max(patterns.values()):.2f}",
                "algorithm": "Adaptive Pazzani & Billsus multi-section",
            }
        except Exception as e:
            return {"error": f"Błąd: {str(e)}"}

    def analyze_user_preference_trends(self, user_id: int) -> Dict[str, any]:
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
        return {
            "algorithm": "Multi-Section Adaptive Hybrid",
            "theory_base": "Pazzani & Billsus + adaptive weighting + multi-section display",
            "innovation": "3 separate sections (TOP 5 KNN + TOP 5 NB + TOP 10 Hybrid) - ZAWSZE 20 unique",
            "sections": {
                "top_knn": "TOP 5 structural similarity (genres/directors/actors)",
                "top_nb": "TOP 5 textual similarity (description keywords)",
                "top_hybrid": "TOP 10 combined (weighted KNN + NB + optional MMR, no duplicates)",
            },
            "components": {
                "structural": "k-NN cosine z adaptive weights",
                "textual": "NB multinomial na tf*idf",
                "hybrid": "Adaptive weighted sum + conditional MMR",
            },
            "weights": {
                "base_knn": ENSEMBLE_KNN_WEIGHT,
                "base_nb": ENSEMBLE_NB_WEIGHT,
                "adaptation": "Boost structural jeśli preference_strength > 0.5",
            },
        }
