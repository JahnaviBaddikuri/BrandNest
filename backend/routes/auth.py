"""
Authentication Routes
Handles user authentication, profile fetching, and role management
"""

from flask import Blueprint, request, jsonify
from models import db, Creator, Brand
from firebase_auth import require_auth, get_firebase_user_from_request

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile(current_user):
    """
    Get user profile based on Firebase UID
    Returns creator or brand profile with role information
    
    Flow: Frontend sends Firebase token → Backend verifies → Returns profile
    """
    firebase_uid = current_user['uid']
    
    # Check if user is a creator
    creator = Creator.query.filter_by(firebase_uid=firebase_uid).first()
    if creator:
        profile = creator.to_dict()
        profile['role'] = 'creator'
        return jsonify({
            'status': 'success',
            'data': profile
        }), 200
    
    # Check if user is a brand
    brand = Brand.query.filter_by(firebase_uid=firebase_uid).first()
    if brand:
        profile = brand.to_dict()
        profile['role'] = 'brand'
        return jsonify({
            'status': 'success',
            'data': profile
        }), 200

    # Fallback: Try to locate profile by email and repair firebase_uid
    email = current_user.get('email')
    if email:
        creator = Creator.query.filter_by(email=email).first()
        if creator:
            creator.firebase_uid = firebase_uid
            db.session.commit()
            profile = creator.to_dict()
            profile['role'] = 'creator'
            return jsonify({
                'status': 'success',
                'data': profile
            }), 200

        brand = Brand.query.filter_by(email=email).first()
        if brand:
            brand.firebase_uid = firebase_uid
            db.session.commit()
            profile = brand.to_dict()
            profile['role'] = 'brand'
            return jsonify({
                'status': 'success',
                'data': profile
            }), 200
    
    # User authenticated but no profile exists
    return jsonify({
        'status': 'error',
        'message': 'Profile not found. Please complete your profile setup.',
        'firebase_uid': firebase_uid,
        'email': current_user.get('email')
    }), 404


@auth_bp.route('/verify', methods=['POST'])
def verify_token():
    """
    Verify Firebase token without fetching full profile
    Useful for quick auth checks
    """
    user = get_firebase_user_from_request()
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': 'Invalid token'
        }), 401
    
    return jsonify({
        'status': 'success',
        'data': {
            'uid': user['uid'],
            'email': user.get('email'),
            'email_verified': user.get('email_verified', False)
        }
    }), 200


@auth_bp.route('/check-profile', methods=['GET'])
@require_auth
def check_profile_exists(current_user):
    """
    Check if user has completed profile setup
    Returns existence status without full profile data
    """
    firebase_uid = current_user['uid']
    
    creator = Creator.query.filter_by(firebase_uid=firebase_uid).first()
    brand = Brand.query.filter_by(firebase_uid=firebase_uid).first()
    
    return jsonify({
        'status': 'success',
        'data': {
            'has_profile': bool(creator or brand),
            'profile_type': 'creator' if creator else ('brand' if brand else None)
        }
    }), 200
