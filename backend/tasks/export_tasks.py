from celery import current_task
from controllers.models import User, Quiz, QuizAttempt, Subject, Chapter
from controllers.extensions import db
from datetime import datetime
import csv
import os
import tempfile
import uuid
from sqlalchemy import func

def export_user_quiz_attempts(user_id):
    """
    Export quiz attempts for a specific user to CSV format
    This is a synchronous version that can work without Celery
    """
    try:
        # Get user data
        user = User.query.get(user_id)
        if not user:
            raise Exception(f"User with ID {user_id} not found")
        
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
        
        return {
            'status': 'SUCCESS',
            'message': f'Successfully exported {len(attempts)} quiz attempts',
            'filename': filename,
            'filepath': filepath,
            'file_size': file_size,
            'total_records': len(attempts),
            'user_name': user.full_name,
            'export_date': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise Exception(f"Export failed: {str(e)}")

def export_admin_data(admin_id, export_type='users'):
    """
    Export admin data (users or quiz statistics) to CSV format
    """
    try:
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 1, 'total': 100, 'status': f'Starting {export_type} export...'}
        )
        
        if export_type == 'users':
            return _export_users_data(admin_id)
        elif export_type == 'quiz_stats':
            return _export_quiz_statistics(admin_id)
        else:
            raise Exception(f"Invalid export type: {export_type}")
            
    except Exception as e:
        current_task.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise

def _export_users_data(admin_id):
    """Export all users and their quiz performance"""
    
    current_task.update_state(
        state='PROGRESS',
        meta={'current': 20, 'total': 100, 'status': 'Fetching user data...'}
    )
    
    # Get all users with their quiz statistics
    users_data = db.session.query(
        User.id,
        User.email,
        User.full_name,
        User.qualification,
        User.date_of_birth,
        User.created_at,
        func.count(QuizAttempt.id).label('total_attempts'),
        func.count(
            db.case((QuizAttempt.status == 'completed', 1))
        ).label('completed_attempts'),
        func.avg(QuizAttempt.score_percentage).label('avg_score'),
        func.max(QuizAttempt.score_percentage).label('best_score'),
        func.count(
            db.case((QuizAttempt.is_passed == True, 1))
        ).label('passed_quizzes')
    ).outerjoin(QuizAttempt, User.id == QuizAttempt.user_id)\
     .group_by(User.id)\
     .all()
    
    current_task.update_state(
        state='PROGRESS',
        meta={'current': 50, 'total': 100, 'status': f'Processing {len(users_data)} users...'}
    )
    
    # Create temporary file
    temp_dir = tempfile.gettempdir()
    filename = f"users_export_{admin_id}_{uuid.uuid4().hex[:8]}.csv"
    filepath = os.path.join(temp_dir, filename)
    
    # Write CSV file
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'User ID', 'Email', 'Full Name', 'Qualification', 'Date of Birth',
            'Registration Date', 'Total Quiz Attempts', 'Completed Quizzes',
            'Average Score (%)', 'Best Score (%)', 'Passed Quizzes', 'Pass Rate (%)'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, user in enumerate(users_data):
            # Calculate progress
            progress = 50 + int((i / len(users_data)) * 40)
            current_task.update_state(
                state='PROGRESS',
                meta={'current': progress, 'total': 100, 'status': f'Writing user {i+1} of {len(users_data)}...'}
            )
            
            # Calculate pass rate
            pass_rate = 0
            if user.completed_attempts > 0:
                pass_rate = round((user.passed_quizzes / user.completed_attempts) * 100, 1)
            
            writer.writerow({
                'User ID': user.id,
                'Email': user.email,
                'Full Name': user.full_name,
                'Qualification': user.qualification,
                'Date of Birth': user.date_of_birth.strftime('%Y-%m-%d') if user.date_of_birth else 'N/A',
                'Registration Date': user.created_at.strftime('%Y-%m-%d') if user.created_at else 'N/A',
                'Total Quiz Attempts': user.total_attempts or 0,
                'Completed Quizzes': user.completed_attempts or 0,
                'Average Score (%)': f"{round(user.avg_score or 0, 1)}%",
                'Best Score (%)': f"{user.best_score or 0}%",
                'Passed Quizzes': user.passed_quizzes or 0,
                'Pass Rate (%)': f"{pass_rate}%"
            })
    
    file_size = os.path.getsize(filepath)
    
    return {
        'status': 'SUCCESS',
        'message': f'Successfully exported {len(users_data)} users',
        'filename': filename,
        'filepath': filepath,
        'file_size': file_size,
        'total_records': len(users_data),
        'export_date': datetime.now().isoformat()
    }

