"""
Authentication and JWT token management
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import database

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Admin login endpoint"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({"success": False, "error": "Username and password required"}), 400
        
        # Verify credentials
        user = database.verify_user(username, password)
        
        if not user:
            return jsonify({"success": False, "error": "Invalid credentials"}), 401
        
        # Create JWT token (expires in 24 hours)
        access_token = create_access_token(
            identity=str(user['id']),  # Convert to string for JWT
            additional_claims={"role": user['role']},
            expires_delta=timedelta(hours=24)
        )
        
        return jsonify({
            "success": True,
            "access_token": access_token,
            "user": {
                "id": user['id'],
                "username": user['username'],
                "role": user['role']
            }
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@auth_bp.route('/api/auth/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify JWT token and return current user"""
    try:
        user_id = int(get_jwt_identity())  # Convert back to int
        user = database.get_user_by_id(user_id)
        
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        return jsonify({
            "success": True,
            "user": user
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@auth_bp.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout endpoint (client-side token removal)"""
    return jsonify({"success": True, "message": "Logged out successfully"}), 200
