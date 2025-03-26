from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app.models.user import User
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Sprawdzenie, czy wymagane pola są obecne
    if not all(key in data for key in ['username', 'email', 'password']):
        return jsonify({"error": "Brakujące dane: wymagane są username, email i password"}), 400
    
    # Sprawdzenie, czy użytkownik już istnieje
    if db.session.query(User).filter_by(username=data['username']).first():
        return jsonify({"error": "Nazwa użytkownika jest już zajęta"}), 409
        
    if db.session.query(User).filter_by(email=data['email']).first():
        return jsonify({"error": "Email jest już używany"}), 409
    
    # Utworzenie nowego użytkownika
    new_user = User(
        username=data['username'],
        email=data['email'],
        registration_date=datetime.utcnow()
    )
    new_user.set_password(data['password'])
    
    # Zapisanie do bazy danych
    try:
        db.session.add(new_user)
        db.session.commit()
        
        # Utworzenie tokenu JWT
        access_token = create_access_token(
            identity=str(new_user.user_id),  # Konwersja na string
            additional_claims={"role": new_user.role},
            expires_delta=timedelta(days=1)
        )
        
        return jsonify({
            "message": "Rejestracja zakończona pomyślnie",
            "access_token": access_token,
            "user": new_user.serialize()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Sprawdzenie, czy wymagane pola są obecne
    if not all(key in data for key in ['username', 'password']):
        return jsonify({"error": "Brakujące dane: wymagane są username i password"}), 400
    
    # Wyszukanie użytkownika
    user = db.session.query(User).filter((User.username == data['username']) | (User.email == data['username'])).first()
    
    # Sprawdzenie hasła
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Nieprawidłowa nazwa użytkownika lub hasło"}), 401
    
    # Aktualizacja ostatniego logowania
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Utworzenie tokenu JWT
    access_token = create_access_token(
        identity=str(user.user_id),  # Konwersja na string
        additional_claims={"role": user.role},
        expires_delta=timedelta(days=1)
    )
    
    return jsonify({
        "message": "Logowanie zakończone pomyślnie",
        "access_token": access_token,
        "user": user.serialize()
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    print("Received request for profile")
    print("Authorization header:", request.headers.get('Authorization'))
    
    user_id = get_jwt_identity()
    print("Decoded user_id:", user_id)
    
    # Konwersja user_id z powrotem na liczbę, jeśli jest stringiem
    if isinstance(user_id, str) and user_id.isdigit():
        user_id = int(user_id)
    
    user = db.session.query(User).get(user_id)
    
    if not user:
        print("User not found for id:", user_id)
        return jsonify({"error": "Użytkownik nie znaleziony"}), 404
    
    print("User found:", user.username)
    return jsonify(user.serialize()), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    
    # Konwersja user_id z powrotem na liczbę, jeśli jest stringiem
    if isinstance(user_id, str) and user_id.isdigit():
        user_id = int(user_id)
    
    user = db.session.query(User).get(user_id)
    
    if not user:
        return jsonify({"error": "Użytkownik nie znaleziony"}), 404
    
    data = request.get_json()
    
    # Aktualizacja pól profilu
    if 'bio' in data:
        user.bio = data['bio']
    if 'profile_picture' in data:
        user.profile_picture = data['profile_picture']
    
    try:
        db.session.commit()
        return jsonify({
            "message": "Profil zaktualizowany pomyślnie",
            "user": user.serialize()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
