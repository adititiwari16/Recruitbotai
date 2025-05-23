import os
import json
import logging
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from models import db, User, Interview, Question

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
}
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Enable CORS for frontend compatibility
CORS(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize database
db.init_app(app)

# Define the interviewer prompt
interviewer_prompt = """
You are a **strict technical interviewer**. Your sole responsibility is to assess the candidate's technical competency across the following subjects:

- Data Structures & Algorithms (DSA)
- Data Communication & Computer Networks (DCCN)
- Object-Oriented Programming (OOPs)
- Operating Systems (OS)
- Coding (subjective problems similar to those on platforms like LeetCode)

**Assessment Format:**
- Conduct a total of 10 questions, distributed across the topics listed.
- Assessment should be dynamic with 3 modules -> 5 MCQs, 3 Concept based, 2 Coding problems.
- Each question should be followed by a **brief pause** to allow the candidate to think.

**Core Rules:**
- Do **not** reveal if an answer is correct or incorrect during the interview.
- **No explanations, no teaching, no guiding.** You are here to assess silently, not to assist.
- **Never repeat questions.** Once a question is asked, move on.
- Keep your tone **professional, concise, and assertive**.
- If the candidate asks for feedback, respond with: "All feedback will be provided at the end of the assessment."
- **Challenge the candidate.** Dynamically increase question complexity based on their responses and perceived experience level.

**Assessment Focus:**
1. **DSA**:
   - Ask about time and space complexity.
   - Test understanding of edge cases and trade-offs.
   - Prioritize fundamental algorithms (Binary Search, Sorting, Graphs, Trees, etc.).

2. **OOPs**:
   - Focus on core principles: inheritance, polymorphism, abstraction, encapsulation.
   - Ask for real-world analogies or code-based reasoning if needed.

3. **DCCN**:
   - Ask about OSI vs TCP/IP models, protocols (TCP, UDP, IP, HTTP, etc.), and concepts like latency, throughput, congestion.

4. **Operating Systems**:
   - Evaluate understanding of process/thread management, scheduling algorithms, memory management, deadlocks, and synchronization.

5. **Coding**:
   - Present real coding problems.
   - Ask for time/space analysis, approach justification, and edge case handling.
   - Match difficulty to experience level. Do not make it easy without justification.

**General Behavior:**
- Do not validate or critique any answers mid-assessment. Stay neutral and move to the next question.
- Keep transitions minimal and maintain control of the assessment flow.
- If the candidate is underperforming, **tighten the evaluation** — do not lower the bar.

**End of Interview:**
- After all 10 questions are complete, generate a **summary report** indicating:
   - Subject-wise performance
   - Strengths and weaknesses
   - Final recommendation: Pass / Borderline / Fail

Stick to your role. You are a gatekeeper of technical quality — serious, silent, and focused.
"""

# Define job roles
JOB_ROLES = {
    'sde': 'Software Development Engineer',
    'frontend': 'Frontend Developer',
    'backend': 'Backend Developer',
    'fullstack': 'Full Stack Developer',
    'devops': 'DevOps Engineer'
}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Role-based access control decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'recruiter':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'recruiter':
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('profile'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('register.html')
            
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already registered.', 'danger')
            return render_template('register.html')
            
        # Create new user
        new_user = User(email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html')
            
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return render_template('login.html')
            
        # Login user
        login_user(user)
        
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            if user.role == 'recruiter':
                next_page = url_for('dashboard')
            else:
                next_page = url_for('profile')
                
        return redirect(next_page)
        
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.role == 'recruiter':
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        experience = request.form.get('experience')
        
        if not name or not age or not experience:
            flash('All fields are required.', 'danger')
            return render_template('profile.html')
            
        # Update user profile
        current_user.name = name
        current_user.age = int(age)
        current_user.experience = int(experience)
        
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('interview_setup'))
        
    return render_template('profile.html', user=current_user)

@app.route('/interview/setup', methods=['GET', 'POST'])
@login_required
def interview_setup():
    if current_user.role == 'recruiter':
        return redirect(url_for('dashboard'))
        
    # Check if user has completed profile
    if not current_user.name or not current_user.age or current_user.experience is None:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('profile'))
        
    if request.method == 'POST':
        job_role = request.form.get('job_role')
        
        if not job_role or job_role not in JOB_ROLES:
            flash('Please select a valid job role.', 'danger')
            return render_template('interview_setup.html', job_roles=JOB_ROLES)
            
        # Create new interview
        interview = Interview(
            user_id=current_user.id,
            job_role=JOB_ROLES[job_role],
            status='in_progress'
        )
        
        db.session.add(interview)
        db.session.commit()
        
        return redirect(url_for('interview_session', interview_id=interview.id))
        
    return render_template('interview_setup.html', job_roles=JOB_ROLES)

@app.route('/interview/<int:interview_id>', methods=['GET'])
@login_required
def interview_session(interview_id):
    interview = Interview.query.get_or_404(interview_id)
    
    # Security check
    if interview.user_id != current_user.id and current_user.role != 'recruiter':
        flash('You do not have permission to access this interview.', 'danger')
        return redirect(url_for('index'))
        
    return render_template('interview.html', interview=interview)

@app.route('/api/interviews/<int:interview_id>/chat', methods=['POST'])
@login_required
def interview_chat(interview_id):
    interview = Interview.query.get_or_404(interview_id)
    
    # Security check
    if interview.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    # Get message from request
    data = request.json
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
        
    user_message = data['message']
    
    # Process the message and generate a response
    # This is where you would integrate with an LLM like OpenAI
    # For now, we'll use a simple response system
    
    # Sample response for demonstration
    response = generate_interview_response(interview, user_message)
    
    return jsonify({
        'response': response
    })

@app.route('/api/interviews/<int:interview_id>/complete', methods=['POST'])
@login_required
def complete_interview(interview_id):
    interview = Interview.query.get_or_404(interview_id)
    
    # Security check
    if interview.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    # Update interview status
    interview.status = 'completed'
    interview.completed_at = datetime.utcnow()
    
    # Generate evaluation (this would use the LLM in production)
    evaluation = generate_evaluation_report(interview)
    interview.evaluation_report = evaluation['report']
    interview.summary = evaluation['summary']
    interview.result = evaluation['result']
    interview.score = evaluation['score']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'redirect': url_for('interview_result', interview_id=interview.id)
    })

