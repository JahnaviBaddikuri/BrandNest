"""
OTP Utilities
Handles OTP generation and validation
"""

import random
from datetime import datetime, timedelta


def generate_otp(length=4):
    """
    Generate a random OTP code
    
    Args:
        length: Number of digits (default: 4)
    
    Returns:
        String OTP code
    """
    otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    return otp


def generate_otp_expiry(minutes=5):
    """
    Generate OTP expiry timestamp
    
    Args:
        minutes: Expiry time in minutes (default: 5)
    
    Returns:
        DateTime object
    """
    return datetime.utcnow() + timedelta(minutes=minutes)


def is_otp_valid(otp_code, otp_expiry, entered_otp):
    """
    Validate OTP code and expiry
    
    Args:
        otp_code: Stored OTP code
        otp_expiry: Stored OTP expiry datetime
        entered_otp: User entered OTP
    
    Returns:
        Tuple (is_valid: bool, error_message: str)
    """
    # Check if OTP exists
    if not otp_code or not otp_expiry:
        return False, "No OTP found. Please request a new one."
    
    # Check if OTP has expired
    if datetime.utcnow() > otp_expiry:
        return False, "OTP has expired. Please request a new one."
    
    # Check if OTP matches
    if otp_code != entered_otp:
        return False, "Invalid OTP. Please try again."
    
    return True, "OTP verified successfully"
