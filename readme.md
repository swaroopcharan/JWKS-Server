# JWKS Server

This project implements a simple JWKS (JSON Web Key Set) server using Flask, which provides a public key for verifying JWT (JSON Web Tokens). The server can generate RSA key pairs, expose them through a RESTful API, and handle expired keys for JWT verification.

## Features

- Generates and serves public keys in JWKS format.
- Supports key expiry, with automatic key refresh upon expiration.
- Can generate JWTs (valid and expired) using RSA keys.
- Provides a simple `/auth` endpoint to generate JWT tokens.
- Supports key rotation and regeneration.

---

## Requirements

### Prerequisites
- Python 3.x
- Flask
- PyJWT
- Cryptography

---

## Installation

### Clone this repository:
```bash
git clone https://github.com/swaroopcharan/JWKS-Server.git
cd jwks-server
```


## Set up a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
```

### Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Install the requirements manually:
```bash
pip install Flask pyjwt cryptography pytest
```

## Running the Server
1. Ensure you are in the project directory.
2. Run the Flask App
   ```bash
   python app.py
   ```
3. The server will start on http://127.0.0.1:8080.

### Visit the following end points
Home route:
GET / – Displays "JWKS Server Running!".

JWKS endpoint:
GET /.well-known/jwks.json – Serves the public keys in JWKS format.

Auth endpoint:
POST /auth – Generates a new JWT token.

Auth with expired token:
POST /auth?expired=true – Generates an expired JWT token.


## Testing:

To ensure everything works correctly, you can run the test suite using pytest.

### Running Tests:
1. Ensure you have installed the necessary dependencies (Flask, pytest, etc.).
2. Run the tests:
   ```bash
   pytest test_app.py
   ```
3. This will run the test cases to check the functionality of the endpoints, key generation, JWT creation, and error handling.

### Test Coverage:
Home route
JWKS endpoint (with valid and expired keys)
/auth endpoint (with valid and expired tokens)
Error handling when no key is available

## Project Structure
jwks-server/
│
├── app.py              # Main Flask application
├── test_app.py         # Test suite using pytest
├── keys/               # Directory to store generated keys
│   └── key.json        # RSA key pair
├── requirements.txt    # List of required Python packages
└── README.md           # Project documentation


## Code Explanation
### Key Generation:
The server generates an RSA key pair, which is then serialized and saved as a .pem file. The key is used for signing JWT tokens and for public key exposure in JWKS format.

### JWKS Endpoint:
The /jwks endpoint serves the public key in JWK format. If the key is expired, a new key is generated and used for JWT signing.

### JWT Generation:
The /auth endpoint creates a JWT token using the private key. The expired query parameter can be used to generate a token with an expiration in the past, simulating an expired token.

### Key Expiry:
Keys are considered expired after 1 hour by default. If the key is expired, a new key pair is generated automatically.

## Future Improvements
Key Rotation: Implement automatic key rotation at regular intervals.
Error Handling: Add more comprehensive error handling for edge cases.
Authentication: Integrate with a proper authentication system in real-world applications.
