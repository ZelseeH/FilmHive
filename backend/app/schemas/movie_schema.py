from app.services.database import ma
from app.models.movie import Movie
from marshmallow import fields


# Schematy uproszczone do relacji
class GenreShortSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Movie.genres.property.mapper.class_
        fields = ("genre_id", "genre_name")


class ActorShortSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Movie.actors.property.mapper.class_
        fields = ("actor_id", "actor_name", "photo_url")


class DirectorShortSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Movie.directors.property.mapper.class_
        fields = ("director_id", "director_name")


class RatingShortSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Movie.ratings.property.mapper.class_
        fields = ("rating_id", "user_id", "rating", "rated_at")


class CommentShortSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Movie.comments.property.mapper.class_
        fields = ("comment_id", "user_id", "comment_text", "created_at")


class RecommendationShortSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Movie.recommendations.property.mapper.class_
        fields = ("recommendation_id", "user_id", "created_at")


class MovieSchema(ma.SQLAlchemyAutoSchema):
    release_date = fields.Date(format="%Y-%m-%d")
    poster_url = fields.Method("get_poster_url")
    genres = fields.Nested(GenreShortSchema, many=True)
    actors = fields.Nested(ActorShortSchema, many=True)
    directors = fields.Nested(DirectorShortSchema, many=True)
    ratings = fields.Nested(RatingShortSchema, many=True)
    comments = fields.Nested(CommentShortSchema, many=True)
    recommendations = fields.Nested(RecommendationShortSchema, many=True)
    average_rating = fields.Method("get_average_rating")
    rating_count = fields.Method("get_rating_count")
    user_rating = fields.Method("get_user_rating")

    class Meta:
        model = Movie
        load_instance = True
        include_relationships = True
        include_fk = True

    def get_poster_url(self, obj):
        from flask import url_for

        if obj.poster_url:
            return url_for(
                "static", filename=f"posters/{obj.poster_url}", _external=True
            )
        return None

    def get_average_rating(self, obj):
        return getattr(obj, "average_rating", None)

    def get_rating_count(self, obj):
        return getattr(obj, "rating_count", None)

    def get_user_rating(self, obj):
        # Jeśli Movie ma atrybut _user_rating ustawiony dynamicznie (np. przez serwis)
        return getattr(obj, "_user_rating", None)
