from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.sql import func
from controllers.models import Subject, Chapter, Quiz, Question, User, QuizAttempt, QuizResponse
from controllers.extensions import db, cache
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
from utils.decorators import cached, rate_limit

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@cached(timeout=60, user_specific=True, key_prefix='user_dashboard')
@rate_limit(limit=30, per=60, by="user")
def user_dashboard():
    """Get stats for user dashboard with caching"""
    try:
        user_id = get_jwt_identity()
        
        # Get total attempts
        total_attempts = QuizAttempt.query.filter_by(user_id=user_id).count()
        
        # Get average score - handle case with no attempts
        avg_score_query = db.session.query(
            func.avg(QuizAttempt.score_percentage).label('average_score')
        ).filter_by(user_id=user_id).first()
        average_score = round(avg_score_query.average_score or 0)
        
        # Get completed quizzes count
        completed_quizzes = QuizAttempt.query.filter_by(
            user_id=user_id, 
            status='completed'
        ).count()
        
        # Get available quizzes count
        available_quizzes = Quiz.query.filter_by(is_active=True).count()
        
        return jsonify({
            'totalAttempts': total_attempts,
            'averageScore': average_score,
            'completedQuizzes': completed_quizzes,
            'availableQuizzes': available_quizzes
        })
        
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@user_bp.route('/quizzes/available', methods=['GET'])
@jwt_required()
def get_available_quizzes():
    """Get list of available quizzes for the user with scheduling checks"""
    try:
        # Use cache if available, but don't fail if caching doesn't work
        try:
            # Try to use cached version
            cached_data = cache.get('available_quizzes')
            if cached_data:
                return jsonify(cached_data)
        except Exception as cache_error:
            print(f"Cache error (continuing without cache): {str(cache_error)}")

        # Get quizzes that are active and check scheduling
        from datetime import datetime
        now = datetime.now()
        
        # First, get all the quizzes with their details
        quizzes = db.session.query(
            Quiz.id, 
            Quiz.title, 
            Quiz.description, 
            Quiz.start_date,
            Quiz.start_time,
            Quiz.end_date,
            Quiz.end_time,
            Quiz.time_duration,
            Quiz.is_locked,
            Quiz.auto_lock_after_expiry,
            Chapter.name.label('chapter_name'),
            Subject.name.label('subject_name')
        ).join(Chapter, Quiz.chapter_id == Chapter.id)\
         .join(Subject, Chapter.subject_id == Subject.id)\
         .filter(Quiz.is_active == True)\
         .order_by(Quiz.start_date.desc(), Quiz.start_time.desc())\
         .all()
         
        result = []
        for q in quizzes:
            # Create quiz object to use is_available method
            quiz_obj = Quiz.query.get(q.id)
            
            # Only add quizzes that are actually available
            if quiz_obj and quiz_obj.is_available():
                quiz_data = {
                    'id': q.id,
                    'title': q.title,
                    'description': q.description,
                    'start_date': q.start_date.isoformat() if q.start_date else None,
                    'start_time': q.start_time.strftime('%H:%M') if q.start_time else None,
                    'end_date': q.end_date.isoformat() if q.end_date else None,
                    'end_time': q.end_time.strftime('%H:%M') if q.end_time else None,
                    'time_duration': q.time_duration,
                    'chapter_name': q.chapter_name,
                    'subject_name': q.subject_name,
                    'is_available': True,  # Only available quizzes are included
                    'is_locked': q.is_locked,
                    'time_until_start': None, # Already available
                    'time_until_end': str(quiz_obj.time_until_end()) if quiz_obj and quiz_obj.time_until_end() else None,
                    'date_of_quiz': q.start_date.isoformat() if q.start_date else datetime.now().date().isoformat()
                }
                result.append(quiz_data)
        
        # Try to store in cache, but don't fail if it doesn't work
        try:
            cache.set('available_quizzes', result, timeout=60)  # Shorter cache for scheduling
        except Exception as cache_error:
            print(f"Failed to store in cache: {str(cache_error)}")
            
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in get_available_quizzes: {str(e)}")
        return jsonify({"error": str(e)}), 500


