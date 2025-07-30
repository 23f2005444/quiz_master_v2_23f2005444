from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.models import Quiz, Question, User, QuizAttempt, QuizResponse
from controllers.extensions import db
from sqlalchemy import exc
from datetime import datetime

attempts_bp = Blueprint('attempts', __name__)

@attempts_bp.route('/<int:quiz_id>/start', methods=['POST'])
@jwt_required()
def start_attempt(quiz_id):
    """Start a new quiz attempt"""
    try:
        user_id = get_jwt_identity()
        
        quiz = Quiz.query.get_or_404(quiz_id)
        
        if not quiz.is_active:
            return jsonify({"error": "This quiz is not currently active"}), 400
        
        existing_attempt = QuizAttempt.query.filter_by(
            user_id=user_id, 
            quiz_id=quiz_id, 
            status='in_progress'
        ).first()
        
        if existing_attempt:
            return jsonify({
                "id": existing_attempt.id,
                "message": "You already have an attempt in progress"
            }), 200
        
        new_attempt = QuizAttempt(
            user_id=user_id,
            quiz_id=quiz_id,
            start_time=datetime.now(),
            status='in_progress'
        )
        
        db.session.add(new_attempt)
        db.session.flush()  
        
        # Get questions for this quiz
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        
        # Create response objects for each question
        for question in questions:
            response = QuizResponse(
                attempt_id=new_attempt.id,
                question_id=question.id
            )
            db.session.add(response)
        
        db.session.commit()
        
        return jsonify({
            "id": new_attempt.id,
            "message": "Quiz attempt started successfully"
        }), 201
        
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@attempts_bp.route('/<int:attempt_id>', methods=['GET'])
@jwt_required()
def get_attempt(attempt_id):
    """Get details of a specific quiz attempt"""
    try:
        user_id = get_jwt_identity()
        
        # Get the attempt and ensure it belongs to this user
        attempt = QuizAttempt.query.get_or_404(attempt_id)
        if attempt.user_id != int(user_id):
            return jsonify({"error": "Unauthorized access to this attempt"}), 403
        
        # Get quiz details
        quiz = Quiz.query.get(attempt.quiz_id)
        
        result = {
            "id": attempt.id,
            "quiz_id": attempt.quiz_id,
            "quiz_title": quiz.title if quiz else "Unknown Quiz",
            "status": attempt.status,
            "start_time": attempt.start_time.isoformat() if attempt.start_time else None,
            "end_time": attempt.end_time.isoformat() if attempt.end_time else None,
            "time_taken": attempt.time_taken,
            "score": attempt.score,
            "total_marks": attempt.total_marks,
            "score_percentage": attempt.score_percentage,
            "is_passed": attempt.is_passed
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@attempts_bp.route('/<int:attempt_id>/questions', methods=['GET'])
@jwt_required()
def get_attempt_questions(attempt_id):
    """Get questions for a specific quiz attempt"""
    try:
        user_id = get_jwt_identity()
        
        # Get the attempt and ensure it belongs to this user
        attempt = QuizAttempt.query.get_or_404(attempt_id)
        if attempt.user_id != int(user_id):
            return jsonify({"error": "Unauthorized access to this attempt"}), 403
        
        # Get questions from responses
        questions = db.session.query(
            Question.id,
            Question.question_text,
            Question.option_1,
            Question.option_2,
            Question.option_3,
            Question.option_4,
            Question.marks,
            QuizResponse.selected_option
        ).join(
            QuizResponse, Question.id == QuizResponse.question_id
        ).filter(
            QuizResponse.attempt_id == attempt_id
        ).all()
        
        result = [{
            "id": q.id,
            "question_text": q.question_text,
            "option_1": q.option_1,
            "option_2": q.option_2,
            "option_3": q.option_3,
            "option_4": q.option_4,
            "marks": q.marks,
            "selected_option": q.selected_option
        } for q in questions]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@attempts_bp.route('/<int:attempt_id>/submit', methods=['PUT'])
@jwt_required()
def submit_attempt(attempt_id):
    """Submit answers for a quiz attempt"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        if not data or 'answers' not in data:
            return jsonify({"error": "Missing answer data"}), 400
        
        # Get the attempt and ensure it belongs to this user
        attempt = QuizAttempt.query.get_or_404(attempt_id)
        if attempt.user_id != int(user_id):
            return jsonify({"error": "Unauthorized access to this attempt"}), 403
        
        # Check if attempt is already completed
        if attempt.status == 'completed':
            return jsonify({"error": "This attempt has already been submitted"}), 400
        
        # Get the quiz
        quiz = Quiz.query.get(attempt.quiz_id)
        if not quiz:
            return jsonify({"error": "Associated quiz not found"}), 404
        
        # Process answers and calculate score
        total_score = 0
        total_possible = 0
        
        for answer_data in data['answers']:
            question_id = answer_data.get('question_id')
            selected_option = answer_data.get('selected_option', 0)
            
            # Get the question
            question = Question.query.get(question_id)
            if not question:
                continue
                
            # Get the response
            response = QuizResponse.query.filter_by(
                attempt_id=attempt_id,
                question_id=question_id
            ).first()
            
            if not response:
                continue
                
            # Update the response
            response.selected_option = selected_option
            
            # Check if answer is correct
            is_correct = selected_option == question.correct_option
            response.is_correct = is_correct
            
            # Calculate marks and update the score field (not marks_obtained)
            score = question.marks if is_correct else 0
            response.score = score
            
            # Add to total score
            total_score += score
            total_possible += question.marks
        
        # Update the attempt
        attempt.end_time = datetime.now()
        attempt.status = 'completed'
        attempt.score = total_score
        attempt.total_marks = total_possible
        attempt.score_percentage = round((total_score / total_possible) * 100) if total_possible > 0 else 0
        attempt.is_passed = attempt.score_percentage >= quiz.passing_score
        attempt.time_taken = data.get('time_taken', 0)
        
        db.session.commit()
        
        return jsonify({
            "id": attempt.id,
            "score": attempt.score,
            "total_marks": attempt.total_marks,
            "score_percentage": attempt.score_percentage,
            "is_passed": attempt.is_passed,
            "message": "Quiz submitted successfully"
        })
        
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@attempts_bp.route('/<int:attempt_id>/results', methods=['GET'])
@jwt_required()
def get_attempt_results(attempt_id):
    """Get detailed results for a completed quiz attempt"""
    try:
        user_id = get_jwt_identity()
        
        # Get the attempt and ensure it belongs to this user
        attempt = QuizAttempt.query.get_or_404(attempt_id)
        if attempt.user_id != int(user_id):
            return jsonify({"error": "Unauthorized access to this attempt"}), 403
        
        # Check if attempt is completed
        if attempt.status != 'completed':
            return jsonify({"error": "Results are only available for completed attempts"}), 400
        
        # Get quiz details
        quiz = Quiz.query.get(attempt.quiz_id)
        
        # Get question responses with details
        responses = db.session.query(
            QuizResponse.id,
            QuizResponse.question_id,
            QuizResponse.selected_option,
            QuizResponse.is_correct,
            QuizResponse.score, 
            Question.question_text,
            Question.option_1,
            Question.option_2,
            Question.option_3,
            Question.option_4,
            Question.correct_option,
            Question.marks
        ).join(
            Question, QuizResponse.question_id == Question.id
        ).filter(
            QuizResponse.attempt_id == attempt_id
        ).all()
        
        response_list = [{
            "id": r.id,
            "question_id": r.question_id,
            "question_text": r.question_text,
            "options": [r.option_1, r.option_2, r.option_3, r.option_4],
            "correct_option": r.correct_option,
            "selected_option": r.selected_option,
            "is_correct": r.is_correct,
            "marks_possible": r.marks,
            "score": r.score
        } for r in responses]
        
        result = {
            "attempt_id": attempt.id,
            "quiz_id": attempt.quiz_id,
            "quiz_title": quiz.title if quiz else "Unknown Quiz",
            "quiz_passing_score": quiz.passing_score if quiz else 0,
            "date_of_quiz": quiz.date_of_quiz.isoformat() if quiz and quiz.date_of_quiz else None,
            "time_duration": quiz.time_duration if quiz else 0,
            "start_time": attempt.start_time.isoformat() if attempt.start_time else None,
            "end_time": attempt.end_time.isoformat() if attempt.end_time else None,
            "time_taken": attempt.time_taken,
            "score": attempt.score,
            "total_marks": attempt.total_marks,
            "score_percentage": attempt.score_percentage,
            "is_passed": attempt.is_passed,
            "responses": response_list
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500