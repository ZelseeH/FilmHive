from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, DATETIME, UniqueConstraint, Float
from sqlalchemy.orm import validates
from datetime import datetime

class Base(DeclarativeBase):
    pass


class Movie(Base):
    __tablename__ = "movies"  # Nazwa tabeli w bazie danych

    movie_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)  # TEXT w SQL = String w SQLAlchemy
    release_date: Mapped[Date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(String(1000))  # Opcjonalne pole
    poster_url: Mapped[str] = mapped_column(String(255))  # Opcjonalne pole
    duration_minutes: Mapped[int] = mapped_column(Integer)  # Czas trwania filmu w minutach
    country: Mapped[str] = mapped_column(String(100))  # Kraj produkcji
    original_language: Mapped[str] = mapped_column(String(50))  # Język oryginalny

    # Relacje
    genres = relationship("Genre", secondary="movies_genres", back_populates="movies")  # Wiele-do-wiele
    actors = relationship("Actor", secondary="movie_actors", back_populates="movies")  # Wiele-do-wiele
    directors = relationship("Director", secondary="movie_directors", back_populates="movies")  # Wiele-do-wiele
    ratings = relationship("Rating", back_populates="movie")  # Jeden-do-wiele
    comments = relationship("Comment", back_populates="movie")  # Jeden-do-wiele
    recommendations: Mapped[list["Recommendation"]] = relationship("Recommendation", back_populates="movie")  # Relacja jeden-do-wiele z rekomendacjami

    def __repr__(self):
        return f"<Movie(id={self.movie_id}, title='{self.title}', release_date={self.release_date})>"

    

class Genre(Base):
    __tablename__ = "genres"  # Nazwa tabeli w bazie danych

    genre_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    genre_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Relacja wiele-do-wiele z Movie
    movies: Mapped[list["Movie"]] = relationship(
        "Movie", secondary="movies_genres", back_populates="genres"
    )

    def __repr__(self):
        return f"<Genre(id={self.genre_id}, name='{self.genre_name}')>"

 
    
class MovieGenre(Base):
    __tablename__ = "movies_genres"  # Nazwa tabeli w bazie danych

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.movie_id", ondelete="CASCADE"), primary_key=True, index=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.genre_id", ondelete="CASCADE"), primary_key=True, index=True)

    def __repr__(self):
        return f"<MovieGenre(movie_id={self.movie_id}, genre_id={self.genre_id})>"



class User(Base):
    __tablename__ = "users"  # Nazwa tabeli w bazie danych

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)  # Dodano indeks na nazwie użytkownika
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)  # Dodano indeks na e-mailu
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)  # Hash hasła
    role: Mapped[int] = mapped_column(Integer, default=3, nullable=False)  # Domyślna rola (3 - Użytkownik)
    registration_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)  # Data rejestracji użytkownika

    # Relacje
    ratings: Mapped[list["Rating"]] = relationship("Rating", back_populates="user")  # Relacja jeden-do-wiele z ocenami
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="user")  # Relacja jeden-do-wiele z komentarzami
    activity_logs: Mapped[list["UserActivityLog"]] = relationship("UserActivityLog", back_populates="user")  # Relacja jeden-do-wiele z aktywnościami
    login_activities: Mapped[list["LoginActivity"]] = relationship("LoginActivity", back_populates="user")  # Relacja jeden-do-wiele z logowaniami
    recommendations: Mapped[list["Recommendation"]] = relationship("Recommendation", back_populates="user")  # Relacja jeden-do-wiele z rekomendacjami

    def __repr__(self):
        return f"<User(id={self.user_id}, username='{self.username}', email='{self.email}', role={self.role})>"



