import os
import json
import logging
from datetime import datetime
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from backend.config import LLAMA_MODEL, INTERVIEW_QUESTION_TEMPLATE, ANSWER_EVALUATION_TEMPLATE, FINAL_EVALUATION_TEMPLATE

# Configure logging
logger = logging.getLogger(__name__)

def get_llama_model():
    """Initialize and return the Llama model."""
    try:
        # Set up the model
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        
        # Initialize the model
        llm = LlamaCpp(
            model_path=LLAMA_MODEL,
            temperature=0.7,
            max_tokens=2000,
            top_p=1,
            callback_manager=callback_manager,
            verbose=True
        )
        
        return llm
    except Exception as e:
        logger.error(f"Error initializing Llama model: {str(e)}")
        return None

def generate_interview_questions(role, experience, num_questions=5):
    """Generate interview questions based on role and experience."""
    try:
        llm = get_llama_model()
        if not llm:
            return {"error": "Failed to initialize AI model"}
        
        prompt = INTERVIEW_QUESTION_TEMPLATE.format(
            num_questions=num_questions,
            role=role,
            experience=experience
        )
        
        response = llm(prompt)
        
        # Parse the response to get the questions
        try:
            questions = json.loads(response)
            return questions
        except json.JSONDecodeError:
            # Fallback parsing if the model doesn't return valid JSON
            lines = response.strip().split('\n')
            questions = []
            current_question = ""
            
            for line in lines:
                if line.strip().startswith(("Question", "Q", "-", "*")) and current_question:
                    questions.append(current_question.strip())
                    current_question = line
                else:
                    current_question += " " + line
            
            if current_question:
                questions.append(current_question.strip())
            
            return [{"question": q} for q in questions[:num_questions]]
    
    except Exception as e:
        logger.error(f"Error generating interview questions: {str(e)}")
        return {"error": f"Failed to generate questions: {str(e)}"}

def evaluate_answer(question, answer, role, experience):
    """Evaluate the candidate's answer to a question."""
    try:
        llm = get_llama_model()
        if not llm:
            return {"error": "Failed to initialize AI model"}
        
        prompt = ANSWER_EVALUATION_TEMPLATE.format(
            question=question,
            answer=answer,
            role=role,
            experience=experience
        )
        
        response = llm(prompt)
        
        # Parse the response
        try:
            evaluation = json.loads(response)
            return evaluation
        except json.JSONDecodeError:
            # Fallback parsing if the model doesn't return valid JSON
            return {
                "score": 5,  # Default middle score
                "strengths": "Response parsing error - please try again",
                "areas_for_improvement": "Response parsing error - please try again",
                "additional_insights": "",
                "overall_feedback": "The system was unable to properly evaluate your answer. Please try again."
            }
    
    except Exception as e:
        logger.error(f"Error evaluating answer: {str(e)}")
        return {"error": f"Failed to evaluate answer: {str(e)}"}

def generate_final_report(name, age, role, experience, responses):
    """Generate a final evaluation report based on all responses."""
    try:
        llm = get_llama_model()
        if not llm:
            return {"error": "Failed to initialize AI model"}
        
        # Format responses for the prompt
        formatted_responses = ""
        for i, resp in enumerate(responses):
            formatted_responses += f"Q{i+1}: {resp['question']}\n"
            formatted_responses += f"A{i+1}: {resp['answer']}\n"
            formatted_responses += f"Score: {resp['score']}/10\n\n"
        
        prompt = FINAL_EVALUATION_TEMPLATE.format(
            name=name,
            age=age,
            role=role,
            experience=experience,
            responses=formatted_responses
        )
        
        response = llm(prompt)
        return response
    
    except Exception as e:
        logger.error(f"Error generating final report: {str(e)}")
        return {"error": f"Failed to generate final report: {str(e)}"}

def format_markdown_report(interview_data, user_data, questions_data):
    """Format the final report in markdown."""
    report = f"""# Interview Evaluation Report

## Candidate Information
- **Name:** {user_data.get('name')}
- **Age:** {user_data.get('age')}
- **Experience:** {user_data.get('experience')} years
- **Applied Position:** {interview_data.get('role')}
- **Date:** {datetime.now().strftime('%Y-%m-%d')}

## Overall Results
- **Score:** {interview_data.get('score')}/100
- **Status:** {"PASS" if interview_data.get('status') == 'completed' else "FAIL"}

## Detailed Feedback
{interview_data.get('feedback', 'No feedback available')}

## Question & Answer Analysis
"""

    for q in questions_data:
        report += f"""
### Question {q.get('order')}
**Q:** {q.get('text')}

**A:** {q.get('answer', 'No answer provided')}

**Score:** {q.get('score')}/10

**Feedback:**
{q.get('feedback', 'No feedback available')}

---
"""

    report += """
## Recommendation
"""
    if interview_data.get('status') == 'completed':
        report += "Based on the candidate's performance, we **recommend proceeding** with their application."
    else:
        report += "Based on the candidate's performance, we **do not recommend proceeding** with their application at this time."

    return report
