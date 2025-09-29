from app.models.genre import Genre


class GenreRepository:
    def __init__(self, session):
        self.session = session

    def get_all(self):
        return self.session.query(Genre).order_by(Genre.genre_name.asc()).all()

    def get_by_id(self, genre_id):
        return self.session.get(Genre, genre_id)

    def add(self, genre):
        self.session.add(genre)
        self.session.commit()
        return genre

    def delete(self, genre_id):
        genre = self.get_by_id(genre_id)
        if genre:
            self.session.delete(genre)
            self.session.commit()
            return True
        return False

    def update(self, genre_id, genre_name):
        genre = self.get_by_id(genre_id)
        if not genre:
            return None
        genre.genre_name = genre_name
        self.session.commit()
        return genre

    def get_basic_statistics(self):
        """Pobiera podstawowe statystyki gatunków - tylko zliczanie"""
        try:
            total_genres = self.session.query(Genre).count()
            return {"total_genres": total_genres}
        except Exception as e:
            print(f"Błąd podczas pobierania statystyk gatunków: {e}")
            return {"total_genres": 0}

    def get_dashboard_data(self):
        """Pobiera dane dashboard dla gatunków - tylko podstawowe"""
        try:
            basic_stats = self.get_basic_statistics()
            return {"statistics": basic_stats}
        except Exception as e:
            print(f"Błąd dashboard gatunków: {e}")
            return {"statistics": {"total_genres": 0}}
