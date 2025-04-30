from app.services.database import ma
from app.models.user import User
from marshmallow import fields


# Schematy uproszczone do relacji
class RatingShortSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User.ratings.property.mapper.class_
        fields = ("rating_id", "movie_id", "rating", "rated_at")


class CommentShortSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User.comments.property.mapper.class_
        fields = ("comment_id", "movie_id", "comment_text", "created_at")


class RecommendationShortSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User.recommendations.property.mapper.class_
        fields = ("recommendation_id", "movie_id", "created_at")


class WatchlistShortSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User.watchlist.property.mapper.class_
        fields = ("watchlist_id", "movie_id", "added_at")


class ActivityLogShortSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User.activity_logs.property.mapper.class_
        fields = ("log_id", "action", "created_at")


class LoginActivityShortSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User.login_activities.property.mapper.class_
        fields = ("activity_id", "ip_address", "timestamp")


class UserSchema(ma.SQLAlchemyAutoSchema):
    registration_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S")
    last_login = fields.DateTime(format="%Y-%m-%d %H:%M:%S")
    profile_picture = fields.Method("get_profile_picture_url")
    background_image = fields.Method("get_background_image_url")
    background_position = fields.Method("get_background_position")
    ratings = fields.Nested(RatingShortSchema, many=True)
    comments = fields.Nested(CommentShortSchema, many=True)
    recommendations = fields.Nested(RecommendationShortSchema, many=True)
    watchlist = fields.Nested(WatchlistShortSchema, many=True)
    activity_logs = fields.Nested(ActivityLogShortSchema, many=True)
    login_activities = fields.Nested(LoginActivityShortSchema, many=True)

    class Meta:
        model = User
        load_instance = True
        include_relationships = True
        exclude = ("password_hash",)  # Nigdy nie serializuj hasła!

    def get_profile_picture_url(self, obj):
        from flask import url_for

        if obj.profile_picture:
            return url_for(
                "static",
                filename=obj.profile_picture.lstrip("/static/"),
                _external=True,
            )
        return None

    def get_background_image_url(self, obj):
        from flask import url_for

        if obj.background_image:
            filename = (
                obj.background_image.lstrip("/static/")
                if obj.background_image.startswith("/static/")
                else obj.background_image
            )
            return url_for("static", filename=filename, _external=True)
        return None

    def get_background_position(self, obj):
        # Odtwarza logikę z modelu User
        import os, json
        from flask import current_app

        background_position = {"x": 50, "y": 50}
        if obj.background_image:
            bg_path = obj.background_image.lstrip("/static/")
            position_file = bg_path.replace(".jpg", "_position.json").replace(
                ".png", "_position.json"
            )
            position_path = os.path.join(current_app.root_path, "static", position_file)
            if os.path.exists(position_path):
                try:
                    with open(position_path, "r") as f:
                        background_position = json.load(f)
                except Exception:
                    pass
        return background_position
