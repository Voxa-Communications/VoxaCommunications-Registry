import bcrypt
from flask import Blueprint, Request, jsonify, session
from util.sqlExecutor import SQLExecutor
from util.logging import log

def handler(request: Request):
    logger = log()
    logger.info(f"Login API called, w/ method: {request.method}")
    if request.method == "POST":
        data: dict = request.get_json()  # I mean, this is a json API, so it should be JSON.
        if not data or not all(key in data for key in ['email', 'password']):
            logger.warning(f"Login attempt missing required fields: {list(data.keys()) if data else 'No data provided'}")
            return jsonify({"error": "Missing email or password"}), 400
        
        email = data.get('email')
        logger.info(f"Login attempt for email: {email}")
        password: str = data.get('password')
        
        try:
            sql_executor = SQLExecutor("fetch_user", None)
            logger.debug(f"Executing SQL query to fetch user with email: {email}")
            user = sql_executor.fetch_one((email,))
            
            if not user:
                logger.warning(f"Login failed: No user found with email {email}")
                return jsonify({"error": "Invalid credentials or account not activated"}), 401
            
            if not user[3]:
                logger.warning(f"Login failed: Account not activated for email {email}")
                return jsonify({"error": "Invalid credentials or account not activated"}), 401
            
            password_valid = bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8'))
            if password_valid and user[3]:
                session['user_id'] = user[0]
                session['tfa_secret'] = user[2]
                logger.info(f"Login successful for user {user[0]} (email: {email}), proceeding to 2FA")
                return jsonify({"message": "Credentials valid. Proceed to 2FA verification.", "user_id": user[0], "tfa_secret": user[2]}), 200
            else:
                logger.warning(f"Login failed: Invalid password for email {email}")
                return jsonify({"error": "Invalid credentials or account not activated"}), 401
        except Exception as e:
            logger.error(f"Error during login for {email}: {e}")
            return jsonify({"error": str(e)}), 500
    else:
        logger.warning(f"Invalid request method for login: {request.method}")
        return jsonify({"error": "Invalid request method"}), 405