from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .base import Base
from .movie import Movie
from .genre import Genre
from .movie_genre import MovieGenre
from .user import User
from .rating import Rating
from .comment import Comment
from .favorite_movie import FavoriteMovie
from .watchlist import Watchlist
from .actor import Actor
from .movie_actor import MovieActor
from .director import Director
from .movie_director import MovieDirector
from .recommendation import Recommendation
from .user_activity_log import UserActivityLog
from .login_activity import LoginActivity

__all__ = [
    "Base",
    "Movie",
    "Genre",
    "MovieGenre",
    "User",
    "Rating",
    "Comment",
    "FavoriteMovie",
    "Watchlist",
    "Actor",
    "MovieActor",
    "Director",
    "MovieDirector",
    "Recommendation",
    "UserActivityLog",
    "LoginActivity",
]