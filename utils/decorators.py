"""
Rate Limiting and Security Decorators
"""

from functools import wraps
from flask import request, jsonify, render_template
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Simple in-memory rate limit store (use Redis in production)
rate_limit_store = {}


def clean_rate_limits():
    """Remove expired entries from rate limit store"""
    now = datetime.utcnow()
    expired = [key for key, data in rate_limit_store.items() if data['expires'] < now]
    for key in expired:
        del rate_limit_store[key]


def rate_limit(max_requests=5, window_seconds=300):
    """
    Rate limiting decorator
    
    Args:
        max_requests: Max number of requests allowed
        window_seconds: Time window in seconds
    
    Usage:
        @rate_limit(max_requests=5, window_seconds=300)
        def my_route():
            return "success"
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Clean expired entries
            clean_rate_limits()
            
            # Get client identifier (IP address or user ID)
            if hasattr(request, 'user') and request.user:
                client_id = f"user_{request.user.id}"
            else:
                client_id = request.remote_addr
            
            # Create rate limit key
            limit_key = f"{client_id}:{request.endpoint}"
            
            now = datetime.utcnow()
            
            if limit_key not in rate_limit_store:
                rate_limit_store[limit_key] = {
                    'count': 1,
                    'expires': now + timedelta(seconds=window_seconds)
                }
            else:
                data = rate_limit_store[limit_key]
                
                # Check if window expired
                if data['expires'] < now:
                    rate_limit_store[limit_key] = {
                        'count': 1,
                        'expires': now + timedelta(seconds=window_seconds)
                    }
                else:
                    # Check if limit exceeded
                    if data['count'] >= max_requests:
                        logger.warning(f"Rate limit exceeded for {limit_key}")
                        
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return jsonify({'error': 'Too many requests. Please try again later.'}), 429
                        
                        return render_template('429.html'), 429
                    
                    data['count'] += 1
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def login_rate_limit(max_attempts=5, window_seconds=900):
    """
    Rate limiting specific for login attempts (15 min window, 5 attempts)
    """
    return rate_limit(max_requests=max_attempts, window_seconds=window_seconds)


def require_https(f):
    """Require HTTPS in production"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_secure and not request.remote_addr == '127.0.0.1':
            logger.warning(f"Non-HTTPS access attempted: {request.remote_addr}")
            return "HTTPS required", 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def validate_referer(allowed_origins=None):
    """Validate request referer for CSRF protection"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            referer = request.headers.get('Referer', '')
            
            if allowed_origins is None:
                # Use request host as default allowed origin
                allowed = [request.host_url.rstrip('/')]
            else:
                allowed = allowed_origins
            
            if referer and not any(origin in referer for origin in allowed):
                logger.warning(f"Invalid referer: {referer}")
                return "Invalid request", 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
