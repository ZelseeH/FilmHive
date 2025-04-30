from app.services.database import ma
from app.models.favorite_movie import FavoriteMovie
from marshmallow import fields


class FavoriteMovieSchema(ma.SQLAlchemyAutoSchema):
    added_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = FavoriteMovie
        load_instance = True
        include_fk = True


from app.models.movie import Movie


class MovieShortSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Movie
        fields = ("movie_id", "title", "poster_url")


class FavoriteMovieWithDetailsSchema(FavoriteMovieSchema):
    movie = fields.Nested(MovieShortSchema)
