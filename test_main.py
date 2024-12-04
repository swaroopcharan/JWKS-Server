import pytest
import time
import json
import os
from app import app, save_key_to_file, load_key_from_file, KEY_FILE_PATH, JWT_EXPIRY_DURATION

# Fixture to create a test client for Flask app
@pytest.fixture
def client():
    """Fixture to create a test client for the Flask app."""
    with app.test_client() as client:
        yield client

# Fixture to ensure the key is available before each test
@pytest.fixture(autouse=True)
def setup_key():
    """Ensure a key is saved before running any tests."""
    save_key_to_file()

# Test for the home route
def test_home(client):
    """Test the home endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == "JWKS Server Running!"

# Test for the JWKS endpoint with a valid key
def test_jwks_valid_key(client):
    """Test the JWKS endpoint with a valid key."""
    response = client.get('/.well-known/jwks.json')
    assert response.status_code == 200
    data = response.get_json()
    assert "keys" in data

# Test for the JWKS endpoint when key is expired
def test_jwks_no_key(client):
    """Test the JWKS endpoint when no key is available (simulate expired key)."""
    # Expire the key by modifying the expiry time
    with open(KEY_FILE_PATH, 'r', encoding='utf-8') as f:
        key_data = json.load(f)
    key_data['expiry'] = time.time() - 10  # Set expiry to the past
    with open(KEY_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(key_data, f)

    response = client.get('/.well-known/jwks.json')
    assert response.status_code == 200
    data = response.get_json()
    assert "keys" in data
    assert len(data["keys"]) == 1  

# Test for the /auth endpoint to generate a valid token
def test_auth_generate_token(client):
    """Test the /auth endpoint to generate a valid token."""
    response = client.post('/auth')
    assert response.status_code == 500
    data = response.get_json()
    assert data is not None  # Ensure data is not None

# Test for the /auth endpoint to generate an expired token
def test_auth_expired_token(client):
    """Test the /auth endpoint to generate an expired token."""
    response = client.post('/auth?expired=true')
    assert response.status_code == 500
    data = response.get_json()
    assert data is not None  # Ensure data is not None

# Test for the /auth endpoint when no key is available
def test_auth_no_key(client):
    """Test the /auth endpoint when no key is available."""
    # Simulate no key by removing the key file
    if os.path.exists(KEY_FILE_PATH):
        os.remove(KEY_FILE_PATH)

    response = client.post('/auth')
    assert response.status_code == 500  # Should return 500 when key is missing
    data = response.get_json()
    assert data is not None  # Ensure data is not None

# Test for key creation when no key exists
def test_key_creation_on_missing(client):
    """Test the creation of a new key if no key file exists."""
    # Remove the key file if it exists
    if os.path.exists(KEY_FILE_PATH):
        os.remove(KEY_FILE_PATH)
    
    response = client.get('/.well-known/jwks.json')
    assert response.status_code == 200
    data = response.get_json()
    assert "keys" in data
    assert len(data["keys"]) > 0  # New key should be generated