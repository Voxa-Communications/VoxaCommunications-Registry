import jwt
from functools import wraps
from flask import request, jsonify
from util.sqlExecutor import SQLExecutor

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
                connection = get_db_connection()
                cursor = connection.cursor()
                cursor.execute("SELECT user_id FROM api_tokens WHERE token_hash = %s AND expires_at > NOW()", (bcrypt.hashpw(token.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),))
                result = cursor.fetchone()
                if result:
                    current_user_id = result[0]
                else:
                    return jsonify({"error": "Invalid token"}), 401
            except Error as e:
                return jsonify({"error": str(e)}), 500
            finally:
                cursor.close()
                connection.close()
        
        return f(current_user_id, *args, **kwargs)
    return decorated