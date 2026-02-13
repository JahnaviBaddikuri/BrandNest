
import firebase_admin
from firebase_admin import credentials, auth
from functools import wraps
from flask import request, jsonify
import os


try:
    if not firebase_admin._apps:
        # Load service account credentials
        cred_path = os.path.join(os.path.dirname(__file__), 'firebase-credentials.json')
        
        if os.path.exists(cred_path):
            # Use real Firebase credentials
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print(" Firebase Admin SDK initialized with service account credentials")
        else:
            # Fallback: Try environment variable
            cred_path_env = os.getenv('FIREBASE_CREDENTIALS_PATH')
            if cred_path_env and os.path.exists(cred_path_env):
                cred = credentials.Certificate(cred_path_env)
                firebase_admin.initialize_app(cred)
                print(" Firebase Admin SDK initialized from environment variable")
            else:
                print("  WARNING: firebase-credentials.json not found!")
                print("   Download from: https://console.firebase.google.com/project/collabstr-5181a/settings/serviceaccounts/adminsdk")
                print("   Place at: d:\\collabstr\\backend\\firebase-credentials.json")
                raise FileNotFoundError("Firebase credentials not found")
except Exception as e:
    print(f" Firebase Admin SDK initialization failed: {e}")
    print("   Token verification will not work!")
    raise


def verify_firebase_token(token):
    """
    Verify Firebase ID token and return decoded token with user info
    
    Args:
        token (str): Firebase ID token from frontend
        
    Returns:
        dict: Decoded token with user info (uid, email, etc.)
        None: If token is invalid
    """
    try:
        # Verify token using Firebase Admin SDK
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print(f" Token verification failed: {e}")
        return None


def require_auth(f):
   
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
        decoded_token = verify_firebase_token(token)
        
        if not decoded_token:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired token'
            }), 401
        
        # Add user info to kwargs
        kwargs['current_user'] = decoded_token
        
        return f(*args, **kwargs)
    
    return decorated_function


def get_firebase_user_from_request():
 
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.replace('Bearer ', '')
    return verify_firebase_token(token)
