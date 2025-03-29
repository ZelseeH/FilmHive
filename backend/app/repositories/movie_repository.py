from app.models.movie import Movie

class MovieRepository:
    def __init__(self, session):
        self.session = session

    def get_all(self):
        return self.session.query(Movie).all()

    def get_by_id(self, movie_id):
        return self.session.get(Movie, movie_id)

    def add(self, movie):
        self.session.add(movie)
        self.session.commit()
        return movie

    def delete(self, movie_id):
        movie = self.get_by_id(movie_id)
        if movie:
            self.session.delete(movie)
            self.session.commit()
            return True
        return False
