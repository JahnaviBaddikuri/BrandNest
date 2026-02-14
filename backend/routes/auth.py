"""
Authentication Routes
Handles user registration, login, profile management, and JWT token operations
"""

from flask import Blueprint, request, jsonify
from models import db, Creator, Brand
from jwt_auth import require_auth, get_user_from_request, generate_token
from password_utils import validate_password_strength

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register/creator', methods=['POST'])
def register_creator():
    """
    Register a new creator with email and password
    
    Expected JSON:
        {
            "email": "user@example.com",
            "password": "securepassword",
            "username": "username",
            "platform": "instagram",
            "category": "fashion",
            "rate": 100.0,
            ... other creator fields
        }
    
    Returns:
        201: Success with JWT token and profile
        400: Validation errors
        409: User already exists
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['email', 'password', 'username', 'platform', 'category', 'rate']
        missing = [field for field in required if not data.get(field)]
        if missing:
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing)}'
            }), 400
        
        # Validate password strength
        is_valid, error_msg = validate_password_strength(data['password'])
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': error_msg
            }), 400
        
        # Check if email already exists
        if Creator.query.filter_by(email=data['email']).first():
            return jsonify({
                'status': 'error',
                'message': 'Email already registered as creator'
            }), 409
        
        # Check if username already exists
        if Creator.query.filter_by(username=data['username']).first():
            return jsonify({
                'status': 'error',
                'message': 'Username already taken'
            }), 409
        
        # Create new creator
        creator = Creator(
            username=data['username'],
            email=data['email'],
            platform=data.get('platform', 'instagram'),
            category=data['category'],
            rate=float(data['rate']),
            followers_count=data.get('followers_count', 0),
            engagement_rate=data.get('engagement_rate', 0.0),
            location=data.get('location'),
            bio=data.get('bio'),
            profile_image_url=data.get('profile_image_url', '')
        )
        
        # Set password (this hashes it)
        creator.set_password(data['password'])
        
        # Save to database
        db.session.add(creator)
        db.session.commit()
        
        # Generate JWT token
        token = generate_token(
            user_id=creator.id,
            email=creator.email,
            role='creator'
        )
        
        # Return success with token and profile
        return jsonify({
            'status': 'success',
            'message': 'Creator account created successfully',
            'data': {
                'token': token,
                'user': creator.to_dict(),
                'role': 'creator'
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Registration failed: {str(e)}'
        }), 500


@auth_bp.route('/register/brand', methods=['POST'])
def register_brand():
    """
    Register a new brand with email and password
    
    Expected JSON:
        {
            "email": "brand@example.com",
            "password": "securepassword",
            "company_name": "Brand Name",
            "industry": "E-commerce",
            ... other brand fields
        }
    
    Returns:
        201: Success with JWT token and profile
        400: Validation errors
        409: User already exists
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['email', 'password', 'company_name', 'industry']
        missing = [field for field in required if not data.get(field)]
        if missing:
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing)}'
            }), 400
        
        # Validate password strength
        is_valid, error_msg = validate_password_strength(data['password'])
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': error_msg
            }), 400
        
        # Check if email already exists
        if Brand.query.filter_by(email=data['email']).first():
            return jsonify({
                'status': 'error',
                'message': 'Email already registered as brand'
            }), 409
        
        # Check if company name already exists
        if Brand.query.filter_by(company_name=data['company_name']).first():
            return jsonify({
                'status': 'error',
                'message': 'Company name already registered'
            }), 409
        
        # Create new brand
        brand = Brand(
            company_name=data['company_name'],
            email=data['email'],
            industry=data['industry'],
            location=data.get('location'),
            website=data.get('website'),
            logo_url=data.get('logo_url', '')
        )
        
        # Set password (this hashes it)
        brand.set_password(data['password'])
        
        # Save to database
        db.session.add(brand)
        db.session.commit()
        
        # Generate JWT token
        token = generate_token(
            user_id=brand.id,
            email=brand.email,
            role='brand'
        )
        
        # Return success with token and profile
        return jsonify({
            'status': 'success',
            'message': 'Brand account created successfully',
            'data': {
                'token': token,
                'user': brand.to_dict(),
                'role': 'brand'
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Registration failed: {str(e)}'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login with email, password, and role
    
    Expected JSON:
        {
            "email": "user@example.com",
            "password": "password",
            "role": "creator" or "brand"
        }
    
    Returns:
        200: Success with JWT token and profile
        400: Missing fields
        401: Invalid credentials or role mismatch
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        
        if not all([email, password, role]):
            return jsonify({
                'status': 'error',
                'message': 'Email, password, and role are required'
            }), 400
        
        if role not in ['creator', 'brand']:
            return jsonify({
                'status': 'error',
                'message': 'Role must be either "creator" or "brand"'
            }), 400
        
        # Find user based on role
        user = None
        if role == 'creator':
            user = Creator.query.filter_by(email=email).first()
        else:
            user = Brand.query.filter_by(email=email).first()
        
        # Check if user exists
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'Invalid email or password'
            }), 401
        
        # Verify password
        if not user.check_password(password):
            return jsonify({
                'status': 'error',
                'message': 'Invalid email or password'
            }), 401
        
        # Generate JWT token
        token = generate_token(
            user_id=user.id,
            email=user.email,
            role=role
        )
        
        # Return success with token and profile
        profile = user.to_dict()
        profile['role'] = role
        
        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'data': {
                'token': token,
                'user': profile,
                'role': role
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Login failed: {str(e)}'
        }), 500


@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile(current_user):
    """
    Get user profile based on JWT token
    Returns creator or brand profile with role information
    
    Protected route - requires valid JWT token in Authorization header
    """
    user_id = current_user['user_id']
    role = current_user['role']
    
    try:
        # Find user based on role
        if role == 'creator':
            user = Creator.query.get(user_id)
        elif role == 'brand':
            user = Brand.query.get(user_id)
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid role in token'
            }), 400
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        # Return profile with role
        profile = user.to_dict()
        profile['role'] = role
        
        return jsonify({
            'status': 'success',
            'data': profile
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch profile: {str(e)}'
        }), 500


@auth_bp.route('/verify', methods=['POST'])
def verify_token():
    """
    Verify JWT token without fetching full profile
    Useful for quick auth checks
    
    Returns decoded token data if valid
    """
    user = get_user_from_request()
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': 'Invalid or expired token'
        }), 401
    
    return jsonify({
        'status': 'success',
        'data': {
            'user_id': user['user_id'],
            'email': user.get('email'),
            'role': user.get('role')
        }
    }), 200


@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user(current_user):
    """
    Get current authenticated user info from token
    Lightweight endpoint that doesn't query database
    """
    return jsonify({
        'status': 'success',
        'data': {
            'user_id': current_user['user_id'],
            'email': current_user['email'],
            'role': current_user['role']
        }
    }), 200
