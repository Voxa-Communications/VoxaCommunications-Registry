import jwt
import pyotp
from datetime import datetime, timedelta, timezone
from flask import Request, jsonify, session
from lib.jwt_manager import app as main_app
from util.sqlExecutor import SQLExecutor
from util.logging import log

def handler(request: Request):
    if request.method == "POST":
        data: dict = request.get_json()
        logger = log()
        logger.info(f"2FA Verification API called, w/ method: {request.method}")
        if 'user_id' not in data:
            return jsonify({"error": "Session expired or invalid"}), 401
        
        if not data or 'code' not in data:
            return jsonify({"error": "Missing 2FA code"}), 400
        
        code = data['code']
        totp = pyotp.TOTP(data['tfa_secret'])
        
        if totp.verify(code):
            # Generate JWT
            token = jwt.encode({
                'user_id': data['user_id'],
                'exp': datetime.now(timezone.utc) + timedelta(hours=24)
            }, main_app.config['SECRET_KEY'], algorithm='HS256')
            session.clear()
            return jsonify({"message": "2FA verified. Login successful.", "token": token}), 200
        else:
            return jsonify({"error": "Invalid 2FA code"}), 400
    else:
        return jsonify({"error": "Invalid request method"}), 405
    