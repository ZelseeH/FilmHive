from sqlalchemy.orm import Session
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging
import numpy as np
from collections import Counter
import re

from ..config import (
    MIN_USER_RATINGS,
    POSITIVE_RATING_THRESHOLD,
    NEGATIVE_RATING_THRESHOLD,
    BATCH_SIZE,
    TRAINING_POSITIVE_LIMIT,
    TRAINING_NEGATIVE_LIMIT,
    USE_ALL_NEGATIVES_IF_FEW,
    MAX_CANDIDATES,
    TFIDF_MAX_FEATURES,
    TFIDF_MIN_DF,
    TFIDF_MAX_DF,
    TFIDF_NGRAM_RANGE,
    TFIDF_SUBLINEAR_TF,
    TOP_ENTITIES,
    ADAPTIVE_BASE_WEIGHT,
    ADAPTIVE_SCALING_FACTOR,
    ADAPTIVE_BASE_GENRE_WEIGHT,
    ADAPTIVE_BASE_ACTOR_WEIGHT,
    ADAPTIVE_BASE_DIRECTOR_WEIGHT,
    ADAPTIVE_BASE_COUNTRY_WEIGHT,
    ADAPTIVE_BASE_YEAR_WEIGHT,
    USE_SNOWBALL_STEMMER,
    STEMMER_LANGUAGE,
    MIN_POSITIVES_FOR_QUALITY,
    TOP_ACTORS_IN_PATTERN,
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
from ..content_based.tfidf_processor import TFIDFProcessor


class DataPreprocessor:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.logger = logging.getLogger(__name__)
        # Polski stemmer dla TF-IDF
        self.tfidf_processor = TFIDFProcessor(
            use_snowball=USE_SNOWBALL_STEMMER, language=STEMMER_LANGUAGE
        )

    def check_user_eligibility(self, user_id: int) -> bool:
        """Sprawdza czy użytkownik ma minimum MIN_USER_RATINGS ocen"""
        rating_count = self.db.query(Rating).filter(Rating.user_id == user_id).count()
        is_eligible = rating_count >= MIN_USER_RATINGS

        if not is_eligible:
            self.logger.warning(
                f"User {user_id} has only {rating_count} ratings (minimum {MIN_USER_RATINGS} required)"
            )

        return is_eligible

    def get_user_ratings(self, user_id: int) -> pd.DataFrame:
        """
        Pobiera WSZYSTKIE oceny użytkownika (bez limitu)
        Filtrowanie na pozytywne/negatywne będzie w get_training_data
        """
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
            .order_by(Rating.rated_at.desc())  # Sortuj od najnowszych
            .all()
        )

        data = [
            {
                "movie_id": result.movie_id,
                "rating": result.rating,
                "rated_at": result.rated_at,
                "title": result.title,
                "description": result.description or "",
                "release_date": result.release_date,
                "duration_minutes": result.duration_minutes,
                "country": result.country or "Unknown",
                "original_language": result.original_language,
            }
            for result in results
        ]

        df = pd.DataFrame(data)
        df = self._add_genres_to_dataframe(df)
        df = self._add_actors_to_dataframe(df)
        df = self._add_directors_to_dataframe(df)

        self.logger.info(f"Pobrano {len(df)} total ratings dla user {user_id}")
        return df

    def get_training_data(
        self, user_ratings: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, any]]:
        """
        Zwraca balanced training set: 5 ostatnich pozytywnych + 5 ostatnich negatywnych

        Returns:
            positive_ratings: DataFrame z 5 ostatnimi pozytywnymi (≥6)
            negative_ratings: DataFrame z 5 ostatnimi negatywnymi (≤4)
            stats: Dict z statystykami (warnings, counts)
        """
        stats = {
            "total_ratings": len(user_ratings),
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "warnings": [],
        }

        # Filtruj pozytywne (≥6)
        positive = user_ratings[
            user_ratings["rating"] >= POSITIVE_RATING_THRESHOLD
        ].copy()
        positive = positive.sort_values("rated_at", ascending=False)

        # Filtruj negatywne (≤4)
        negative = user_ratings[
            user_ratings["rating"] <= NEGATIVE_RATING_THRESHOLD
        ].copy()
        negative = negative.sort_values("rated_at", ascending=False)

        # Neutralne (4 < rating < 6) - ignorowane
        neutral = user_ratings[
            (user_ratings["rating"] > NEGATIVE_RATING_THRESHOLD)
            & (user_ratings["rating"] < POSITIVE_RATING_THRESHOLD)
        ]

        stats["positive_count"] = len(positive)
        stats["negative_count"] = len(negative)
        stats["neutral_count"] = len(neutral)

        # Warning jeśli za mało pozytywnych
        if len(positive) < MIN_POSITIVES_FOR_QUALITY:
            warning = (
                f"User ma tylko {len(positive)} pozytywnych ocen (≥{POSITIVE_RATING_THRESHOLD}). "
                f"Rekomendacje mogą być niedokładne. Zachęć do ocenienia więcej filmów wysoko."
            )
            stats["warnings"].append(warning)
            self.logger.warning(warning)

        # Wybierz 5 ostatnich pozytywnych (lub wszystkie jeśli <5)
        positive_training = positive.head(TRAINING_POSITIVE_LIMIT)

        # Wybierz 5 ostatnich negatywnych
        if len(negative) < TRAINING_NEGATIVE_LIMIT and USE_ALL_NEGATIVES_IF_FEW:
            # Użyj wszystkich negatywnych jeśli <5
            negative_training = negative
            if len(negative) > 0:
                self.logger.info(
                    f"Using all {len(negative)} negative ratings (less than {TRAINING_NEGATIVE_LIMIT})"
                )
        else:
            negative_training = negative.head(TRAINING_NEGATIVE_LIMIT)

        # Warning jeśli brak negatywnych
        if len(negative_training) == 0:
            warning = (
                f"User nie ma negatywnych ocen (≤{NEGATIVE_RATING_THRESHOLD}). "
                f"Naive Bayes nie będzie mógł nauczyć się czego unikać."
            )
            stats["warnings"].append(warning)
            self.logger.warning(warning)

        self.logger.info(
            f"Training data: {len(positive_training)} positive (≥{POSITIVE_RATING_THRESHOLD}), "
            f"{len(negative_training)} negative (≤{NEGATIVE_RATING_THRESHOLD}), "
            f"{len(neutral)} neutral (ignored)"
        )

        return positive_training, negative_training, stats

    def get_candidate_movies(self, user_id: int) -> pd.DataFrame:
        """
        Pobiera wszystkie nieocenione filmy (bez limitu)
        Random shuffle w Pythonie (szybsze niż SQL ORDER BY random())
        """
        # Pobierz ID filmów już ocenionych
        rated_movie_ids = [
            r.movie_id
            for r in self.db.query(Rating.movie_id)
            .filter(Rating.user_id == user_id)
            .all()
        ]

        # Query wszystkich nieocenionych
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

        # Pobierz bez ORDER BY (szybsze)
        results = query.all()

        data = [
            {
                "movie_id": result.movie_id,
                "title": result.title,
                "description": result.description or "",
                "release_date": result.release_date,
                "duration_minutes": result.duration_minutes,
                "country": result.country or "Unknown",
                "original_language": result.original_language,
            }
            for result in results
        ]

        df = pd.DataFrame(data)

        # Random shuffle w Pythonie
        if not df.empty:
            df = df.sample(frac=1.0, random_state=None).reset_index(drop=True)

        df = self._add_genres_to_dataframe(df)
        df = self._add_actors_to_dataframe(df)
        df = self._add_directors_to_dataframe(df)

        self.logger.info(f"Pobrano {len(df)} candidate movies (all unrated, shuffled)")
        return df

    def analyze_user_preferences(self, user_ratings: pd.DataFrame) -> Dict[str, float]:
        """
        Adaptacyjna analiza wzorców w pozytywnych ocenach
        Zwraca 5 wag: genres, actors, directors, country, year
        """
        if user_ratings.empty:
            return self._get_default_weights()

        high_rated = user_ratings[user_ratings["rating"] >= POSITIVE_RATING_THRESHOLD]

        if len(high_rated) < 2:
            self.logger.info(
                "Za mało pozytywnych ocen (<2) – fallback do default weights"
            )
            return self._get_default_weights()

        # Analizuj patterns
        director_patterns = self._analyze_director_patterns(high_rated)
        actor_patterns = self._analyze_actor_patterns(high_rated)
        genre_patterns = self._analyze_genre_patterns(high_rated)
        country_patterns = self._analyze_country_patterns(high_rated)
        year_patterns = self._analyze_year_patterns(high_rated)

        return self._calculate_adaptive_weights(
            director_patterns,
            actor_patterns,
            genre_patterns,
            country_patterns,
            year_patterns,
        )

    def _get_default_weights(self) -> Dict[str, float]:
        """Zwraca domyślne wagi (gdy brak danych do analizy patterns)"""
        return {
            "genres": ADAPTIVE_BASE_GENRE_WEIGHT,
            "actors": ADAPTIVE_BASE_ACTOR_WEIGHT,
            "directors": ADAPTIVE_BASE_DIRECTOR_WEIGHT,
            "country": ADAPTIVE_BASE_COUNTRY_WEIGHT,
            "year": ADAPTIVE_BASE_YEAR_WEIGHT,
        }

    def _analyze_director_patterns(self, high_rated: pd.DataFrame) -> Dict[str, int]:
        """Zlicza powtarzających się reżyserów w pozytywnych ocenach"""
        director_counts = {}
        for _, row in high_rated.iterrows():
            directors = row.get("directors", [])
            if isinstance(directors, list):
                for director in directors:
                    director_counts[director] = director_counts.get(director, 0) + 1

        # Tylko ci którzy występują >1 raz (pattern)
        repeated = {d: c for d, c in director_counts.items() if c > 1}
        if repeated:
            self.logger.info(f"Director patterns: {repeated}")
        return repeated

    def _analyze_actor_patterns(self, high_rated: pd.DataFrame) -> Dict[str, int]:
        """Zlicza powtarzających się aktorów w pozytywnych ocenach"""
        actor_counts = {}
        for _, row in high_rated.iterrows():
            actors = row.get("actors", [])
            if isinstance(actors, list):
                # Bierz tylko top TOP_ACTORS_IN_PATTERN aktorów z każdego filmu
                for actor in actors[:TOP_ACTORS_IN_PATTERN]:
                    actor_counts[actor] = actor_counts.get(actor, 0) + 1

        repeated = {a: c for a, c in actor_counts.items() if c > 1}
        if repeated:
            self.logger.info(f"Actor patterns: {repeated}")
        return repeated

    def _analyze_genre_patterns(self, high_rated: pd.DataFrame) -> Dict[str, int]:
        """Zlicza powtarzające się gatunki w pozytywnych ocenach"""
        genre_counts = {}
        for _, row in high_rated.iterrows():
            genres = row.get("genres", [])
            if isinstance(genres, list):
                for genre in genres:
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1

        repeated = {g: c for g, c in genre_counts.items() if c > 1}
        if repeated:
            self.logger.info(f"Genre patterns: {repeated}")
        return repeated

    def _analyze_country_patterns(self, high_rated: pd.DataFrame) -> Dict[str, int]:
        """Zlicza powtarzające się kraje w pozytywnych ocenach"""
        country_counts = {}
        for _, row in high_rated.iterrows():
            country = row.get("country", "Unknown")
            if country and country != "Unknown":
                country_counts[country] = country_counts.get(country, 0) + 1

        repeated = {c: cnt for c, cnt in country_counts.items() if cnt > 1}
        if repeated:
            self.logger.info(f"Country patterns: {repeated}")
        return repeated

    def _analyze_year_patterns(self, high_rated: pd.DataFrame) -> Dict[str, int]:
        """
        Zlicza powtarzające się dekady w pozytywnych ocenach
        Np. jeśli user lubi filmy z lat 90', boost year weight
        """
        year_counts = {}
        for _, row in high_rated.iterrows():
            release_date = row.get("release_date")
            if pd.notna(release_date):
                year = pd.to_datetime(release_date, errors="coerce").year
                if year:
                    # Grupuj po dekadach (1990-1999 → 1990)
                    decade = (year // 10) * 10
                    year_counts[decade] = year_counts.get(decade, 0) + 1

        repeated = {d: c for d, c in year_counts.items() if c > 1}
        if repeated:
            self.logger.info(f"Year patterns (decades): {repeated}")
        return repeated

    def _calculate_adaptive_weights(
        self,
        director_patterns: Dict[str, int],
        actor_patterns: Dict[str, int],
        genre_patterns: Dict[str, int],
        country_patterns: Dict[str, int],
        year_patterns: Dict[str, int],
    ) -> Dict[str, float]:
        """
        Oblicza adaptive weights na podstawie siły patterns
        Im silniejszy pattern, tym wyższa waga dla tej cechy
        """
        director_strength = max(director_patterns.values()) if director_patterns else 0
        actor_strength = max(actor_patterns.values()) if actor_patterns else 0
        genre_strength = max(genre_patterns.values()) if genre_patterns else 0
        country_strength = max(country_patterns.values()) if country_patterns else 0
        year_strength = max(year_patterns.values()) if year_patterns else 0

        total_strength = (
            director_strength
            + actor_strength
            + genre_strength
            + country_strength
            + year_strength
        )

        if total_strength == 0:
            # Brak patterns → default weights
            return self._get_default_weights()

        # Oblicz adaptive weights: base + proporcja strength
        director_w = (
            ADAPTIVE_BASE_WEIGHT
            + (director_strength / total_strength) * ADAPTIVE_SCALING_FACTOR
        )
        actor_w = (
            ADAPTIVE_BASE_WEIGHT
            + (actor_strength / total_strength) * ADAPTIVE_SCALING_FACTOR
        )
        genre_w = (
            ADAPTIVE_BASE_WEIGHT
            + (genre_strength / total_strength) * ADAPTIVE_SCALING_FACTOR
        )
        country_w = (
            ADAPTIVE_BASE_WEIGHT
            + (country_strength / total_strength) * ADAPTIVE_SCALING_FACTOR
        )
        year_w = (
            ADAPTIVE_BASE_WEIGHT
            + (year_strength / total_strength) * ADAPTIVE_SCALING_FACTOR
        )

        # Normalizuj do sumy 1.0
        total_w = director_w + actor_w + genre_w + country_w + year_w
        weights = {
            "directors": director_w / total_w,
            "actors": actor_w / total_w,
            "genres": genre_w / total_w,
            "country": country_w / total_w,
            "year": year_w / total_w,
        }

        self.logger.info(
            f"Adaptive weights: genres={weights['genres']:.3f}, actors={weights['actors']:.3f}, "
            f"directors={weights['directors']:.3f}, country={weights['country']:.3f}, "
            f"year={weights['year']:.3f}"
        )

        return weights

    def align_features(
        self, features_rated: pd.DataFrame, features_candidates: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Wyrównuje przestrzeń cech między rated i candidates
        (Oba muszą mieć te same kolumny dla cosine similarity)
        """
        if features_rated.empty or features_candidates.empty:
            return features_rated, features_candidates

        rated_cols = set(features_rated.columns) - {"movie_id"}
        candidate_cols = set(features_candidates.columns) - {"movie_id"}
        all_cols = sorted(rated_cols | candidate_cols)

        self.logger.info(
            f"Feature alignment: rated {len(rated_cols)}, candidates {len(candidate_cols)}, "
            f"union {len(all_cols)}"
        )

        # Dodaj brakujące kolumny (wypełnione 0.0)
        missing_rated = {
            col: 0.0 for col in all_cols if col not in features_rated.columns
        }
        missing_candidates = {
            col: 0.0 for col in all_cols if col not in features_candidates.columns
        }

        if missing_rated:
            missing_rated_df = pd.DataFrame(missing_rated, index=features_rated.index)
            features_rated = pd.concat([features_rated, missing_rated_df], axis=1)

        if missing_candidates:
            missing_candidates_df = pd.DataFrame(
                missing_candidates, index=features_candidates.index
            )
            features_candidates = pd.concat(
                [features_candidates, missing_candidates_df], axis=1
            )

        # Upewnij się że kolumny są w tej samej kolejności
        final_cols = ["movie_id"] + all_cols
        features_rated_aligned = features_rated[final_cols].fillna(0.0)
        features_candidates_aligned = features_candidates[final_cols].fillna(0.0)

        return features_rated_aligned, features_candidates_aligned

    def prepare_structural_features(
        self, movies_df: pd.DataFrame, user_ratings: pd.DataFrame = None
    ) -> pd.DataFrame:
        """
        Przygotowuje strukturalne cechy: genres, actors, directors, country, year, duration

        WAŻNE: NIE stosuje adaptive weights tutaj - to jest w k-NN similarity!
        Zwraca RAW binary features (0/1) + normalized numeric
        """
        if movies_df.empty:
            return pd.DataFrame()

        features_df = movies_df[["movie_id"]].copy()

        # ===== GENRES (one-hot binary) =====
        all_genres = set()
        for genres_list in movies_df["genres"]:
            if isinstance(genres_list, list):
                all_genres.update(genres_list)

        genre_cols = {}
        for genre in sorted(all_genres):
            genre_cols[f"genre_{genre}"] = movies_df["genres"].apply(
                lambda x: 1.0 if isinstance(x, list) and genre in x else 0.0
            )
        if genre_cols:
            features_df = pd.concat(
                [features_df, pd.DataFrame(genre_cols, index=features_df.index)], axis=1
            )

        # ===== ACTORS (binary, top TOP_ENTITIES) =====
        all_actors = []
        for actors_list in movies_df["actors"]:
            if isinstance(actors_list, list):
                all_actors.extend(actors_list)
        top_actors = [
            actor for actor, _ in Counter(all_actors).most_common(TOP_ENTITIES)
        ]

        actor_cols = {}
        for actor in sorted(top_actors):
            actor_cols[f"actor_{actor}"] = movies_df["actors"].apply(
                lambda x: 1.0 if isinstance(x, list) and actor in x else 0.0
            )
        if actor_cols:
            features_df = pd.concat(
                [features_df, pd.DataFrame(actor_cols, index=features_df.index)], axis=1
            )

        # ===== DIRECTORS (binary, top TOP_ENTITIES) =====
        all_directors = []
        for directors_list in movies_df["directors"]:
            if isinstance(directors_list, list):
                all_directors.extend(directors_list)
        top_directors = [
            director for director, _ in Counter(all_directors).most_common(TOP_ENTITIES)
        ]

        director_cols = {}
        for director in sorted(top_directors):
            director_cols[f"director_{director}"] = movies_df["directors"].apply(
                lambda x: 1.0 if isinstance(x, list) and director in x else 0.0
            )
        if director_cols:
            features_df = pd.concat(
                [features_df, pd.DataFrame(director_cols, index=features_df.index)],
                axis=1,
            )

        # ===== COUNTRY (binary, top TOP_ENTITIES) =====
        all_countries = movies_df["country"].dropna().unique().tolist()
        all_countries = [c for c in all_countries if c != "Unknown"]
        top_countries = Counter(all_countries).most_common(TOP_ENTITIES)

        country_cols = {}
        for country, _ in top_countries:
            country_cols[f"country_{country}"] = movies_df["country"].apply(
                lambda x: 1.0 if x == country else 0.0
            )
        if country_cols:
            features_df = pd.concat(
                [features_df, pd.DataFrame(country_cols, index=features_df.index)],
                axis=1,
            )

        # ===== YEAR (normalized [0,1]) =====
        if "release_date" in movies_df.columns:
            movies_df_copy = movies_df.copy()
            movies_df_copy["release_year"] = pd.to_datetime(
                movies_df_copy["release_date"], errors="coerce"
            ).dt.year
            year_series = movies_df_copy["release_year"].fillna(0)
            if year_series.nunique() > 1:
                year_min, year_max = year_series.min(), year_series.max()
                features_df["release_year_normalized"] = (year_series - year_min) / (
                    year_max - year_min + 1e-9
                )
            else:
                features_df["release_year_normalized"] = 0.0

        # ===== DURATION (normalized [0,1]) =====
        if "duration_minutes" in movies_df.columns:
            duration_series = pd.to_numeric(
                movies_df["duration_minutes"], errors="coerce"
            ).fillna(0)
            if duration_series.nunique() > 1:
                duration_min, duration_max = (
                    duration_series.min(),
                    duration_series.max(),
                )
                features_df["duration_normalized"] = (
                    duration_series - duration_min
                ) / (duration_max - duration_min + 1e-9)
            else:
                features_df["duration_normalized"] = 0.0

        genre_count = len([c for c in features_df.columns if c.startswith("genre_")])
        actor_count = len([c for c in features_df.columns if c.startswith("actor_")])
        director_count = len(
            [c for c in features_df.columns if c.startswith("director_")]
        )
        country_count = len(
            [c for c in features_df.columns if c.startswith("country_")]
        )

        self.logger.info(
            f"Structural features: {genre_count} genres, {actor_count} actors, "
            f"{director_count} directors, {country_count} countries + year/duration (RAW binary)"
        )

        return features_df.fillna(0.0)

    def prepare_textual_features(self, movies_df: pd.DataFrame) -> pd.DataFrame:
        """
        TF-IDF features z opisów filmów (z polskim stemmingiem)
        """
        if movies_df.empty or "description" not in movies_df.columns:
            return pd.DataFrame({"movie_id": movies_df.get("movie_id", [])})

        descriptions = movies_df["description"].fillna("").tolist()

        # Filtruj zbyt krótkie opisy (<10 znaków)
        valid_indices = [
            i for i, desc in enumerate(descriptions) if len(desc.strip()) >= 10
        ]

        if len(valid_indices) == 0:
            self.logger.warning(
                "No valid descriptions for TF-IDF (all too short or empty)"
            )
            return pd.DataFrame({"movie_id": movies_df["movie_id"]})

        try:
            valid_descriptions = [descriptions[i] for i in valid_indices]
            self.tfidf_processor.fit_transform(valid_descriptions)
            tfidf_matrix = self.tfidf_processor.transform(valid_descriptions)

            feature_names = self.tfidf_processor.feature_names
            tfidf_df = pd.DataFrame(
                tfidf_matrix.toarray(),
                columns=[f"tfidf_{name}" for name in feature_names],
                index=[valid_indices[i] for i in range(len(valid_indices))],
            )
            tfidf_df["movie_id"] = movies_df.iloc[valid_indices]["movie_id"].values

            self.logger.info(
                f"TF-IDF: {len(feature_names)} terms from {len(valid_descriptions)} descriptions "
                f"(Polish stemming: {USE_SNOWBALL_STEMMER})"
            )

            # Merge z oryginalnym DataFrame (filmy bez opisów dostaną 0.0)
            full_tfidf = (
                movies_df[["movie_id"]]
                .merge(tfidf_df, on="movie_id", how="left")
                .fillna(0.0)
            )
            return full_tfidf

        except Exception as e:
            self.logger.error(f"TF-IDF error: {e}", exc_info=True)
            return pd.DataFrame({"movie_id": movies_df["movie_id"]})

    def create_semi_structured_features(
        self, movies_df: pd.DataFrame, user_ratings: pd.DataFrame = None
    ) -> pd.DataFrame:
        """
        Łączy structural + textual features w jeden DataFrame
        (Używane jeśli chcesz jedną przestrzeń cech dla hybrid)
        """
        structural = self.prepare_structural_features(movies_df, user_ratings)
        textual = self.prepare_textual_features(movies_df)

        if not textual.empty and len(textual.columns) > 1:
            semi = structural.merge(textual, on="movie_id", how="left").fillna(0.0)
            structural_cols = len(structural.columns) - 1
            textual_cols = len(textual.columns) - 1
            self.logger.info(
                f"Semi-structured: {structural_cols} structural + {textual_cols} TF-IDF features"
            )
        else:
            semi = structural
            self.logger.info("Only structural features (no TF-IDF)")

        return semi

    # ========================================================================
    # HELPER FUNCTIONS (batch queries dla genres, actors, directors)
    # ========================================================================

    def _add_genres_to_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Dodaje kolumnę 'genres' (lista) do DataFrame"""
        if df.empty:
            return df

        movie_ids = df["movie_id"].tolist()
        genres_data = []

        for i in range(0, len(movie_ids), BATCH_SIZE):
            batch_ids = movie_ids[i : i + BATCH_SIZE]
            batch_results = (
                self.db.query(MovieGenre.movie_id, Genre.genre_name)
                .join(Genre, MovieGenre.genre_id == Genre.genre_id)
                .filter(MovieGenre.movie_id.in_(batch_ids))
                .all()
            )
            genres_data.extend(
                [
                    {"movie_id": r.movie_id, "genre_name": r.genre_name}
                    for r in batch_results
                ]
            )

        if not genres_data:
            df["genres"] = [[] for _ in range(len(df))]
            return df

        genres_df = pd.DataFrame(genres_data)
        genres_grouped = (
            genres_df.groupby("movie_id")["genre_name"].apply(list).reset_index()
        )
        genres_grouped.columns = ["movie_id", "genres"]

        df = df.merge(genres_grouped, on="movie_id", how="left")
        df["genres"] = df["genres"].apply(lambda x: x if isinstance(x, list) else [])
        return df

    def _add_actors_to_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Dodaje kolumnę 'actors' (lista) do DataFrame"""
        if df.empty:
            return df

        movie_ids = df["movie_id"].tolist()
        actors_data = []

        for i in range(0, len(movie_ids), BATCH_SIZE):
            batch_ids = movie_ids[i : i + BATCH_SIZE]
            batch_results = (
                self.db.query(MovieActor.movie_id, Actor.actor_name)
                .join(Actor, MovieActor.actor_id == Actor.actor_id)
                .filter(MovieActor.movie_id.in_(batch_ids))
                .all()
            )
            actors_data.extend(
                [
                    {"movie_id": r.movie_id, "actor_name": r.actor_name}
                    for r in batch_results
                ]
            )

        if not actors_data:
            df["actors"] = [[] for _ in range(len(df))]
            return df

        actors_df = pd.DataFrame(actors_data)
        actors_grouped = (
            actors_df.groupby("movie_id")["actor_name"].apply(list).reset_index()
        )
        actors_grouped.columns = ["movie_id", "actors"]

        df = df.merge(actors_grouped, on="movie_id", how="left")
        df["actors"] = df["actors"].apply(lambda x: x if isinstance(x, list) else [])
        return df

    def _add_directors_to_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Dodaje kolumnę 'directors' (lista) do DataFrame"""
        if df.empty:
            return df

        movie_ids = df["movie_id"].tolist()
        directors_data = []

        for i in range(0, len(movie_ids), BATCH_SIZE):
            batch_ids = movie_ids[i : i + BATCH_SIZE]
            batch_results = (
                self.db.query(MovieDirector.movie_id, Director.director_name)
                .join(Director, MovieDirector.director_id == Director.director_id)
                .filter(MovieDirector.movie_id.in_(batch_ids))
                .all()
            )
            directors_data.extend(
                [
                    {"movie_id": r.movie_id, "director_name": r.director_name}
                    for r in batch_results
                ]
            )

        if not directors_data:
            df["directors"] = [[] for _ in range(len(df))]
            return df

        directors_df = pd.DataFrame(directors_data)
        directors_grouped = (
            directors_df.groupby("movie_id")["director_name"].apply(list).reset_index()
        )
        directors_grouped.columns = ["movie_id", "directors"]

        df = df.merge(directors_grouped, on="movie_id", how="left")
        df["directors"] = df["directors"].apply(
            lambda x: x if isinstance(x, list) else []
        )
        return df

    # ========================================================================
    # LEGACY FUNCTIONS (dla backward compatibility)
    # ========================================================================

    def get_positive_negative_ratings(
        self, user_ratings: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        DEPRECATED: Użyj get_training_data() zamiast tego

        Zachowane dla backward compatibility z starym kodem
        """
        self.logger.warning(
            "get_positive_negative_ratings() is deprecated. Use get_training_data() instead."
        )

        positive, negative, _ = self.get_training_data(user_ratings)
        return positive, negative

    def get_movie_descriptions(self, movie_ids: List[int]) -> pd.DataFrame:
        """
        Pobiera opisy filmów dla Naive Bayes (z fallback do title)
        """
        try:
            movies = (
                self.db.query(Movie.movie_id, Movie.description, Movie.title)
                .filter(Movie.movie_id.in_(movie_ids))
                .all()
            )

            data = []
            fallback_count = 0

            for m in movies:
                desc = m.description

                if not desc or len(str(desc).strip()) == 0:
                    # Fallback do tytułu jeśli brak opisu
                    desc = f"Film: {m.title}" if m.title else "Film bez opisu"
                    fallback_count += 1

                data.append({"movie_id": m.movie_id, "description": desc})

            df = pd.DataFrame(data)

            if fallback_count > 0:
                self.logger.warning(
                    f"get_movie_descriptions: {fallback_count}/{len(df)} movies used fallback "
                    f"(NULL or empty descriptions)"
                )

            self.logger.info(f"Pobrano {len(df)} descriptions dla Naive Bayes")
            return df

        except Exception as e:
            self.logger.error(f"Error get_movie_descriptions: {e}", exc_info=True)
            return pd.DataFrame(columns=["movie_id", "description"])
