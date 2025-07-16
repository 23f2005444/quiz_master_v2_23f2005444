from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from controllers.models import User, Admin
from controllers.extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if not all(k in data for k in ('email', 'password', 'full_name', 'qualification', 'date_of_birth')):
        return jsonify({'msg': 'Missing fields'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'msg': 'Email already registered'}), 400
    user = User(
        email=data['email'],
        full_name=data['full_name'],
        qualification=data['qualification'],
        date_of_birth=data['date_of_birth']
    )
    user.password = data['password']
    db.session.add(user)
    db.session.commit()
    return jsonify({'msg': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    role = data.get('role', 'user')
    if role == 'admin':
        admin = Admin.query.filter_by(username=data.get('username')).first()
        if admin and admin.verify_password(data.get('password')):
            token = create_access_token(identity={'id': admin.id, 'role': 'admin'})
            return jsonify(access_token=token, role='admin'), 200
        return jsonify({'msg': 'Invalid admin credentials'}), 401
    else:
        user = User.query.filter_by(email=data.get('email')).first()
        if user and user.verify_password(data.get('password')):
            token = create_access_token(identity={'id': user.id, 'role': 'user'})
            return jsonify(access_token=token, role='user'), 200
        return jsonify({'msg': 'Invalid user credentials'}), 401