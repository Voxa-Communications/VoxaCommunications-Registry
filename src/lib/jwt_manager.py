import jwt
import bcrypt
from functools import wraps
from flask import Flask, request, jsonify
from util.sqlExecutor import SQLExecutor

app: Flask = None

def set_app(flask_app: Flask):
    global app
    app = flask_app

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].replace('Bearer ', '')
        
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        try:
            # Try decoding as JWT
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            # Check if it's an API token
            try:
                sql_executor = SQLExecutor("fetch_api_tokens")
                result = sql_executor.fetch_one((token,))
                if result and bcrypt.checkpw(token.encode('utf-8'), result[1].encode('utf-8')):
                    current_user_id = result[0]
                else:
                    return jsonify({"error": "Invalid token"}), 401
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        return f(current_user_id, *args, **kwargs)
    return decorated