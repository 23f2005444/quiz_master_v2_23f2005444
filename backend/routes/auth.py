from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from controllers.models import User, Admin
from controllers.extensions import db
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['email', 'password', 'full_name', 'qualification', 'date_of_birth']
        if not all(field in data for field in required_fields):
            return jsonify({'msg': 'Missing required fields'}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({'msg': 'Email already registered'}), 400

        try:
            date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'msg': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Create new user
        user = User(
            email=data['email'],
            full_name=data['full_name'],
            qualification=data['qualification'],
            date_of_birth=date_of_birth
        )
        user.password = data['password']

        db.session.add(user)
        db.session.commit()

        return jsonify({
            'msg': 'User registered successfully',
            'user': {
                'email': user.email,
                'full_name': user.full_name
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    role = data.get('role', 'user')
    
    if role == 'admin':
        admin = Admin.query.filter_by(username=data.get('username')).first()
        if admin and admin.verify_password(data.get('password')):
            # Create token with 24 hour expiry
            token = create_access_token(
                identity=str(admin.id), 
                additional_claims={'role': 'admin'},
                expires_delta=timedelta(hours=24)
            )
            return jsonify({
                'access_token': token,
                'role': 'admin',
                'user': {
                    'id': admin.id,
                    'username': admin.username,
                    'role': 'admin'
                }
            }), 200
        return jsonify({'msg': 'Invalid admin credentials'}), 401
    else:
        user = User.query.filter_by(email=data.get('email')).first()
        if user and user.verify_password(data.get('password')):
            # Create token with 24 hour expiry
            token = create_access_token(
                identity=str(user.id), 
                additional_claims={'role': 'user'},
                expires_delta=timedelta(hours=24)
            )
            return jsonify({
                'access_token': token,
                'role': 'user',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': 'user'
                }
            }), 200
        return jsonify({'msg': 'Invalid user credentials'}), 401

# Add a validation endpoint
@auth_bp.route('/validate', methods=['GET'])
@jwt_required()
def validate_token():
    # If JWT is valid, this endpoint will be accessible
    # Get the user ID from the token
    user_id = get_jwt_identity()
    
    return jsonify({
        'valid': True,
        'user_id': user_id
    })