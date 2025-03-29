from app.models.user import User

class UserRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, user_id):
        """Pobiera użytkownika na podstawie ID."""
        return self.session.get(User, user_id)

    def get_by_username_or_email(self, identifier):
        """Pobiera użytkownika na podstawie nazwy użytkownika lub emaila."""
        return self.session.query(User).filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()

    def add(self, user):
        """Dodaje nowego użytkownika do bazy danych."""
        self.session.add(user)
        self.session.commit()
        return user

    def update(self, user):
        """Aktualizuje dane użytkownika."""
        self.session.commit()
        return user
