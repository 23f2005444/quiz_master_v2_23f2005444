from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.models import User, Quiz, QuizAttempt, Subject, Chapter
from controllers.extensions import db
from datetime import datetime
import csv
import os
import tempfile
import uuid
from sqlalchemy import func

exports_bp = Blueprint('exports', __name__)

@exports_bp.route('/user/quiz-attempts', methods=['POST'])
@jwt_required()
def export_user_quiz_attempts_sync():
    """Export user's quiz attempts synchronously (WORKING VERSION)"""
    try:
        user_id = get_jwt_identity()
        
        # Get user data
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': f'User with ID {user_id} not found'}), 404
        
        # Get all quiz attempts for the user with related data
        attempts = db.session.query(
            QuizAttempt.id,
            QuizAttempt.score,
            QuizAttempt.total_marks,
            QuizAttempt.score_percentage,
            QuizAttempt.time_taken,
            QuizAttempt.status,
            QuizAttempt.is_passed,
            QuizAttempt.created_at,
            QuizAttempt.start_time,
            QuizAttempt.end_time,
            Quiz.title.label('quiz_title'),
            Quiz.passing_score,
            Quiz.time_duration,
            Chapter.name.label('chapter_name'),
            Subject.name.label('subject_name')
        ).join(Quiz, QuizAttempt.quiz_id == Quiz.id)\
         .join(Chapter, Quiz.chapter_id == Chapter.id)\
         .join(Subject, Chapter.subject_id == Subject.id)\
         .filter(QuizAttempt.user_id == user_id)\
         .order_by(QuizAttempt.created_at.desc())\
         .all()
        
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        filename = f"quiz_attempts_{user_id}_{uuid.uuid4().hex[:8]}.csv"
        filepath = os.path.join(temp_dir, filename)
        
        # Write CSV file
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Attempt ID', 'Subject', 'Chapter', 'Quiz Title', 'Date Attempted',
                'Start Time', 'End Time', 'Time Taken (mins)', 'Duration Limit (mins)',
                'Score', 'Total Marks', 'Score Percentage', 'Passing Score',
                'Result', 'Status'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for attempt in attempts:
                writer.writerow({
                    'Attempt ID': attempt.id,
                    'Subject': attempt.subject_name,
                    'Chapter': attempt.chapter_name,
                    'Quiz Title': attempt.quiz_title,
                    'Date Attempted': attempt.created_at.strftime('%Y-%m-%d %H:%M:%S') if attempt.created_at else 'N/A',
                    'Start Time': attempt.start_time.strftime('%Y-%m-%d %H:%M:%S') if attempt.start_time else 'N/A',
                    'End Time': attempt.end_time.strftime('%Y-%m-%d %H:%M:%S') if attempt.end_time else 'N/A',
                    'Time Taken (mins)': attempt.time_taken or 'N/A',
                    'Duration Limit (mins)': attempt.time_duration,
                    'Score': attempt.score or 0,
                    'Total Marks': attempt.total_marks or 0,
                    'Score Percentage': f"{attempt.score_percentage or 0}%",
                    'Passing Score': f"{attempt.passing_score}%",
                    'Result': 'PASSED' if attempt.is_passed else 'FAILED' if attempt.is_passed is not None else 'INCOMPLETE',
                    'Status': attempt.status.upper()
                })
        
        # Get file size for response
        file_size = os.path.getsize(filepath)
        
        # Return the CSV file directly
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500