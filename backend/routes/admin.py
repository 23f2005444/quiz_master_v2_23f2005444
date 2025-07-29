from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.models import Admin, User, Subject, Chapter, Quiz, Question
from controllers.extensions import db
from sqlalchemy.exc import SQLAlchemyError

admin_bp = Blueprint('admin', __name__)

# Authentication middleware
def admin_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        print("JWT Identity:", current_user_id)
        
        try:
            admin_id = int(current_user_id)
            admin = Admin.query.get(admin_id)
            if not admin:
                return jsonify({"msg": "Admin not found"}), 403
        except (ValueError, TypeError) as e:
            return jsonify({"msg": "Invalid admin ID"}), 400
            
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

# User Management
@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    try:
        users = User.query.all()
        user_list = [{
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'qualification': user.qualification,
            'date_of_birth': user.date_of_birth.isoformat(),
            'created_at': user.created_at.isoformat()
        } for user in users]
        
        return jsonify(user_list)  # FIXED: Added return
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # FIXED: Added return
    
@admin_bp.route('/subjects', methods=['GET'])
@admin_required
def get_subjects():
    try:
        subjects = Subject.query.all()
        subject_list = [{
            'id': subject.id,
            'name': subject.name,
            'description': subject.description,
            'is_active': subject.is_active,
            'created_at': subject.created_at.isoformat()
        } for subject in subjects]
        
        return jsonify(subject_list)  # FIXED: Added return
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

# Subject Management
@admin_bp.route('/subjects/<int:subject_id>', methods=['GET'])
@admin_required
def get_subject(subject_id):
    try:
        subject = Subject.query.get_or_404(subject_id)
        
        return jsonify({
            'id': subject.id,
            'name': subject.name,
            'description': subject.description,
            'is_active': subject.is_active,
            'created_at': subject.created_at.isoformat() if subject.created_at else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/subjects', methods=['POST'])
@admin_required
def create_subject():
    try:
        data = request.json
        current_user_id = get_jwt_identity()
        
        # Validate required fields
        if 'name' not in data or not data['name']:
            return jsonify({"msg": "Subject name is required"}), 422
        if 'description' not in data or not data['description']:
            return jsonify({"msg": "Subject description is required"}), 422
            
        # Convert string ID to integer
        try:
            admin_id = int(current_user_id)
        except (ValueError, TypeError):
            return jsonify({"msg": "Invalid admin ID format"}), 422
        
        # Check if subject with same name already exists
        existing_subject = Subject.query.filter_by(name=data['name']).first()
        if existing_subject:
            return jsonify({"msg": "A subject with this name already exists"}), 422
        
        new_subject = Subject(
            name=data['name'],
            description=data['description'],
            created_by=admin_id,  # Use the integer ID directly
            is_active=data.get('is_active', True)
        )
        
        db.session.add(new_subject)
        db.session.commit()
        
        return jsonify({
            'id': new_subject.id,
            'name': new_subject.name,
            'description': new_subject.description,
            'is_active': new_subject.is_active
        }), 201
    except KeyError as e:
        return jsonify({"msg": f"Missing required field: {str(e)}"}), 422
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"msg": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"msg": f"Error creating subject: {str(e)}"}), 500

@admin_bp.route('/subjects/<int:subject_id>', methods=['PUT'])
@admin_required
def update_subject(subject_id):
    try:
        data = request.json
        subject = Subject.query.get_or_404(subject_id)
        
        subject.name = data.get('name', subject.name)
        subject.description = data.get('description', subject.description)
        subject.is_active = data.get('is_active', subject.is_active)
        
        db.session.commit()
        
        return jsonify({
            'id': subject.id,
            'name': subject.name,
            'description': subject.description,
            'is_active': subject.is_active
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"msg": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"msg": f"Error updating subject: {str(e)}"}), 500

