from app.services.database import ma
from app.models.director import Director
from marshmallow import fields


class MovieShortSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Director.movies.property.mapper.class_
        fields = ("movie_id", "title")
        load_instance = True


class DirectorSchema(ma.SQLAlchemyAutoSchema):
    birth_date = fields.Date(format="%Y-%m-%d", allow_none=True)
    movies = fields.Nested(MovieShortSchema, many=True)

    class Meta:
        model = Director
        load_instance = True
        include_relationships = True
