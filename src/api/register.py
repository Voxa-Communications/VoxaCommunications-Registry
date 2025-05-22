import bcrypt
import qrcode
import pyotp
import os
import re
import html
import datetime
from util.sqlExecutor import SQLExecutor
from util.logging import log
from util.field_validators import validate_email, validate_password_strength
from flask import redirect, jsonify, Request, url_for, session

# /api/v1/register
# test: curl -X POST -H "Content-Type: application/json" -d '{"name":"admin","email":"connor@connor33341.dev","password":"passowrd"}' http://127.0.0.1:8000/api/v1/register
def handler(request: Request):
    logger = log()
    logger.info(f"Registration API called, w/ method: {request.method}")
    
    if request.method == "POST":
        try:
            data: dict = request.get_json()
            if not data:
                logger.warning("Registration attempt with no data provided")
                return jsonify({"error": "No data provided"}), 400
            
            # Extract and sanitize user inputs
            name = html.escape(data.get("name", "").strip())
            email = data.get("email", "").strip().lower()
            password = data.get("password", "")
            
            # Validate required fields
            if not name or not email or not password:
                logger.warning("Registration missing required fields")
                return jsonify({"error": "Missing required fields"}), 400
            
            # Validate name length
            if len(name) < 2 or len(name) > 100:
                return jsonify({"error": "Name must be between 2 and 100 characters"}), 400
            
            # Validate email format
            if not validate_email(email):
                logger.warning(f"Invalid email format: {email}")
                return jsonify({"error": "Invalid email format"}), 400
            
            # Validate password strength
            is_valid_password, password_error = validate_password_strength(password)
            if not is_valid_password:
                logger.warning(f"Weak password: {password_error}")
                return jsonify({"error": password_error}), 400
            
            # Hash the password with bcrypt
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            created_at = datetime.datetime.now().isoformat()
            tfa_secret = pyotp.random_base32()
            
            logger.info(f"Creating new user: {email}")
            
            # Create the user in the database
            sql_executor = SQLExecutor("input_user", None)
            sql_executor.execute_sql((name, email, password_hash, created_at, tfa_secret, True, False))
            user_id = sql_executor.DBManager.cursor.lastrowid
            
            # Store user info in session
            session["tfa_secret"] = tfa_secret
            session["email"] = email
            session["user_id"] = user_id
            
            logger.info(f"User created successfully with ID: {user_id}")
            return jsonify({"message": "User created successfully. Please log in.", "user_id": user_id}), 201
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return jsonify({"error": "An error occurred during registration. Please try again."}), 500
    else:
        logger.warning(f"Invalid request method for registration: {request.method}")
        return redirect(url_for("index"))