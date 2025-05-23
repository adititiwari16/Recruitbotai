import os
import json
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

@app.route('/')
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    # Ensure templates directory exists
    os.makedirs('templates', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)