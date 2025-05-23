import logging
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from app import db
from models import User

# Initialize blueprint and logger
users_bp = Blueprint('users', __name__)
logger = logging.getLogger(__name__)

@users_bp.route('/register', methods=['POST'])
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
            
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Error in register_user: {str(e)}")
        return jsonify({"error": str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user details by ID."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify({"user": user.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Error in get_user: {str(e)}")
        return jsonify({"error": str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user details."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        data = request.json
        
        # Update fields if provided
        if 'name' in data:
            user.name = data['name']
        if 'age' in data:
            user.age = data['age']
        if 'experience' in data:
            user.experience = data['experience']
        if 'job_title' in data:
            user.job_title = data['job_title']
            
        db.session.commit()
        
        return jsonify({
            "message": "User updated successfully",
            "user": user.to_dict()
        }), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Error in update_user: {str(e)}")
        return jsonify({"error": str(e)}), 500
