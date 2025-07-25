from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.models import Subject, Chapter, Quiz, Question, User, QuizAttempt, QuizResponse
from controllers.extensions import db, cache
from datetime import datetime
import random
from sqlalchemy import func, distinct

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/subjects/details', methods=['GET'])
@jwt_required()
def get_subjects_with_details():
    """Get all subjects with chapter and quiz counts"""
    try:
        subjects = db.session.query(
            Subject.id,
            Subject.name,
            Subject.description,
            Subject.created_at,
            func.count(distinct(Chapter.id)).label('chapter_count'),
            func.count(distinct(Quiz.id)).label('quiz_count')
        ).outerjoin(Chapter, Subject.id == Chapter.subject_id)\
         .outerjoin(Quiz, Chapter.id == Quiz.chapter_id)\
         .filter(Subject.is_active == True)\
         .group_by(Subject.id)\
         .all()
         
        result = [{
            'id': s.id,
            'name': s.name,
            'description': s.description,
            'created_at': s.created_at.isoformat() if s.created_at else None,
            'chapter_count': s.chapter_count,
            'quiz_count': s.quiz_count
        } for s in subjects]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@quiz_bp.route('/subjects/<int:subject_id>', methods=['GET'])
@jwt_required()
def get_subject(subject_id):
    """Get subject by ID"""
    try:
        subject = Subject.query.get_or_404(subject_id)
        
        if not subject.is_active:
            return jsonify({"error": "Subject not found"}), 404
        
        return jsonify({
            'id': subject.id,
            'name': subject.name,
            'description': subject.description,
            'created_at': subject.created_at.isoformat() if subject.created_at else None,
            'is_active': subject.is_active
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@quiz_bp.route('/subjects/<int:subject_id>/chapters', methods=['GET'])
@jwt_required()
def get_chapters_by_subject(subject_id):
    """Get all chapters for a specific subject"""
    try:
        chapters = db.session.query(
            Chapter.id,
            Chapter.name,
            Chapter.description,
            Chapter.created_at,
            func.count(Quiz.id).label('quiz_count')
        ).outerjoin(Quiz, Chapter.id == Quiz.chapter_id)\
         .filter(Chapter.subject_id == subject_id, Chapter.is_active == True)\
         .group_by(Chapter.id)\
         .all()
         
        result = [{
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'created_at': c.created_at.isoformat() if c.created_at else None,
            'quiz_count': c.quiz_count
        } for c in chapters]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@quiz_bp.route('/subjects', methods=['GET'])
@jwt_required()
def get_all_subjects():
    """Get all active subjects"""
    try:
        subjects = Subject.query.filter_by(is_active=True).all()
        
        result = [{
            'id': subject.id,
            'name': subject.name,
            'description': subject.description,
            'created_at': subject.created_at.isoformat() if subject.created_at else None
        } for subject in subjects]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@quiz_bp.route('/chapters/<int:chapter_id>', methods=['GET'])
@jwt_required()
def get_chapter(chapter_id):
    """Get chapter by ID"""
    try:
        chapter = Chapter.query.get_or_404(chapter_id)
        
        if not chapter.is_active:
            return jsonify({"error": "Chapter not found"}), 404
        
        return jsonify({
            'id': chapter.id,
            'name': chapter.name,
            'description': chapter.description,
            'subject_id': chapter.subject_id,
            'created_at': chapter.created_at.isoformat() if chapter.created_at else None,
            'is_active': chapter.is_active
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@quiz_bp.route('/chapters/<int:chapter_id>/quizzes', methods=['GET'])
@jwt_required()
def get_quizzes_by_chapter(chapter_id):
    """Get all quizzes for a specific chapter"""
    try:
        quizzes = db.session.query(
            Quiz.id,
            Quiz.title,
            Quiz.description,
            Quiz.date_of_quiz,
            Quiz.time_duration,
            Quiz.passing_score,
            Quiz.total_marks,
            Quiz.created_at,
            func.count(Question.id).label('question_count')
        ).outerjoin(Question, Quiz.id == Question.quiz_id)\
         .filter(Quiz.chapter_id == chapter_id, Quiz.is_active == True)\
         .group_by(Quiz.id)\
         .all()
         
        result = [{
            'id': q.id,
            'title': q.title,
            'description': q.description,
            'date_of_quiz': q.date_of_quiz.isoformat() if q.date_of_quiz else None,
            'time_duration': q.time_duration,
            'passing_score': q.passing_score,
            'total_marks': q.total_marks,
            'created_at': q.created_at.isoformat() if q.created_at else None,
            'question_count': q.question_count
        } for q in quizzes]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@quiz_bp.route('/quizzes/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_quiz(quiz_id):
    """Get quiz by ID"""
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        
        if not quiz.is_active:
            return jsonify({"error": "Quiz not found"}), 404
        
        return jsonify({
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
            'time_duration': quiz.time_duration,
            'passing_score': quiz.passing_score,
            'total_marks': quiz.total_marks,
            'chapter_id': quiz.chapter_id,
            'created_at': quiz.created_at.isoformat() if quiz.created_at else None,
            'is_active': quiz.is_active
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@quiz_bp.route('/quizzes/<int:quiz_id>/questions/count', methods=['GET'])
@jwt_required()
def get_question_count(quiz_id):
    """Get question count for a quiz"""
    try:
        count = Question.query.filter_by(quiz_id=quiz_id).count()
        return jsonify({"count": count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@quiz_bp.route('/quizzes/<int:quiz_id>/attempts', methods=['POST'])
@jwt_required()
def create_attempt(quiz_id):
    """Create a new quiz attempt"""
    try:
        user_id = get_jwt_identity()
        
        # Check if quiz exists and is active
        quiz = Quiz.query.get_or_404(quiz_id)
        if not quiz.is_active:
            return jsonify({"error": "Quiz not available"}), 400
        
        # Create new attempt
        new_attempt = QuizAttempt(
            user_id=user_id,
            quiz_id=quiz_id,
            status='in_progress',
            score=0,
            total_marks=quiz.total_marks
        )
        
        db.session.add(new_attempt)
        db.session.commit()
        
        return jsonify({
            'id': new_attempt.id,
            'quiz_id': new_attempt.quiz_id,
            'status': new_attempt.status
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@quiz_bp.route('/attempts/<int:attempt_id>', methods=['GET'])
@jwt_required()
def get_attempt(attempt_id):
    """Get attempt details"""
    try:
        user_id = get_jwt_identity()
        
        # Find the attempt and verify ownership
        attempt = QuizAttempt.query.get_or_404(attempt_id)
        if attempt.user_id != int(user_id):
            return jsonify({"error": "Unauthorized access"}), 403
        
        return jsonify({
            'id': attempt.id,
            'user_id': attempt.user_id,
            'quiz_id': attempt.quiz_id,
            'status': attempt.status,
            'score': attempt.score,
            'total_marks': attempt.total_marks,
            'score_percentage': attempt.score_percentage,
            'time_taken': attempt.time_taken,
            'created_at': attempt.created_at.isoformat() if attempt.created_at else None
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@quiz_bp.route('/attempts/<int:attempt_id>/questions', methods=['GET'])
@jwt_required()
def get_attempt_questions(attempt_id):
    """Get questions for an attempt"""
    try:
        user_id = get_jwt_identity()
        
        # Find the attempt and verify ownership
        attempt = QuizAttempt.query.get_or_404(attempt_id)
        if attempt.user_id != int(user_id):
            return jsonify({"error": "Unauthorized access"}), 403
        
        # Only allow accessing questions if attempt is in progress
        if attempt.status != 'in_progress':
            return jsonify({"error": "Quiz attempt already completed"}), 400
        
        # Get all questions for the quiz
        questions = Question.query.filter_by(quiz_id=attempt.quiz_id).all()
        
        # Shuffle questions for randomization
        random.shuffle(questions)
        
        result = [{
            'id': q.id,
            'question_text': q.question_text,
            'option_1': q.option_1,
            'option_2': q.option_2,
            'option_3': q.option_3,
            'option_4': q.option_4,
            'marks': q.marks
        } for q in questions]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@quiz_bp.route('/attempts/<int:attempt_id>/submit', methods=['PUT'])
@jwt_required()
def submit_attempt(attempt_id):
    """Submit a quiz attempt with answers"""
    try:
        user_id = get_jwt_identity()
        
        # Find the attempt and verify ownership
        attempt = QuizAttempt.query.get_or_404(attempt_id)
        if attempt.user_id != int(user_id):
            return jsonify({"error": "Unauthorized access"}), 403
        
        # Check if attempt is still in progress
        if attempt.status != 'in_progress':
            return jsonify({"error": "Quiz attempt already submitted"}), 400
        
        # Get quiz details
        quiz = Quiz.query.get_or_404(attempt.quiz_id)
        
        # Get submitted answers
        data = request.json
        if not data or 'answers' not in data:
            return jsonify({"error": "No answers provided"}), 400
            
        answers = data['answers']
        time_taken = data.get('time_taken', quiz.time_duration)
        
        # Process each answer and calculate score
        total_score = 0
        
        for answer in answers:
            question_id = answer.get('question_id')
            selected_option = answer.get('selected_option', 0)
            
            if not question_id:
                continue
                
            # Get question
            question = Question.query.get(question_id)
            if not question or question.quiz_id != quiz.id:
                continue
                
            # Check if answer is correct
            is_correct = (selected_option == question.correct_option)
            score = question.marks if is_correct else 0
            total_score += score
            
            # Save response
            response = QuizResponse(
                attempt_id=attempt_id,
                question_id=question_id,
                selected_option=selected_option,
                is_correct=is_correct,
                score=score
            )
            
            db.session.add(response)
            
        # Update attempt
        attempt.status = 'completed'
        attempt.score = total_score
        attempt.score_percentage = round((total_score / attempt.total_marks) * 100) if attempt.total_marks > 0 else 0
        attempt.time_taken = time_taken
        
        db.session.commit()
        
        return jsonify({
            'id': attempt.id,
            'score': attempt.score,
            'total_marks': attempt.total_marks,
            'score_percentage': attempt.score_percentage,
            'status': 'completed'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@quiz_bp.route('/attempts/<int:attempt_id>/results', methods=['GET'])
@jwt_required()
def get_attempt_results(attempt_id):
    """Get detailed results for a completed attempt"""
    try:
        user_id = get_jwt_identity()
        
        # Find the attempt and verify ownership
        attempt = QuizAttempt.query.get_or_404(attempt_id)
        if attempt.user_id != int(user_id):
            return jsonify({"error": "Unauthorized access"}), 403
        
        # Get quiz details
        quiz = Quiz.query.get_or_404(attempt.quiz_id)
        
        # Get all responses with question details
        responses = db.session.query(
            QuizResponse.id,
            QuizResponse.selected_option,
            QuizResponse.is_correct,
            QuizResponse.score,
            Question.id.label('question_id'),
            Question.question_text,
            Question.option_1,
            Question.option_2,
            Question.option_3,
            Question.option_4,
            Question.correct_option,
            Question.marks
        ).join(Question, QuizResponse.question_id == Question.id)\
         .filter(QuizResponse.attempt_id == attempt_id)\
         .all()
         
        result = {
            'attempt_id': attempt.id,
            'quiz_id': attempt.quiz_id,
            'quiz_title': quiz.title,
            'score': attempt.score,
            'total_marks': attempt.total_marks,
            'score_percentage': attempt.score_percentage,
            'passing_score': quiz.passing_score,
            'time_taken': attempt.time_taken,
            'status': attempt.status,
            'created_at': attempt.created_at.isoformat() if attempt.created_at else None,
            'submitted_at': attempt.updated_at.isoformat() if attempt.updated_at else None,
            'questions': [{
                'id': r.question_id,
                'question_text': r.question_text,
                'option_1': r.option_1,
                'option_2': r.option_2,
                'option_3': r.option_3,
                'option_4': r.option_4,
                'selected_option': r.selected_option,
                'correct_option': r.correct_option,
                'is_correct': r.is_correct,
                'score': r.score,
                'marks': r.marks
            } for r in responses]
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500