from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='candidate')  # 'candidate' or 'recruiter'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User profile data
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    experience = db.Column(db.Integer)  # Experience in years
    
    # Relationships
    interviews = db.relationship('Interview', backref='candidate', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'age': self.age,
            'experience': self.experience,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


class Interview(db.Model):
    __tablename__ = 'interviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_profile_id = db.Column(db.Integer, db.ForeignKey('job_profiles.id'), nullable=False)
    experience_level = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    feedback = db.Column(db.Text, nullable=True)
    report = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship with questions
    questions = db.relationship('Question', backref='interview', lazy=True)
    
    def __repr__(self):
        return f'<Interview {self.id} for User {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_profile': self.job_profile.to_dict() if self.job_profile else None,
            'experience_level': self.experience_level,
            'score': self.score,
            'status': self.status,
            'feedback': self.feedback,
            'report': self.report,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interviews.id'), nullable=False)
    
    # Question details
    text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))  # e.g., "DSA", "OOP", etc.
    type = db.Column(db.String(20))  # 'mcq', 'concept', 'coding'
    
    # Response and evaluation
    answer = db.Column(db.Text)
    score = db.Column(db.Float)  # Score for this question
    feedback = db.Column(db.Text)  # Feedback on the answer
    
    # Order in the interview
    order = db.Column(db.Integer)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    answered_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'interview_id': self.interview_id,
            'text': self.text,
            'category': self.category,
            'type': self.type,
            'answer': self.answer,
            'score': self.score,
            'feedback': self.feedback,
            'order': self.order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'answered_at': self.answered_at.isoformat() if self.answered_at else None
        }
    
    def __repr__(self):
        return f'<Question {self.id} for Interview {self.interview_id}>'


class JobProfile(db.Model):
    __tablename__ = 'job_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    evaluation_criteria = db.Column(db.JSON, nullable=False)  # Stores evaluation parameters
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with interviews
    interviews = db.relationship('Interview', backref='job_profile', lazy=True)
    
    def __repr__(self):
        return f'<JobProfile {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'evaluation_criteria': self.evaluation_criteria,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }