import pyotp
from flask import Request, jsonify, session
from util.sqlExecutor import SQLExecutor
from util.logging import log

def handler(request: Request):
    pass
    """
    Completes the two-factor authentication setup by verifying the provided code
    and enabling 2FA for the user account.
    """
    logger = log()
    logger.info(f"2FA completion API called, w/ method: {request.method}")
    
    if request.method == "POST":
        data: dict = request.get_json()
        if not data:
            logger.warning("2FA completion attempt with no data provided")
            return jsonify({"error": "No data provided"}), 400
            
        # Check required fields
        required_fields = ['user_id', 'tfa_secret', 'verification_code']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            logger.warning(f"2FA completion missing required fields: {missing_fields}")
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        user_id = data.get('user_id')
        tfa_secret = data.get('tfa_secret')
        verification_code = data.get('verification_code')
        
        # If user_id and tfa_secret are in session, use those for extra validation
        session_user_id = session.get('tfa_setup_user_id')
        session_tfa_secret = session.get('tfa_setup_secret')
        
        if session_user_id and str(session_user_id) != str(user_id):
            logger.warning(f"2FA completion failed: User ID mismatch ({session_user_id} vs {user_id})")
            return jsonify({"error": "Session expired or invalid"}), 401
            
        if session_tfa_secret and session_tfa_secret != tfa_secret:
            logger.warning("2FA completion failed: TFA secret mismatch")
            return jsonify({"error": "Session expired or invalid"}), 401
            
        # Verify the user exists and has the correct TFA secret
        fetch_user_sql = "SELECT id, tfa_secret, tfa_enabled FROM users WHERE id = %s;"
        sql_executor = SQLExecutor("", None)
        sql_executor.DBManager.cursor.execute(fetch_user_sql, (user_id,))
        user = sql_executor.DBManager.cursor.fetchone()
        
        if not user:
            logger.warning(f"2FA completion failed: User {user_id} not found")
            return jsonify({"error": "User not found"}), 404
            
        # Check if 2FA is already enabled
        if user[2]:  # user[2] is the tfa_enabled field
            logger.warning(f"2FA completion failed: 2FA already enabled for user {user_id}")
            return jsonify({"error": "2FA is already enabled for this account"}), 400
            
        # Verify the 2FA secret matches what's stored or in session
        db_tfa_secret = user[1]
        if not db_tfa_secret:
            logger.warning(f"2FA completion failed: No TFA secret found for user {user_id}")
            return jsonify({"error": "No TFA secret found"}), 400
            
        if tfa_secret != db_tfa_secret:
            logger.warning(f"2FA completion failed: TFA secret mismatch for user {user_id}")
            return jsonify({"error": "Invalid TFA secret"}), 400
            
        # Verify the code is valid
        totp = pyotp.TOTP(tfa_secret)
        if not totp.verify(verification_code):
            logger.warning(f"2FA completion failed: Invalid verification code for user {user_id}")
            return jsonify({"error": "Invalid verification code"}), 400
            
        # Enable 2FA for the user
        try:
            update_sql = "UPDATE users SET tfa_enabled = TRUE WHERE id = %s;"
            sql_executor.DBManager.cursor.execute(update_sql, (user_id,))
            sql_executor.DBManager.connection.commit()
            
            # Clear setup session data
            if 'tfa_setup_user_id' in session:
                session.pop('tfa_setup_user_id')
            if 'tfa_setup_secret' in session:
                session.pop('tfa_setup_secret')
                
            logger.info(f"2FA enabled successfully for user {user_id}")
            return jsonify({
                "message": "2FA enabled successfully", 
                "user_id": user_id
            }), 200
        except Exception as e:
            logger.error(f"Error enabling 2FA for user {user_id}: {e}")
            return jsonify({"error": str(e)}), 500
    else:
        logger.warning(f"Invalid request method for 2FA completion: {request.method}")
        return jsonify({"error": "Invalid request method"}), 405