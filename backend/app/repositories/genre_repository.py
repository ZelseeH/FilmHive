from app.models.genre import Genre

class GenreRepository:
    def __init__(self, session):
        self.session = session

    def get_all(self):
        return self.session.query(Genre).all()

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
