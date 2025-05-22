import bcrypt
import qrcode
import pyotp
import os
import io
from util.sqlExecutor import SQLExecutor
import datetime
from flask import redirect, jsonify, Request, url_for, session

# /api/v1/register_2fa
def handler(request: Request):
    if request.method == "POST":
        data: dict = request.get_json()  # I mean, this is a json API, so it should be JSON.
        # STUB for now
        pass
    else:
        return redirect(url_for("index"))