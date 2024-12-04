import json
import time
import uuid
import os
import base64
from flask import Flask, jsonify, request
import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Constants
JWT_EXPIRY_DURATION = 600  # 10 minutes
JWT_ALGORITHM = "RS256"
KEY_FILE_PATH = 'keys/key.json'
DEFAULT_EXPIRY_TIME = 3600  # 1 hour expiry

app = Flask(__name__)

def jwk_from_rsa_public_key(public_key):
    """Convert RSA public key to JWK format."""
    numbers = public_key.public_numbers()
    n = base64.urlsafe_b64encode(numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, 'big')).decode('utf-8').rstrip('=')
    e = base64.urlsafe_b64encode(numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, 'big')).decode('utf-8').rstrip('=')
    return {
        "kty": "RSA",
        "use": "sig",
        "alg": "RS256",
        "n": n,
        "e": e
    }

def generate_rsa_key(expiry=DEFAULT_EXPIRY_TIME):
    """Generate RSA key pair with a unique key ID and expiry timestamp."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    kid = str(uuid.uuid4())  # Unique key ID
    expiry_timestamp = time.time() + expiry  # Calculate expiry time

    return {
        "kid": kid,
        "private_key": private_pem.decode('utf-8'),
        "public_key": public_pem.decode('utf-8'),
        "expiry": expiry_timestamp
    }

def save_key_to_file():
    """Generate a new RSA key pair and save it to a file."""
    try:
        key_data = generate_rsa_key()
        os.makedirs(os.path.dirname(KEY_FILE_PATH), exist_ok=True)  # Ensure directory exists
        with open(KEY_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(key_data, f, indent=4)  # Pretty-print JSON for readability
        print("Key saved successfully.")
    except Exception as e:
        print(f"Failed to save key: {e}")

def load_key_from_file():
    """Load RSA key data from a JSON file."""
    try:
        if os.path.exists(KEY_FILE_PATH):
            with open(KEY_FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print("Key file does not exist.")
            return None
    except Exception as e:
        print(f"Error loading key: {e}")
        return None
    
# Load key on startup
key_data = load_key_from_file()

@app.route('/')
def home():
    """Simple home route to indicate that the server is running."""
    return "JWKS Server Running!"

@app.route('/.well-known/jwks.json', methods=['GET'])
def jwks():
    global key_data
    """Serve JWKS with the public key if it has not expired."""
    if key_data and key_data['expiry'] > time.time():
        public_key = serialization.load_pem_public_key(
            key_data['public_key'].encode('utf-8'),
            backend=default_backend()
        )
        jwk = jwk_from_rsa_public_key(public_key)
        jwk["kid"] = key_data['kid']
        return jsonify({"keys": [jwk]})
    else:
        # Regenerate the key if expired or not available
        save_key_to_file()
        key_data = load_key_from_file()
        return jsonify({"keys": []})

@app.route('/auth', methods=['POST'])
def auth():
    """Generate a JWT token, with an optional expired token based on a query parameter."""
    global key_data
    if not key_data:
        save_key_to_file()
        key_data = load_key_from_file()

    expired = request.args.get('expired')
    now = time.time()

    # Create JWT payload
    payload = {
        "sub": "user123",
        "iat": now,
        "exp": now + JWT_EXPIRY_DURATION if not expired else now - 60  # Expire token based on query param
    }

    try:
        token = jwt.encode(payload, key_data['private_key'], algorithm=JWT_ALGORITHM, headers={"kid": key_data['kid']})
        return jsonify({"token": token})
    except Exception as e:
        return jsonify({"error": f"Error generating token: {e}"}), 500

# Ensure the key exists when app starts
save_key_to_file()

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080)