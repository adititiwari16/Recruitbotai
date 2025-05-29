import logging
import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from backend.app import db
from backend.models import User, Interview, Question
from backend.utils import generate_interview_questions, evaluate_answer, generate_final_report, format_markdown_report

# Initialize blueprint and logger
interview_bp = Blueprint('interview', __name__)
logger = logging.getLogger(__name__)

@interview_bp.route('/start', methods=['POST'])
def start_interview():
    """Start a new interview session."""
    try:
        data = request.json
        
        # Validate required fields
        if not all(key in data for key in ['user_id', 'role', 'experience_level']):
            return jsonify({"error": "User ID, role, and experience level are required"}), 400
        
        # Check if user exists
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Create new interview
        new_interview = Interview(
            user_id=data['user_id'],
            role=data['role'],
            experience_level=data['experience_level'],
            status='pending'
        )
        
        db.session.add(new_interview)
        db.session.flush()  # Get ID before committing
        
        # Generate questions for the interview
        questions_data = generate_interview_questions(
            role=data['role'],
            experience=user.experience or data['experience_level'],
            num_questions=5
        )
        
        if "error" in questions_data:
            return jsonify(questions_data), 500
        
        # Store questions
        for i, q_data in enumerate(questions_data):
            question = Question(
                interview_id=new_interview.id,
                text=q_data.get('question'),
                order=i+1
            )
            db.session.add(question)
        
        db.session.commit()
        
        # Fetch the created questions
        questions = Question.query.filter_by(interview_id=new_interview.id).order_by(Question.order).all()
        
        return jsonify({
            "message": "Interview started successfully",
            "interview": new_interview.to_dict(),
            "questions": [q.to_dict() for q in questions]
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Error in start_interview: {str(e)}")
        return jsonify({"error": str(e)}), 500

@interview_bp.route('/question/<int:question_id>/answer', methods=['POST'])
def submit_answer(question_id):
    """Submit an answer to a question and get evaluation."""
    try:
        data = request.json
        
        # Validate required fields
        if 'answer' not in data:
            return jsonify({"error": "Answer is required"}), 400
        
        # Get question
        question = Question.query.get(question_id)
        if not question:
            return jsonify({"error": "Question not found"}), 404
        
        # Get interview and user details
        interview = Interview.query.get(question.interview_id)
        user = User.query.get(interview.user_id)
        
        # Evaluate the answer
        evaluation = evaluate_answer(
            question=question.text,
            answer=data['answer'],
            role=interview.role,
            experience=user.experience or interview.experience_level
        )
        
        if "error" in evaluation:
            return jsonify(evaluation), 500
        
        # Update question with answer and evaluation
        question.answer = data['answer']
        question.score = evaluation.get('score', 0)
        question.feedback = json.dumps(evaluation)
        
        db.session.commit()
        
        return jsonify({
            "message": "Answer submitted and evaluated",
            "question": question.to_dict(),
            "evaluation": evaluation
        }), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Error in submit_answer: {str(e)}")
        return jsonify({"error": str(e)}), 500

@interview_bp.route('/<int:interview_id>/complete', methods=['POST'])
def complete_interview(interview_id):
    """Complete the interview and generate final report."""
    try:
        # Get interview
        interview = Interview.query.get(interview_id)
        if not interview:
            return jsonify({"error": "Interview not found"}), 404
        
        # Get user details
        user = User.query.get(interview.user_id)
        
        # Get questions and answers
        questions = Question.query.filter_by(interview_id=interview_id).order_by(Question.order).all()
        
        # Prepare responses for report generation
        responses = []
        total_score = 0
        
        for q in questions:
            if not q.answer:
                return jsonify({"error": f"Question {q.order} has not been answered yet"}), 400
                
            try:
                feedback = json.loads(q.feedback) if q.feedback else {}
            except:
                feedback = {}
                
            responses.append({
                "question": q.text,
                "answer": q.answer,
                "score": q.score or 0,
                "feedback": feedback
            })
            
            total_score += q.score or 0
        
        # Calculate average score
        avg_score = total_score / len(questions) if questions else 0
        normalized_score = min(100, avg_score * 10)  # Scale to 100
        
        # Set result based on score thresholds
        if normalized_score >= 70:
            result_value = 'pass'
        elif normalized_score >= 50:
            result_value = 'borderline'
        else:
            result_value = 'fail'
        
        # Generate final report
        report = generate_final_report(
            name=user.name,
            age=user.age,
            role=interview.role,
            experience=user.experience or interview.experience_level,
            responses=responses
        )
        
        if isinstance(report, dict) and "error" in report:
            return jsonify(report), 500
        
        # Update interview
        interview.score = normalized_score
        interview.status = 'completed'  # Always set to completed since we have a separate result field
        interview.result = result_value  # Set the result based on score thresholds
        interview.feedback = report
        interview.report = format_markdown_report(
            interview_data={
                'role': interview.role,
                'score': normalized_score,
                'status': interview.status,
                'result': result_value,  # Include result in the report data
                'feedback': report
            },
            user_data=user.to_dict(),
            questions_data=[q.to_dict() for q in questions]
        )
        interview.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "message": "Interview completed successfully",
            "interview": interview.to_dict(),
            "score": normalized_score,
            "status": interview.status,
            "result": result_value,
            "report": interview.report
        }), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Error in complete_interview: {str(e)}")
        return jsonify({"error": str(e)}), 500

@interview_bp.route('/<int:interview_id>', methods=['GET'])
def get_interview(interview_id):
    """Get interview details by ID."""
    try:
        interview = Interview.query.get(interview_id)
        
        if not interview:
            return jsonify({"error": "Interview not found"}), 404
            
        # Get questions
        questions = Question.query.filter_by(interview_id=interview_id).order_by(Question.order).all()
        
        return jsonify({
            "interview": interview.to_dict(),
            "questions": [q.to_dict() for q in questions]
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_interview: {str(e)}")
        return jsonify({"error": str(e)}), 500

@interview_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_interviews(user_id):
    """Get all interviews for a user."""
    try:
        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get interviews
        interviews = Interview.query.filter_by(user_id=user_id).order_by(Interview.created_at.desc()).all()
        
        return jsonify({
            "interviews": [i.to_dict() for i in interviews]
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_user_interviews: {str(e)}")
        return jsonify({"error": str(e)}), 500
