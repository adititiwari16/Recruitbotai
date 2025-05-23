from backend.app import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=True)
    experience = db.Column(db.Integer, nullable=True)
    job_title = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with interviews
    interviews = db.relationship('Interview', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'age': self.age,
            'experience': self.experience,
            'job_title': self.job_title,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Interview(db.Model):
    __tablename__ = 'interviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(120), nullable=False)
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
            'role': self.role,
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
    text = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    answer = db.Column(db.Text, nullable=True)
    score = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Question {self.id} for Interview {self.interview_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'interview_id': self.interview_id,
            'text': self.text,
            'order': self.order,
            'answer': self.answer,
            'score': self.score,
            'feedback': self.feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
