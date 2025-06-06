# RecruitBotAI: AI-Powered Interview Evaluation System

## Project Goal

RecruitBotAI is an AI-powered system designed to streamline the technical interview process. It provides a platform for both recruiters and candidates, enabling automated interview sessions, AI-driven question generation and evaluation, and job profile management.

## Features

*   **User Authentication:** Secure registration and login for both recruiter and candidate roles.
*   **Role-Based Access Control:** Different functionalities based on user roles (Recruiter/Candidate).
*   **Candidate Profile:** Candidates can update their profile with relevant experience.
*   **Job Profile Management (Recruiter):** Recruiters can create, edit, activate/deactivate, and delete job profiles with customizable evaluation criteria and prompts.
*   **Dynamic AI Interviews (Candidate):** Candidates can start interviews based on available job profiles.
*   **AI-Powered Question Generation:** Interview questions are dynamically generated by an LLM (Ollama) based on the job profile and candidate's experience/previous answers.
*   **Real-time Chat Interface:** Interactive chat interface for the interview session.
*   **Individual Answer Evaluation:** Each answer is evaluated by the LLM, assigning an individual score and feedback.
*   **Comprehensive Evaluation Report:** A detailed report generated at the end of the interview, including overall assessment, technical/soft skills evaluation, strengths, weaknesses, and a final recommendation.
*   **Performance-Based Scoring:** The overall interview score is calculated based on the aggregation of individual question scores.
*   **Dashboard (Recruiter):** Overview of completed interviews with results and access to job profile management.

## Technologies Used

*   **Backend:** Flask (Python framework)
*   **Database:** PostgreSQL (using SQLAlchemy ORM)
*   **AI/LLM:** Ollama (for running language models locally)
*   **Frontend:** HTML, CSS (Bootstrap), JavaScript
*   **Package Management:** Poetry
*   **Development:** Git

## Setup and Installation

Follow these steps to set up and run the project locally:

### Prerequisites

*   Python 3.8+
*   Poetry (Installation instructions: [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation))
*   Docker (Optional, for running Ollama)
*   Ollama (Installation instructions: [https://ollama.com/download](https://ollama.com/download))
*   PostgreSQL Database (e.g., using Supabase, ElephantSQL, or local installation)

### 1. Clone the Repository

```bash
git clone <repository_url>
cd RecruitBotAi
```

### 2. Install Dependencies

Use Poetry to install the project dependencies:

```bash
poetry install
```

This will create a virtual environment and install all required packages based on `pyproject.toml`.

If you prefer using `pip`, you can generate `requirements.txt` from `pyproject.toml`:

```bash
poetry export -f requirements.txt --output requirements.txt
pip install -r requirements.txt
```

### 3. Set up Environment Variables

Create a `.env` file in the root directory of the project. Copy the contents from `.env.example` (if provided, otherwise create it manually) and update the values.

```env
DATABASE_URL="postgresql://user:password@host:port/database_name"
SESSION_SECRET="your_random_secret_key_here"
DEBUG=True
# Add any other necessary variables here
```

**DATABASE_URL:** Replace with your PostgreSQL connection string.
**SESSION_SECRET:** Replace with a random string for Flask session security.

### 4. Set up Ollama and Download Model

Install Ollama and download the required language model. The application is currently configured to use `llama3.2:latest`.

```bash
ollama pull llama3.2:latest
```

Ensure your Ollama instance is running.

### 5. Initialize the Database

Run the Flask application context to create the database tables. Make sure your `DATABASE_URL` in `.env` is correct and the PostgreSQL server is accessible.

```bash
poetry run python -c "from app import app, db; with app.app_context(): db.create_all()"
```

If using `pip` without Poetry:

```bash
python -c "from app import app, db; from flask import Flask; app.app_context().push(); db.create_all()"
```

This will create the necessary tables and also create a default recruiter user if one doesn't exist.

### 6. Run the Application

Start the Flask development server:

```bash
poetry run flask run --port 5001 --host 0.0.0.0
```

If using `pip` without Poetry:

```bash
export FLASK_APP=app.py
export FLASK_ENV=development # or production
python app.py
```

The application should now be running at `http://localhost:5001`.

## Usage

### Default Recruiter Login

Upon initial database initialization, a default recruiter user is created:

*   **Email:** `recruiter@example.com`
*   **Password:** `admin123`

Login with these credentials to access the recruiter dashboard and manage job profiles.

### Candidate Registration and Interview Process

*   Candidates can register via the `/register` page.
*   After logging in, candidates should complete their profile.
*   They can then navigate to the Interview Setup page to select a job profile and start an interview.
*   The interview proceeds in a chat format with questions generated by the AI.
*   Upon completion, a detailed evaluation report is available.

## Development Notes

*   The database initialization (`db.create_all()`) is suitable for initial setup but not for schema migrations in production. Consider using Alembic for managing database migrations in a production environment.
*   The application currently uses a local Ollama instance. For production, consider a dedicated LLM service or a more robust deployment of Ollama.
*   The application structure has both a main `app.py` and a `backend` directory. Ensure logic is consolidated and clear to avoid confusion.

## Contributing

Feel free to fork the repository and contribute! Pull requests are welcome.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 