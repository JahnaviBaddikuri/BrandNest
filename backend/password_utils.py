"""
Password Utilities Module
Provides secure password hashing and verification using Werkzeug
"""

from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password):
    """
    Hash a password using Werkzeug's secure password hashing (PBKDF2)
    
    Args:
        password (str): Plain text password
        
    Returns:
        str: Hashed password suitable for database storage
    """
    return generate_password_hash(password, method='pbkdf2:sha256')


def verify_password(password_hash, password):
    """
    Verify a password against its hash
    
    Args:
        password_hash (str): Stored password hash from database
        password (str): Plain text password to verify
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return check_password_hash(password_hash, password)


def validate_password_strength(password):
    """
    Validate password meets minimum security requirements
    
    Requirements:
        - At least 6 characters long
        - Contains at least one letter
        - Contains at least one number (optional but recommended)
    
    Args:
        password (str): Password to validate
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    if not any(c.isalpha() for c in password):
        return False, "Password must contain at least one letter"
    
    # Optional: Uncomment for stricter validation
    # if not any(c.isdigit() for c in password):
    #     return False, "Password must contain at least one number"
    
    return True, None
