import jwt
import pyotp
from datetime import datetime, timedelta, timezone
from flask import Request, jsonify, session
from lib.jwt_manager import app as main_app
from util.sqlExecutor import SQLExecutor
from util.logging import log

def handler(request: Request):
    logger = log()
    logger.info(f"2FA verification API called, w/ method: {request.method}")
    
    if request.method == "POST":
        data: dict = request.get_json()
        if not data:
            logger.warning("2FA verification attempt with no data provided")
            return jsonify({"error": "No data provided"}), 400
            
        if 'code' not in data:
            logger.warning("2FA verification missing required 'code' field")
            return jsonify({"error": "Missing verification code"}), 400
            
        code = data.get('code')
        
        # Check if session contains required data
        if 'user_id' not in session or 'tfa_secret' not in session:
            logger.warning("2FA verification failed: Missing session data")
            return jsonify({"error": "Missing session data. Please log in first."}), 401
            
        user_id = session.get('user_id')
        tfa_secret = session.get('tfa_secret')
        
        logger.info(f"Processing 2FA verification for user_id: {user_id}")
        
        if not tfa_secret:
            logger.warning(f"2FA verification failed: User {user_id} has no 2FA secret configured")
            return jsonify({"error": "Two-factor authentication not set up for this account."}), 400
            
        try:
            totp = pyotp.TOTP(tfa_secret)
            if totp.verify(code):
                # Update user's 'activated' status if not already activated
                sql_executor = SQLExecutor("fetch_user", None)
                user = sql_executor.fetch_one_by_id((user_id,))
                
                if user and not user[3]:  # user[3] is the 'activated' field
                    logger.info(f"Activating user account for user_id: {user_id}")
                    # Code to update user's activated status would go here
                
                logger.info(f"2FA verification successful for user_id: {user_id}")
                session['authenticated'] = True
                # Generate JWT
                token = jwt.encode({
                    'user_id': user_id,
                    'exp': datetime.now(timezone.utc) + timedelta(hours=24)
                }, main_app.config['SECRET_KEY'], algorithm='HS256')
                session.clear()
                return jsonify({"message": "2FA verified. Login successful.", "token": token}), 200
            else:
                logger.warning(f"2FA verification failed: Invalid code for user_id: {user_id}")
                return jsonify({"error": "Invalid verification code"}), 401
        except Exception as e:
            logger.error(f"Error during 2FA verification for user {user_id}: {e}")
            return jsonify({"error": str(e)}), 500
    else:
        logger.warning(f"Invalid request method for 2FA verification: {request.method}")
        return jsonify({"error": "Invalid request method"}), 405
