import bcrypt
import qrcode
import pyotp
import os
from flask import redirect, jsonify, Request, url_for

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
    else:
        return redirect(url_for("index"))