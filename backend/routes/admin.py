from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.models import Subject, Chapter, Quiz, Question, User
from controllers.extensions import db

admin_bp = Blueprint('admin', __name__)

def admin_required():
    identity = get_jwt_identity()
    return identity and identity.get('role') == 'admin'

@admin_bp.route('/subjects', methods=['POST'])
@jwt_required()
def create_subject():
    if not admin_required():
        return jsonify({'msg': 'Admins only'}), 403
    data = request.json
    subject = Subject(
        name=data['name'],
        description=data.get('description', ''),
        created_by=get_jwt_identity()['id']
    )
    db.session.add(subject)
    db.session.commit()
    return jsonify({'msg': 'Subject created'}), 201
