"""
JWT Authentication Module
Provides JWT token generation, verification, and authentication decorators
"""

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app


def generate_token(user_id, email, role, expiration_hours=168):
    """
    Generate JWT token for authenticated user
    
    Args:
        user_id (int): Database user ID
        email (str): User email
        role (str): User role ('creator' or 'brand')
        expiration_hours (int): Token expiration time in hours (default: 168 = 7 days)
        
    Returns:
        str: JWT token
    """
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'iat': datetime.utcnow(),  # Issued at
        'exp': datetime.utcnow() + timedelta(hours=expiration_hours)  # Expiration
    }
    
    token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    return token


def verify_token(token):
    """
    Verify JWT token and return decoded payload
    
    Args:
        token (str): JWT token string
        
    Returns:
        dict: Decoded token payload with user info
        None: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        print("⚠️ Token verification failed: Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"⚠️ Token verification failed: {e}")
        return None


def require_auth(f):
    """
    Decorator to protect routes requiring authentication
    Extracts and verifies JWT token from Authorization header
    
    Usage:
        @require_auth
        def protected_route(current_user):
            # current_user contains decoded token data
            user_id = current_user['user_id']
            role = current_user['role']
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'status': 'error',
                'message': 'Missing or invalid authorization header'
            }), 401
        
        token = auth_header.replace('Bearer ', '')
        
        # Verify token
        decoded_token = verify_token(token)
        
        if not decoded_token:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired token'
            }), 401
        
        # Add user info to kwargs
        kwargs['current_user'] = decoded_token
        
        return f(*args, **kwargs)
    
    return decorated_function


def get_user_from_request():
    """
    Extract and verify user from Authorization header without decorator
    Useful for optional authentication endpoints
    
    Returns:
        dict: Decoded token with user info
        None: If token is missing or invalid
    """
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.replace('Bearer ', '')
    return verify_token(token)
