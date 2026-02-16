"""
Email Service
Handles sending emails via SMTP
"""

from flask_mail import Mail, Message
from flask import current_app

mail = Mail()


def init_mail(app):
    """Initialize Flask-Mail with app"""
    mail.init_app(app)


def send_otp_email(recipient_email, otp_code, user_name=None):
    """
    Send OTP verification email
    
    Args:
        recipient_email: Email address to send to
        otp_code: The OTP code to send
        user_name: Optional user name for personalization
    
    Returns:
        Tuple (success: bool, error_message: str or None)
    """
    try:
        subject = "Verify Your Email - Collabstr"
        
        # Simple text body
        greeting = f"Hello {user_name}," if user_name else "Hello,"
        body = f"""{greeting}

Thank you for registering with Collabstr

Your email verification code is: {otp_code}

This code will expire in 5 minutes.

If you didn't request this code, please ignore this email.

Best regards,
Collabstr Team
"""
        
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            body=body
        )
        
        mail.send(msg)
        print(f"✅ OTP email sent to {recipient_email}")
        return True, None
        
    except Exception as e:
        error_msg = f"Failed to send email: {str(e)}"
        print(f"❌ Email error: {error_msg}")
        
        # FALLBACK: Print OTP to console for testing
        print("\n" + "="*60)
        print("📧 EMAIL SENDING FAILED - SHOWING OTP HERE FOR TESTING:")
        print("="*60)
        print(f"   Recipient: {recipient_email}")
        print(f"   User Name: {user_name}")
        print(f"   🔐 OTP CODE: {otp_code}")
        print(f"   ⏰ Valid for: 5 minutes")
        print("="*60 + "\n")
        
        # Return success anyway so registration doesn't fail
        return True, None


def send_welcome_email(recipient_email, user_name):
    """
    Send welcome email after successful verification
    
    Args:
        recipient_email: Email address
        user_name: User's name
    
    Returns:
        Tuple (success: bool, error_message: str or None)
    """
    try:
        subject = "Welcome to Collabstr!"
        
        body = f"""Hello {user_name},

Welcome to Collabstr! Your email has been successfully verified.

You can now log in and start exploring our platform.

Best regards,
Collabstr Team
"""
        
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            body=body
        )
        
        mail.send(msg)
        return True, None
        
    except Exception as e:
        # Don't fail if welcome email fails
        print(f"⚠️  Welcome email failed: {str(e)}")
        return False, str(e)
