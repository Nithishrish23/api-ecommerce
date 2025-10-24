import jwt
from flask import request, session, jsonify
from functools import wraps
from datetime import datetime, timedelta

# Use a more secure secret key in production
SECRET_KEY = "pclinfo"  # Consider moving this to environment variables


def generate_token(user_data, expiration_minutes=60):
    """
    Generate a JWT token for the given user data
    """
    try:
        payload = user_data.copy()
        payload['exp'] = datetime.utcnow() + timedelta(minutes=expiration_minutes)
        payload['iat'] = datetime.utcnow()

        # Make sure we're using PyJWT's encode method
        token = jwt.encode(
            payload,
            SECRET_KEY,
            algorithm="HS256"
        )

        # PyJWT >= 2.0.0 returns string instead of bytes
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        return token

    except Exception as e:
        print(f"Token Generation Error: {str(e)}")
        return None


def validate_token(token):
    """
    Validate and decode the JWT token
    """
    if not token or not isinstance(token, str):
        return None

    try:
        decoded_payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        return decoded_payload

    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid Token Error: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected Token Validation Error: {str(e)}")
        return None


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        # Check Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(' ')[1]

        # Fallback to session token
        if not token:
            token = session.get('token')

        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401

        if not isinstance(token, str) or '.' not in token:
            return jsonify({'error': 'Invalid token format'}), 401

        decoded_token = validate_token(token)
        if not decoded_token:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Add decoded token to request object
        request.token_payload = decoded_token

        return f(*args, **kwargs)

    return decorated_function
