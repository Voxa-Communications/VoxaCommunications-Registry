"""
Tests for the authentication API endpoints.
Covers register.py and login.py
"""
import json
import pytest
import os
import re
from flask import session


class TestAuthentication:
    """Test class for authentication API endpoints."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        # Generate random email to avoid conflicts
        import random
        import string
        random_str = ''.join(random.choices(string.ascii_lowercase, k=8))
        test_data = {
            "name": f"_TEST_{random_str}",
            "email": f"_test_{random_str}@voxacommunications.com",
            "password": "Test_Password123!"
        }
        
        response = client.post(
            '/api/v1/register',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        assert response.status_code == 201
        assert "message" in data
        assert "user_id" in data
        assert data["message"] == "User created successfully. Please log in."
    
    def test_register_invalid_data(self, client):
        """Test registration with invalid data."""
        test_cases = [
            # Missing required fields
            ({"name": "_TEST_user"}, "Missing required fields"),
            ({"email": "_test@voxacommunications.com"}, "Missing required fields"),
            ({"password": "Test_Password123!"}, "Missing required fields"),
            # Invalid email format
            ({"name": "_TEST_user", "email": "invalid_email", "password": "Test_Password123!"}, "Invalid email format"),
            # Weak password
            ({"name": "_TEST_user", "email": "_test@voxacommunications.com", "password": "weak"}, "Password is too short")
        ]
        
        for test_data, expected_error in test_cases:
            response = client.post(
                '/api/v1/register',
                data=json.dumps(test_data),
                content_type='application/json'
            )
            
            data = json.loads(response.data)
            assert response.status_code == 400
            assert "error" in data
            assert expected_error in data["error"]
    
    def test_login_success(self, client, create_test_account):
        """Test successful login with valid credentials."""
        login_data = {
            "email": create_test_account["email"],
            "password": create_test_account["password"]
        }
        
        response = client.post(
            '/api/v1/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        assert response.status_code == 200
        assert "message" in data
        assert "token" in data
        assert "user_id" in data
        assert data["message"] == "Login successful"
        
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        test_cases = [
            # Non-existent user
            ({"email": "nonexistent@voxacommunications.com", "password": "Test_Password123!"}, "Invalid credentials"),
            # Wrong password
            ({"email": "_test@voxacommunications.com", "password": "WrongPassword123!"}, "Invalid credentials"),
            # Missing fields
            ({"email": "_test@voxacommunications.com"}, "Missing email or password"),
            ({"password": "Test_Password123!"}, "Missing email or password"),
            # Invalid email format
            ({"email": "invalid_email", "password": "Test_Password123!"}, "Invalid email format")
        ]
        
        for test_data, expected_error in test_cases:
            response = client.post(
                '/api/v1/login',
                data=json.dumps(test_data),
                content_type='application/json'
            )
            
            data = json.loads(response.data)
            assert response.status_code in [400, 401]
            assert "error" in data
            assert expected_error in data["error"]
    
    def test_method_not_allowed(self, client):
        """Test method not allowed for both endpoints."""
        endpoints = ["/api/v1/register", "/api/v1/login"]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code in [405, 302]  # Either method not allowed or redirect