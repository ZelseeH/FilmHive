from app.services.database import ma
from app.models.actor import Actor, Gender
from marshmallow import fields
from marshmallow_enum import EnumField


class ActorSchema(ma.SQLAlchemyAutoSchema):
    gender = EnumField(Gender, by_value=True, allow_none=True)
    birth_date = fields.Date(format="%Y-%m-%d", allow_none=True)
    photo_url = fields.Method("get_photo_url")

    class Meta:
        model = Actor
        load_instance = True
        include_relationships = True

    def get_photo_url(self, obj):
        from flask import url_for

        if obj.photo_url:
            return url_for("static", filename=f"actors/{obj.photo_url}", _external=True)
        return None


class MovieShortSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Actor.movies.property.mapper.class_
        fields = ("movie_id", "title")
        load_instance = True


class ActorWithMoviesSchema(ActorSchema):
    movies = fields.Nested(MovieShortSchema, many=True)
