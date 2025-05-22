"""
Tests for token management API endpoints.
Covers create_token.py
"""
import json
import pytest
import re


class TestTokens:
    """Test class for token management API endpoints."""
    
    def test_create_token(self, client, authenticated_client):
        """Test creating a new API token."""
        client, token = authenticated_client
        
        # Create test data for token creation
        test_data = {
            "token_name": "_TEST_Token",
            "scopes": ["read", "write"],
            "expiration": "30d"  # 30 days expiration
        }
        
        response = client.post(
            '/api/v1/create_token',
            data=json.dumps(test_data),
            content_type='application/json',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = json.loads(response.data)
        assert response.status_code == 201
        assert "message" in data
        assert "token" in data
        assert "Token created successfully" in data["message"]
        
        # Check that the token is in the expected format (JWT or similar)
        assert re.match(r'^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$', data["token"])
        
    def test_create_token_invalid_data(self, client, authenticated_client):
        """Test token creation with invalid data."""
        client, token = authenticated_client
        
        test_cases = [
            # Missing required fields
            ({"token_name": "_TEST_Token"}, "Missing required fields"),
            ({"scopes": ["read", "write"]}, "Missing required fields"),
            # Invalid scopes
            ({"token_name": "_TEST_Token", "scopes": ["invalid_scope"], "expiration": "30d"}, "Invalid scope"),
            # Invalid expiration
            ({"token_name": "_TEST_Token", "scopes": ["read"], "expiration": "invalid"}, "Invalid expiration format")
        ]
        
        for test_data, expected_error in test_cases:
            response = client.post(
                '/api/v1/create_token',
                data=json.dumps(test_data),
                content_type='application/json',
                headers={"Authorization": f"Bearer {token}"}
            )
            
            data = json.loads(response.data)
            assert response.status_code == 400
            assert "error" in data
            assert expected_error in data["error"] or data["error"].startswith(expected_error)
    
    def test_create_token_unauthorized(self, client):
        """Test creating a token without authentication."""
        test_data = {
            "token_name": "_TEST_Token",
            "scopes": ["read", "write"],
            "expiration": "30d"
        }
        
        response = client.post(
            '/api/v1/create_token',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert "error" in data