def _export_quiz_statistics(admin_id):
    """Export quiz statistics"""
    
    current_task.update_state(
        state='PROGRESS',
        meta={'current': 20, 'total': 100, 'status': 'Fetching quiz statistics...'}
    )
    
    # Get quiz statistics
    quiz_stats = db.session.query(
        Quiz.id,
        Quiz.title,
        Quiz.description,
        Quiz.start_date,
        Quiz.time_duration,
        Quiz.passing_score,
        Quiz.total_marks,
        Chapter.name.label('chapter_name'),
        Subject.name.label('subject_name'),
        func.count(QuizAttempt.id).label('total_attempts'),
        func.count(
            db.case((QuizAttempt.status == 'completed', 1))
        ).label('completed_attempts'),
        func.avg(QuizAttempt.score_percentage).label('avg_score'),
        func.count(
            db.case((QuizAttempt.is_passed == True, 1))
        ).label('passed_attempts')
    ).join(Chapter, Quiz.chapter_id == Chapter.id)\
     .join(Subject, Chapter.subject_id == Subject.id)\
     .outerjoin(QuizAttempt, Quiz.id == QuizAttempt.quiz_id)\
     .filter(Quiz.is_active == True)\
     .group_by(Quiz.id)\
     .all()
    
    current_task.update_state(
        state='PROGRESS',
        meta={'current': 50, 'total': 100, 'status': f'Processing {len(quiz_stats)} quizzes...'}
    )
    
    # Create temporary file
    temp_dir = tempfile.gettempdir()
    filename = f"quiz_statistics_{admin_id}_{uuid.uuid4().hex[:8]}.csv"
    filepath = os.path.join(temp_dir, filename)
    
    # Write CSV file
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'Quiz ID', 'Subject', 'Chapter', 'Quiz Title', 'Description',
            'Quiz Date', 'Duration (mins)', 'Total Marks', 'Passing Score (%)',
            'Total Attempts', 'Completed Attempts', 'Average Score (%)',
            'Passed Attempts', 'Pass Rate (%)', 'Completion Rate (%)'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, quiz in enumerate(quiz_stats):
            # Calculate progress
            progress = 50 + int((i / len(quiz_stats)) * 40)
            current_task.update_state(
                state='PROGRESS',
                meta={'current': progress, 'total': 100, 'status': f'Writing quiz {i+1} of {len(quiz_stats)}...'}
            )
            
            # Calculate rates
            pass_rate = 0
            completion_rate = 0
            
            if quiz.total_attempts > 0:
                completion_rate = round((quiz.completed_attempts / quiz.total_attempts) * 100, 1)
                
            if quiz.completed_attempts > 0:
                pass_rate = round((quiz.passed_attempts / quiz.completed_attempts) * 100, 1)
            
            writer.writerow({
                'Quiz ID': quiz.id,
                'Subject': quiz.subject_name,
                'Chapter': quiz.chapter_name,
                'Quiz Title': quiz.title,
                'Description': quiz.description[:100] + '...' if len(quiz.description) > 100 else quiz.description,
                'Quiz Date': quiz.start_date.strftime('%Y-%m-%d') if quiz.start_date else 'N/A',
                'Duration (mins)': quiz.time_duration,
                'Total Marks': quiz.total_marks,
                'Passing Score (%)': f"{quiz.passing_score}%",
                'Total Attempts': quiz.total_attempts or 0,
                'Completed Attempts': quiz.completed_attempts or 0,
                'Average Score (%)': f"{round(quiz.avg_score or 0, 1)}%",
                'Passed Attempts': quiz.passed_attempts or 0,
                'Pass Rate (%)': f"{pass_rate}%",
                'Completion Rate (%)': f"{completion_rate}%"
            })
    
    file_size = os.path.getsize(filepath)
    
    return {
        'status': 'SUCCESS',
        'message': f'Successfully exported statistics for {len(quiz_stats)} quizzes',
        'filename': filename,
        'filepath': filepath,
        'file_size': file_size,
        'total_records': len(quiz_stats),
        'export_date': datetime.now().isoformat()
    }

# Register tasks with Celery
from celery_app import celery

# User export task
export_user_quiz_attempts_task = celery.task(bind=True)(export_user_quiz_attempts)

# Admin export task  
export_admin_data_task = celery.task(bind=True)(export_admin_data)