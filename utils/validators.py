import re


def validate_email(email):
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    Validate password strength
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter (optional but recommended)
    """
    if not password or len(password) < 8:
        return False
    return True


def validate_phone(phone):
    """Validate phone number"""
    # Simple validation - adjust as needed for your region
    pattern = r"^\+?1?\d{9,15}$"
    return re.match(pattern, phone) is not None


def validate_slug(slug):
    """Validate slug format"""
    pattern = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    return re.match(pattern, slug) is not None


def validate_url(url):
    """Validate URL format"""
    pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    return re.match(pattern, url, re.IGNORECASE) is not None
