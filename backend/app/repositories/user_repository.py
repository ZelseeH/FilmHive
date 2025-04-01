from app.models.user import User


class UserRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, user_id):
        """Pobiera użytkownika na podstawie ID."""
        return self.session.get(User, user_id)

    def get_by_username_or_email(self, identifier):
        """Pobiera użytkownika na podstawie nazwy użytkownika lub emaila."""
        return (
            self.session.query(User)
            .filter((User.username == identifier) | (User.email == identifier))
            .first()
        )

    def get_by_username(self, username):
        """Pobiera użytkownika na podstawie nazwy użytkownika."""
        return self.session.query(User).filter(User.username == username).first()

    def add(self, user):
        """Dodaje nowego użytkownika do bazy danych."""
        self.session.add(user)
        self.session.commit()
        return user

    def update(self, user):
        """Aktualizuje dane użytkownika."""
        self.session.commit()
        return user

    def update_profile(self, user_id, data):
        """Aktualizuje profil użytkownika."""
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
        """Zmienia hasło użytkownika."""
        user = self.get_by_id(user_id)
        if not user:
            return False
        user.set_password(new_password)
        self.session.commit()
        return True
