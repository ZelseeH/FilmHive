from app.models.comment import Comment
from app.models.movie import Movie
from app.models.user import User
from app.models.rating import Rating
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime


class CommentRepository:
    def __init__(self, session):
        self.session = session

    def add_comment(self, user_id, movie_id, comment_text):
        try:
            comment = Comment(
                user_id=user_id, movie_id=movie_id, comment_text=comment_text
            )
            self.session.add(comment)
            self.session.commit()
            print(f"Dodano komentarz do filmu {movie_id} przez użytkownika {user_id}")
            return comment
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Błąd podczas dodawania komentarza: {e}")
            raise

    def update_comment(self, comment_id, user_id, new_text):
        try:
            comment = (
                self.session.query(Comment)
                .filter_by(comment_id=comment_id, user_id=user_id)
                .first()
            )

            if not comment:
                print(
                    f"Komentarz {comment_id} nie istnieje lub nie należy do użytkownika {user_id}"
                )
                return None

            comment.comment_text = new_text
            self.session.commit()
            print(f"Zaktualizowano komentarz {comment_id}")
            return comment
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Błąd podczas aktualizacji komentarza: {e}")
            raise

    def delete_comment(self, comment_id, user_id):
        try:
            comment = (
                self.session.query(Comment)
                .filter_by(comment_id=comment_id, user_id=user_id)
                .first()
            )

            if not comment:
                print(
                    f"Komentarz {comment_id} nie istnieje lub nie należy do użytkownika {user_id}"
                )
                return False

            self.session.delete(comment)
            self.session.commit()
            print(f"Usunięto komentarz {comment_id}")
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Błąd podczas usuwania komentarza: {e}")
            raise

    def get_comment_by_id(self, comment_id):
        try:
            comment = (
                self.session.query(Comment)
                .options(joinedload(Comment.user))
                .filter_by(comment_id=comment_id)
                .first()
            )
            return comment
        except SQLAlchemyError as e:
            print(f"Błąd podczas pobierania komentarza: {e}")
            raise

    def get_movie_comments(
        self,
        movie_id,
        page=1,
        per_page=10,
        sort_by="created_at",
        sort_order="desc",
        include_user_ratings=True,
    ):
        try:
            from app.models.rating import Rating
            from sqlalchemy import desc, asc, case, nullslast

            query = (
                self.session.query(Comment)
                .options(joinedload(Comment.user))
                .filter(Comment.movie_id == movie_id)
            )
            if sort_by == "rating":
                query = query.outerjoin(
                    Rating,
                    (Rating.user_id == Comment.user_id)
                    & (Rating.movie_id == Comment.movie_id),
                )

                if sort_order == "desc":
                    query = query.order_by(nullslast(desc(Rating.rating)))
                else:
                    query = query.order_by(nullslast(asc(Rating.rating)))
            else:
                if sort_order == "desc":
                    query = query.order_by(Comment.created_at.desc())
                else:
                    query = query.order_by(Comment.created_at.asc())

            total = query.count()

            comments = query.limit(per_page).offset((page - 1) * per_page).all()
            total_pages = (total + per_page - 1) // per_page if total > 0 else 0
            if include_user_ratings:
                user_ids = [comment.user_id for comment in comments]

                ratings = (
                    self.session.query(Rating)
                    .filter(Rating.user_id.in_(user_ids), Rating.movie_id == movie_id)
                    .all()
                )

                user_ratings = {rating.user_id: rating for rating in ratings}

                serialized_comments = []
                for comment in comments:
                    comment_data = comment.serialize(include_user=True)
                    if comment.user_id in user_ratings:
                        comment_data["user_rating"] = user_ratings[
                            comment.user_id
                        ].rating
                    else:
                        comment_data["user_rating"] = None
                    serialized_comments.append(comment_data)
            else:
                serialized_comments = [
                    comment.serialize(include_user=True) for comment in comments
                ]

            print(
                f"Pobrano {len(comments)} z {total} komentarzy dla filmu {movie_id} (strona {page}/{total_pages})"
            )

            return {
                "comments": serialized_comments,
                "pagination": {
                    "total": total,
                    "total_pages": total_pages,
                    "page": page,
                    "per_page": per_page,
                },
            }
        except SQLAlchemyError as e:
            print(f"Błąd podczas pobierania komentarzy: {e}")
            raise
        except Exception as e:
            print(f"Nieoczekiwany błąd podczas pobierania komentarzy: {e}")
            raise

    def get_user_comments(self, user_id, page=1, per_page=10, include_ratings=True):
        try:
            query = (
                self.session.query(Comment)
                .options(joinedload(Comment.movie))
                .filter_by(user_id=user_id)
                .order_by(Comment.created_at.desc())
            )

            total = query.count()
            comments = query.limit(per_page).offset((page - 1) * per_page).all()

            total_pages = (total + per_page - 1) // per_page if total > 0 else 0

            if include_ratings:
                movie_ids = [comment.movie_id for comment in comments]

                ratings = (
                    self.session.query(Rating)
                    .filter(Rating.user_id == user_id, Rating.movie_id.in_(movie_ids))
                    .all()
                )

                movie_ratings = {rating.movie_id: rating for rating in ratings}

                serialized_comments = []
                for comment in comments:
                    comment_data = comment.serialize(include_movie=True)
                    if comment.movie_id in movie_ratings:
                        comment_data["user_rating"] = movie_ratings[
                            comment.movie_id
                        ].rating
                    else:
                        comment_data["user_rating"] = None
                    serialized_comments.append(comment_data)
            else:
                serialized_comments = [
                    comment.serialize(include_movie=True) for comment in comments
                ]

            print(
                f"Pobrano {len(comments)} z {total} komentarzy użytkownika {user_id} (strona {page}/{total_pages})"
            )

            return {
                "comments": serialized_comments,
                "pagination": {
                    "total": total,
                    "total_pages": total_pages,
                    "page": page,
                    "per_page": per_page,
                },
            }
        except SQLAlchemyError as e:
            print(f"Błąd podczas pobierania komentarzy użytkownika: {e}")
            raise

    def count_movie_comments(self, movie_id):
        try:
            count = self.session.query(Comment).filter_by(movie_id=movie_id).count()
            print(f"Film {movie_id} ma {count} komentarzy")
            return count
        except SQLAlchemyError as e:
            print(f"Błąd podczas liczenia komentarzy: {e}")
            raise

    def get_user_comment_for_movie(self, user_id, movie_id, include_rating=True):
        try:
            comment = (
                self.session.query(Comment)
                .filter_by(user_id=user_id, movie_id=movie_id)
                .first()
            )

            if comment and include_rating:
                rating = (
                    self.session.query(Rating)
                    .filter_by(user_id=user_id, movie_id=movie_id)
                    .first()
                )
                if rating:
                    comment_data = comment.serialize(include_user=True)
                    comment_data["user_rating"] = rating.rating
                    return comment, comment_data
                else:
                    return comment, comment.serialize(include_user=True)

            print(
                f"Pobrano komentarz użytkownika {user_id} dla filmu {movie_id}: {comment is not None}"
            )
            return comment
        except SQLAlchemyError as e:
            print(f"Błąd podczas pobierania komentarza użytkownika dla filmu: {e}")
            raise

    def get_all_comments(
        self,
        page=1,
        per_page=20,
        search=None,
        date_from=None,
        date_to=None,
        sort_by="created_at",
        sort_order="desc",
    ):
        """
        Pobiera wszystkie komentarze z zaawansowanym filtrowaniem i sortowaniem

        Args:
            page: numer strony
            per_page: ilość na stronę
            search: wyszukiwanie w nazwie filmu, nazwie użytkownika lub treści komentarza
            date_from: data od (format: YYYY-MM-DD)
            date_to: data do (format: YYYY-MM-DD)
            sort_by: "created_at", "movie_title", "username"
            sort_order: "desc" lub "asc"
        """
        try:
            # IMPORTY WEWNĄTRZ METODY - rozwiązuje problem cyklicznych importów
            from sqlalchemy import desc, asc, or_, and_
            from sqlalchemy.orm import joinedload
            from datetime import datetime, timedelta
            from app.models.user import User
            from app.models.movie import Movie

            query = self.session.query(Comment).options(
                joinedload(Comment.user), joinedload(Comment.movie)
            )

            # FILTROWANIE PO WYSZUKIWANEJ FRAZIE
            if search and search.strip():
                search_term = f"%{search.strip()}%"
                query = (
                    query.join(User)
                    .join(Movie)
                    .filter(
                        or_(
                            Comment.comment_text.ilike(
                                search_term
                            ),  # w treści komentarza
                            User.username.ilike(search_term),  # w nazwie użytkownika
                            Movie.title.ilike(search_term),  # w nazwie filmu
                        )
                    )
                )
            else:
                # Jeśli nie ma search, dodaj join dla sortowania
                query = query.join(User).join(Movie)

            # FILTROWANIE PO DACIE (WIDEŁKI)
            if date_from:
                try:
                    date_from_obj = datetime.strptime(date_from, "%Y-%m-%d")
                    query = query.filter(Comment.created_at >= date_from_obj)
                except ValueError:
                    print(f"Nieprawidłowy format daty 'date_from': {date_from}")

            if date_to:
                try:
                    date_to_obj = datetime.strptime(date_to, "%Y-%m-%d")
                    # Dodaj 23:59:59 żeby uwzględnić cały dzień
                    date_to_obj = date_to_obj + timedelta(days=1) - timedelta(seconds=1)
                    query = query.filter(Comment.created_at <= date_to_obj)
                except ValueError:
                    print(f"Nieprawidłowy format daty 'date_to': {date_to}")

            # SORTOWANIE
            if sort_by == "movie_title":
                if sort_order == "desc":
                    query = query.order_by(desc(Movie.title))
                else:
                    query = query.order_by(asc(Movie.title))
            elif sort_by == "username":
                if sort_order == "desc":
                    query = query.order_by(desc(User.username))
                else:
                    query = query.order_by(asc(User.username))
            else:  # created_at (domyślne)
                if sort_order == "desc":
                    query = query.order_by(desc(Comment.created_at))
                else:
                    query = query.order_by(asc(Comment.created_at))

            # PAGINACJA
            total = query.count()
            comments = query.limit(per_page).offset((page - 1) * per_page).all()
            total_pages = (total + per_page - 1) // per_page if total > 0 else 0

            # SERIALIZACJA
            serialized_comments = [
                comment.serialize(include_user=True, include_movie=True)
                for comment in comments
            ]

            print(
                f"Pobrano {len(comments)} z {total} komentarzy (strona {page}/{total_pages})"
            )

            return {
                "comments": serialized_comments,
                "pagination": {
                    "total": total,
                    "total_pages": total_pages,
                    "page": page,
                    "per_page": per_page,
                },
                "filters": {
                    "search": search,
                    "date_from": date_from,
                    "date_to": date_to,
                    "sort_by": sort_by,
                    "sort_order": sort_order,
                },
            }
        except Exception as e:
            print(f"Błąd podczas pobierania wszystkich komentarzy: {e}")
            raise

    def update_comment_by_staff(self, comment_id, new_text, staff_user_id):
        """Aktualizuje komentarz przez staff (bez sprawdzania właściciela)"""
        try:
            comment = (
                self.session.query(Comment).filter_by(comment_id=comment_id).first()
            )

            if not comment:
                print(f"Komentarz {comment_id} nie istnieje")
                return None

            # Zapisz oryginalny tekst do logów
            original_text = comment.comment_text

            comment.comment_text = new_text
            self.session.commit()

            print(f"Staff {staff_user_id} zaktualizował komentarz {comment_id}")
            print(f"Oryginalny tekst: {original_text}")
            print(f"Nowy tekst: {new_text}")

            return comment
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Błąd podczas aktualizacji komentarza przez staff: {e}")
            raise

    def delete_comment_by_staff(self, comment_id, staff_user_id):
        """Usuwa komentarz przez staff (bez sprawdzania właściciela)"""
        try:
            comment = (
                self.session.query(Comment).filter_by(comment_id=comment_id).first()
            )

            if not comment:
                print(f"Komentarz {comment_id} nie istnieje")
                return False

            # Zapisz informacje do logów
            comment_info = {
                "id": comment.comment_id,
                "user_id": comment.user_id,
                "movie_id": comment.movie_id,
                "text": comment.comment_text,
                "created_at": comment.created_at,
            }

            self.session.delete(comment)
            self.session.commit()

            print(f"Staff {staff_user_id} usunął komentarz {comment_id}")
            print(f"Usunięty komentarz: {comment_info}")

            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Błąd podczas usuwania komentarza przez staff: {e}")
            raise

    def get_comment_with_details(self, comment_id):
        """Pobiera komentarz z pełnymi szczegółami (dla staff)"""
        try:
            comment = (
                self.session.query(Comment)
                .options(joinedload(Comment.user), joinedload(Comment.movie))
                .filter_by(comment_id=comment_id)
                .first()
            )

            if comment:
                return comment.serialize(
                    include_user=True, include_movie=True, include_rating=True
                )

            return None
        except SQLAlchemyError as e:
            print(f"Błąd podczas pobierania szczegółów komentarza: {e}")
            raise

    def get_comments_stats(self):
        """Pobiera statystyki komentarzy (dla staff dashboard)"""
        try:
            from sqlalchemy import func
            from datetime import datetime, timedelta

            total_comments = self.session.query(Comment).count()

            # Komentarze z ostatnich 24h
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_comments = (
                self.session.query(Comment)
                .filter(Comment.created_at >= yesterday)
                .count()
            )

            # Komentarze z ostatniego tygodnia
            week_ago = datetime.utcnow() - timedelta(days=7)
            weekly_comments = (
                self.session.query(Comment)
                .filter(Comment.created_at >= week_ago)
                .count()
            )

            # Najaktywniejszy użytkownik (komentarze)
            most_active_user = (
                self.session.query(
                    Comment.user_id,
                    User.username,
                    func.count(Comment.comment_id).label("comment_count"),
                )
                .join(User)
                .group_by(Comment.user_id, User.username)
                .order_by(func.count(Comment.comment_id).desc())
                .first()
            )

            return {
                "total_comments": total_comments,
                "recent_comments_24h": recent_comments,
                "weekly_comments": weekly_comments,
                "most_active_user": (
                    {
                        "user_id": (
                            most_active_user.user_id if most_active_user else None
                        ),
                        "username": (
                            most_active_user.username if most_active_user else None
                        ),
                        "comment_count": (
                            most_active_user.comment_count if most_active_user else 0
                        ),
                    }
                    if most_active_user
                    else None
                ),
            }
        except SQLAlchemyError as e:
            print(f"Błąd podczas pobierania statystyk komentarzy: {e}")
            raise

    def get_basic_statistics(self):
        """Pobiera podstawowe statystyki komentarzy"""
        try:
            from sqlalchemy import func
            from datetime import datetime, timedelta

            # Podstawowe liczby
            total_comments = self.session.query(Comment).count()

            # Komentarze z ostatnich 30 dni
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_comments = (
                self.session.query(Comment)
                .filter(Comment.created_at >= thirty_days_ago)
                .count()
            )

            # Komentarze z ostatnich 7 dni
            week_ago = datetime.utcnow() - timedelta(days=7)
            weekly_comments = (
                self.session.query(Comment)
                .filter(Comment.created_at >= week_ago)
                .count()
            )

            # Średnia długość komentarza
            avg_length = self.session.query(
                func.avg(func.length(Comment.comment_text))
            ).scalar()

            return {
                "total_comments": total_comments,
                "recent_comments_30_days": recent_comments,
                "weekly_comments": weekly_comments,
                "average_comment_length": round(avg_length, 1) if avg_length else 0,
            }

        except Exception as e:
            print(f"Błąd podczas pobierania podstawowych statystyk: {e}")
            raise

    def get_dashboard_data(self):
        """Pobiera dane dashboard dla komentarzy"""
        try:
            from sqlalchemy import func, extract
            from datetime import datetime, timedelta

            # Podstawowe statystyki
            basic_stats = self.get_basic_statistics()

            # Top 5 filmów z największą liczbą komentarzy
            from app.models.movie import Movie

            top_movies = (
                self.session.query(
                    Movie.title, func.count(Comment.comment_id).label("comment_count")
                )
                .join(Comment)
                .group_by(Movie.movie_id, Movie.title)
                .order_by(func.count(Comment.comment_id).desc())
                .limit(5)
                .all()
            )

            # Najaktywniejszy użytkownik
            from app.models.user import User

            top_user = (
                self.session.query(
                    User.username, func.count(Comment.comment_id).label("comment_count")
                )
                .join(Comment)
                .group_by(User.user_id, User.username)
                .order_by(func.count(Comment.comment_id).desc())
                .first()
            )

            # Komentarze według miesięcy (ostatnie 6 miesięcy)
            monthly_stats = []
            for i in range(6):
                month_start = datetime.utcnow().replace(day=1) - timedelta(days=30 * i)
                month_end = (month_start + timedelta(days=32)).replace(
                    day=1
                ) - timedelta(days=1)

                count = (
                    self.session.query(Comment)
                    .filter(
                        Comment.created_at >= month_start,
                        Comment.created_at <= month_end,
                    )
                    .count()
                )

                monthly_stats.append(
                    {"month": month_start.strftime("%Y-%m"), "count": count}
                )

            return {
                "statistics": basic_stats,
                "top_movies": [
                    {"title": title, "comment_count": count}
                    for title, count in top_movies
                ],
                "most_active_user": {
                    "username": top_user.username if top_user else None,
                    "comment_count": top_user.comment_count if top_user else 0,
                },
                "monthly_trends": list(reversed(monthly_stats)),
            }

        except Exception as e:
            print(f"Błąd podczas pobierania danych dashboard: {e}")
            raise
