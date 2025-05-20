import pyotp
import PIL
import qrcode
import base64
import io
from flask import Request, jsonify, session
from util.logging import log

def handler(request: Request):
    logger = log()
    logger.info(f"2FA Setup API called, w/ method: {request.method}")
    if request.method == "POST":
        data: dict = request.get_json()  # I mean, this is a json API, so it should be JSON.
        if 'user_id' not in data:
            return jsonify({"error": "Session expired or invalid"}), 401
        
        try:
            tfa_secret = data.get("tfa_secret") or session['tfa_secret']
        except KeyError:
            tfa_secret = pyotp.random_base32()
        email = data.get("email") or session['email']
        
        # Generate TOTP URI
        totp = pyotp.TOTP(tfa_secret)
        qr_uri = totp.provisioning_uri(name=email, issuer_name="VoxaCommunications-Registry")
        
        # Generate QR code image
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert image to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        qr_code = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return jsonify({
            "message": "Scan the QR code with your authenticator app",
            "qr_code": f"data:image/png;base64,{qr_code}",
            "tfa_secret": tfa_secret  # Optional: for manual entry
        }), 200
    else:
        return jsonify({"error": "Invalid request method"}), 405