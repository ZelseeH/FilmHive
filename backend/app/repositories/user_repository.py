from app.models.user import User


class UserRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, user_id):
        return self.session.get(User, user_id)

    def get_by_username_or_email(self, identifier):
        return (
            self.session.query(User)
            .filter((User.username == identifier) | (User.email == identifier))
            .first()
        )

    def get_by_username(self, username):
        return self.session.query(User).filter(User.username == username).first()

    def add(self, user):
        self.session.add(user)
        self.session.commit()
        return user

    def update(self, user):
        self.session.commit()
        return user

    def update_profile(self, user_id, data):
        user = self.get_by_id(user_id)
        if not user:
            return None

        if "username" in data and data["username"] != user.username:
            existing_user = self.get_by_username_or_email(data["username"])
            if existing_user and existing_user.user_id != user.user_id:
                raise ValueError("Nazwa użytkownika jest już zajęta")
            user.username = data["username"]

        if "email" in data and data["email"] != user.email:
            existing_user = self.get_by_username_or_email(data["email"])
            if existing_user and existing_user.user_id != user.user_id:
                raise ValueError("Email jest już zajęty")
            user.email = data["email"]

        if "name" in data:
            user.name = data["name"]

        if "bio" in data:
            user.bio = data["bio"]

        if "profile_picture" in data:
            user.profile_picture = data["profile_picture"]

        if "is_active" in data:
            user.is_active = data["is_active"]

        self.session.commit()
        return user

    def change_password(self, user_id, new_password):
        user = self.get_by_id(user_id)
        if not user:
            return False
        user.set_password(new_password)
        self.session.commit()
        return True

    def update_profile_picture(self, user_id, profile_picture_path):
        user = self.get_by_id(user_id)
        if not user:
            return None
        user.profile_picture = profile_picture_path
        self.session.commit()
        return user

    def update_background_image(self, user_id, background_image_path):
        user = self.get_by_id(user_id)
        if not user:
            return None
        user.background_image = background_image_path
        self.session.commit()
        return user
