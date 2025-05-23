import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Enable CORS
CORS(app)

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

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models
    from backend import models  # noqa: F401
    
    # Create tables
    db.create_all()
    
    # Register blueprints
    from backend.api.users import users_bp
    from backend.api.interview import interview_bp
    from backend.api.query import query_bp
    
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(interview_bp, url_prefix='/api/interview')
    app.register_blueprint(query_bp, url_prefix='/api/query')
