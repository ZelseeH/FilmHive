from flask import request
from datetime import datetime
from app.models.login_activity import LoginActivity
from app.services.database import db


def log_login_activity(user_id, status="Success", additional_info=None):
    """
    Loguje aktywność logowania użytkownika

    Args:
        user_id (int): ID użytkownika
        status (str): Status logowania (Success, Failed, OAuth)
        additional_info (dict): Dodatkowe informacje (np. provider dla OAuth)
    """
    try:
        # Pobierz informacje o żądaniu
        ip_address = get_client_ip()
        user_agent = request.headers.get("User-Agent", "Unknown")

        # Utwórz rekord aktywności
        login_activity = LoginActivity(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            login_timestamp=datetime.utcnow(),
        )

        db.session.add(login_activity)
        db.session.commit()

        print(
            f"Zalogowano aktywność: User {user_id}, IP: {ip_address}, Status: {status}"
        )

    except Exception as e:
        print(f"Błąd podczas logowania aktywności: {str(e)}")
        db.session.rollback()


def get_client_ip():
    """Pobiera prawdziwy IP klienta z debugiem"""
    print("=== DEBUG IP ===")
    print(f"request.remote_addr: {request.remote_addr}")
    print(f"X-Forwarded-For: {request.headers.get('X-Forwarded-For')}")
    print(f"X-Real-IP: {request.headers.get('X-Real-IP')}")
    print(f"CF-Connecting-IP: {request.headers.get('CF-Connecting-IP')}")
    print(f"X-Forwarded-Proto: {request.headers.get('X-Forwarded-Proto')}")
    print("Wszystkie nagłówki:")
    for header, value in request.headers:
        if "ip" in header.lower() or "forward" in header.lower():
            print(f"  {header}: {value}")
    print("=== END DEBUG ===")

    return request.remote_addr or "Unknown"


def log_failed_login_attempt(username_or_email):
    """
    Loguje nieudaną próbę logowania (bez user_id)
    """
    try:
        ip_address = get_client_ip()
        user_agent = request.headers.get("User-Agent", "Unknown")

        login_activity = LoginActivity(
            user_id=None,  # Brak user_id dla nieudanych prób
            ip_address=ip_address,
            user_agent=user_agent,
            status=f"Failed - {username_or_email}",
            login_timestamp=datetime.utcnow(),
        )

        db.session.add(login_activity)
        db.session.commit()

        print(f"Zalogowano nieudaną próbę: {username_or_email}, IP: {ip_address}")

    except Exception as e:
        print(f"Błąd podczas logowania nieudanej próby: {str(e)}")
        db.session.rollback()
