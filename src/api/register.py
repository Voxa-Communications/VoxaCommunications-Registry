import bcrypt
import qrcode
import pyotp
import os
from util.sqlExecutor import SQLExecutor
import datetime
from flask import redirect, jsonify, Request, url_for

# /api/v1/register
def handler(request: Request):
    if request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        if not name or not email or not password:
            return jsonify({"error": "Missing required fields"}), 400
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        tfa_secret = pyotp.random_base32()
        created_at = datetime.datetime.now().isoformat()  # Add created_at timestamp
        tfa_secret = pyotp.random_base32()

        try:
            sql_executor = SQLExecutor("input_user", None)
            sql_executor.execute_sql((name, email, password_hash, created_at, tfa_secret, True, True))
        except Exception as e:
            return jsonify({"error": f"Error creating user: {e}"}), 500
    else:
        return redirect(url_for("index"))