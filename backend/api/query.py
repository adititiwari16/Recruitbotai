import logging
import json
import os
from flask import Blueprint, request, jsonify
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize blueprint and logger
query_bp = Blueprint('query', __name__)
logger = logging.getLogger(__name__)

@query_bp.route('/ask', methods=['POST'])
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
        
        # Prepare the prompt template
        template = """
        You are RecruitBot, an AI assistant specializing in interview preparation and career advice.
        
        User Query: {query}
        
        Additional Context: {context}
        
        Please provide a helpful, detailed response to the query.
        Format your response in markdown syntax to make it easy to read.
        Include sections, bullet points, and other markdown formatting as appropriate.
        Keep your response professional, informative, and supportive.
        
        Your response:
        """
        
        # Initialize the language model
        try:
            # First try using Llama model from utils
            from backend.utils import get_llama_model
            llm = get_llama_model()
            
            if llm:
                # Format the prompt with user inputs
                formatted_prompt = template.format(
                    query=query,
                    context=context
                )
                
                # Generate the response
                response_text = llm(formatted_prompt)
                
                # Return the response
                return jsonify({
                    "response": response_text,
                    "format": response_format
                }), 200
            else:
                return jsonify({"error": "AI model initialization failed"}), 500
                
        except Exception as model_error:
            logger.error(f"Error using local model: {str(model_error)}")
            return jsonify({"error": f"Failed to process query: {str(model_error)}"}), 500
        
    except Exception as e:
        logger.error(f"Error in ask_question: {str(e)}")
        return jsonify({"error": str(e)}), 500


@query_bp.route('/evaluate', methods=['POST'])
def evaluate_response():
    """
    Evaluate a user's response to an interview question.
    
    Expected request body:
    {
        "question": "The interview question",
        "answer": "User's answer to evaluate",
        "role": "The job role (e.g., Software Engineer)",
        "experience_level": "Experience level (e.g., entry, mid, senior)"
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        # Validate required fields
        required_fields = ['question', 'answer', 'role', 'experience_level']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        # Import utility functions
        from backend.utils import evaluate_answer
        
        # Evaluate the answer
        evaluation = evaluate_answer(
            question=data.get('question', ''),
            answer=data.get('answer', ''),
            role=data.get('role', ''),
            experience=data.get('experience_level', '')
        )
        
        if isinstance(evaluation, dict) and "error" in evaluation:
            return jsonify(evaluation), 500
        
        # Return the evaluation
        return jsonify({
            "evaluation": evaluation,
            "format": "json"
        }), 200
        
    except Exception as e:
        logger.error(f"Error in evaluate_response: {str(e)}")
        return jsonify({"error": str(e)}), 500