import os
import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv
import re

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from models import db, User, Interview, Question, JobProfile
from backend.ollama_client import get_ollama_client
from backend.utils import evaluate_answer

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the app
app = Flask(__name__)

# Use DATABASE_URL from .env for Supabase Postgres
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
}
app.secret_key = os.getenv("SESSION_SECRET", "dev-secret-key")
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
        role = request.form.get('role')
        
        if not email or not password or not role:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
            
        # Validate role
        if role not in ['candidate', 'recruiter']:
            flash('Invalid role selected.', 'danger')
            return render_template('register.html')
            
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already registered.', 'danger')
            return render_template('register.html')
            
        # Create new user with specified role
        new_user = User(
            email=email,
            role=role,
            name=email.split('@')[0]  # Set initial name from email
        )
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
    # Check if user is a candidate
    if current_user.role != 'candidate':
        flash('Only candidates can access the interview setup page.', 'error')
        return redirect(url_for('dashboard'))
        
    # Check if user has completed profile
    if not current_user.name or not current_user.age or current_user.experience is None:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('profile'))
        
    if request.method == 'POST':
        job_profile_id = request.form.get('job_profile_id')
        
        if not job_profile_id:
            flash('Please select a job profile.', 'danger')
            return redirect(url_for('interview_setup'))
            
        # Get the job profile
        job_profile = JobProfile.query.get(job_profile_id)
        if not job_profile or not job_profile.is_active:
            flash('Selected job profile is not available.', 'danger')
            return redirect(url_for('interview_setup'))
            
        # Create new interview
        interview = Interview(
            user_id=current_user.id,
            job_profile_id=job_profile.id,
            experience_level='mid',
            status='in_progress'
        )
        
        db.session.add(interview)
        db.session.commit()
        
        return redirect(url_for('interview_session', interview_id=interview.id))
        
    # Get all active job profiles
    job_profiles = JobProfile.query.filter_by(is_active=True).order_by(JobProfile.title).all()
    return render_template('interview_setup.html', job_profiles=job_profiles)

@app.route('/interview/<int:interview_id>', methods=['GET'])
@login_required
def interview_session(interview_id):
    interview = Interview.query.get_or_404(interview_id)
    
    # Security check - allow both the candidate and recruiters to access
    if interview.user_id != current_user.id and current_user.role != 'recruiter':
        flash('You do not have permission to access this interview.', 'danger')
        return redirect(url_for('index'))
        
    return render_template('interview.html', interview=interview)

@app.route('/api/interviews/<int:interview_id>/chat', methods=['POST'])
@login_required
def interview_chat(interview_id):
    interview = Interview.query.get_or_404(interview_id)
    
    # Security check - allow both the candidate and recruiters to access
    if interview.user_id != current_user.id and current_user.role != 'recruiter':
        return jsonify({'error': 'Unauthorized'}), 403
        
    # Get message from request
    data = request.json
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
        
    user_message = data['message']
    
    # Find the question with the highest order for this interview that doesn't have an answer yet
    # This assumes the user is answering questions in sequential order.
    question_to_answer = Question.query.filter_by(interview_id=interview.id, answer=None).order_by(Question.order.desc()).first()

    if question_to_answer:
        question_to_answer.answer = user_message
        question_to_answer.answered_at = datetime.utcnow()

        # Get user details for evaluation context
        user = User.query.get(interview.user_id)

        # Evaluate the answer using the imported function
        # Ensure job_profile relationship is loaded or accessed correctly
        job_profile_title = interview.job_profile.title if interview.job_profile else ''

        evaluation = evaluate_answer(
            question=question_to_answer.text,
            answer=user_message,
            role=job_profile_title, # Use job profile title as role for evaluation context
            experience=user.experience or 'mid' # Use user experience or default to 'mid'
        )

        # Update question with score and feedback from evaluation
        if isinstance(evaluation, dict) and "error" not in evaluation:
            # evaluate_answer in backend.utils returns a score out of 10
            question_to_answer.score = evaluation.get('score', 0)
            question_to_answer.feedback = json.dumps(evaluation) # Store full evaluation feedback as JSON
        else:
            # Log error if evaluation failed and set default score/feedback
            logger.error(f"Failed to evaluate answer for question {question_to_answer.id}: {evaluation.get('error', 'Unknown error')}")
            question_to_answer.score = 0
            question_to_answer.feedback = json.dumps({'error': 'Evaluation failed'})

        db.session.commit()
        logger.debug(f"Successfully saved answer and evaluation for Question ID: {question_to_answer.id}, Score: {question_to_answer.score}")

    # Now, generate the AI's response (which is either the next question or a completion message)
    # This should happen regardless of whether an answer was saved/evaluated, to keep the chat flow going.
    response = generate_interview_response(interview, user_message)

    # If generate_interview_response created a new question, commit that change as well
    # (though generate_interview_response already commits, being explicit here doesn't hurt)
    db.session.commit()

    return jsonify({
        'response': response
    })

