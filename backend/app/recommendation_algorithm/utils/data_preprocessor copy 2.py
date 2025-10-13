from sqlalchemy.orm import Session
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging
import numpy as np
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
import re

from ..config import (
    MIN_USER_RATINGS,
    POSITIVE_RATING_THRESHOLD,
    NEGATIVE_RATING_THRESHOLD,
    BATCH_SIZE,
    RECENT_RATINGS_LIMIT,
)
from app.models.rating import Rating
from app.models.movie import Movie
from app.models.user import User
from app.models.genre import Genre
from app.models.actor import Actor
from app.models.director import Director
from app.models.movie_genre import MovieGenre
from app.models.movie_actor import MovieActor
from app.models.movie_director import MovieDirector


class DataPreprocessor:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.logger = logging.getLogger(__name__)

    def check_user_eligibility(self, user_id: int) -> bool:
        """Sprawdza czy użytkownik ma minimum wymaganych ocen (Pazzani & Billsus)"""
        rating_count = self.db.query(Rating).filter(Rating.user_id == user_id).count()
        return rating_count >= MIN_USER_RATINGS

    def get_user_ratings(
        self, user_id: int, limit: int = RECENT_RATINGS_LIMIT
    ) -> pd.DataFrame:
        """Pobiera ostatnie N ocen użytkownika z metadanymi - budowa profilu użytkownika"""
        results = (
            self.db.query(
                Rating.movie_id,
                Rating.rating,
                Rating.rated_at,
                Movie.title,
                Movie.description,
                Movie.release_date,
                Movie.duration_minutes,
                Movie.country,
                Movie.original_language,
            )
            .join(Movie, Rating.movie_id == Movie.movie_id)
            .filter(Rating.user_id == user_id)
            .order_by(Rating.rated_at.desc())
            .limit(limit)
            .all()
        )

        data = []
        for result in results:
            data.append(
                {
                    "movie_id": result.movie_id,
                    "rating": result.rating,
                    "rated_at": result.rated_at,
                    "title": result.title,
                    "description": result.description,
                    "release_date": result.release_date,
                    "duration_minutes": result.duration_minutes,
                    "country": result.country,
                    "original_language": result.original_language,
                }
            )

        df = pd.DataFrame(data)
        df = self._add_genres_to_dataframe(df)
        df = self._add_actors_to_dataframe(df)
        df = self._add_directors_to_dataframe(df)

        self.logger.info(
            f"Pobrano {len(df)} ostatnich ocen użytkownika {user_id} (limit: {limit})"
        )
        return df

    def get_candidate_movies(self, user_id: int) -> pd.DataFrame:
        """Pobiera nieocenione filmy jako kandydatów do rekomendacji"""
        rated_movie_ids = [
            r.movie_id
            for r in self.db.query(Rating.movie_id)
            .filter(Rating.user_id == user_id)
            .all()
        ]

        query = self.db.query(
            Movie.movie_id,
            Movie.title,
            Movie.description,
            Movie.release_date,
            Movie.duration_minutes,
            Movie.country,
            Movie.original_language,
        )

        if rated_movie_ids:
            query = query.filter(~Movie.movie_id.in_(rated_movie_ids))

        results = query.all()

        data = []
        for result in results:
            data.append(
                {
                    "movie_id": result.movie_id,
                    "title": result.title,
                    "description": result.description,
                    "release_date": result.release_date,
                    "duration_minutes": result.duration_minutes,
                    "country": result.country,
                    "original_language": result.original_language,
                }
            )

        df = pd.DataFrame(data)
        df = self._add_genres_to_dataframe(df)
        df = self._add_actors_to_dataframe(df)
        df = self._add_directors_to_dataframe(df)
        return df

    def analyze_user_preferences(self, user_ratings: pd.DataFrame) -> Dict[str, float]:
        """
        ADAPTACYJNA ANALIZA WZORCÓW PREFERENCJI
        Identyfikuje czy użytkownik ma specyficzne preferencje (reżyser, aktor, gatunek)
        """
        if user_ratings.empty:
            return {"genres": 0.33, "actors": 0.33, "directors": 0.34}

        # Analizuj tylko wysokie oceny (8-10)
        high_rated = user_ratings[user_ratings["rating"] >= 8.0]

        if len(high_rated) < 2:
            self.logger.info(
                "Za mało wysokich ocen dla analizy wzorców - używam równomiernych wag"
            )
            return {"genres": 0.33, "actors": 0.33, "directors": 0.34}

        # Zlicz powtórzenia w wysokich ocenach
        director_patterns = self._analyze_director_patterns(high_rated)
        actor_patterns = self._analyze_actor_patterns(high_rated)
        genre_patterns = self._analyze_genre_patterns(high_rated)

        self.logger.info(
            f"Wzorce preferencji - Reżyserzy: {director_patterns}, Aktorzy: {actor_patterns}, Gatunki: {genre_patterns}"
        )

        # Oblicz adaptive weights na podstawie wzorców
        return self._calculate_adaptive_weights(
            director_patterns, actor_patterns, genre_patterns
        )

    def _analyze_director_patterns(self, high_rated: pd.DataFrame) -> Dict[str, int]:
        """Analizuje czy użytkownik lubi konkretnych reżyserów"""
        director_counts = {}

        for _, row in high_rated.iterrows():
            directors = row.get("directors", [])
            if isinstance(directors, list):
                for director in directors:
                    director_counts[director] = director_counts.get(director, 0) + 1

        # Znajdź reżyserów z więcej niż 1 wysoką oceną
        repeated_directors = {
            d: count for d, count in director_counts.items() if count > 1
        }

        if repeated_directors:
            self.logger.info(
                f"Powtarzalni reżyserzy w wysokich ocenach: {repeated_directors}"
            )

        return repeated_directors

    def _analyze_actor_patterns(self, high_rated: pd.DataFrame) -> Dict[str, int]:
        """Analizuje czy użytkownik lubi konkretnych aktorów"""
        actor_counts = {}

        for _, row in high_rated.iterrows():
            actors = row.get("actors", [])
            if isinstance(actors, list):
                for actor in actors[:5]:  # Top 5 aktorów per film
                    actor_counts[actor] = actor_counts.get(actor, 0) + 1

        repeated_actors = {a: count for a, count in actor_counts.items() if count > 1}

        if repeated_actors:
            self.logger.info(
                f"Powtarzalni aktorzy w wysokich ocenach: {repeated_actors}"
            )

        return repeated_actors

    def _analyze_genre_patterns(self, high_rated: pd.DataFrame) -> Dict[str, int]:
        """Analizuje czy użytkownik lubi konkretne gatunki"""
        genre_counts = {}

        for _, row in high_rated.iterrows():
            genres = row.get("genres", [])
            if isinstance(genres, list):
                for genre in genres:
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1

        repeated_genres = {g: count for g, count in genre_counts.items() if count > 1}

        if repeated_genres:
            self.logger.info(
                f"Powtarzalne gatunki w wysokich ocenach: {repeated_genres}"
            )

        return repeated_genres

    def _calculate_adaptive_weights(
        self,
        director_patterns: Dict[str, int],
        actor_patterns: Dict[str, int],
        genre_patterns: Dict[str, int],
    ) -> Dict[str, float]:
        """
        ADAPTACYJNE WAŻENIE na podstawie wzorców:
        - Jeśli użytkownik lubi konkretnych reżyserów -> zwiększ wagę reżyserów
        - Jeśli brak wzorców -> równomierne wagi
        """

        # Oblicz siłę wzorców (max powtórzeń)
        director_strength = max(director_patterns.values()) if director_patterns else 0
        actor_strength = max(actor_patterns.values()) if actor_patterns else 0
        genre_strength = max(genre_patterns.values()) if genre_patterns else 0

        total_strength = director_strength + actor_strength + genre_strength

        if total_strength == 0:
            # Brak wzorców - równomierne wagi
            weights = {"genres": 0.33, "actors": 0.33, "directors": 0.34}
            self.logger.info("Brak wzorców preferencji - równomierne wagi")
        else:
            # Adaptacyjne wagi na podstawie siły wzorców
            base_weight = 0.1  # minimum 10% dla każdej kategorii

            director_weight = base_weight + (director_strength / total_strength) * 0.7
            actor_weight = base_weight + (actor_strength / total_strength) * 0.7
            genre_weight = base_weight + (genre_strength / total_strength) * 0.7

            # Normalizuj do sumy = 1.0
            total_weight = director_weight + actor_weight + genre_weight

            weights = {
                "directors": director_weight / total_weight,
                "actors": actor_weight / total_weight,
                "genres": genre_weight / total_weight,
            }

            self.logger.info(
                f"ADAPTACYJNE wagi: reżyserzy={weights['directors']:.2f}, aktorzy={weights['actors']:.2f}, gatunki={weights['genres']:.2f}"
            )

            # Debug: pokaż najsilniejsze wzorce
            if director_strength >= 2:
                top_directors = [
                    d for d, c in director_patterns.items() if c == director_strength
                ]
                self.logger.info(
                    f"Dominujący reżyser(zy): {top_directors} (powtórzenia: {director_strength})"
                )

        return weights

    def align_features(
        self, features_rated: pd.DataFrame, features_candidates: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Wyrównuje cechy w reprezentacji pół-strukturalnej (Pazzani & Billsus)"""
        if features_rated.empty or features_candidates.empty:
            return features_rated, features_candidates

        rated_cols = set(features_rated.columns) - {"movie_id"}
        candidate_cols = set(features_candidates.columns) - {"movie_id"}

        # Union wszystkich cech - dane pół-strukturalne
        all_cols = rated_cols | candidate_cols
        all_cols = ["movie_id"] + sorted(list(all_cols))

        self.logger.info(
            f"Reprezentacja pół-strukturalna: rated={len(rated_cols)}, candidates={len(candidate_cols)}, union={len(all_cols)-1}"
        )

        # Dodaj brakujące kolumny z zerami
        for col in all_cols:
            if col not in features_rated.columns:
                features_rated[col] = 0.0
            if col not in features_candidates.columns:
                features_candidates[col] = 0.0

        features_rated_aligned = features_rated[all_cols].fillna(0.0)
        features_candidates_aligned = features_candidates[all_cols].fillna(0.0)

        # Debug cech reżyserów
        director_cols = [col for col in all_cols if col.startswith("director_")]
        self.logger.info(f"Cechy strukturalne reżyserów: {len(director_cols)}")

        return features_rated_aligned, features_candidates_aligned

    def prepare_structural_features(
        self, movies_df: pd.DataFrame, user_ratings: pd.DataFrame = None
    ) -> pd.DataFrame:
        """
        NOWA WERSJA z adaptacyjnymi wagami na podstawie wzorców użytkownika
        Przygotowuje dane strukturalne zgodnie z teorią Pazzaniego i Billsusa
        """
        if movies_df.empty:
            return pd.DataFrame()

        features_df = movies_df[["movie_id"]].copy()

        # === DANE STRUKTURALNE - DYSKRETNE CECHY ===

        # 1. One-hot encoding gatunków
        all_genres = set()
        for genres_list in movies_df["genres"]:
            if isinstance(genres_list, list):
                all_genres.update(genres_list)

        for genre in sorted(all_genres):
            features_df[f"genre_{genre}"] = movies_df["genres"].apply(
                lambda x: 1.0 if isinstance(x, list) and genre in x else 0.0
            )

        # 2. Binary encoding aktorów (top N według częstości)
        all_actors = []
        for actors_list in movies_df["actors"]:
            if isinstance(actors_list, list):
                all_actors.extend(actors_list)

        top_actors = [actor for actor, _ in Counter(all_actors).most_common(50)]
        for actor in sorted(top_actors):
            features_df[f"actor_{actor}"] = movies_df["actors"].apply(
                lambda x: 1.0 if isinstance(x, list) and actor in x else 0.0
            )

        # 3. Binary encoding reżyserów
        all_directors = []
        for directors_list in movies_df["directors"]:
            if isinstance(directors_list, list):
                all_directors.extend(directors_list)

        top_directors = [
            director for director, _ in Counter(all_directors).most_common(50)
        ]
        for director in sorted(top_directors):
            features_df[f"director_{director}"] = movies_df["directors"].apply(
                lambda x: 1.0 if isinstance(x, list) and director in x else 0.0
            )

        # 4. Normalizowane cechy numeryczne (rok, czas trwania)
        if "release_date" in movies_df.columns:
            movies_df_copy = movies_df.copy()
            movies_df_copy["release_year"] = pd.to_datetime(
                movies_df_copy["release_date"], errors="coerce"
            ).dt.year

            if not movies_df_copy["release_year"].isna().all():
                year_min = movies_df_copy["release_year"].min()
                year_max = movies_df_copy["release_year"].max()
                if year_max > year_min:
                    features_df["release_year_normalized"] = (
                        movies_df_copy["release_year"] - year_min
                    ) / (year_max - year_min)
                else:
                    features_df["release_year_normalized"] = 0.0

        if "duration_minutes" in movies_df.columns:
            duration_series = pd.to_numeric(
                movies_df["duration_minutes"], errors="coerce"
            )
            if not duration_series.isna().all():
                duration_min = duration_series.min()
                duration_max = duration_series.max()
                if duration_max > duration_min:
                    features_df["duration_normalized"] = (
                        duration_series - duration_min
                    ) / (duration_max - duration_min)
                else:
                    features_df["duration_normalized"] = 0.0

        # === ADAPTACYJNE WAŻENIE CECH (NOWE!) ===
        genre_cols = [col for col in features_df.columns if col.startswith("genre_")]
        actor_cols = [col for col in features_df.columns if col.startswith("actor_")]
        director_cols = [
            col for col in features_df.columns if col.startswith("director_")
        ]

        # Analiza wzorców preferencji użytkownika
        if user_ratings is not None and not user_ratings.empty:
            adaptive_weights = self.analyze_user_preferences(user_ratings)
            GENRE_WEIGHT = adaptive_weights["genres"]
            ACTOR_WEIGHT = adaptive_weights["actors"]
            DIRECTOR_WEIGHT = adaptive_weights["directors"]
        else:
            # Fallback do równomiernych wag
            GENRE_WEIGHT = 0.25
            ACTOR_WEIGHT = 0.4
            DIRECTOR_WEIGHT = 0.35

        # Zastosuj adaptacyjne wagi
        for col in genre_cols:
            features_df[col] = features_df[col] * GENRE_WEIGHT
        for col in actor_cols:
            features_df[col] = features_df[col] * ACTOR_WEIGHT
        for col in director_cols:
            features_df[col] = features_df[col] * DIRECTOR_WEIGHT

        self.logger.info(
            f"ADAPTACYJNE wagi - Gatunki: {len(genre_cols)} × {GENRE_WEIGHT:.2f}, Aktorzy: {len(actor_cols)} × {ACTOR_WEIGHT:.2f}, Reżyserzy: {len(director_cols)} × {DIRECTOR_WEIGHT:.2f}"
        )

        # Debug konkretnych reżyserów
        nolan_cols = [col for col in director_cols if "nolan" in col.lower()]
        if nolan_cols:
            self.logger.info(f"Cechy Nolana w danych strukturalnych: {nolan_cols}")

        return features_df.fillna(0.0)

    def prepare_textual_features(
        self, movies_df: pd.DataFrame, max_features: int = 1000
    ) -> pd.DataFrame:
        """Przygotowuje wagi tf*idf z opisów filmów (dane niestrukturalne -> strukturalne)"""
        if movies_df.empty or "description" not in movies_df.columns:
            return pd.DataFrame(
                {
                    "movie_id": (
                        movies_df["movie_id"] if "movie_id" in movies_df.columns else []
                    )
                }
            )

        # Preprocessing tekstu zgodny z teorią
        descriptions = movies_df["description"].fillna("").tolist()
        cleaned_descriptions = [self._preprocess_text(desc) for desc in descriptions]

        # TF*IDF zgodnie ze wzorem z pracy inżynierskiej
        vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words="english",  # usuwa stop words
            ngram_range=(1, 2),  # unigramy i bigramy
            min_df=2,  # minimum 2 dokumenty
            max_df=0.8,  # maksimum 80% dokumentów
            sublinear_tf=True,  # log normalization
        )

        try:
            tfidf_matrix = vectorizer.fit_transform(cleaned_descriptions)
            feature_names = vectorizer.get_feature_names_out()

            # Tworzenie DataFrame z wagami tf*idf
            tfidf_df = pd.DataFrame(
                tfidf_matrix.toarray(),
                columns=[f"tfidf_{name}" for name in feature_names],
            )
            tfidf_df["movie_id"] = movies_df["movie_id"].values

            self.logger.info(
                f"Wagi tf*idf: {len(feature_names)} terminów z {len(movies_df)} opisów"
            )

            # Debug najważniejszych terminów
            term_importance = tfidf_matrix.sum(axis=0).A1
            top_terms = [
                (feature_names[i], term_importance[i])
                for i in term_importance.argsort()[-10:]
            ]
            self.logger.info(f"Top terminy tf*idf: {top_terms}")

            return tfidf_df

        except Exception as e:
            self.logger.warning(f"Błąd tf*idf: {e}")
            return pd.DataFrame({"movie_id": movies_df["movie_id"]})

    def create_semi_structured_features(
        self, movies_df: pd.DataFrame, user_ratings: pd.DataFrame = None
    ) -> pd.DataFrame:
        """Łączy dane strukturalne z tf*idf - reprezentacja pół-strukturalna z adaptacyjnymi wagami"""
        structural_features = self.prepare_structural_features(movies_df, user_ratings)
        textual_features = self.prepare_textual_features(movies_df)

        # Połączenie danych strukturalnych z tf*idf
        if not textual_features.empty and len(textual_features.columns) > 1:
            semi_structured = structural_features.merge(
                textual_features, on="movie_id", how="left"
            )
            semi_structured = semi_structured.fillna(0.0)

            structural_cols = len(structural_features.columns) - 1  # -1 dla movie_id
            textual_cols = len(textual_features.columns) - 1

            self.logger.info(
                f"Reprezentacja pół-strukturalna z adaptacyjnymi wagami: {structural_cols} cech strukturalnych + {textual_cols} wag tf*idf"
            )
        else:
            semi_structured = structural_features
            self.logger.info(
                "Używam tylko cech strukturalnych z adaptacyjnymi wagami (brak tf*idf)"
            )

        return semi_structured

    def _preprocess_text(self, text: str) -> str:
        """Podstawowy preprocessing tekstu"""
        if not isinstance(text, str):
            return ""

        # Lowercase i usuwanie znaków specjalnych
        text = re.sub(r"[^a-zA-Z\s]", "", text.lower())

        # Podstawowy stemming (uproszczony)
        # W pełnej implementacji użyj NLTK lub spaCy
        text = re.sub(r"ing\b", "", text)  # usuwanie -ing
        text = re.sub(r"ed\b", "", text)  # usuwanie -ed

        return text

    def _add_genres_to_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Dodaje gatunki jako listę do DataFrame"""
        if df.empty:
            return df

        movie_ids = df["movie_id"].tolist()
        genres_results = (
            self.db.query(MovieGenre.movie_id, Genre.genre_name)
            .join(Genre, MovieGenre.genre_id == Genre.genre_id)
            .filter(MovieGenre.movie_id.in_(movie_ids))
            .all()
        )

        genres_data = []
        for result in genres_results:
            genres_data.append(
                {"movie_id": result.movie_id, "genre_name": result.genre_name}
            )

        genres_df = pd.DataFrame(genres_data)

        if genres_df.empty:
            df["genres"] = df.apply(lambda x: [], axis=1)
            return df

        genres_grouped = (
            genres_df.groupby("movie_id")["genre_name"].apply(list).reset_index()
        )
        genres_grouped.columns = ["movie_id", "genres"]

        df = df.merge(genres_grouped, on="movie_id", how="left")
        df["genres"] = (
            df["genres"].fillna("").apply(lambda x: x if isinstance(x, list) else [])
        )
        return df

    def _add_actors_to_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Dodaje aktorów jako listę do DataFrame"""
        if df.empty:
            return df

        movie_ids = df["movie_id"].tolist()
        actors_results = (
            self.db.query(MovieActor.movie_id, Actor.actor_name, MovieActor.movie_role)
            .join(Actor, MovieActor.actor_id == Actor.actor_id)
            .filter(MovieActor.movie_id.in_(movie_ids))
            .all()
        )

        actors_data = []
        for result in actors_results:
            actors_data.append(
                {
                    "movie_id": result.movie_id,
                    "actor_name": result.actor_name,
                    "movie_role": result.movie_role,
                }
            )

        actors_df = pd.DataFrame(actors_data)

        if actors_df.empty:
            df["actors"] = df.apply(lambda x: [], axis=1)
            return df

        actors_grouped = (
            actors_df.groupby("movie_id")["actor_name"].apply(list).reset_index()
        )
        actors_grouped.columns = ["movie_id", "actors"]

        df = df.merge(actors_grouped, on="movie_id", how="left")
        df["actors"] = (
            df["actors"].fillna("").apply(lambda x: x if isinstance(x, list) else [])
        )
        return df

    def _add_directors_to_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Dodaje reżyserów jako listę do DataFrame"""
        if df.empty:
            return df

        movie_ids = df["movie_id"].tolist()
        directors_results = (
            self.db.query(MovieDirector.movie_id, Director.director_name)
            .join(Director, MovieDirector.director_id == Director.director_id)
            .filter(MovieDirector.movie_id.in_(movie_ids))
            .all()
        )

        directors_data = []
        for result in directors_results:
            directors_data.append(
                {"movie_id": result.movie_id, "director_name": result.director_name}
            )

        directors_df = pd.DataFrame(directors_data)

        if directors_df.empty:
            df["directors"] = df.apply(lambda x: [], axis=1)
            return df

        directors_grouped = (
            directors_df.groupby("movie_id")["director_name"].apply(list).reset_index()
        )
        directors_grouped.columns = ["movie_id", "directors"]

        df = df.merge(directors_grouped, on="movie_id", how="left")
        df["directors"] = (
            df["directors"].fillna("").apply(lambda x: x if isinstance(x, list) else [])
        )
        return df

    def get_positive_negative_ratings(
        self, user_ratings: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Dzieli oceny na pozytywne i negatywne dla algorytmu Naive Bayes"""
        positive_ratings = user_ratings[
            user_ratings["rating"] >= POSITIVE_RATING_THRESHOLD
        ].copy()
        negative_ratings = user_ratings[
            user_ratings["rating"] <= NEGATIVE_RATING_THRESHOLD
        ].copy()
        return positive_ratings, negative_ratings

    def get_movie_descriptions(self, movies_df: pd.DataFrame) -> List[str]:
        """Pobiera opisy filmów do przetwarzania tekstowego"""
        return movies_df["description"].fillna("").tolist()
