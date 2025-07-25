from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.models import User
from sqlalchemy.orm.exc import NoResultFound

users_bp = Blueprint('users', __name__)

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user details"""
    try:
        current_user_id = get_jwt_identity()
        
        # Users can access their own data
        if int(current_user_id) != user_id:
            # Allow admins to access any user data
            admin_role = False  # You'd need to check if current user is admin
            if not admin_role:
                return jsonify({"error": "Unauthorized access"}), 403
                
        user = User.query.get_or_404(user_id)
        
        return jsonify({
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None
        })
        
    except NoResultFound:
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500