"""
Authentication Service
Handles user signup, login, password reset, and email verification
"""

import os
import secrets
from datetime import datetime, timedelta
from extensions import db
from models.user import User
from flask import current_app
from utils.validators import validate_email, validate_password


class AuthService:
    """Service for handling authentication operations"""

    @staticmethod
    def signup(login, email, name, password):
        """
        Create a new user account
        
        Args:
            login: Username (unique, alphanumeric)
            email: User email (unique)
            name: User's full name
            password: User's password (min 8 chars)
        
        Returns:
            tuple: (user, error_message)
        """
        # Validate inputs
        if not login or len(login) < 3:
            return None, "Username must be at least 3 characters"
        
        if not validate_email(email):
            return None, "Invalid email address"
        
        if not validate_password(password):
            return None, "Password must be at least 8 characters"
        
        # Check if user exists
        if User.query.filter_by(login=login.lower()).first():
            return None, "Username already taken"
        
        if User.query.filter_by(email=email.lower()).first():
            return None, "Email already registered"
        
        try:
            user = User(
                login=login.lower(),
                email=email.lower(),
                name=name or login,
                is_active=True,
                email_verified=False  # Email verification required
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            current_app.logger.info(f"New user signup: {login} ({email})")
            return user, None
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Signup error: {str(e)}")
            return None, "An error occurred during signup"

    @staticmethod
    def login(login_or_email, password):
        """
        Authenticate user with login/email and password
        
        Args:
            login_or_email: Username or email
            password: User's password
        
        Returns:
            tuple: (user, error_message)
        """
        if not login_or_email or not password:
            return None, "Username and password required"
        
        # Find user by login or email
        user = User.query.filter(
            db.or_(
                User.login == login_or_email.lower(),
                User.email == login_or_email.lower()
            )
        ).first()
        
        if not user:
            return None, "Invalid credentials"
        
        # Check if account is locked
        if user.is_locked():
            return None, "Account locked due to too many failed attempts"
        
        # Verify password
        if not user.check_password(password):
            user.record_failed_login()
            return None, "Invalid credentials"
        
        # Check if account is active
        if not user.is_active:
            return None, "Account is disabled"
        
        # Record successful login
        user.record_login()
        current_app.logger.info(f"User login: {user.login}")
        return user, None

    @staticmethod
    def request_password_reset(email):
        """
        Generate password reset token for user
        
        Args:
            email: User's email address
        
        Returns:
            tuple: (user, error_message, token)
        """
        user = User.query.filter_by(email=email.lower()).first()
        
        if not user:
            # Don't reveal if email exists
            return None, None, None
        
        try:
            # Generate secure token
            token = secrets.token_urlsafe(32)
            user.password_reset_token = token
            user.password_reset_expires = datetime.utcnow() + timedelta(hours=24)
            
            db.session.commit()
            current_app.logger.info(f"Password reset requested for: {user.email}")
            return user, None, token
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Password reset request error: {str(e)}")
            return None, "An error occurred", None

    @staticmethod
    def reset_password(token, new_password):
        """
        Reset user password using token
        
        Args:
            token: Password reset token
            new_password: New password
        
        Returns:
            tuple: (user, error_message)
        """
        if not token or not new_password:
            return None, "Token and new password required"
        
        # Find user by token
        user = User.query.filter_by(password_reset_token=token).first()
        
        if not user:
            return None, "Invalid or expired token"
        
        # Check if token has expired
        if user.password_reset_expires < datetime.utcnow():
            user.password_reset_token = None
            user.password_reset_expires = None
            db.session.commit()
            return None, "Token has expired"
        
        try:
            if not validate_password(new_password):
                return None, "Password must be at least 8 characters"
            
            user.set_password(new_password)
            user.password_reset_token = None
            user.password_reset_expires = None
            
            db.session.commit()
            current_app.logger.info(f"Password reset successful for: {user.email}")
            return user, None
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Password reset error: {str(e)}")
            return None, "An error occurred during password reset"

    @staticmethod
    def verify_email(user_id, token):
        """
        Verify user email with token
        
        Args:
            user_id: User ID
            token: Email verification token
        
        Returns:
            tuple: (user, error_message)
        """
        user = User.query.get(user_id)
        
        if not user:
            return None, "User not found"
        
        if user.email_verified:
            return user, None
        
        # In a real system, you would verify the token
        # For now, we'll allow manual verification
        try:
            user.email_verified = True
            user.email_verified_at = datetime.utcnow()
            db.session.commit()
            current_app.logger.info(f"Email verified for: {user.email}")
            return user, None
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Email verification error: {str(e)}")
            return None, "An error occurred during email verification"

    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        return User.query.filter_by(email=email.lower()).first()

    @staticmethod
    def get_user_by_login(login):
        """Get user by login"""
        return User.query.filter_by(login=login.lower()).first()
