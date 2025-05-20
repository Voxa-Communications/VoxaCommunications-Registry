import jwt
import pyotp
import requests
import traceback
from requests import Request
from colorama import Fore
from datetime import datetime, timedelta, timezone
from flask import Request, jsonify, session
from lib.jwt_manager import app as main_app
from util.sqlExecutor import SQLExecutor
from util.logging import log
from util.printColor import print_color
from util.exception_handlers import log_exceptions

@log_exceptions
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
            
        code: str = str(data.get('code'))
        
        # Check if session contains required data
        if 'user_id' not in data:
            logger.warning("2FA verification failed: Missing session data")
            return jsonify({"error": "Missing session data. Please log in first."}), 401
            
        user_id: int = data.get('user_id')

        sql_executor = SQLExecutor("fetch_user_from_id")
        user = sql_executor.fetch_one((user_id,))
        # Fixed the index - tfa_secret is at index 2, not 3
        tfa_secret: str = str(user[2]) or data.get('tfa_secret')
        
        logger.info(f"Processing 2FA verification for user_id: {user_id}")
        
        if not tfa_secret:
            logger.warning(f"2FA verification failed: User {user_id} has no 2FA secret configured")
            return jsonify({"error": "Two-factor authentication not set up for this account."}), 400
            
        try:
            totp = pyotp.TOTP(tfa_secret)
            if totp.verify(code):
                # Update user's 'activated' status if not already activated
                
                if user and not user[3]:  # user[3] is the 'is_active' field
                    logger.info(f"Activating user account for user_id: {user_id}")
                    # Call the API to complete the 2FA setup
                    response: Request = requests.post(
                        f"{main_app.config["API_URL"]}/api/v1/enable_2fa",
                        json={"user_id": user_id, "tfa_secret": tfa_secret}
                    )

                    if "error" in response.json():
                        logger.error(f"Error enabling 2FA for user {user_id}: {response.json()['error']}")
                        return jsonify({"error": response.json()["error"]}), 500
                
                logger.info(f"2FA verification successful for user_id: {user_id}")
                session['authenticated'] = True
                # Generate JWT
                token = jwt.encode({
                    'user_id': str(user_id),
                    'exp': datetime.now(timezone.utc) + timedelta(hours=24)
                }, main_app.config['SECRET_KEY'], algorithm='HS256')
                session.clear()
                return jsonify({"message": "2FA verified. Login successful.", "token": token}), 200
            else:
                logger.warning(f"2FA verification failed: Invalid code for user_id: {user_id}")
                return jsonify({"error": "Invalid verification code"}), 401
        except Exception as e:
            # The decorator will handle logging the stack trace
            # We still need this block to return a proper API response
            logger.error(f"Error during 2FA verification for user {user_id}: {e}")
            stack_trace = traceback.format_exc()
            print_color(f"Stack trace: {stack_trace}", Fore.MAGENTA) # This is just for debugging purposes as log_exceptions dosent work well
            return jsonify({"error": str(e)}), 500
    else:
        logger.warning(f"Invalid request method for 2FA verification: {request.method}")
        return jsonify({"error": "Invalid request method"}), 405
