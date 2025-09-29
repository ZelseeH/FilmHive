from datetime import datetime
from app.models.user_activity_log import UserActivityLog
from app.services.database import db


def log_user_activity(user_id, activity):
    """
    Loguje aktywność użytkownika

    Args:
        user_id (int): ID użytkownika
        activity (str): Opis aktywności
    """
    try:
        activity_log = UserActivityLog(
            user_id=user_id, activity=activity, activity_timestamp=datetime.utcnow()
        )

        db.session.add(activity_log)
        db.session.commit()

        print(f"Zalogowano aktywność: User {user_id} - {activity}")

    except Exception as e:
        print(f"Błąd podczas logowania aktywności: {str(e)}")
        db.session.rollback()


def log_password_change(user_id):
    """Loguje zmianę hasła"""
    log_user_activity(user_id, "Zmiana hasła")


def log_profile_update(user_id):
    """Loguje aktualizację profilu"""
    log_user_activity(user_id, "Aktualizacja profilu")


def log_username_change(user_id, old_username, new_username):
    """Loguje zmianę nazwy użytkownika"""
    log_user_activity(
        user_id, f"Zmiana nazwy użytkownika z {old_username} na {new_username}"
    )


def log_email_change(user_id, old_email, new_email):
    """Loguje zmianę emailu"""
    log_user_activity(user_id, f"Zmiana emailu z {old_email} na {new_email}")


def log_role_change(user_id, old_role, new_role):
    """Loguje zmianę roli"""
    role_names = {1: "admin", 2: "moderator", 3: "user"}
    old_role_name = role_names.get(old_role, f"rola {old_role}")
    new_role_name = role_names.get(new_role, f"rola {new_role}")
    log_user_activity(user_id, f"Zmiana roli z {old_role_name} na {new_role_name}")


def log_account_block(user_id, admin_id):
    """Loguje zablokowanie konta przez admina"""
    log_user_activity(
        user_id, f"Konto zablokowane przez administratora (ID: {admin_id})"
    )


def log_account_unblock(user_id, admin_id):
    """Loguje odblokowanie konta przez admina"""
    log_user_activity(
        user_id, f"Konto odblokowane przez administratora (ID: {admin_id})"
    )