class Rating(Base):
    __tablename__ = "ratings"  # Nazwa tabeli w bazie danych

    rating_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)  # Klucz obcy do tabeli Users
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.movie_id", ondelete="CASCADE"), nullable=False, index=True)  # Klucz obcy do tabeli Movies
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # Ocena od 0 do 10
    rated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)  # Data oceny

    # Walidacja wartości oceny
    @validates('rating')
    def validate_rating(self, key, value):
        if not (0 <= value <= 10):
            raise ValueError("Rating must be between 0 and 10.")
        return value

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="unique_user_movie_rating"),  # Każdy użytkownik może ocenić dany film tylko raz
    )

    # Relacje
    user: Mapped["User"] = relationship("User", back_populates="ratings")  # Relacja z tabelą Users
    movie: Mapped["Movie"] = relationship("Movie", back_populates="ratings")  # Relacja z tabelą Movies

    def __repr__(self):
        return f"<Rating(id={self.rating_id}, user_id={self.user_id}, movie_id={self.movie_id}, rating={self.rating})>"


class Comment(Base):
    __tablename__ = "comments"  # Nazwa tabeli w bazie danych

    comment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)  # Klucz obcy do tabeli Users
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.movie_id", ondelete="CASCADE"), nullable=False, index=True)  # Klucz obcy do tabeli Movies
    comment_text: Mapped[str] = mapped_column(String(1000), nullable=False)  # Tekst komentarza (wymagany)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)  # Data utworzenia komentarza

    # Relacje
    user: Mapped["User"] = relationship("User", back_populates="comments")  # Relacja z tabelą Users
    movie: Mapped["Movie"] = relationship("Movie", back_populates="comments")  # Relacja z tabelą Movies

    def __repr__(self):
        return f"<Comment(id={self.comment_id}, user_id={self.user_id}, movie_id={self.movie_id}, text='{self.comment_text}')>"


class FavoriteMovie(Base):
    __tablename__ = "favorite_movies"  # Nazwa tabeli w bazie danych

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True, index=True)  # Klucz obcy do tabeli Users
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.movie_id", ondelete="CASCADE"), primary_key=True, index=True)  # Klucz obcy do tabeli Movies

    def __repr__(self):
        return f"<FavoriteMovie(user_id={self.user_id}, movie_id={self.movie_id})>"


class Watchlist(Base):
    __tablename__ = "watchlist"  # Nazwa tabeli w bazie danych

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True, index=True)  # Klucz obcy do tabeli Users
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.movie_id", ondelete="CASCADE"), primary_key=True, index=True)  # Klucz obcy do tabeli Movies

    def __repr__(self):
        return f"<Watchlist(user_id={self.user_id}, movie_id={self.movie_id})>"


class Actor(Base):
    __tablename__ = "actors"  # Nazwa tabeli w bazie danych

    actor_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)  # Unikalna nazwa aktora
    birth_date: Mapped[datetime] = mapped_column(Date)  # Data urodzenia (opcjonalna)
    birth_place: Mapped[str] = mapped_column(String(255))  # Miejsce urodzenia (opcjonalne)
    biography: Mapped[str] = mapped_column(String(2000))  # Biografia (opcjonalne)

    # Relacje
    movies: Mapped[list["Movie"]] = relationship(
        "Movie", secondary="movie_actors", back_populates="actors"
    )  # Relacja wiele-do-wiele z filmami

    def __repr__(self):
        return f"<Actor(id={self.actor_id}, name='{self.actor_name}', birth_date={self.birth_date})>"


class MovieActor(Base):
    __tablename__ = "movie_actors"  # Nazwa tabeli w bazie danych

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.movie_id", ondelete="CASCADE"), primary_key=True, index=True)  # Klucz obcy do tabeli Movies
    actor_id: Mapped[int] = mapped_column(ForeignKey("actors.actor_id", ondelete="CASCADE"), primary_key=True, index=True)  # Klucz obcy do tabeli Actors
    movie_role: Mapped[str] = mapped_column(String(255))  # Rola aktora w filmie (opcjonalne)

    def __repr__(self):
        return f"<MovieActor(movie_id={self.movie_id}, actor_id={self.actor_id}, role='{self.movie_role}')>"


