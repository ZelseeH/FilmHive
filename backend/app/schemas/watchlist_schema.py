from app.services.database import ma
from app.models.watchlist import Watchlist
from marshmallow import fields


class MovieShortSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Watchlist.movie.property.mapper.class_
        fields = ("movie_id", "title", "poster_url")


class WatchlistSchema(ma.SQLAlchemyAutoSchema):
    added_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S")
    movie = fields.Nested(MovieShortSchema)

    class Meta:
        model = Watchlist
        load_instance = True
        include_fk = True
        include_relationships = True
