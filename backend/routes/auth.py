"""
Authentication Routes
Handles user registration, login, profile management, and JWT token operations
"""

from flask import Blueprint, request, jsonify
from models import db, Creator, Brand
from jwt_auth import require_auth, get_user_from_request, generate_token
from password_utils import validate_password_strength
from otp_utils import generate_otp, generate_otp_expiry, is_otp_valid
from email_service import send_otp_email

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
            profile_image_url=data.get('profile_image_url', ''),
            email_verified=False  # Not verified yet
        )
        
        # Set password (this hashes it)
        creator.set_password(data['password'])
        
        # Generate OTP
        otp_code = generate_otp(length=4)
        creator.otp_code = otp_code
        creator.otp_expiry = generate_otp_expiry(minutes=5)
        
        # Save to database
        db.session.add(creator)
        db.session.commit()
        
        # Send OTP email
        email_sent, email_error = send_otp_email(
            recipient_email=creator.email,
            otp_code=otp_code,
            user_name=creator.username
        )
        
        if not email_sent:
            print(f"⚠️  Failed to send OTP email: {email_error}")
            # Don't fail registration if email fails
        
        # Return success WITHOUT token (user must verify email first)
        return jsonify({
            'status': 'success',
            'message': 'Account created successfully. Please check your email for verification code.',
            'data': {
                'email': creator.email,
                'user_id': creator.id,
                'role': 'creator',
                'requires_verification': True
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
            logo_url=data.get('logo_url', ''),
            email_verified=False  # Not verified yet
        )
        
        # Set password (this hashes it)
        brand.set_password(data['password'])
        
        # Generate OTP
        otp_code = generate_otp(length=4)
        brand.otp_code = otp_code
        brand.otp_expiry = generate_otp_expiry(minutes=5)
        
        # Save to database
        db.session.add(brand)
        db.session.commit()
        
        # Send OTP email
        email_sent, email_error = send_otp_email(
            recipient_email=brand.email,
            otp_code=otp_code,
            user_name=brand.company_name
        )
        
        if not email_sent:
            print(f"⚠️  Failed to send OTP email: {email_error}")
            # Don't fail registration if email fails
        
        # Return success WITHOUT token (user must verify email first)
        return jsonify({
            'status': 'success',
            'message': 'Account created successfully. Please check your email for verification code.',
            'data': {
                'email': brand.email,
                'user_id': brand.id,
                'role': 'brand',
                'requires_verification': True
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
        
        # Check if email is verified (treat NULL as verified for existing users)
        if hasattr(user, 'email_verified') and user.email_verified is False:
            return jsonify({
                'status': 'error',
                'message': 'Please verify your email before logging in. Check your email for the verification code.',
                'requires_verification': True,
                'email': user.email
            }), 403
        
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


@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """
    Verify email with OTP code
    
    Expected JSON:
        {
            "email": "user@example.com",
            "otp": "1234",
            "role": "creator" or "brand"
        }
    
    Returns:
        200: Email verified successfully
        400: Invalid or expired OTP
        404: User not found
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        email = data.get('email')
        otp = data.get('otp')
        role = data.get('role')
        
        if not all([email, otp, role]):
            return jsonify({
                'status': 'error',
                'message': 'Email, OTP, and role are required'
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
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        # Check if already verified
        if user.email_verified:
            return jsonify({
                'status': 'success',
                'message': 'Email already verified. You can now log in.',
                'already_verified': True
            }), 200
        
        # Validate OTP
        is_valid, error_message = is_otp_valid(user.otp_code, user.otp_expiry, otp)
        
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': error_message
            }), 400
        
        # Mark email as verified
        user.email_verified = True
        user.otp_code = None  # Clear OTP
        user.otp_expiry = None
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Email verified successfully! You can now log in.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Verification failed: {str(e)}'
        }), 500


@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """
    Resend OTP code to email
    
    Expected JSON:
        {
            "email": "user@example.com",
            "role": "creator" or "brand"
        }
    
    Returns:
        200: OTP resent successfully
        404: User not found
        400: Email already verified
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        email = data.get('email')
        role = data.get('role')
        
        if not all([email, role]):
            return jsonify({
                'status': 'error',
                'message': 'Email and role are required'
            }), 400
        
        if role not in ['creator', 'brand']:
            return jsonify({
                'status': 'error',
                'message': 'Role must be either "creator" or "brand"'
            }), 400
        
        # Find user based on role
        user = None
        user_name = None
        if role == 'creator':
            user = Creator.query.filter_by(email=email).first()
            user_name = user.username if user else None
        else:
            user = Brand.query.filter_by(email=email).first()
            user_name = user.company_name if user else None
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        # Check if already verified
        if user.email_verified:
            return jsonify({
                'status': 'error',
                'message': 'Email already verified. You can log in now.'
            }), 400
        
        # Generate new OTP
        otp_code = generate_otp(length=4)
        user.otp_code = otp_code
        user.otp_expiry = generate_otp_expiry(minutes=5)
        db.session.commit()
        
        # Send OTP email
        email_sent, email_error = send_otp_email(
            recipient_email=user.email,
            otp_code=otp_code,
            user_name=user_name
        )
        
        if not email_sent:
            return jsonify({
                'status': 'error',
                'message': f'Failed to send email: {email_error}'
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': 'OTP has been resent to your email'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to resend OTP: {str(e)}'
        }), 500
