import bcrypt
import pyotp
import time
import re
import html
import hmac
from datetime import datetime
from flask import Blueprint, Request, jsonify, session, current_app
from lib.jwt_manager import generate_token
from util.timing_utils import constant_time_compare
from util.field_validators import is_valid_email
from util.sqlExecutor import SQLExecutor
from util.logging import log

def handler(request: Request):
    logger = log()
    logger.info(f"Login API called, w/ method: {request.method}")
    
    if request.method == "POST":
            
        try:
            data: dict = request.get_json()
            if not data:
                logger.warning("Login attempt with no data provided")
                return jsonify({"error": "No data provided"}), 400
            
            # Validate required fields
            if not all(key in data for key in ['email', 'password']):
                logger.warning(f"Login attempt missing required fields: {list(data.keys())}")
                return jsonify({"error": "Missing email or password"}), 400
            
            # Sanitize and validate inputs
            email = str(data.get('email', '')).strip().lower()
            password = data.get('password', '')
            code = data.get('code')
            
            # Email validation
            if not is_valid_email(email):
                logger.warning(f"Login attempt with invalid email format: {email}")
                return jsonify({"error": "Invalid email format"}), 400
            
            logger.info(f"Login attempt for email: {email}")
            
            # Get user from database
            sql_executor = SQLExecutor("fetch_user", None)
            user = sql_executor.fetch_one((email,))
            
            # User not found or account not activated
            if not user or not user[3]:
                logger.warning(f"Login failed: {'No user found' if not user else 'Account not activated'} for email {email}")
                # Return generic error to prevent user enumeration
                return jsonify({"error": "Invalid credentials"}), 401
            
            # Verify password
            password_valid = bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8'))
            if not password_valid:
                logger.warning(f"Login failed: Invalid password for email {email}")
                return jsonify({"error": "Invalid credentials"}), 401
                
            # Check 2FA if enabled
            if user[4] and user[2]:  # If 2FA is enabled and secret exists
                if not code:
                    logger.info(f"2FA code required but not provided for email {email}")
                    return jsonify({"error": "2FA code required", "requires_2fa": True}), 401
                    
                totp = pyotp.TOTP(user[2])
                if not totp.verify(code):
                    logger.warning(f"Login failed: Invalid 2FA code for email {email}")
                    return jsonify({"error": "Invalid 2FA code"}), 401
            
            # Login successful
            logger.info(f"Login successful for user {user[0]} (email: {email})")
            
            # Store minimal user information in session
            session['user_id'] = user[0]
            session['last_activity'] = datetime.now().timestamp()
            
            # Generate JWT token with appropriate expiration
            token = generate_token(user[0])
                
            # Return success response with minimal information
            return jsonify({
                "message": "Login successful",
                "user_id": user[0],
                "token": token,
                "tfa_enabled": user[4]
            }), 200
                
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            # Don't expose detailed error information to the client
            return jsonify({"error": "An error occurred during login. Please try again."}), 500
    else:
        logger.warning(f"Invalid request method for login: {request.method}")
        return jsonify({"error": "Invalid request method"}), 405