@admin_bp.route('/subjects/<int:subject_id>', methods=['DELETE'])
@admin_required
def delete_subject(subject_id):
    try:
        subject = Subject.query.get_or_404(subject_id)
        
        db.session.delete(subject)
        db.session.commit()
        
        return jsonify({"msg": "Subject deleted successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"msg": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"msg": f"Error deleting subject: {str(e)}"}), 500

# Chapter Management
@admin_bp.route('/subjects/<int:subject_id>/chapters', methods=['GET'])
@admin_required
def get_chapters(subject_id):
    try:
        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        chapter_list = [{
            'id': chapter.id,
            'name': chapter.name,
            'description': chapter.description,
            'sequence_number': chapter.sequence_number,
            'is_active': chapter.is_active,
            'created_at': chapter.created_at.isoformat()
        } for chapter in chapters]
        
        return jsonify(chapter_list), 200
    except Exception as e:
        return jsonify({"msg": f"Error retrieving chapters: {str(e)}"}), 500

@admin_bp.route('/subjects/<int:subject_id>/chapters', methods=['POST'])
@admin_required
def create_chapter(subject_id):
    try:
        data = request.json
        current_user_id = get_jwt_identity()
        
        # Convert string ID to integer
        try:
            admin_id = int(current_user_id)
        except (ValueError, TypeError):
            return jsonify({"msg": "Invalid admin ID format"}), 422
            
        # Check if subject exists
        subject = Subject.query.get_or_404(subject_id)
        
        # Get the highest sequence number for this subject
        max_seq = db.session.query(db.func.max(Chapter.sequence_number))\
            .filter_by(subject_id=subject_id).scalar() or 0
        
        new_chapter = Chapter(
            subject_id=subject_id,
            name=data['name'],
            description=data['description'],
            sequence_number=max_seq + 1,
            created_by=admin_id,  # Use the integer ID directly
            is_active=data.get('is_active', True)
        )
        
        db.session.add(new_chapter)
        db.session.commit()
        
        return jsonify({
            'id': new_chapter.id,
            'name': new_chapter.name,
            'description': new_chapter.description,
            'sequence_number': new_chapter.sequence_number,
            'is_active': new_chapter.is_active
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"msg": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"msg": f"Error creating chapter: {str(e)}"}), 500
    
@admin_bp.route('/chapters/<int:chapter_id>', methods=['GET'])
@admin_required
def get_chapter(chapter_id):
    try:
        chapter = Chapter.query.get_or_404(chapter_id)

        return jsonify({
            'id': chapter.id,
            'name': chapter.name,
            'description': chapter.description,
            'subject_id': chapter.subject_id,
            'sequence_number': chapter.sequence_number,
            'is_active': chapter.is_active,
            'created_at': chapter.created_at.isoformat() if chapter.created_at else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/chapters/<int:chapter_id>', methods=['PUT'])
@admin_required
def update_chapter(chapter_id):
    try:
        data = request.json
        chapter = Chapter.query.get_or_404(chapter_id)
        
        chapter.name = data.get('name', chapter.name)
        chapter.description = data.get('description', chapter.description)
        chapter.is_active = data.get('is_active', chapter.is_active)
        
        db.session.commit()
        
        return jsonify({
            'id': chapter.id,
            'name': chapter.name,
            'description': chapter.description,
            'sequence_number': chapter.sequence_number,
            'is_active': chapter.is_active
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"msg": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"msg": f"Error updating chapter: {str(e)}"}), 500

@admin_bp.route('/chapters/<int:chapter_id>', methods=['DELETE'])
@admin_required
def delete_chapter(chapter_id):
    try:
        chapter = Chapter.query.get_or_404(chapter_id)
        
        db.session.delete(chapter)
        db.session.commit()
        
        return jsonify({"msg": "Chapter deleted successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"msg": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"msg": f"Error deleting chapter: {str(e)}"}), 500

# Quiz Management
@admin_bp.route('/chapters/<int:chapter_id>/quizzes', methods=['GET'])
@admin_required
def get_quizzes(chapter_id):
    try:
        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
        quiz_list = [{
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'start_date': quiz.start_date.isoformat() if quiz.start_date else None,
            'start_time': quiz.start_time.strftime('%H:%M') if quiz.start_time else None,
            'end_date': quiz.end_date.isoformat() if quiz.end_date else None,
            'end_time': quiz.end_time.strftime('%H:%M') if quiz.end_time else None,
            'time_duration': quiz.time_duration,
            'passing_score': quiz.passing_score,
            'total_marks': quiz.total_marks,
            'auto_lock_after_expiry': quiz.auto_lock_after_expiry,
            'is_locked': quiz.is_locked,
            'is_active': quiz.is_active,
            'is_available': quiz.is_available(),
            'time_until_start': str(quiz.time_until_start()) if quiz.time_until_start() else None,
            'time_until_end': str(quiz.time_until_end()) if quiz.time_until_end() else None,
            'created_at': quiz.created_at.isoformat() if quiz.created_at else None
        } for quiz in quizzes]
        
        return jsonify(quiz_list)  # This was missing!
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add this function to the existing admin.py file
@admin_bp.route('/chapters/<int:chapter_id>/quizzes', methods=['POST'])
@admin_required
def create_quiz(chapter_id):
    try:
        data = request.json
        current_user_id = get_jwt_identity()
        
        admin_id = int(current_user_id)
        
        # Validate required fields
        required_fields = ['title', 'description', 'start_date', 'start_time', 'time_duration', 'passing_score', 'total_marks']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Parse dates and times
        from datetime import datetime, date, time
        
        try:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            start_time = datetime.strptime(data['start_time'], '%H:%M').time()
            
            end_date = None
            end_time = None
            if data.get('end_date'):
                end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            if data.get('end_time'):
                end_time = datetime.strptime(data['end_time'], '%H:%M').time()
                
        except ValueError as e:
            return jsonify({"error": f"Invalid date/time format: {str(e)}"}), 400
        
        new_quiz = Quiz(
            chapter_id=chapter_id,
            title=data['title'],
            description=data['description'],
            start_date=start_date,
            start_time=start_time,
            end_date=end_date,
            end_time=end_time,
            time_duration=int(data['time_duration']),
            passing_score=int(data['passing_score']),
            total_marks=int(data['total_marks']),
            auto_lock_after_expiry=data.get('auto_lock_after_expiry', True),
            created_by=admin_id,
            is_active=data.get('is_active', True)
        )
        
        db.session.add(new_quiz)
        db.session.commit()
        
        return jsonify({
            'id': new_quiz.id,
            'message': 'Quiz created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/quizzes/<int:quiz_id>', methods=['GET'])
@admin_required
def get_quiz(quiz_id):
    try:
        quiz = Quiz.query.get_or_404(quiz_id)

        return jsonify({
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'start_date': quiz.start_date.isoformat(),
            'start_time': quiz.start_time.strftime('%H:%M'),
            'end_date': quiz.end_date.isoformat() if quiz.end_date else None,
            'end_time': quiz.end_time.strftime('%H:%M') if quiz.end_time else None,
            'time_duration': quiz.time_duration,
            'passing_score': quiz.passing_score,
            'total_marks': quiz.total_marks,
            'auto_lock_after_expiry': quiz.auto_lock_after_expiry,
            'is_locked': quiz.is_locked,
            'chapter_id': quiz.chapter_id,
            'created_at': quiz.created_at.isoformat() if quiz.created_at else None,
            'is_active': quiz.is_active,
            'is_available': quiz.is_available(),
            'time_until_start': str(quiz.time_until_start()) if quiz.time_until_start() else None,
            'time_until_end': str(quiz.time_until_end()) if quiz.time_until_end() else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add quiz lock/unlock endpoints
@admin_bp.route('/quizzes/<int:quiz_id>/lock', methods=['PUT'])
@admin_required
def lock_quiz(quiz_id):
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        quiz.is_locked = True
        db.session.commit()
        
        return jsonify({"msg": "Quiz locked successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/quizzes/<int:quiz_id>/unlock', methods=['PUT'])
@admin_required
def unlock_quiz(quiz_id):
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        quiz.is_locked = False
        db.session.commit()
        
        return jsonify({"msg": "Quiz unlocked successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/quizzes/<int:quiz_id>', methods=['PUT'])
@admin_required
def update_quiz(quiz_id):
    try:
        data = request.json
        quiz = Quiz.query.get_or_404(quiz_id)
        
        print("Received quiz update data:", data)
        
        # Update basic text fields
        if 'title' in data:
            quiz.title = data['title']
        if 'description' in data:
            quiz.description = data['description']
            
        # Handle numeric fields with validation
        if 'time_duration' in data:
            try:
                quiz.time_duration = int(data['time_duration'])
            except (ValueError, TypeError):
                return jsonify({"msg": "Invalid time duration"}), 400
                
        if 'passing_score' in data:
            try:
                quiz.passing_score = int(data['passing_score'])
            except (ValueError, TypeError):
                return jsonify({"msg": "Invalid passing score"}), 400
                
        if 'total_marks' in data:
            try:
                quiz.total_marks = int(data['total_marks'])
            except (ValueError, TypeError):
                return jsonify({"msg": "Invalid total marks"}), 400
        
        # Handle scheduling fields
        if 'start_date' in data and data['start_date']:
            try:
                from datetime import datetime
                quiz.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"msg": "Invalid start date format"}), 400
                
        if 'start_time' in data and data['start_time']:
            try:
                from datetime import datetime
                quiz.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
            except ValueError:
                return jsonify({"msg": "Invalid start time format"}), 400
                
        # Handle optional end date and time
        if 'end_date' in data:
            if data['end_date'] and data['end_date'].strip():
                try:
                    quiz.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({"msg": "Invalid end date format"}), 400
            else:
                quiz.end_date = None
                
        if 'end_time' in data:
            if data['end_time'] and data['end_time'].strip():
                try:
                    quiz.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
                except ValueError:
                    return jsonify({"msg": "Invalid end time format"}), 400
            else:
                quiz.end_time = None
        
        # Handle boolean fields
        if 'auto_lock_after_expiry' in data:
            quiz.auto_lock_after_expiry = bool(data['auto_lock_after_expiry'])
            
        if 'is_active' in data:
            quiz.is_active = bool(data['is_active'])
        
        # Validate logical constraints
        if quiz.passing_score > 100:
            return jsonify({"msg": "Passing score cannot exceed 100%"}), 400
            
        if quiz.total_marks <= 0:
            return jsonify({"msg": "Total marks must be greater than 0"}), 400
        
        db.session.commit()
        
        return jsonify({
            "msg": "Quiz updated successfully",
            "quiz": {
                "id": quiz.id,
                "title": quiz.title,
                "description": quiz.description,
                "start_date": quiz.start_date.isoformat() if quiz.start_date else None,
                "start_time": quiz.start_time.strftime('%H:%M') if quiz.start_time else None,
                "end_date": quiz.end_date.isoformat() if quiz.end_date else None,
                "end_time": quiz.end_time.strftime('%H:%M') if quiz.end_time else None,
                "time_duration": quiz.time_duration,
                "passing_score": quiz.passing_score,
                "total_marks": quiz.total_marks,
                "auto_lock_after_expiry": quiz.auto_lock_after_expiry,
                "is_active": quiz.is_active,
                "is_available": quiz.is_available()
            }
        })
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"msg": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"msg": f"Error updating quiz: {str(e)}"}), 500

@admin_bp.route('/quizzes/<int:quiz_id>', methods=['DELETE'])
@admin_required
def delete_quiz(quiz_id):
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        
        db.session.delete(quiz)
        db.session.commit()
        
        return jsonify({"msg": "Quiz deleted successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"msg": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"msg": f"Error deleting quiz: {str(e)}"}), 500

# Question Management
@admin_bp.route('/quizzes/<int:quiz_id>/questions', methods=['GET'])
@admin_required
def get_questions(quiz_id):
    try:
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        question_list = [{
            'id': question.id,
            'question_text': question.question_text,
            'option_1': question.option_1,
            'option_2': question.option_2,
            'option_3': question.option_3,
            'option_4': question.option_4,
            'correct_option': question.correct_option,
            'marks': question.marks,
            'created_at': question.created_at.isoformat()
        } for question in questions]
        
        return jsonify(question_list), 200
    except Exception as e:
        return jsonify({"msg": f"Error retrieving questions: {str(e)}"}), 500

@admin_bp.route('/quizzes/<int:quiz_id>/questions', methods=['POST'])
@admin_required
def create_question(quiz_id):
    try:
        data = request.json
        current_user_id = get_jwt_identity()
        
        # Print received data for debugging
        print("Received question data:", data)
        
        # Convert string ID to integer
        try:
            admin_id = int(current_user_id)
        except (ValueError, TypeError):
            return jsonify({"msg": "Invalid admin ID format"}), 422
            
        # Check if quiz exists
        quiz = Quiz.query.get_or_404(quiz_id)
        
        # Validate required fields
        required_fields = ['question_text', 'option_1', 'option_2', 'option_3', 'option_4', 'correct_option', 'marks']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"msg": f"Field '{field}' is required"}), 422
        
        # Validate correct_option is between 1 and 4
        try:
            correct_option = int(data['correct_option'])
            if correct_option < 1 or correct_option > 4:
                return jsonify({"msg": "Correct option must be between 1 and 4"}), 422
        except (ValueError, TypeError):
            return jsonify({"msg": "Correct option must be a number between 1 and 4"}), 422
            
        # Validate marks is a positive number
        try:
            marks = int(data['marks'])
            if marks <= 0:
                return jsonify({"msg": "Marks must be greater than 0"}), 422
        except (ValueError, TypeError):
            return jsonify({"msg": "Marks must be a positive number"}), 422
        
        # Create the new question
        new_question = Question(
            quiz_id=quiz_id,
            question_text=data['question_text'],
            option_1=data['option_1'],
            option_2=data['option_2'],
            option_3=data['option_3'],
            option_4=data['option_4'],
            correct_option=correct_option,
            marks=marks,
            created_by=admin_id
        )
        
        db.session.add(new_question)
        db.session.commit()
        
        return jsonify({
            'id': new_question.id,
            'question_text': new_question.question_text,
            'option_1': new_question.option_1,
            'option_2': new_question.option_2,
            'option_3': new_question.option_3,
            'option_4': new_question.option_4,
            'correct_option': new_question.correct_option,
            'marks': new_question.marks
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"msg": f"Database error: {str(e)}"}), 500
    except Exception as e:
        print(f"Error creating question: {str(e)}")
        return jsonify({"msg": f"Error creating question: {str(e)}"}), 500

@admin_bp.route('/questions/<int:question_id>', methods=['PUT'])
@admin_required
def update_question(question_id):
    try:
        data = request.json
        question = Question.query.get_or_404(question_id)
        
        question.question_text = data.get('question_text', question.question_text)
        question.option_1 = data.get('option_1', question.option_1)
        question.option_2 = data.get('option_2', question.option_2)
        question.option_3 = data.get('option_3', question.option_3)
        question.option_4 = data.get('option_4', question.option_4)
        question.correct_option = data.get('correct_option', question.correct_option)
        question.marks = data.get('marks', question.marks)
        
        db.session.commit()
        
        return jsonify({
            'id': question.id,
            'question_text': question.question_text,
            'option_1': question.option_1,
            'option_2': question.option_2,
            'option_3': question.option_3,
            'option_4': question.option_4,
            'correct_option': question.correct_option,
            'marks': question.marks
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"msg": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"msg": f"Error updating question: {str(e)}"}), 500

@admin_bp.route('/questions/<int:question_id>', methods=['DELETE'])
@admin_required
def delete_question(question_id):
    try:
        question = Question.query.get_or_404(question_id)
        
        db.session.delete(question)
        db.session.commit()
        
        return jsonify({"msg": "Question deleted successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"msg": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"msg": f"Error deleting question: {str(e)}"}), 500

# Dashboard Statistics
@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard_stats():
    try:
        # Get counts for dashboard stats
        users_count = User.query.count()
        subjects_count = Subject.query.filter_by(is_active=True).count()
        quizzes_count = Quiz.query.filter_by(is_active=True).count()
        questions_count = Question.query.count()
        
        return jsonify({
            'users_count': users_count,
            'subjects_count': subjects_count,
            'quizzes_count': quizzes_count,
            'questions_count': questions_count
        })  # FIXED: Added return
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

# Debugging endpoint to check JWT token
@admin_bp.route('/debug-token', methods=['GET'])
@jwt_required()
def debug_token():
    current_user_id = get_jwt_identity()
    
    # Get admin info if exists
    admin = None
    try:
        admin_id = int(current_user_id)
        admin = Admin.query.get(admin_id)
    except (ValueError, TypeError):
        pass
        
    return jsonify({
        "msg": "Token decoded successfully",
        "identity": current_user_id,
        "admin_exists": admin is not None
    }), 200