"""
Pytest configuration for VoxaCommunications-Registry API tests
"""
import os
import sys
import pytest
import tempfile
import json
from flask import Flask, session
from datetime import datetime

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import Main
from src.routes import Routes
from lib.dbManager import DBManager, set_global_db_manager
from util.sqlExecutor import SQLExecutor
from util.logging import log


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Create a temporary instance of the application
    logger = log()
    main = Main(logger)
    app = main.app
    
    # Set up the app for testing
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def test_account():
    """Fixture to provide test account credentials."""
    return {
        "name": "_TEST",
        "email": "_test@voxacommunications.com",
        "password": "Test_Password123!",
    }


@pytest.fixture
def create_test_account(client, test_account):
    """Create a test account if it doesn't exist."""
    # Try to login first to check if account exists
    login_data = {
        "email": test_account["email"],
        "password": test_account["password"]
    }
    
    login_response = client.post(
        '/api/v1/login', 
        data=json.dumps(login_data),
        content_type='application/json'
    )
    
    # If login fails with 401, account doesn't exist - create it
    if login_response.status_code == 401:
        response = client.post(
            '/api/v1/register',
            data=json.dumps(test_account),
            content_type='application/json'
        )
        
        assert response.status_code == 201, f"Failed to create test account: {response.data}"
        
    return test_account


@pytest.fixture
def authenticated_client(client, create_test_account):
    """A test client that is authenticated with the test account."""
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
    
    # Return client with auth token
    if response.status_code == 200:
        return client, data.get('token')
    elif response.status_code == 401 and data.get('requires_2fa'):
        # Handle 2FA if enabled
        pytest.fail("Test account has 2FA enabled, but test framework doesn't support it yet.")
    else:
        pytest.fail(f"Authentication failed: {response.data}")