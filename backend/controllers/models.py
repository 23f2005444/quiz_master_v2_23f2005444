from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from controllers.extensions import db
from datetime import datetime, timedelta
import random

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    is_active = db.Column(db.Boolean, default=True)

    # Use string reference for forward declaration
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade='all, delete-orphan')
    creator = db.relationship('Admin', backref='created_subjects')

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    sequence_number = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    is_active = db.Column(db.Boolean, default=True)

    # Use string reference for forward declaration
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade='all, delete-orphan')
    creator = db.relationship('Admin', backref='created_chapters')

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Enhanced scheduling fields
    start_date = db.Column(db.Date, nullable=False)  # Quiz available from this date
    start_time = db.Column(db.Time, nullable=False)  # Quiz available from this time
    end_date = db.Column(db.Date, nullable=True)     # Quiz expires on this date (optional)
    end_time = db.Column(db.Time, nullable=True)     # Quiz expires at this time (optional)
    
    time_duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    passing_score = db.Column(db.Integer, nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)
    
    # Auto-lock settings
    auto_lock_after_expiry = db.Column(db.Boolean, default=True)
    is_locked = db.Column(db.Boolean, default=False)  # Manual lock override
    
    created_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    is_active = db.Column(db.Boolean, default=True)

    # Use string references for forward declarations
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    creator = db.relationship('Admin', backref='created_quizzes')
    attempts = db.relationship('QuizAttempt', backref='quiz', cascade='all, delete-orphan')
    scores = db.relationship('Score', backref='quiz', cascade='all, delete-orphan')
    
    def is_available(self):
        """Check if quiz is currently available for attempts"""
        if not self.is_active or self.is_locked:
            return False
            
        now = datetime.now()
        
        # Check start time
        start_datetime = datetime.combine(self.start_date, self.start_time)
        if now < start_datetime:
            return False
            
        # Check end time if set
        if self.end_date and self.end_time:
            end_datetime = datetime.combine(self.end_date, self.end_time)
            if now > end_datetime:
                return False
                
        return True
    
    def time_until_start(self):
        """Get time until quiz becomes available"""
        now = datetime.now()
        start_datetime = datetime.combine(self.start_date, self.start_time)
        
        if now >= start_datetime:
            return None
            
        return start_datetime - now
    
    def time_until_end(self):
        """Get time until quiz expires"""
        if not self.end_date or not self.end_time:
            return None
            
        now = datetime.now()
        end_datetime = datetime.combine(self.end_date, self.end_time)
        
        if now >= end_datetime:
            return None
            
        return end_datetime - now

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_1 = db.Column(db.String(255), nullable=False)
    option_2 = db.Column(db.String(255), nullable=False)
    option_3 = db.Column(db.String(255), nullable=False)
    option_4 = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)
    marks = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    creator = db.relationship('Admin', backref='created_questions')
    # Use string reference for forward declaration
    responses = db.relationship('QuizResponse', backref='question', cascade='all, delete-orphan')

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=db.func.now())

    user = db.relationship('User', backref='scores', lazy=True)

class QuizAttempt(db.Model):
    """Model for storing quiz attempts by users"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    
    # Quiz scores
    score = db.Column(db.Integer, nullable=True)  # Null until attempt is submitted
    total_marks = db.Column(db.Integer, nullable=True)  # Null until attempt is submitted
    score_percentage = db.Column(db.Float, nullable=True)  # Null until attempt is submitted
    
    # Timing information
    start_time = db.Column(db.DateTime, nullable=False, default=db.func.now())
    end_time = db.Column(db.DateTime, nullable=True)  # Null until attempt is submitted
    time_taken = db.Column(db.Integer, nullable=True)  # Minutes taken, null until submitted
    
    # Status of the attempt
    status = db.Column(db.String(20), nullable=False, default='in_progress')  # 'in_progress', 'completed', 'expired'
    is_passed = db.Column(db.Boolean, nullable=True)  # Null until attempt is submitted
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    # Relationships with cascade delete
    user = db.relationship('User', backref='quiz_attempts')
    responses = db.relationship('QuizResponse', backref='attempt', cascade='all, delete-orphan')

class QuizResponse(db.Model):
    """Model for storing individual question responses in a quiz attempt"""
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempt.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_option = db.Column(db.Integer, nullable=True)  # Can be null if not answered
    is_correct = db.Column(db.Boolean, nullable=True)  # Null until attempt is submitted
    score = db.Column(db.Integer, nullable=True)  # Changed from marks_obtained to score
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())