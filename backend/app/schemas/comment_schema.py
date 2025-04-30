from app.services.database import ma
from app.models.comment import Comment
from marshmallow import fields


class UserShortSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Comment.user.property.mapper.class_
        fields = ("user_id", "username", "profile_picture")


class MovieShortSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Comment.movie.property.mapper.class_
        fields = ("movie_id", "title")


class CommentSchema(ma.SQLAlchemyAutoSchema):
    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S")
    user = fields.Nested(UserShortSchema)
    movie = fields.Nested(MovieShortSchema)

    class Meta:
        model = Comment
        load_instance = True
        include_fk = True
        include_relationships = True