@user_bp.route('/attempts/recent', methods=['GET'])
@jwt_required()
def get_recent_attempts():
    """Get recent quiz attempts by the user"""
    try:
        user_id = get_jwt_identity()
        
        attempts = db.session.query(
            QuizAttempt.id,
            QuizAttempt.quiz_id,
            QuizAttempt.score,
            QuizAttempt.total_marks,
            QuizAttempt.score_percentage,
            QuizAttempt.created_at,
            Quiz.title.label('quiz_title'),
            Chapter.name.label('chapter_name'),
            Subject.name.label('subject_name')
        ).join(Quiz, QuizAttempt.quiz_id == Quiz.id)\
         .join(Chapter, Quiz.chapter_id == Chapter.id)\
         .join(Subject, Chapter.subject_id == Subject.id)\
         .filter(QuizAttempt.user_id == user_id)\
         .order_by(QuizAttempt.created_at.desc())\
         .limit(5)\
         .all()
         
        result = [{
            'id': a.id,
            'quiz_id': a.quiz_id,
            'score': a.score,
            'total_marks': a.total_marks,
            'score_percentage': a.score_percentage,
            'created_at': a.created_at.isoformat() if a.created_at else None,
            'quiz_title': a.quiz_title,
            'chapter_name': a.chapter_name,
            'subject_name': a.subject_name
        } for a in attempts]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route('/attempts/by-quiz/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_attempts_by_quiz(quiz_id):
    """Get all attempts for a specific quiz by the user"""
    try:
        user_id = get_jwt_identity()
        
        attempts = db.session.query(
            QuizAttempt.id,
            QuizAttempt.score,
            QuizAttempt.total_marks,
            QuizAttempt.score_percentage,
            QuizAttempt.time_taken,
            QuizAttempt.created_at
        ).filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.quiz_id == quiz_id
        ).order_by(QuizAttempt.created_at.desc()).all()
        
        result = [{
            'id': a.id,
            'score': a.score,
            'total_marks': a.total_marks,
            'score_percentage': a.score_percentage,
            'time_taken': a.time_taken,
            'created_at': a.created_at.isoformat() if a.created_at else None
        } for a in attempts]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route('/attempts', methods=['GET'])
@jwt_required()
def get_all_attempts():
    """Get all quiz attempts by the user"""
    try:
        user_id = get_jwt_identity()
        
        attempts = db.session.query(
            QuizAttempt.id,
            QuizAttempt.quiz_id,
            QuizAttempt.score,
            QuizAttempt.total_marks,
            QuizAttempt.score_percentage,
            QuizAttempt.time_taken,
            QuizAttempt.created_at,
            Quiz.title.label('quiz_title'),
            Chapter.name.label('chapter_name'),
            Subject.name.label('subject_name')
        ).join(Quiz, QuizAttempt.quiz_id == Quiz.id)\
         .join(Chapter, Quiz.chapter_id == Chapter.id)\
         .join(Subject, Chapter.subject_id == Subject.id)\
         .filter(QuizAttempt.user_id == user_id)\
         .order_by(QuizAttempt.created_at.desc())\
         .all()
         
        result = [{
            'id': a.id,
            'quiz_id': a.quiz_id,
            'score': a.score,
            'total_marks': a.total_marks,
            'score_percentage': a.score_percentage,
            'time_taken': a.time_taken,
            'created_at': a.created_at.isoformat() if a.created_at else None,
            'quiz_title': a.quiz_title,
            'chapter_name': a.chapter_name,
            'subject_name': a.subject_name
        } for a in attempts]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user details"""
    try:
        current_user_id = get_jwt_identity()
        
        # Only allow users to access their own data
        if int(current_user_id) != user_id:
            return jsonify({"error": "Unauthorized"}), 403
            
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