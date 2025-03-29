from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from datetime import datetime, timedelta
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.database import db

auth_bp = Blueprint('auth', __name__)
user_repo = UserRepository(db.session)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not all(key in data for key in ['username', 'email', 'password']):
        return jsonify({"error": "Brakujące dane: wymagane są username, email i password"}), 400
    
    if user_repo.get_by_username_or_email(data['username']):
        return jsonify({"error": "Nazwa użytkownika jest już zajęta"}), 409
    
    if user_repo.get_by_username_or_email(data['email']):
        return jsonify({"error": "Email jest już używany"}), 409
    
    new_user = User(
        username=data['username'],
        email=data['email'],
        registration_date=datetime.utcnow()
    )
    new_user.set_password(data['password'])
    
    try:
        user_repo.add(new_user)
        
        access_token = create_access_token(
            identity=str(new_user.user_id),
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
    
    if not all(key in data for key in ['username', 'password']):
        return jsonify({"error": "Brakujące dane: wymagane są username i password"}), 400
    
    user = user_repo.get_by_username_or_email(data['username'])
    
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Nieprawidłowa nazwa użytkownika lub hasło"}), 401
    
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    access_token = create_access_token(
        identity=str(user.user_id),
        additional_claims={"role": user.role},
        expires_delta=timedelta(days=1)
    )
    
    return jsonify({
        "message": "Logowanie zakończone pomyślnie",
        "access_token": access_token,
        "user": user.serialize()
    }), 200
