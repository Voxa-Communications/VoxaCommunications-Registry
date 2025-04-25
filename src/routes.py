import bcrypt
import qrcode
import pyotp
from flask import render_template, request, redirect, url_for, jsonify, flash, session, Flask

class Routes:
    def __init__(self, app: Flask, config: dict):
        self.app: Flask = app
        self.config: dict = config
    
    def initialize_routes(self):
        @self.app.route('/')
        def index():
            return "This is an API Server, Requires a client to interface with. Or, if you are a nerd, you can use CURL to interface with it. :)"
        
        @self.app.route("/api/v1/register", methods=["POST", "GET"])
        def api_register():
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

    
    def run(self):
        self.app.run(debug=True, port=self.config.get("PORT", 8000))
    
    