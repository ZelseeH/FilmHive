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
    RECENT_RATINGS_LIMIT,
    MAX_CANDIDATES,
    TFIDF_MAX_FEATURES,
    TFIDF_MIN_DF,
    TFIDF_MAX_DF,
    TFIDF_NGRAM_RANGE,
    TFIDF_SUBLINEAR_TF,
    TOP_ENTITIES,
    ADAPTIVE_BASE_WEIGHT,
    ADAPTIVE_SCALING_FACTOR,
    ADAPTIVE_GENRE_WEIGHT,
    ADAPTIVE_ACTOR_WEIGHT,
    ADAPTIVE_DIRECTOR_WEIGHT,
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
        self.tfidf_processor = TFIDFProcessor(use_snowball=True)

    def check_user_eligibility(self, user_id: int) -> bool:
        """Sprawdza minimum ocen"""
        rating_count = self.db.query(Rating).filter(Rating.user_id == user_id).count()
        return rating_count >= MIN_USER_RATINGS

    def get_user_ratings(
        self, user_id: int, limit: int = RECENT_RATINGS_LIMIT
    ) -> pd.DataFrame:
        """Pobiera recent oceny z metadanymi"""
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

        data = [
            {
                "movie_id": result.movie_id,
                "rating": result.rating,
                "rated_at": result.rated_at,
                "title": result.title,
                "description": result.description or "",
                "release_date": result.release_date,
                "duration_minutes": result.duration_minutes,
                "country": result.country,
                "original_language": result.original_language,
            }
            for result in results
        ]

        df = pd.DataFrame(data)
        df = self._add_genres_to_dataframe(df)
        df = self._add_actors_to_dataframe(df)
        df = self._add_directors_to_dataframe(df)

        self.logger.info(f"Pobrano {len(df)} ratings dla user {user_id}")
        return df

    def get_candidate_movies(self, user_id: int) -> pd.DataFrame:
        """Pobiera unrated movies (max MAX_CANDIDATES)"""
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
        ).order_by(Movie.release_date.desc())

        if rated_movie_ids:
            query = query.filter(~Movie.movie_id.in_(rated_movie_ids))

        results = query.limit(MAX_CANDIDATES).all()

        data = [
            {
                "movie_id": result.movie_id,
                "title": result.title,
                "description": result.description or "",
                "release_date": result.release_date,
                "duration_minutes": result.duration_minutes,
                "country": result.country,
                "original_language": result.original_language,
            }
            for result in results
        ]

        df = pd.DataFrame(data)
        df = self._add_genres_to_dataframe(df)
        df = self._add_actors_to_dataframe(df)
        df = self._add_directors_to_dataframe(df)
        self.logger.info(f"Pobrano {len(df)} candidates (max {MAX_CANDIDATES})")
        return df

    def analyze_user_preferences(self, user_ratings: pd.DataFrame) -> Dict[str, float]:
        """Adaptacyjna analiza wzorców w high ratings"""
        if user_ratings.empty:
            return {
                "genres": ADAPTIVE_GENRE_WEIGHT,
                "actors": ADAPTIVE_ACTOR_WEIGHT,
                "directors": ADAPTIVE_DIRECTOR_WEIGHT,
            }

        high_rated = user_ratings[user_ratings["rating"] >= POSITIVE_RATING_THRESHOLD]

        if len(high_rated) < 2:
            self.logger.info("Za mało high ratings – fallback wagi")
            return {
                "genres": ADAPTIVE_GENRE_WEIGHT,
                "actors": ADAPTIVE_ACTOR_WEIGHT,
                "directors": ADAPTIVE_DIRECTOR_WEIGHT,
            }

        director_patterns = self._analyze_director_patterns(high_rated)
        actor_patterns = self._analyze_actor_patterns(high_rated)
        genre_patterns = self._analyze_genre_patterns(high_rated)

        return self._calculate_adaptive_weights(
            director_patterns, actor_patterns, genre_patterns
        )

    def _analyze_director_patterns(self, high_rated: pd.DataFrame) -> Dict[str, int]:
        director_counts = {}
        for _, row in high_rated.iterrows():
            directors = row.get("directors", [])
            if isinstance(directors, list):
                for director in directors:
                    director_counts[director] = director_counts.get(director, 0) + 1
        repeated = {d: c for d, c in director_counts.items() if c > 1}
        if repeated:
            self.logger.info(f"Repeated directors: {repeated}")
        return repeated

    def _analyze_actor_patterns(self, high_rated: pd.DataFrame) -> Dict[str, int]:
        actor_counts = {}
        for _, row in high_rated.iterrows():
            actors = row.get("actors", [])
            if isinstance(actors, list):
                for actor in actors[:5]:
                    actor_counts[actor] = actor_counts.get(actor, 0) + 1
        repeated = {a: c for a, c in actor_counts.items() if c > 1}
        if repeated:
            self.logger.info(f"Repeated actors: {repeated}")
        return repeated

    def _analyze_genre_patterns(self, high_rated: pd.DataFrame) -> Dict[str, int]:
        genre_counts = {}
        for _, row in high_rated.iterrows():
            genres = row.get("genres", [])
            if isinstance(genres, list):
                for genre in genres:
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
        repeated = {g: c for g, c in genre_counts.items() if c > 1}
        if repeated:
            self.logger.info(f"Repeated genres: {repeated}")
        return repeated

    def _calculate_adaptive_weights(
        self,
        director_patterns: Dict[str, int],
        actor_patterns: Dict[str, int],
        genre_patterns: Dict[str, int],
    ) -> Dict[str, float]:
        """Adaptacyjne wagi proporcjonalne do siły wzorców"""
        director_strength = max(director_patterns.values()) if director_patterns else 0
        actor_strength = max(actor_patterns.values()) if actor_patterns else 0
        genre_strength = max(genre_patterns.values()) if genre_patterns else 0

        total_strength = director_strength + actor_strength + genre_strength

        if total_strength == 0:
            weights = {
                "genres": ADAPTIVE_GENRE_WEIGHT,
                "actors": ADAPTIVE_ACTOR_WEIGHT,
                "directors": ADAPTIVE_DIRECTOR_WEIGHT,
            }
        else:
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

            total_w = director_w + actor_w + genre_w
            weights = {
                "directors": director_w / total_w,
                "actors": actor_w / total_w,
                "genres": genre_w / total_w,
            }
            self.logger.info(
                f"Adaptive weights: dirs={weights['directors']:.2f}, actors={weights['actors']:.2f}, genres={weights['genres']:.2f}"
            )

        return weights

    def align_features(
        self, features_rated: pd.DataFrame, features_candidates: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Wyrównuje cechy (OPTIMIZED: no loop assignment)"""
        if features_rated.empty or features_candidates.empty:
            return features_rated, features_candidates

        rated_cols = set(features_rated.columns) - {"movie_id"}
        candidate_cols = set(features_candidates.columns) - {"movie_id"}
        all_cols = sorted(rated_cols | candidate_cols)

        self.logger.info(
            f"Align: rated {len(rated_cols)}, candidates {len(candidate_cols)}, union {len(all_cols)}"
        )

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

        final_cols = ["movie_id"] + all_cols
        features_rated_aligned = features_rated[final_cols].fillna(0.0)
        features_candidates_aligned = features_candidates[final_cols].fillna(0.0)

        director_cols = [col for col in all_cols if col.startswith("director_")]
        self.logger.info(f"Director features: {len(director_cols)}")

        return features_rated_aligned, features_candidates_aligned

    def prepare_structural_features(
        self, movies_df: pd.DataFrame, user_ratings: pd.DataFrame = None
    ) -> pd.DataFrame:
        """Strukturalne cechy z adaptacyjnymi wagami"""
        if movies_df.empty:
            return pd.DataFrame()

        features_df = movies_df[["movie_id"]].copy()

        # One-hot genres
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

        # Binary actors (top TOP_ENTITIES)
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

        # Binary directors (top TOP_ENTITIES)
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

        # Normalized numeric (year, duration)
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

        # Adaptive weights application
        if user_ratings is not None and not user_ratings.empty:
            adaptive_weights = self.analyze_user_preferences(user_ratings)
            genre_weight = adaptive_weights["genres"]
            actor_weight = adaptive_weights["actors"]
            director_weight = adaptive_weights["directors"]
        else:
            genre_weight = ADAPTIVE_GENRE_WEIGHT
            actor_weight = ADAPTIVE_ACTOR_WEIGHT
            director_weight = ADAPTIVE_DIRECTOR_WEIGHT

        for col in features_df.columns:
            if col.startswith("genre_"):
                features_df[col] *= genre_weight
            elif col.startswith("actor_"):
                features_df[col] *= actor_weight
            elif col.startswith("director_"):
                features_df[col] *= director_weight

        genre_count = len([c for c in features_df.columns if c.startswith("genre_")])
        actor_count = len([c for c in features_df.columns if c.startswith("actor_")])
        director_count = len(
            [c for c in features_df.columns if c.startswith("director_")]
        )
        self.logger.info(
            f"Structural: {genre_count} genres ×{genre_weight:.2f}, {actor_count} actors ×{actor_weight:.2f}, {director_count} directors ×{director_weight:.2f}"
        )

        return features_df.fillna(0.0)

    def prepare_textual_features(self, movies_df: pd.DataFrame) -> pd.DataFrame:
        """TF-IDF via TFIDFProcessor"""
        if movies_df.empty or "description" not in movies_df.columns:
            return pd.DataFrame({"movie_id": movies_df.get("movie_id", [])})

        descriptions = movies_df["description"].fillna("").tolist()

        valid_indices = [
            i for i, desc in enumerate(descriptions) if len(desc.strip()) >= 10
        ]

        if len(valid_indices) == 0:
            self.logger.warning(
                "No valid descriptions for TF-IDF (all too short/empty)"
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
                f"TF-IDF: {len(feature_names)} terms from {len(valid_descriptions)} descriptions"
            )

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
        """Łączy structural + textual"""
        structural = self.prepare_structural_features(movies_df, user_ratings)
        textual = self.prepare_textual_features(movies_df)

        if not textual.empty and len(textual.columns) > 1:
            semi = structural.merge(textual, on="movie_id", how="left").fillna(0.0)
            structural_cols = len(structural.columns) - 1
            textual_cols = len(textual.columns) - 1
            self.logger.info(
                f"Semi-structured: {structural_cols} structural + {textual_cols} TF-IDF"
            )
        else:
            semi = structural
            self.logger.info("Only structural (no TF-IDF)")

        return semi

    def _add_genres_to_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Dodaje genres (batch)"""
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
        """Dodaje actors (batch)"""
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
        """Dodaje directors (batch)"""
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

    def get_positive_negative_ratings(
        self, user_ratings: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Podział dla NB"""
        positive = user_ratings[
            user_ratings["rating"] >= POSITIVE_RATING_THRESHOLD
        ].copy()
        negative = user_ratings[
            user_ratings["rating"] <= NEGATIVE_RATING_THRESHOLD
        ].copy()
        return positive, negative

    def get_movie_descriptions(self, movie_ids: List[int]) -> pd.DataFrame:
        """
        Pobiera opisy filmów dla Naive Bayes
        FIX: Handle NULL descriptions (fallback to title)
        """
        try:
            # Query movie_id, description, AND title (dla fallback)
            movies = (
                self.db.query(Movie.movie_id, Movie.description, Movie.title)
                .filter(Movie.movie_id.in_(movie_ids))
                .all()
            )

            # Convert to DataFrame with NULL handling
            data = []
            fallback_count = 0

            for m in movies:
                desc = m.description

                # FIX: Fallback jeśli NULL/empty (use title as minimal description)
                if not desc or len(str(desc).strip()) == 0:
                    desc = f"Film: {m.title}" if m.title else "Film bez opisu"
                    fallback_count += 1

                data.append({"movie_id": m.movie_id, "description": desc})

            df = pd.DataFrame(data)

            # Log stats
            non_empty = len([d for d in df["description"] if len(str(d)) > 0])
            if fallback_count > 0:
                self.logger.warning(
                    f"get_movie_descriptions: {fallback_count}/{len(df)} movies used fallback (NULL descriptions)"
                )
            self.logger.info(f"Pobrano {len(df)} opisów dla NB ({non_empty} non-empty)")

            return df

        except Exception as e:
            self.logger.error(f"Error get_movie_descriptions: {e}", exc_info=True)
            return pd.DataFrame(columns=["movie_id", "description"])
