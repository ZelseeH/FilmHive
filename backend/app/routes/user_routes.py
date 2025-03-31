from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import get_user_by_id, get_user_by_username, update_user_profile, change_user_password
from werkzeug.exceptions import BadRequest

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = int(get_jwt_identity())
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404
        
        return jsonify(user), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/profile/<username>', methods=['GET'])
def get_user_profile(username):
    try:
        user = get_user_by_username(username)
        
        if not user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404
        
        # Return only public information
        public_data = {
            "username": user.get("username"),
            "name": user.get("name"),
            "bio": user.get("bio"),
            "profile_picture": user.get("profile_picture"),
            "registration_date": user.get("registration_date")
        }
        
        return jsonify(public_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            raise BadRequest("Brak danych do aktualizacji")
        
        updated_user = update_user_profile(user_id, data)
        
        if not updated_user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404
        
        return jsonify(updated_user), 200
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Wystąpił nieoczekiwany błąd"}), 500

@user_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data or 'current_password' not in data or 'new_password' not in data:
            raise BadRequest("Brakujące dane: obecne hasło i nowe hasło są wymagane")
        
        result = change_user_password(user_id, data['current_password'], data['new_password'])
        
        if not result:
            return jsonify({"error": "Nieprawidłowe obecne hasło"}), 401
        
        return jsonify({"message": "Hasło zostało zmienione pomyślnie"}), 200
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Wystąpił nieoczekiwany błąd"}), 500
