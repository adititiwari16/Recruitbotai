import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000

# Llama model configuration
LLAMA_MODEL = "llama3.2:1b"

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Application Settings
DEBUG = os.getenv("DEBUG", "True") == "True"

# Prompt Templates
INTERVIEW_QUESTION_TEMPLATE = """
You are RecruitBot, an AI-powered interview assistant. Generate {num_questions} interview questions for a candidate applying for a {role} position with {experience} years of experience. 
The questions should be relevant to the role and suitable for their experience level.
Format the output as a JSON array of question objects.
"""

ANSWER_EVALUATION_TEMPLATE = """
You are RecruitBot, an AI-powered interview evaluator. Evaluate the following answer for a candidate applying for a {role} position with {experience} years of experience.

Question: {question}

Candidate Answer: {answer}

Provide a detailed evaluation with the following:
1. Score (0-10)
2. Strengths
3. Areas for improvement
4. Additional insights
5. Overall feedback

Format the output as JSON.
"""

FINAL_EVALUATION_TEMPLATE = """
You are RecruitBot, an AI-powered interview evaluator. Based on the candidate's responses to the following questions, provide a comprehensive evaluation for a {role} position with {experience} years of experience.

Candidate: {name}, {age} years old

Responses:
{responses}

Provide a final evaluation with:
1. Overall score (0-100)
2. Key strengths
3. Areas for improvement
4. Hiring recommendation (Pass/Fail)
5. Detailed feedback

Format your response in markdown for a readable report.
"""