class Director(Base):
    __tablename__ = "directors"  # Nazwa tabeli w bazie danych

    director_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    director_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)  # Unikalna nazwa reżysera
    birth_date: Mapped[datetime] = mapped_column(Date)  # Data urodzenia (opcjonalna)
    birth_place: Mapped[str] = mapped_column(String(255))  # Miejsce urodzenia (opcjonalne)
    biography: Mapped[str] = mapped_column(String(2000))  # Biografia (opcjonalne)

    # Relacje
    movies: Mapped[list["Movie"]] = relationship(
        "Movie", secondary="movie_directors", back_populates="directors"
    )  # Relacja wiele-do-wiele z filmami

    def __repr__(self):
        return f"<Director(id={self.director_id}, name='{self.director_name}', birth_date={self.birth_date})>"


class MovieDirector(Base):
    __tablename__ = "movie_directors"  # Nazwa tabeli w bazie danych

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.movie_id", ondelete="CASCADE"), primary_key=True, index=True)  # Klucz obcy do tabeli Movies
    director_id: Mapped[int] = mapped_column(ForeignKey("directors.director_id", ondelete="CASCADE"), primary_key=True, index=True)  # Klucz obcy do tabeli Directors

    def __repr__(self):
        return f"<MovieDirector(movie_id={self.movie_id}, director_id={self.director_id})>"


class Recommendation(Base):
    __tablename__ = "recommendations"  # Nazwa tabeli w bazie danych

    recommendation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)  # Klucz obcy do tabeli Users
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.movie_id", ondelete="CASCADE"), nullable=False, index=True)  # Klucz obcy do tabeli Movies
    score: Mapped[float] = mapped_column(Float, nullable=False)  # Wartość między 0 a 1
    algorithm_used: Mapped[str] = mapped_column(String(255))  # Algorytm użyty do rekomendacji (opcjonalne)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)  # Data utworzenia rekomendacji

    # Walidacja wartości score
    @validates('score')
    def validate_score(self, key, value):
        if not (0 <= value <= 1):
            raise ValueError("Score must be between 0 and 1.")
        return value

    # Relacje
    user: Mapped["User"] = relationship("User", back_populates="recommendations")  # Relacja z tabelą Users
    movie: Mapped["Movie"] = relationship("Movie", back_populates="recommendations")  # Relacja z tabelą Movies

    def __repr__(self):
        return f"<Recommendation(id={self.recommendation_id}, user_id={self.user_id}, movie_id={self.movie_id}, score={self.score})>"


class UserActivityLog(Base):
    __tablename__ = "user_activity_logs"  # Nazwa tabeli w bazie danych

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)  # Klucz obcy do tabeli Users
    activity: Mapped[str] = mapped_column(String(255), nullable=False)  # Opis aktywności (np. "Dodano komentarz")
    activity_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)  # Data i czas aktywności

    # Relacja
    user: Mapped["User"] = relationship("User", back_populates="activity_logs")  # Relacja z tabelą Users

    def __repr__(self):
        return f"<UserActivityLog(log_id={self.log_id}, user_id={self.user_id}, activity='{self.activity}', timestamp={self.activity_timestamp})>"


class LoginActivity(Base):
    __tablename__ = "login_activities"  # Nazwa tabeli w bazie danych

    login_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)  # Klucz obcy do tabeli Users
    ip_address: Mapped[str] = mapped_column(String(50))  # Adres IP użytkownika podczas logowania
    login_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)  # Data i czas logowania
    user_agent: Mapped[str] = mapped_column(String(255))  # Informacje o przeglądarce/urządzeniu
    status: Mapped[str] = mapped_column(String(50), default="Success")  # Status logowania

    # Relacja
    user: Mapped["User"] = relationship("User", back_populates="login_activities")  # Relacja z tabelą Users

    def __repr__(self):
        return f"<LoginActivity(login_id={self.login_id}, user_id={self.user_id}, ip_address='{self.ip_address}', timestamp={self.login_timestamp})>"
