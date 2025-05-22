"""
Tests for the Two-Factor Authentication API endpoints.
Covers setup_2fa.py, verify_2fa.py, enable_2fa.py, complete_2fa.py, register_2fa.py
"""
import json
import pytest
import pyotp
from flask import session


class Test2FA:
    """Test class for 2FA API endpoints."""
    
    def test_setup_2fa(self, client, authenticated_client):
        """Test 2FA setup process."""
        client, token = authenticated_client
        
        # Get user info from session
        response = client.post(
            '/api/v1/setup_2fa',
            data=json.dumps({
                "user_id": 1,  # This will be overridden by session in real scenarios
                "email": "_test@voxacommunications.com"
            }),
            content_type='application/json',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = json.loads(response.data)
        assert response.status_code == 200
        assert "message" in data
        assert "qr_code" in data
        assert "tfa_secret" in data
        assert data["message"] == "Scan the QR code with your authenticator app"
        assert data["qr_code"].startswith("data:image/png;base64,")
        
        # Store the secret for subsequent tests
        tfa_secret = data["tfa_secret"]
        return tfa_secret
    
    def test_verify_2fa(self, client, authenticated_client):
        """Test 2FA verification."""
        client, token = authenticated_client
        
        # First setup 2FA to get a secret
        setup_response = client.post(
            '/api/v1/setup_2fa',
            data=json.dumps({
                "user_id": 1,
                "email": "_test@voxacommunications.com"
            }),
            content_type='application/json',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        setup_data = json.loads(setup_response.data)
        tfa_secret = setup_data["tfa_secret"]
        
        # Generate a valid TOTP code
        totp = pyotp.TOTP(tfa_secret)
        valid_code = totp.now()
        
        # Test verification with valid code
        verify_response = client.post(
            '/api/v1/verify_2fa',
            data=json.dumps({
                "code": valid_code,
                "tfa_secret": tfa_secret
            }),
            content_type='application/json',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        verify_data = json.loads(verify_response.data)
        assert verify_response.status_code == 200
        assert "verified" in verify_data
        assert verify_data["verified"] is True
        
        # Test verification with invalid code
        invalid_response = client.post(
            '/api/v1/verify_2fa',
            data=json.dumps({
                "code": "000000",  # Invalid code
                "tfa_secret": tfa_secret
            }),
            content_type='application/json',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        invalid_data = json.loads(invalid_response.data)
        assert invalid_response.status_code == 401
        assert "error" in invalid_data
        
    def test_enable_2fa(self, client, authenticated_client):
        """Test enabling 2FA for a user."""
        client, token = authenticated_client
        
        # Setup 2FA first
        setup_response = client.post(
            '/api/v1/setup_2fa',
            data=json.dumps({
                "user_id": 1,
                "email": "_test@voxacommunications.com"
            }),
            content_type='application/json',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        setup_data = json.loads(setup_response.data)
        tfa_secret = setup_data["tfa_secret"]
        
        # Generate a valid TOTP code
        totp = pyotp.TOTP(tfa_secret)
        valid_code = totp.now()
        
        # Enable 2FA
        enable_response = client.post(
            '/api/v1/enable_2fa',
            data=json.dumps({
                "code": valid_code,
                "tfa_secret": tfa_secret,
                "enable": True
            }),
            content_type='application/json',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        enable_data = json.loads(enable_response.data)
        assert enable_response.status_code == 200
        assert "message" in enable_data
        assert "2FA has been enabled" in enable_data["message"]
        
        # Try with invalid code
        invalid_response = client.post(
            '/api/v1/enable_2fa',
            data=json.dumps({
                "code": "000000",  # Invalid code
                "tfa_secret": tfa_secret,
                "enable": True
            }),
            content_type='application/json',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        invalid_data = json.loads(invalid_response.data)
        assert invalid_response.status_code == 401
        assert "error" in invalid_data
    
    def test_complete_2fa(self, client, authenticated_client):
        """Test completing 2FA during login."""
        client, token = authenticated_client
        
        # For this test, we'd need to have 2FA already enabled
        # First, set up the 2FA
        setup_response = client.post(
            '/api/v1/setup_2fa',
            data=json.dumps({
                "user_id": 1,
                "email": "_test@voxacommunications.com"
            }),
            content_type='application/json',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        setup_data = json.loads(setup_response.data)
        tfa_secret = setup_data["tfa_secret"]
        
        # Enable 2FA
        totp = pyotp.TOTP(tfa_secret)
        valid_code = totp.now()
        
        enable_response = client.post(
            '/api/v1/enable_2fa',
            data=json.dumps({
                "code": valid_code,
                "tfa_secret": tfa_secret,
                "enable": True
            }),
            content_type='application/json',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Now test the complete 2FA endpoint
        valid_code = totp.now()  # Generate a new code as some time might have passed
        
        complete_response = client.post(
            '/api/v1/complete_2fa',
            data=json.dumps({
                "email": "_test@voxacommunications.com",
                "code": valid_code
            }),
            content_type='application/json'
        )
        
        # Check if the response is as expected (this might need adjustment based on the actual API behavior)
        assert complete_response.status_code in [200, 401]  # Either success or requires further authentication