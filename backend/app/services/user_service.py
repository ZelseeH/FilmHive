from app.repositories.user_repository import UserRepository
from app.services.database import db
from werkzeug.exceptions import BadRequest

user_repo = UserRepository(db.session)

def get_user_by_id(user_id):
    """Pobiera użytkownika na podstawie ID."""
    try:
        user = user_repo.get_by_id(user_id)
        if not user:
            return None
        return user.serialize()
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania użytkownika o ID {user_id}: {str(e)}")

def get_user_by_username(username):
    """Pobiera użytkownika na podstawie nazwy użytkownika."""
    try:
        user = user_repo.get_by_username(username)
        if not user:
            return None
        return user.serialize()
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania użytkownika o nazwie {username}: {str(e)}")

def update_user_profile(user_id, data):
    """Aktualizuje profil użytkownika."""
    try:
        # Walidacja danych
        if 'email' in data and not data['email']:
            raise ValueError("Email nie może być pusty")
        
        if 'name' in data and not data['name'].strip():
            raise ValueError("Imię i nazwisko nie może być puste")
        
        user = user_repo.update_profile(user_id, data)
        if not user:
            return None
        
        return user.serialize()
    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise Exception(f"Błąd podczas aktualizacji profilu użytkownika o ID {user_id}: {str(e)}")

def change_user_password(user_id, current_password, new_password):
    """Zmienia hasło użytkownika po weryfikacji obecnego hasła."""
    try:
        user = user_repo.get_by_id(user_id)
        if not user:
            return False
        
        if not user.check_password(current_password):
            return False
        
        if len(new_password) < 8:
            raise ValueError("Nowe hasło musi mieć co najmniej 8 znaków")
        
        return user_repo.change_password(user_id, new_password)
    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise Exception(f"Błąd podczas zmiany hasła: {str(e)}")
