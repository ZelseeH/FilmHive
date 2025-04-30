from app.services.database import ma
from app.models.rating import Rating
from marshmallow import fields


class UserShortSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Rating.user.property.mapper.class_
        fields = ("user_id", "username")


class MovieShortSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Rating.movie.property.mapper.class_
        fields = ("movie_id", "title")


class RatingSchema(ma.SQLAlchemyAutoSchema):
    rated_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S")
    user = fields.Nested(UserShortSchema)
    movie = fields.Nested(MovieShortSchema)

    class Meta:
        model = Rating
        load_instance = True
        include_relationships = True
        include_fk = True
