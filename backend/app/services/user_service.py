from app.repositories.user_repository import UserRepository
from app.services.database import db

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

def update_user_profile(user_id, data):
    """Aktualizuje profil użytkownika."""
    try:
        user = user_repo.get_by_id(user_id)
        if not user:
            return None
        
        if 'bio' in data:
            user.bio = data['bio']
        if 'profile_picture' in data:
            user.profile_picture = data['profile_picture']
        
        updated_user = user_repo.update(user)
        return updated_user.serialize()
    except Exception as e:
        raise Exception(f"Błąd podczas aktualizacji profilu użytkownika o ID {user_id}: {str(e)}")
