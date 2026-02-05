from sqlalchemy.orm import Session
import pandas as pd
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime

from .config import (
    MIN_USER_RATINGS,
    NUM_RECOMMENDATIONS,
    KNN_RECOMMENDATIONS,
    NB_RECOMMENDATIONS,
    HYBRID_RECOMMENDATIONS,
    ENSEMBLE_KNN_WEIGHT,
    ENSEMBLE_NB_WEIGHT,
    HYBRID_EXCLUDE_DUPLICATES,
    TRAINING_POSITIVE_LIMIT,
    TRAINING_NEGATIVE_LIMIT,
    POSITIVE_RATING_THRESHOLD,
    NEGATIVE_RATING_THRESHOLD,
    MIN_POSITIVES_FOR_QUALITY,
)
from .utils.data_preprocessor import DataPreprocessor
from .content_based.knn_recommender import KNNRecommender
from .content_based.naive_bayes_recommender import NaiveBayesRecommender
from .utils.similarity_metrics import SimilarityMetrics
from app.models.recommendation import Recommendation
from app.models.rating import Rating


class MovieRecommender:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.preprocessor = DataPreprocessor(db_session)
        self.knn_recommender = KNNRecommender()
        self.nb_recommender = NaiveBayesRecommender(model_type="multinomial")
        self.similarity_metrics = SimilarityMetrics()
        self._knn_scores = {}
        self._nb_scores = {}
        self._adaptive_weights = {}
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def generate_recommendations(self, user_id: int) -> Dict[str, any]:
        try:
            if not self.preprocessor.check_user_eligibility(user_id):
                actual_count = (
                    self.db.query(Rating).filter(Rating.user_id == user_id).count()
                )
                return {
                    "success": False,
                    "message": f"User needs {MIN_USER_RATINGS} ratings minimum (has {actual_count})",
                    "recommendations": {"knn": [], "naive_bayes": [], "hybrid": []},
                }

            all_user_ratings = self.preprocessor.get_user_ratings(user_id)
            positive_ratings, negative_ratings, stats = (
                self.preprocessor.get_training_data(all_user_ratings)
            )

            self.logger.info(
                f"User {user_id}: {stats['total_ratings']} total ratings, "
                f"{stats['positive_count']} positive, {stats['negative_count']} negative"
            )

            if len(positive_ratings) < MIN_POSITIVES_FOR_QUALITY:
                self.logger.warning(
                    f"User has only {len(positive_ratings)} positive ratings "
                    f"(recommended: {MIN_POSITIVES_FOR_QUALITY}+). Results may be suboptimal."
                )

            candidate_movies = self.preprocessor.get_candidate_movies(user_id)

            if candidate_movies.empty:
                return {
                    "success": False,
                    "message": "No candidate movies available",
                    "recommendations": {"knn": [], "naive_bayes": [], "hybrid": []},
                }

            self.logger.info(
                f"Profile: {len(positive_ratings)} positive + {len(negative_ratings)} negative; "
                f"Candidates: {len(candidate_movies)} movies"
            )

            self._adaptive_weights = self.preprocessor.analyze_user_preferences(
                positive_ratings
            )
            preference_strength = (
                max(self._adaptive_weights.values()) if self._adaptive_weights else 0.0
            )

            self.logger.info(
                f"Adaptive weights: {self._adaptive_weights}, "
                f"max_strength={preference_strength:.3f}"
            )

            self._knn_scores = self._get_knn_recommendations(
                positive_ratings, candidate_movies
            )
            self._nb_scores = self._get_nb_recommendations(
                positive_ratings, negative_ratings, candidate_movies
            )
            hybrid_scores = self._get_hybrid_recommendations(
                self._knn_scores, self._nb_scores, preference_strength
            )

            top_recommendations = self._select_top_recommendations(
                self._knn_scores, self._nb_scores, hybrid_scores, candidate_movies
            )

            self._save_recommendations(user_id, top_recommendations)

            return {
                "success": True,
                "message": f"Generated {KNN_RECOMMENDATIONS} KNN + {NB_RECOMMENDATIONS} NB + {HYBRID_RECOMMENDATIONS} Hybrid = {NUM_RECOMMENDATIONS} total",
                "recommendations": top_recommendations,
                "stats": {
                    "user_id": user_id,
                    "total_ratings": stats["total_ratings"],
                    "positive_count": stats["positive_count"],
                    "negative_count": stats["negative_count"],
                    "neutral_count": stats["neutral_count"],
                    "candidates_count": len(candidate_movies),
                    "knn_predictions": len(self._knn_scores),
                    "nb_predictions": len(self._nb_scores),
                    "hybrid_predictions": len(hybrid_scores),
                    "adaptive_weights": self._adaptive_weights,
                    "preference_strength": preference_strength,
                    "warnings": stats.get("warnings", []),
                },
            }

        except Exception as e:
            self.logger.error(f"generate_recommendations failed: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "recommendations": {"knn": [], "naive_bayes": [], "hybrid": []},
            }

    def _get_knn_recommendations(
        self, positive_ratings: pd.DataFrame, candidate_movies: pd.DataFrame
    ) -> Dict[int, float]:
        try:
            self.logger.info(
                f"K-NN: training on {len(positive_ratings)} positive ratings"
            )

            positive_features = self.preprocessor.prepare_structural_features(
                positive_ratings, user_ratings=positive_ratings
            )
            candidate_features = self.preprocessor.prepare_structural_features(
                candidate_movies, user_ratings=positive_ratings
            )

            positive_aligned, candidates_aligned = self.preprocessor.align_features(
                positive_features, candidate_features
            )

            knn_scores = self.knn_recommender.recommend(
                positive_ratings=positive_ratings,
                positive_features=positive_aligned,
                candidate_features=candidates_aligned,
                adaptive_weights=self._adaptive_weights,
                top_k=len(candidate_movies),
            )

            knn_scores_dict = {movie_id: score for movie_id, score in knn_scores}

            if knn_scores_dict:
                avg = sum(knn_scores_dict.values()) / len(knn_scores_dict)
                self.logger.info(
                    f"K-NN: {len(knn_scores_dict)} predictions, avg={avg:.3f}"
                )

            return knn_scores_dict

        except Exception as e:
            self.logger.error(f"K-NN error: {e}", exc_info=True)
            return {}

    def _get_nb_recommendations(
        self,
        positive_ratings: pd.DataFrame,
        negative_ratings: pd.DataFrame,
        candidate_movies: pd.DataFrame,
    ) -> Dict[int, float]:
        try:
            self.logger.info(
                f"Naive Bayes: training on {len(positive_ratings)} positive + "
                f"{len(negative_ratings)} negative"
            )

            positive_movie_ids = positive_ratings["movie_id"].tolist()
            negative_movie_ids = negative_ratings["movie_id"].tolist()
            candidate_movie_ids = candidate_movies["movie_id"].tolist()

            all_movie_ids = list(
                set(positive_movie_ids + negative_movie_ids + candidate_movie_ids)
            )
            all_descriptions = self.preprocessor.get_movie_descriptions(all_movie_ids)

            positive_descriptions = all_descriptions[
                all_descriptions["movie_id"].isin(positive_movie_ids)
            ]
            negative_descriptions = all_descriptions[
                all_descriptions["movie_id"].isin(negative_movie_ids)
            ]
            candidate_descriptions = all_descriptions[
                all_descriptions["movie_id"].isin(candidate_movie_ids)
            ]

            self.logger.info(
                f"Descriptions: {len(positive_descriptions)} positive, "
                f"{len(negative_descriptions)} negative, {len(candidate_descriptions)} candidates"
            )

            nb_predictions = self.nb_recommender.recommend(
                positive_descriptions=positive_descriptions,
                negative_descriptions=negative_descriptions,
                candidate_descriptions=candidate_descriptions,
                top_k=len(candidate_descriptions),
            )

            nb_scores_dict = {movie_id: score for movie_id, score in nb_predictions}

            if nb_scores_dict:
                avg = sum(nb_scores_dict.values()) / len(nb_scores_dict)
                self.logger.info(
                    f"Naive Bayes: {len(nb_scores_dict)} predictions, avg={avg:.3f}"
                )

            return nb_scores_dict

        except Exception as e:
            self.logger.error(f"Naive Bayes error: {e}", exc_info=True)
            return {}

    def _get_hybrid_recommendations(
        self,
        knn_scores: Dict[int, float],
        nb_scores: Dict[int, float],
        preference_strength: float,
    ) -> Dict[int, float]:
        try:
            if preference_strength > 0.5:
                knn_weight = min(0.75, ENSEMBLE_KNN_WEIGHT + 0.15)
                nb_weight = 1.0 - knn_weight
                self.logger.info(
                    f"Strong patterns ({preference_strength:.3f}) → boost KNN weight to {knn_weight:.2f}"
                )
            else:
                knn_weight = ENSEMBLE_KNN_WEIGHT
                nb_weight = ENSEMBLE_NB_WEIGHT

            hybrid_scores = self.similarity_metrics.combine_algorithm_scores(
                knn_scores, nb_scores, knn_weight, nb_weight
            )

            if hybrid_scores:
                avg = sum(hybrid_scores.values()) / len(hybrid_scores)
                self.logger.info(
                    f"Hybrid: {len(hybrid_scores)} scores, avg={avg:.3f}, "
                    f"weights=({knn_weight:.2f} KNN + {nb_weight:.2f} NB)"
                )

            return hybrid_scores

        except Exception as e:
            self.logger.error(f"Hybrid error: {e}", exc_info=True)
            return {}

    def _select_top_recommendations(
        self,
        knn_scores: Dict[int, float],
        nb_scores: Dict[int, float],
        hybrid_scores: Dict[int, float],
        candidate_movies: pd.DataFrame,
    ) -> Dict[str, List[Dict]]:
        used_ids = set()

        top_knn_items = sorted(knn_scores.items(), key=lambda x: x[1], reverse=True)[
            :KNN_RECOMMENDATIONS
        ]
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
                        "algorithm_type": "knn",
                    }
                )
                used_ids.add(movie_id)
            except Exception as e:
                self.logger.error(f"Error serializing KNN movie {movie_id}: {e}")

        nb_candidates = sorted(nb_scores.items(), key=lambda x: x[1], reverse=True)
        top_nb = []
        nb_skipped = 0

        for movie_id, score in nb_candidates:
            if movie_id in used_ids:
                nb_skipped += 1
                continue

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
                        "algorithm_type": "naive_bayes",
                    }
                )
                used_ids.add(movie_id)

                if len(top_nb) >= NB_RECOMMENDATIONS:
                    break

            except Exception as e:
                self.logger.error(f"Error serializing NB movie {movie_id}: {e}")

        top_hybrid = []
        duplicates_skipped = 0
        sorted_hybrid = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)

        for movie_id, score in sorted_hybrid:
            if HYBRID_EXCLUDE_DUPLICATES and movie_id in used_ids:
                duplicates_skipped += 1
                continue

            try:
                movie_info = candidate_movies[
                    candidate_movies["movie_id"] == movie_id
                ].iloc[0]
                knn_score = knn_scores.get(movie_id, 0.0)
                nb_score = nb_scores.get(movie_id, 0.0)

                top_hybrid.append(
                    {
                        "movie_id": int(movie_id),
                        "title": movie_info["title"],
                        "score": float(score),
                        "description": movie_info.get("description", ""),
                        "algorithm_type": "hybrid",
                        "breakdown": {
                            "knn_score": float(knn_score),
                            "nb_score": float(nb_score),
                            "knn_weight": ENSEMBLE_KNN_WEIGHT,
                            "nb_weight": ENSEMBLE_NB_WEIGHT,
                        },
                    }
                )
                used_ids.add(movie_id)

                if len(top_hybrid) >= HYBRID_RECOMMENDATIONS:
                    break

            except Exception as e:
                self.logger.error(f"Error serializing Hybrid movie {movie_id}: {e}")

        self.logger.info(
            f"Selected: {len(top_knn)} KNN + {len(top_nb)} NB (skipped {nb_skipped}) "
            f"+ {len(top_hybrid)} Hybrid (skipped {duplicates_skipped}) = {len(used_ids)} unique"
        )

        return {"knn": top_knn, "naive_bayes": top_nb, "hybrid": top_hybrid}

    def _save_recommendations(
        self, user_id: int, recommendations: Dict[str, List[Dict]]
    ) -> None:
        try:
            deleted = (
                self.db.query(Recommendation)
                .filter(Recommendation.user_id == user_id)
                .delete()
            )
            all_recs = (
                recommendations["knn"]
                + recommendations["naive_bayes"]
                + recommendations["hybrid"]
            )

            for rec in all_recs:
                recommendation = Recommendation(
                    user_id=user_id,
                    movie_id=rec["movie_id"],
                    score=rec["score"],
                    algorithm_type=rec["algorithm_type"],
                    created_at=datetime.utcnow(),
                )
                self.db.add(recommendation)

            self.db.commit()
            self.logger.info(
                f"Saved {len(all_recs)} recommendations (deleted {deleted} old) with algorithm_type tags"
            )

        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Save recommendations failed: {e}", exc_info=True)
            raise

    def get_recommendation_explanation(
        self, user_id: int, movie_id: int
    ) -> Dict[str, any]:
        try:
            all_ratings = self.preprocessor.get_user_ratings(user_id)
            positive_ratings, negative_ratings, _ = self.preprocessor.get_training_data(
                all_ratings
            )
            adaptive_weights = self.preprocessor.analyze_user_preferences(
                positive_ratings
            )

            rec = (
                self.db.query(Recommendation)
                .filter(
                    Recommendation.user_id == user_id,
                    Recommendation.movie_id == movie_id,
                )
                .first()
            )

            if not rec:
                return {"error": "Recommendation not found"}

            explanation = {
                "user_id": user_id,
                "movie_id": movie_id,
                "algorithm_type": rec.algorithm_type,
                "score": float(rec.score),
                "adaptive_weights": adaptive_weights,
            }

            if rec.algorithm_type == "knn":
                explanation["method"] = (
                    "Structural similarity (genres, actors, directors, country, year)"
                )
                explanation["features_used"] = list(adaptive_weights.keys())
            elif rec.algorithm_type == "naive_bayes":
                explanation["method"] = "Textual similarity (TF-IDF on descriptions)"
                explanation["interpretation"] = (
                    f"P(like | description) = {rec.score:.3f}"
                )
            elif rec.algorithm_type == "hybrid":
                explanation["method"] = (
                    f"Weighted combination ({ENSEMBLE_KNN_WEIGHT}*KNN + {ENSEMBLE_NB_WEIGHT}*NB)"
                )

            return explanation

        except Exception as e:
            self.logger.error(f"get_explanation failed: {e}", exc_info=True)
            return {"error": str(e)}

    def analyze_user_preference_trends(self, user_id: int) -> Dict[str, any]:
        try:
            all_ratings = self.preprocessor.get_user_ratings(user_id)
            positive_ratings, _, _ = self.preprocessor.get_training_data(all_ratings)
            adaptive_weights = self.preprocessor.analyze_user_preferences(
                positive_ratings
            )

            max_weight = max(adaptive_weights.values()) if adaptive_weights else 0
            dominant_feature = (
                max(adaptive_weights, key=adaptive_weights.get)
                if adaptive_weights
                else "none"
            )

            if max_weight > 0.6:
                user_type = f"Specialist ({dominant_feature})"
            elif max_weight > 0.4:
                user_type = "Focused"
            else:
                user_type = "Generalist"

            return {
                "user_id": user_id,
                "user_type": user_type,
                "adaptive_weights": adaptive_weights,
                "dominant_feature": dominant_feature,
                "specialization_level": float(max_weight),
                "positive_ratings_count": len(positive_ratings),
                "interpretation": (
                    f"User shows strong preference for {dominant_feature}"
                    if max_weight > 0.5
                    else "User has diverse preferences"
                ),
            }

        except Exception as e:
            self.logger.error(f"analyze_trends failed: {e}", exc_info=True)
            return {"error": str(e)}

    def get_system_info(self) -> Dict[str, any]:
        return {
            "algorithm": "Adaptive Hybrid Content-Based Filtering",
            "theory_base": "Pazzani & Billsus (2007) with adaptive weighting",
            "components": {
                "knn": {
                    "method": "K-Nearest Neighbors",
                    "features": "genres, actors, directors, country, year (structural)",
                    "metric": "weighted cosine similarity",
                    "output": f"Top {KNN_RECOMMENDATIONS} recommendations",
                },
                "naive_bayes": {
                    "method": "Multinomial Naive Bayes",
                    "features": "TF-IDF on movie descriptions (textual)",
                    "metric": "P(positive | description)",
                    "output": f"Top {NB_RECOMMENDATIONS} recommendations",
                },
                "hybrid": {
                    "method": "Weighted ensemble",
                    "formula": f"{ENSEMBLE_KNN_WEIGHT}*KNN + {ENSEMBLE_NB_WEIGHT}*NB",
                    "adaptation": "Boost KNN if strong patterns detected",
                    "output": f"Top {HYBRID_RECOMMENDATIONS} recommendations (excluding duplicates)",
                },
            },
            "total_output": NUM_RECOMMENDATIONS,
            "training_data": {
                "positive": f"{TRAINING_POSITIVE_LIMIT} last positive ratings (≥{POSITIVE_RATING_THRESHOLD})",
                "negative": f"{TRAINING_NEGATIVE_LIMIT} last negative ratings (≤{NEGATIVE_RATING_THRESHOLD})",
                "strategy": "Balanced positive/negative examples",
            },
            "adaptive_features": ["genres", "actors", "directors", "country", "year"],
            "innovation": "Adaptive weighting based on user patterns + 3-section output (KNN/NB/Hybrid)",
        }
