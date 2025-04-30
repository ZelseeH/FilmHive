from app.services.database import ma
from app.models.genre import Genre


class GenreSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Genre
        load_instance = True
