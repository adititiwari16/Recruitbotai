import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Enable CORS
CORS(app)

# Database setup
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Configure the database
database_url = os.environ.get("DATABASE_URL")
# Fix for SQLAlchemy URL format if coming from Supabase
if database_url and database_url.startswith("https://"):
    database_url = database_url.replace("https://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db.init_app(app)

# Define database models
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

# Create all database tables
with app.app_context():
    db.create_all()

# API Routes
@app.route('/api/users/register', methods=['POST'])
def register_user():
    """Register a new user or update existing user."""
    try:
        data = request.json
        
        # Validate required fields
        if not all(key in data for key in ['name', 'email']):
            return jsonify({"error": "Name and email are required"}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        
        if existing_user:
            # Update existing user
            existing_user.name = data.get('name', existing_user.name)
            existing_user.age = data.get('age', existing_user.age)
            existing_user.experience = data.get('experience', existing_user.experience)
            existing_user.job_title = data.get('job_title', existing_user.job_title)
            
            db.session.commit()
            
            return jsonify({
                "message": "User updated successfully",
                "user": existing_user.to_dict()
            }), 200
        else:
            # Create new user
            new_user = User(
                name=data['name'],
                email=data['email'],
                age=data.get('age'),
                experience=data.get('experience'),
                job_title=data.get('job_title')
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            return jsonify({
                "message": "User registered successfully",
                "user": new_user.to_dict()
            }), 201
            
    except Exception as e:
        logger.error(f"Error in register_user: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/query/ask', methods=['POST'])
def ask_question():
    """
    Process a query and return AI-generated response in markdown format.
    
    Expected request body:
    {
        "query": "Your question here",
        "context": "Optional additional context",
        "format": "markdown" // optional, defaults to markdown
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        # Validate required fields
        if 'query' not in data:
            return jsonify({"error": "Query is required"}), 400
        
        query = data.get('query', '')
        context = data.get('context', '')
        response_format = data.get('format', 'markdown')
        
        # Log the incoming query
        logger.info(f"Processing query: {query}")
        
        # Generate a sample markdown response for demonstration
        # In a real application, you would use an AI model here
        response_text = generate_sample_response(query, context)
        
        # Return the response
        return jsonify({
            "response": response_text,
            "format": response_format
        }), 200
        
    except Exception as e:
        logger.error(f"Error in ask_question: {str(e)}")
        return jsonify({"error": str(e)}), 500

def generate_sample_response(query, context=""):
    """Generate a sample markdown response for demonstration purposes."""
    
    # Normalize the query by removing special characters and converting to lowercase
    normalized_query = query.lower().strip()
    
    # Check for interview questions
    if "interview" in normalized_query and "question" in normalized_query:
        return """# Common Interview Questions and Answers

## Technical Questions

### 1. Tell me about yourself
This is often the opening question in an interview and is one of the most important. Keep your answer to under 2 minutes and focus on your professional background, key achievements, and why you're interested in this role.

**Sample Answer Structure:**
- Brief introduction about your educational background
- Overview of your relevant work experience
- Key achievements that relate to the role
- Why you're excited about this opportunity

### 2. What are your strengths?
Focus on 2-3 strengths that are relevant to the position, and provide specific examples that demonstrate these strengths.

### 3. What are your weaknesses?
Choose a genuine weakness, but focus on the steps you're taking to improve in this area.

## Behavioral Questions

### 1. Describe a challenging situation and how you handled it
Use the STAR method (Situation, Task, Action, Result) to structure your answer.

### 2. Tell me about a time you worked effectively in a team
Highlight your collaboration skills, ability to resolve conflicts, and contributions to team success.

## Job-Specific Questions

The interviewer will likely ask questions specific to the role you're applying for. Research the company and role thoroughly to prepare for these questions.

## Questions to Ask the Interviewer

Prepare thoughtful questions to ask at the end of the interview, such as:
- What does success look like in this role?
- Can you describe the team culture?
- What are the biggest challenges facing the team/department right now?

Remember to stay authentic and provide specific examples from your experience whenever possible.
"""
    
    # Check for preparation tips
    elif "prepare" in normalized_query or "preparation" in normalized_query:
        return """# Interview Preparation Guide

## Before the Interview

### Research the Company
- Study the company's website, mission, values, products/services
- Research recent news, press releases, and achievements
- Understand their industry position and competitors
- Review their social media presence

### Understand the Role
- Analyze the job description thoroughly
- Identify key skills and experiences they're looking for
- Prepare examples that demonstrate these skills
- Research typical salary ranges for the position

### Practice Common Questions
- Prepare answers for standard questions like "Tell me about yourself"
- Practice behavioral questions using the STAR method
- Prepare examples that showcase your achievements
- Have questions ready to ask the interviewer

## Day of the Interview

### Presentation
- Dress appropriately for the company culture (when in doubt, dress more formally)
- Arrive 10-15 minutes early
- Bring copies of your resume, a notepad, and pen
- Turn off your phone before entering

### During the Interview
- Make a strong first impression with a firm handshake and smile
- Maintain good posture and eye contact
- Listen actively and take brief notes if necessary
- Be concise but thorough in your answers

## After the Interview

- Send a thank-you email within 24 hours
- Express appreciation for their time
- Reiterate your interest in the position
- Reference a specific topic discussed during the interview

Remember that preparation is key to interview success!
"""
    
    # Default response for other queries
    else:
        return f"""# Response to Your Query: "{query}"

Thank you for your question. As an AI assistant specializing in recruitment and interview preparation, I'd be happy to help you with this.

## Understanding Your Query

You've asked about: **{query}**{f" in the context of {context}" if context else ""}

## Response

This is a sample markdown response that would be generated by an AI model like GPT-3.5 or Llama. In a real implementation, this response would be dynamically generated based on your specific query using natural language processing.

## Key Points to Consider

1. **Preparation is key**: Research the company and role thoroughly
2. **Practice makes perfect**: Rehearse your answers to common questions
3. **Be authentic**: Interviewers appreciate genuine responses
4. **Ask questions**: Show your interest by asking thoughtful questions

## Next Steps

Would you like more specific information about any aspect of the interview process? Please feel free to ask more detailed questions.

---

*This response was generated to demonstrate the markdown formatting capabilities. In a production environment, this would be replaced with an actual AI-generated response tailored to your query.*
"""

# Run the application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)