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
            return jsonify({"error": "Missing email or password"}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        try:
            sql_executor = SQLExecutor("fetch_user", None)
            user = sql_executor.fetch_one((email,))
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')) and user[3]:
                session['user_id'] = user[0]
                session['tfa_secret'] = user[2]
                return jsonify({"message": "Credentials valid. Proceed to 2FA verification.", "user_id": user[0]}), 200
            else:
                return jsonify({"error": "Invalid credentials or account not activated"}), 401
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid request method"}), 405