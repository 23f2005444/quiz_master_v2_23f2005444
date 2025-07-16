from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.models import Quiz, Score
from controllers.extensions import db

user_bp = Blueprint('user', __name__)

def user_required():
    identity = get_jwt_identity()
    return identity and identity.get('role') == 'user'

@user_bp.route('/attempt_quiz', methods=['POST'])
@jwt_required()
def attempt_quiz():
    if not user_required():
        return jsonify({'msg': 'Users only'}), 403
    data = request.json

    score = Score(
        user_id=get_jwt_identity()['id'],
        quiz_id=data['quiz_id'],
        score=data['score']
    )
    db.session.add(score)
    db.session.commit()
    return jsonify({'msg': 'Quiz attempted'}), 200

@user_bp.route('/scores', methods=['GET'])
@jwt_required()
def view_scores():
    if not user_required():
        return jsonify({'msg': 'Users only'}), 403
    user_id = get_jwt_identity()['id']
    scores = Score.query.filter_by(user_id=user_id).all()
    return jsonify([{'quiz_id': s.quiz_id, 'score': s.score, 'date': s.date} for s in scores]), 200