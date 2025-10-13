from sqlalchemy.orm import Session
import pandas as pd
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime

from .config import (
    MIN_USER_RATINGS,
    NUM_RECOMMENDATIONS,
    STRUCTURAL_WEIGHT,
    TEXTUAL_WEIGHT,
    RECENT_RATINGS_LIMIT,
)
from .utils.data_preprocessor import DataPreprocessor
from .content_based.knn_recommender import KNNRecommender
from .content_based.naive_bayes_recommender import NaiveBayesRecommender
from .content_based.tfidf_processor import TFIDFProcessor
from .utils.similarity_metrics import SimilarityMetrics
from app.models.recommendation import Recommendation


class MovieRecommender:
    """
    ADAPTACYJNY HYBRYDOWY SYSTEM REKOMENDACYJNY
    Zgodny z teorią Pazzaniego i Billsusa + adaptacyjne ważenie
    Łączy k-NN (dane strukturalne) z Naive Bayes (dane tekstowe)
    NOWOŚĆ: Automatyczne dostosowywanie do wzorców preferencji użytkownika
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
        GŁÓWNA METODA z ADAPTACYJNYM WAŻENIEM
        1. Analizuje wzorce preferencji użytkownika (reżyserzy, aktorzy, gatunki)
        2. Dynamicznie dostosowuje wagi cech
        3. Generuje hybrydowe rekomendacje
        """
        try:
            from app.models.rating import Rating

            actual_ratings_count = (
                self.db.query(Rating).filter(Rating.user_id == user_id).count()
            )
            self.logger.info(
                f"User {user_id} ma {actual_ratings_count} ocen w bazie (analizujemy ostatnie {RECENT_RATINGS_LIMIT})"
            )

            # Sprawdź kwalifikację użytkownika (minimum ocen)
            if not self.preprocessor.check_user_eligibility(user_id):
                return {
                    "success": False,
                    "message": f"Użytkownik musi mieć co najmniej {MIN_USER_RATINGS} ocenionych filmów (rzeczywista liczba: {actual_ratings_count})",
                    "recommendations": [],
                }

            # 1. BUDOWA PROFILU UŻYTKOWNIKA + ANALIZA WZORCÓW
            user_ratings = self.preprocessor.get_user_ratings(user_id)
            candidate_movies = self.preprocessor.get_candidate_movies(user_id)

            self.logger.info(f"Profil użytkownika: {len(user_ratings)} ostatnich ocen")
            self.logger.info(
                f"Kandydaci do rekomendacji: {len(candidate_movies)} filmów"
            )

            if candidate_movies.empty:
                return {
                    "success": False,
                    "message": "Brak filmów do zarekomendowania",
                    "recommendations": [],
                }

            # 2. ANALIZA WZORCÓW PREFERENCJI (NOWE!)
            user_preference_patterns = self.preprocessor.analyze_user_preferences(
                user_ratings
            )
            self.logger.info(
                f"Wzorce preferencji użytkownika: {user_preference_patterns}"
            )

            # 3. PRZYGOTOWANIE REPREZENTACJI DANYCH z ADAPTACYJNYMI WAGAMI
            # k-NN: cechy strukturalne z adaptacyjnymi wagami
            structural_scores = self._get_adaptive_structural_recommendations(
                user_ratings, candidate_movies
            )

            # Naive Bayes: dane tekstowe (opisy tf*idf)
            textual_scores = self._get_textual_recommendations(
                user_ratings, candidate_movies
            )

            # 4. HYBRYDOWA KOMBINACJA z informacją o wzorcach
            final_scores = self._combine_hybrid_scores(
                structural_scores, textual_scores, user_preference_patterns
            )

            # 5. SELEKCJA TOP N REKOMENDACJI
            top_recommendations = self._select_top_recommendations(
                final_scores, candidate_movies
            )

            # 6. ZAPIS REZULTATÓW
            self._save_recommendations(user_id, top_recommendations)

            self.logger.info(
                f"ADAPTACYJNY hybrydowy system: wygenerowano {len(top_recommendations)} rekomendacji dla użytkownika {user_id}"
            )

            return {
                "success": True,
                "message": f"Adaptacyjne hybrydowe rekomendacje na podstawie wzorców preferencji w {len(user_ratings)} ostatnich ocenach",
                "recommendations": top_recommendations,
                "algorithm_info": {
                    "approach": "Adaptive Pazzani & Billsus hybrid content-based filtering",
                    "adaptive_weights": user_preference_patterns,
                    "structural_weight": STRUCTURAL_WEIGHT,
                    "textual_weight": TEXTUAL_WEIGHT,
                    "knn_scores": len(structural_scores),
                    "nb_scores": len(textual_scores),
                    "feature_adaptation": "Dynamic weighting based on user preference patterns",
                },
            }

        except Exception as e:
            self.logger.error(f"Błąd w adaptacyjnym hybrydowym systemie: {str(e)}")
            import traceback

            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "message": f"Wystąpił błąd w adaptacyjnym systemie: {str(e)}",
                "recommendations": [],
            }

    def _get_adaptive_structural_recommendations(
        self, user_ratings: pd.DataFrame, candidate_movies: pd.DataFrame
    ) -> Dict[int, float]:
        """
        ALGORYTM k-NN z ADAPTACYJNYMI WAGAMI
        NOWOŚĆ: Przekazuje user_ratings do analizy wzorców preferencji
        """
        try:
            self.logger.info(
                f"k-NN z adaptacyjnymi wagami: analiza na {len(user_ratings)} ocenach"
            )

            # PRZEKAŻ user_ratings do analizy wzorców! (KLUCZOWA ZMIANA)
            structural_features_rated = self.preprocessor.prepare_structural_features(
                user_ratings, user_ratings
            )
            structural_features_candidates = (
                self.preprocessor.prepare_structural_features(
                    candidate_movies, user_ratings
                )
            )

            # Wyrównanie przestrzeni cech (dane pół-strukturalne)
            features_rated_aligned, features_candidates_aligned = (
                self.preprocessor.align_features(
                    structural_features_rated, structural_features_candidates
                )
            )

            # Trening k-NN z miarą kosinusową (zgodnie z teorią)
            self.knn_recommender.fit(features_rated_aligned, user_ratings)
            knn_scores = self.knn_recommender.predict_ratings(
                features_candidates_aligned, user_ratings
            )

            # Normalizacja do [0,1] dla kombinacji hybrydowej
            normalized_scores = {}
            for movie_id, rating in knn_scores.items():
                normalized_score = (rating - 1.0) / 9.0  # z [1,10] do [0,1]
                normalized_scores[movie_id] = max(0.0, min(1.0, normalized_score))

            avg_score = (
                sum(normalized_scores.values()) / len(normalized_scores)
                if normalized_scores
                else 0
            )
            self.logger.info(
                f"k-NN (adaptacyjne strukturalne): {len(normalized_scores)} predykcji, średnia={avg_score:.3f}"
            )

            return normalized_scores

        except Exception as e:
            self.logger.error(f"Błąd w adaptacyjnym k-NN: {str(e)}")
            return {}

    def _get_textual_recommendations(
        self, user_ratings: pd.DataFrame, candidate_movies: pd.DataFrame
    ) -> Dict[int, float]:
        """
        NAIVE BAYES NA DANYCH TEKSTOWYCH
        Implementacja zgodna z rozdziałem 2.3.5 (model multinomialny)
        """
        try:
            self.logger.info(
                f"Naive Bayes: analiza opisów tekstowych na {len(user_ratings)} ocenach"
            )

            # Trening Naive Bayes na opisach filmów (tf*idf)
            self.nb_recommender.fit(user_ratings)
            nb_scores = self.nb_recommender.predict_with_movie_ids(candidate_movies)

            avg_score = sum(nb_scores.values()) / len(nb_scores) if nb_scores else 0
            self.logger.info(
                f"Naive Bayes (tekstowe): {len(nb_scores)} predykcji, średnia={avg_score:.3f}"
            )
            return nb_scores

        except Exception as e:
            self.logger.error(f"Błąd w Naive Bayes (tekstowym): {str(e)}")
            return {}

    def _combine_hybrid_scores(
        self,
        structural_scores: Dict[int, float],
        textual_scores: Dict[int, float],
        preference_patterns: Dict[str, float],
    ) -> Dict[int, float]:
        """
        ADAPTACYJNA HYBRYDOWA KOMBINACJA
        Uwzględnia wzorce preferencji przy łączeniu wyników
        """
        combined_scores = {}
        all_movie_ids = set(structural_scores.keys()) | set(textual_scores.keys())

        # Oblicz adaptacyjne wagi hybrydowe na podstawie wzorców
        structural_dominance = (
            max(preference_patterns.values()) if preference_patterns else 0
        )

        # Jeśli użytkownik ma silne wzorce strukturalne (np. lubi konkretnego reżysera)
        # zwiększ wagę strukturalną
        if structural_dominance > 0.5:
            adaptive_structural_weight = min(0.9, STRUCTURAL_WEIGHT + 0.2)
            adaptive_textual_weight = 1.0 - adaptive_structural_weight
            self.logger.info(
                f"Wykryto silne wzorce preferencji - zwiększam wagę strukturalną: {adaptive_structural_weight:.2f}"
            )
        else:
            adaptive_structural_weight = STRUCTURAL_WEIGHT
            adaptive_textual_weight = TEXTUAL_WEIGHT

        self.logger.info(
            f"Adaptacyjna hybrydowa kombinacja: k-NN({len(structural_scores)}) + NB({len(textual_scores)}) = {len(all_movie_ids)} filmów"
        )
        self.logger.info(
            f"Adaptacyjne wagi hybrydowe: strukturalne={adaptive_structural_weight:.2f}, tekstowe={adaptive_textual_weight:.2f}"
        )

        for movie_id in all_movie_ids:
            knn_score = structural_scores.get(movie_id, 0.0)
            nb_score = textual_scores.get(movie_id, 0.0)

            # Adaptacyjny wzór hybrydowy
            combined_score = (
                adaptive_structural_weight * knn_score
                + adaptive_textual_weight * nb_score
            )
            combined_scores[movie_id] = combined_score

        # Debug top wyników hybrydowych
        if combined_scores:
            top_5_hybrid = sorted(
                combined_scores.items(), key=lambda x: x[1], reverse=True
            )[:5]
            self.logger.info(f"Top 5 adaptacyjne hybrydowe: {top_5_hybrid}")

        return combined_scores

    def _select_top_recommendations(
        self, scores: Dict[int, float], candidate_movies: pd.DataFrame
    ) -> List[Dict]:
        """Selekcja top N rekomendacji z metadanymi o adaptacji"""
        if not scores:
            self.logger.warning("Brak scores - fallback do losowych filmów")
            import random

            random_movies = candidate_movies.sample(
                min(NUM_RECOMMENDATIONS, len(candidate_movies))
            )

            top_recommendations = []
            for _, movie_info in random_movies.iterrows():
                top_recommendations.append(
                    {
                        "movie_id": int(movie_info["movie_id"]),
                        "title": movie_info["title"],
                        "score": 0.5,
                        "description": movie_info.get("description", ""),
                        "algorithm": "random_fallback",
                    }
                )
            return top_recommendations

        # Sortowanie według adaptacyjnego hybrydowego score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_recommendations = []

        self.logger.info(f"Top 5 adaptacyjnych hybrydowych scores: {sorted_scores[:5]}")

        for movie_id, score in sorted_scores[:NUM_RECOMMENDATIONS]:
            movie_info = candidate_movies[
                candidate_movies["movie_id"] == movie_id
            ].iloc[0]
            top_recommendations.append(
                {
                    "movie_id": int(movie_id),
                    "title": movie_info["title"],
                    "score": float(score),
                    "description": movie_info.get("description", ""),
                    "algorithm": f"adaptive_hybrid_knn_nb",
                    "adaptation_info": "Weights adapted based on user preference patterns",
                }
            )

        return top_recommendations

    def _save_recommendations(self, user_id: int, recommendations: List[Dict]):
        """Zapisuje adaptacyjne hybrydowe rekomendacje do bazy danych"""
        try:
            # Usuń stare rekomendacje
            deleted_count = (
                self.db.query(Recommendation)
                .filter(Recommendation.user_id == user_id)
                .delete()
            )

            # Zapisz nowe adaptacyjne rekomendacje
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
                f"Adaptacyjne hybrydowe rekomendacje: zapisano {len(recommendations)} (usunięto {deleted_count} starych)"
            )

        except Exception as e:
            self.db.rollback()
            self.logger.error(
                f"Błąd podczas zapisu adaptacyjnych rekomendacji: {str(e)}"
            )
            raise

    def get_recommendation_explanation(
        self, user_id: int, movie_id: int
    ) -> Dict[str, any]:
        """Wyjaśnia dlaczego film został zarekomendowany - z informacją o adaptacji"""
        try:
            # Pobierz wzorce preferencji użytkownika
            user_ratings = self.preprocessor.get_user_ratings(user_id)
            preference_patterns = self.preprocessor.analyze_user_preferences(
                user_ratings
            )

            return {
                "user_id": user_id,
                "movie_id": movie_id,
                "explanation": "Rekomendacja oparta na adaptacyjnym hybrydowym podejściu k-NN + Naive Bayes",
                "structural_similarity": "Podobieństwo w gatunkach, aktorach i reżyserach z adaptacyjnymi wagami",
                "textual_similarity": "Podobieństwo w opisach fabuły (tf*idf)",
                "adaptation_info": f"Wagi dostosowane do wzorców preferencji: {preference_patterns}",
                "algorithm": "Adaptive Pazzani & Billsus hybrid content-based filtering",
            }
        except Exception as e:
            return {"error": f"Błąd wyjaśnienia: {str(e)}"}

    def analyze_user_preference_trends(self, user_id: int) -> Dict[str, any]:
        """NOWA METODA: Analizuje trendy preferencji użytkownika"""
        try:
            user_ratings = self.preprocessor.get_user_ratings(user_id)
            preference_patterns = self.preprocessor.analyze_user_preferences(
                user_ratings
            )

            # Identyfikuj typ użytkownika
            max_weight = max(preference_patterns.values())
            dominant_feature = max(
                preference_patterns.keys(), key=preference_patterns.get
            )

            if max_weight > 0.6:
                user_type = f"Specjalista ({dominant_feature})"
                adaptation = f"Zwiększona waga dla {dominant_feature}"
            else:
                user_type = "Wszechstronny widz"
                adaptation = "Równomierne wagi dla wszystkich cech"

            return {
                "user_id": user_id,
                "user_type": user_type,
                "preference_weights": preference_patterns,
                "adaptation_strategy": adaptation,
                "dominant_feature": dominant_feature,
                "specialization_level": max_weight,
            }
        except Exception as e:
            return {"error": f"Błąd analizy trendów: {str(e)}"}

    def get_system_info(self) -> Dict[str, any]:
        """Zwraca informacje o adaptacyjnym systemie rekomendacyjnym"""
        return {
            "algorithm": "Adaptive Hybrid Content-Based Filtering",
            "theory_base": "Pazzani & Billsus (2007) + Adaptive Weighting",
            "innovation": "Dynamic feature weighting based on user preference patterns",
            "components": {
                "structural": "k-NN with adaptive cosine similarity on genres/actors/directors",
                "textual": "Naive Bayes (multinomial) on tf*idf descriptions",
                "adaptation": "Preference pattern analysis with dynamic weight adjustment",
            },
            "data_representation": "Semi-structured (structural + tf*idf) with adaptive weights",
            "weights": {
                "base_structural": STRUCTURAL_WEIGHT,
                "base_textual": TEXTUAL_WEIGHT,
                "adaptation": "Dynamic based on user patterns",
            },
            "features": {
                "genres": "One-hot encoded with adaptive weights",
                "actors": "Binary (top 50) with adaptive weights",
                "directors": "Binary (top 50) with adaptive weights",
                "descriptions": "tf*idf weighted terms",
                "adaptation_threshold": "High rating patterns (8-10) trigger weight adaptation",
            },
        }