@app.route('/api/interviews/<int:interview_id>/complete', methods=['POST'])
@login_required
def complete_interview(interview_id):
    interview = Interview.query.get_or_404(interview_id)
    
    # Security check - only allow the candidate to complete their own interview
    if interview.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    # Update interview status
    interview.status = 'completed'
    interview.completed_at = datetime.utcnow()
    
    # Generate evaluation
    evaluation = generate_evaluation_report(interview)
    interview.report = evaluation['report']
    interview.feedback = evaluation['summary']
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
    
    # Security check - allow both the candidate and recruiters to view results
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

@app.route('/dashboard/job-profiles', methods=['GET'])
@login_required
@admin_required
def job_profiles():
    """View and manage job profiles."""
    profiles = JobProfile.query.order_by(JobProfile.title).all()
    return render_template('job_profiles.html', profiles=profiles)

@app.route('/dashboard/job-profiles/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_job_profile():
    """Add a new job profile."""
    if request.method == 'POST':
        try:
            data = request.form
            
            # Create new job profile
            profile = JobProfile(
                title=data['title'],
                description=data['description'],
                evaluation_criteria={
                    'technical_skills': data.getlist('technical_skills'),
                    'soft_skills': data.getlist('soft_skills'),
                    'experience_requirements': data.get('experience_requirements'),
                    'evaluation_focus': data.get('evaluation_focus'),
                    'custom_prompt': data.get('custom_prompt')
                }
            )
            
            db.session.add(profile)
            db.session.commit()
            
            flash('Job profile added successfully!', 'success')
            return redirect(url_for('job_profiles'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding job profile: {str(e)}', 'danger')
            
    return render_template('add_job_profile.html')

@app.route('/dashboard/job-profiles/<int:profile_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_job_profile(profile_id):
    """Edit an existing job profile."""
    profile = JobProfile.query.get_or_404(profile_id)
    
    if request.method == 'POST':
        try:
            data = request.form
            
            # Update profile
            profile.title = data['title']
            profile.description = data['description']
            profile.evaluation_criteria = {
                'technical_skills': data.getlist('technical_skills'),
                'soft_skills': data.getlist('soft_skills'),
                'experience_requirements': data.get('experience_requirements'),
                'evaluation_focus': data.get('evaluation_focus'),
                'custom_prompt': data.get('custom_prompt')
            }
            
            db.session.commit()
            
            flash('Job profile updated successfully!', 'success')
            return redirect(url_for('job_profiles'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating job profile: {str(e)}', 'danger')
            
    return render_template('edit_job_profile.html', profile=profile)

@app.route('/dashboard/job-profiles/<int:profile_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_job_profile(profile_id):
    """Delete a job profile."""
    profile = JobProfile.query.get_or_404(profile_id)
    
    try:
        db.session.delete(profile)
        db.session.commit()
        flash('Job profile deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting job profile: {str(e)}', 'danger')
        
    return redirect(url_for('job_profiles'))

@app.route('/dashboard/job-profiles/<int:profile_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_job_profile(profile_id):
    """Toggle job profile active status."""
    profile = JobProfile.query.get_or_404(profile_id)
    
    try:
        profile.is_active = not profile.is_active
        db.session.commit()
        status = 'activated' if profile.is_active else 'deactivated'
        flash(f'Job profile {status} successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating job profile status: {str(e)}', 'danger')
        
    return redirect(url_for('job_profiles'))

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
    """Generate a response for the interview chatbot using Ollama."""
    try:
        # Get the job profile
        job_profile = JobProfile.query.get(interview.job_profile_id)
        if not job_profile:
            return "Error: Job profile not found."

        # Get existing questions for this interview
        existing_questions = Question.query.filter_by(interview_id=interview.id).count()

        # If we haven't asked any questions yet, generate the first question
        if existing_questions == 0:
            # Get user details for context
            user = User.query.get(interview.user_id)

            # Prepare the prompt for the first question
            prompt = f"""You are a technical interviewer conducting an interview for a {job_profile.title} position.
            The candidate has {user.experience} years of experience.
            
            Job Profile Details:
            - Description: {job_profile.description}
            - Technical Skills Required: {', '.join(job_profile.evaluation_criteria['technical_skills'])}
            - Soft Skills Required: {', '.join(job_profile.evaluation_criteria['soft_skills'])}
            - Experience Requirements: {job_profile.evaluation_criteria['experience_requirements']}
            - Evaluation Focus: {job_profile.evaluation_criteria['evaluation_focus']}
            
            Custom Evaluation Instructions:
            {job_profile.evaluation_criteria['custom_prompt']}
            
            Generate a technical question that is appropriate for their experience level.
            The question should be challenging but fair.
            Focus on the technical skills required for this position.
            Return ONLY the question text, nothing else."""

            # Get response from Ollama
            ollama = get_ollama_client()
            result = ollama.generate_response(prompt)

            if not result["success"]:
                return "I apologize, but I'm having trouble generating questions at the moment. Please try again."

            # Create a new question
            new_question = Question(
                interview_id=interview.id,
                text=result["response"].strip(),
                category="Technical",
                type="concept",
                order=1
            )

            db.session.add(new_question)
            db.session.commit()

            return new_question.text

        # If we have questions, evaluate the user's response and generate next question
        elif existing_questions < 10:  # Limit to 10 questions
            # Get the last question
            last_question = Question.query.filter_by(interview_id=interview.id).order_by(Question.order.desc()).first()

            # Save the user's answer to the last question
            if last_question:
                last_question.answer = user_message
                last_question.answered_at = datetime.utcnow()
                # Optionally, you could call an evaluation function here and save feedback/score per question
                db.session.commit()
                logger.debug(f"Saved answer for question {last_question.id} in generate_interview_response.")

            # Prepare the prompt for evaluation and next question
            prompt = f"""You are a technical interviewer evaluating a candidate for a {job_profile.title} position.

            Job Profile Details:
            - Description: {job_profile.description}
            - Technical Skills Required: {', '.join(job_profile.evaluation_criteria['technical_skills'])}
            - Soft Skills Required: {', '.join(job_profile.evaluation_criteria['soft_skills'])}
            - Experience Requirements: {job_profile.evaluation_criteria['experience_requirements']}
            - Evaluation Focus: {job_profile.evaluation_criteria['evaluation_focus']}

            Custom Evaluation Instructions:
            {job_profile.evaluation_criteria['custom_prompt']}

            The candidate just answered this question:
            "{last_question.text}"

            Their answer was: "{user_message}"

            Based on their answer and the job requirements, generate a follow-up technical question that:
            1. Is more challenging if they answered well
            2. Is at the same level if they answered partially
            3. Is slightly easier if they struggled
            4. Covers a different technical skill from the required skills list

            Return ONLY the question text, nothing else."""

            # Get response from Ollama
            ollama = get_ollama_client()
            result = ollama.generate_response(prompt)

            if not result["success"]:
                return "I apologize, but I'm having trouble generating questions at the moment. Please try again."

            # Create a new question
            new_question = Question(
                interview_id=interview.id,
                text=result["response"].strip(),
                category="Technical",
                type=["mcq", "concept", "coding"][min(existing_questions // 4, 2)],
                order=existing_questions + 1
            )

            db.session.add(new_question)
            db.session.commit()

            return new_question.text

        else: # Interview is complete
            return "Thank you for completing all the questions. I'll now generate your evaluation report. Please click the 'Complete Interview' button to see your results."

    except Exception as e:
        logger.error(f"Error in generate_interview_response: {str(e)}")
        return "I apologize, but I encountered an error. Please try again."

def generate_evaluation_report(interview):
    """Generate an evaluation report for the completed interview using Ollama."""
    try:
        # Get user details
        user = User.query.get(interview.user_id)
        if not user:
            logger.error(f"User not found for interview {interview.id}")
            return {
                'report': "Error: User not found.",
                'summary': "Error: User not found.",
                'result': "error",
                'score': 0
            }

        # Get the job profile
        job_profile = JobProfile.query.get(interview.job_profile_id)
        if not job_profile:
            logger.error(f"Job profile not found for interview {interview.id}")
            return {
                'report': "Error: Job profile not found.",
                'summary': "Error: Job profile not found.",
                'result': "error",
                'score': 0
            }

        # Get all questions and answers
        questions = Question.query.filter_by(interview_id=interview.id).order_by(Question.order).all()
        if not questions:
            logger.error(f"No questions found for interview {interview.id}")
            return {
                'report': "Error: No interview questions found.",
                'summary': "Error: No interview questions found.",
                'result': "error",
                'score': 0
            }

        # Prepare the prompt for evaluation
        questions_text = "\n".join([f"Q{i+1}: {q.text}\nA{i+1}: {q.answer or 'No answer provided'}\n" for i, q in enumerate(questions)])

        prompt = f"""You are a technical interviewer evaluating a candidate's performance.

Candidate Information:
- Name: {user.name}
- Experience: {user.experience} years
- Position: {job_profile.title}

Job Profile Requirements:
- Description: {job_profile.description}
- Technical Skills Required: {', '.join(job_profile.evaluation_criteria['technical_skills'])}
- Soft Skills Required: {', '.join(job_profile.evaluation_criteria['soft_skills'])}
- Experience Requirements: {job_profile.evaluation_criteria['experience_requirements']}
- Evaluation Focus: {job_profile.evaluation_criteria['evaluation_focus']}

Custom Evaluation Instructions:
{job_profile.evaluation_criteria['custom_prompt']}

Interview Questions and Answers:
{questions_text}

Based on the candidate's responses and the job requirements, generate a detailed evaluation report in markdown format that includes:
1. Overall assessment
2. Technical skills evaluation (based on required technical skills)
3. Soft skills evaluation (based on required soft skills)
4. Strengths and weaknesses
5. Final recommendation (Pass/Borderline/Fail)

Format the response in markdown with appropriate headers and sections."""

        # Get response from Ollama
        ollama = get_ollama_client()
        result = ollama.generate_response(prompt)

        if not result["success"]:
            error_msg = result.get("error", "Unknown error")
            logger.error(f"Failed to generate evaluation report: {error_msg}")
            return {
                'report': f"Error generating evaluation report: {error_msg}",
                'summary': f"Error generating evaluation report: {error_msg}",
                'result': "error",
                'score': 0
            }

        # Parse the response to extract score and result
        report_text = result["response"]

        # Calculate score based on answers
        answered = sum(1 for q in questions if q.answer and q.answer.strip())
        score = round((answered / len(questions)) * 100) if questions else 0

        # Set result based on score thresholds only
        if score >= 70:
            result_value = 'pass'
        elif score >= 50:
            result_value = 'borderline'
        else:
            result_value = 'fail'

        # Generate a shorter summary
        try:
            strengths = report_text.split("Strengths")[1].split("Areas for Improvement")[0] if "Strengths" in report_text else "Not specified"
            improvements = report_text.split("Areas for Improvement")[1].split("Recommendation")[0] if "Areas for Improvement" in report_text else "Not specified"
        except Exception as e:
            logger.error(f"Error parsing report sections: {str(e)}")
            strengths = "Not specified"
            improvements = "Not specified"

        summary = f"""## Assessment Summary\n- **Score**: {score}%\n- **Result**: {result_value.upper()}\n- **Strengths**: {strengths}\n- **Areas for Improvement**: {improvements}\n"""

        return {
            'report': report_text,
            'summary': summary,
            'result': result_value,  # This will be used for the UI badge
            'score': score
        }

    except Exception as e:
        logger.error(f"Error in generate_evaluation_report: {str(e)}")
        return {
            'report': f"Error generating evaluation report: {str(e)}",
            'summary': f"Error generating evaluation report: {str(e)}",
            'result': "error",
            'score': 0
        }

# Create all tables (do NOT drop tables in production)
with app.app_context():
    # db.drop_all()  # DO NOT DROP TABLES IN PRODUCTION
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
    app.run(debug=True, host='0.0.0.0', port=5001)