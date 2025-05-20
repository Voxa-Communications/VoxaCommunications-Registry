import bcrypt
import qrcode
import pyotp
import os
import datetime
from util.sqlExecutor import SQLExecutor
from util.logging import log
from flask import redirect, jsonify, Request, url_for, session

# /api/v1/register
# test: curl -X POST -H "Content-Type: application/json" -d '{"name":"admin","email":"connor@connor33341.dev","password":"passowrd"}' http://127.0.0.1:8000/api/v1/register
def handler(request: Request):
    logger = log()
    if request.method == "POST":
        data: dict = request.get_json() # I mean, this is a json API, so it should be JSON.
        if not data:
            return jsonify({"error": "No data provided"}), 400
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        if not name or not email or not password:
            return jsonify({"error": "Missing required fields"}), 400
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        created_at = datetime.datetime.now().isoformat()  # Add created_at timestamp
        tfa_secret = pyotp.random_base32()
        # Eventhough we generate a TFA secret, we don't use it yet. But we will in the future.
        try:
            sql_executor = SQLExecutor("input_user", None)
            # Should be handled in the SQLExecutor class, however, i'm just going to doubble check
            sql_executor.execute_sql((name, email, password_hash, created_at, tfa_secret, True, False)) # Is the account active? eh, just pass True for now. Eventhough it is just created.
            session["tfa_secret"] = tfa_secret
            session["email"] = email
            session["user_id"] = sql_executor.DBManager.cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return jsonify({"error": f"Error creating user: {e}"}), 500
    else:
        return redirect(url_for("index"))
    return jsonify({"message": "User created successfully. Please log in."}), 200