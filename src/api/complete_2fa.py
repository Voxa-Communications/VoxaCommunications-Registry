import pyotp
import qrcode
import base64
import io
from flask import Request, jsonify, session
from util.sqlExecutor import SQLExecutor
from util.logging import log

def handler(request: Request):
    if request.method == "POST":
        if 'user_id' not in data:
            return jsonify({"error": "Session expired or invalid"}), 401
        
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({"error": "Missing 2FA code"}), 400
        
        code = data['code']
        totp = pyotp.TOTP(data['tfa_secret'])
        
        if totp.verify(code):
            try:
                sql_executor = SQLExecutor("update_user_totp")
                sql_executor.execute_sql((data['user_id'],))
                session.clear()
                return jsonify({"message": "2FA setup successful. You can now log in."}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify({"error": "Invalid 2FA code"}), 400
    else:
        return jsonify({"error": "Invalid request method"}), 405