@app.route('/interview/<int:interview_id>/result', methods=['GET'])
@login_required
def interview_result(interview_id):
    interview = Interview.query.get_or_404(interview_id)
    
    # Security check
    if interview.user_id != current_user.id and current_user.role != 'recruiter':
        flash('You do not have permission to access this interview.', 'danger')
        return redirect(url_for('index'))
        
    if interview.status != 'completed':
        flash('This interview has not been completed yet.', 'warning')
        return redirect(url_for('interview_session', interview_id=interview.id))
        
    return render_template('result.html', interview=interview)

@app.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get all interviews for the dashboard
    interviews = Interview.query.order_by(Interview.created_at.desc()).all()
    
    return render_template('dashboard.html', interviews=interviews)

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
        response_text = generate_sample_response(query, context)
        
        # Return the response
        return jsonify({
            "response": response_text,
            "format": response_format
        }), 200
        
    except Exception as e:
        logger.error(f"Error in ask_question: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Helper functions
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

def generate_interview_response(interview, user_message):
    """Generate a response for the interview chatbot."""
    # This would be connected to an LLM in production
    
    # For demo, we'll use predefined questions
    questions = [
        "Explain the difference between a stack and a queue. What are their time complexities for basic operations?",
        "What is the time complexity of binary search? Describe how it works.",
        "Explain the concept of inheritance in OOP. Provide an example.",
        "What is polymorphism? How is it implemented in your preferred programming language?",
        "Describe the TCP/IP model and its layers.",
        "Explain the difference between TCP and UDP.",
        "What is a deadlock in an operating system? How can it be prevented?",
        "Explain the concept of virtual memory.",
        "Write a function to determine if a string has all unique characters.",
        "Implement a solution to find the nth Fibonacci number using dynamic programming."
    ]
    
    # Get existing questions for this interview
    existing_questions = Question.query.filter_by(interview_id=interview.id).count()
    
    if existing_questions < len(questions):
        # Create a new question
        new_question = Question(
            interview_id=interview.id,
            text=questions[existing_questions],
            category="Technical",
            type=["mcq", "concept", "coding"][min(existing_questions // 4, 2)],
            order=existing_questions + 1
        )
        
        db.session.add(new_question)
        db.session.commit()
        
        return new_question.text
    else:
        # Interview is complete
        return "Thank you for completing all the questions. I'll now generate your evaluation report. Please click the 'Complete Interview' button to see your results."

def generate_evaluation_report(interview):
    """Generate an evaluation report for the completed interview."""
    # In production, this would use an LLM to evaluate the answers
    
    # For demo, we'll use a random score
    import random
    score = random.uniform(0.4, 0.95)
    
    # Determine result based on score
    if score >= 0.7:
        result = "pass"
    elif score >= 0.5:
        result = "borderline"
    else:
        result = "fail"
    
    # Generate a report
    report = f"""# Technical Interview Evaluation

## Candidate Information
- **Name**: {User.query.get(interview.user_id).name}
- **Experience**: {User.query.get(interview.user_id).experience} years
- **Position Applied**: {interview.job_role}
- **Date**: {interview.created_at.strftime('%Y-%m-%d')}

## Assessment Summary
- **Overall Score**: {score*100:.1f}%
- **Result**: {"PASS" if result == "pass" else "BORDERLINE" if result == "borderline" else "FAIL"}

## Performance by Area
- **Data Structures & Algorithms**: {"Strong" if score > 0.7 else "Average" if score > 0.5 else "Needs Improvement"}
- **Object-Oriented Programming**: {"Strong" if score > 0.7 else "Average" if score > 0.5 else "Needs Improvement"}
- **Networking & Protocols**: {"Strong" if score > 0.7 else "Average" if score > 0.5 else "Needs Improvement"}
- **Operating Systems**: {"Strong" if score > 0.7 else "Average" if score > 0.5 else "Needs Improvement"}
- **Coding Skills**: {"Strong" if score > 0.7 else "Average" if score > 0.5 else "Needs Improvement"}

## Strengths
- {"Strong understanding of core algorithms and data structures" if score > 0.6 else "Demonstrated basic knowledge of algorithms"}
- {"Excellent problem-solving approach" if score > 0.7 else "Reasonable problem-solving abilities"}
- {"Good coding practices" if score > 0.6 else "Basic coding competence"}

## Areas for Improvement
- {"Could improve on time and space complexity analysis" if score < 0.8 else "Minor improvements in efficiency considerations"}
- {"Should strengthen understanding of " + ["operating systems", "network protocols", "OOP principles"][random.randint(0, 2)]}
- {"Work on more complex coding challenges" if score < 0.9 else "Practice edge cases in coding problems"}

## Recommendation
{
"The candidate demonstrated strong technical knowledge and problem-solving abilities. Recommended for the next round." if result == "pass" else
"The candidate shows potential but has some gaps in knowledge. Consider for a lower-level position or provide a chance to reapply after additional preparation." if result == "borderline" else
"The candidate does not meet the technical requirements for this position at this time. Suggest gaining more experience before reapplying."
}

*This evaluation is based on a standardized technical assessment.*
"""
    
    # Generate a shorter summary
    summary = f"""## Assessment Summary
- **Score**: {score*100:.1f}%
- **Result**: {"PASS" if result == "pass" else "BORDERLINE" if result == "borderline" else "FAIL"}
- **Strengths**: {"Strong in algorithms and problem-solving" if score > 0.7 else "Basic technical competence"}
- **Areas for Improvement**: {"Minor efficiency considerations" if score > 0.8 else "Fundamental knowledge gaps in key areas"}
"""
    
    return {
        'report': report,
        'summary': summary,
        'result': result,
        'score': score * 100
    }

# Create all tables
with app.app_context():
    db.create_all()
    
    # Create a recruiter user if none exists
    recruiter = User.query.filter_by(role='recruiter').first()
    if not recruiter:
        recruiter = User(
            email='recruiter@example.com',
            role='recruiter',
            name='Admin Recruiter'
        )
        recruiter.set_password('admin123')
        db.session.add(recruiter)
        db.session.commit()
        logger.info("Created recruiter user")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)