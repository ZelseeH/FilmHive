from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import get_user_by_id, update_user_profile

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

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = int(get_jwt_identity())
        
        data = request.get_json()
        
        updated_user = update_user_profile(user_id, data)
        
        if not updated_user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404
        
        return jsonify(updated_user), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
