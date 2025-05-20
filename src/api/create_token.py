import secrets
import bcrypt
from datetime import datetime, timedelta, timezone
from flask import Request, jsonify, session
from lib.jwt_manager import token_required
from util.sqlExecutor import SQLExecutor
from util.logging import log

@token_required
def handler(current_user_id: int, request: Request, **kwargs):
    logger = log()
    logger.info(f"Create Token API called, w/ method: {request.method}")
    token = secrets.token_urlsafe(32)
    token_hash = bcrypt.hashpw(token.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)

    try:
        sql_executor = SQLExecutor("input_tokens_table")
        sql_executor.execute_sql((current_user_id, token_hash, expires_at))
        return jsonify({"message": "Token created successfully", "token": token}), 200
    except Exception as e:
        logger.error(f"Error creating token: {e}")
        return jsonify({"error": f"Error creating token: {e}"}), 500
