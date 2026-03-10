import os
import json
import re
import hmac

from functools import wraps
from flask import session, redirect, url_for, request

from werkzeug.security import check_password_hash


# ---------------------------------------------------
# Paths
# ---------------------------------------------------

CREDENTIALS_PATH = os.path.join("instance", "admin_credentials.json")


# ---------------------------------------------------
# Credential Storage
# ---------------------------------------------------

def load_credentials():
    """
    Load admin credentials from instance JSON file.
    """
    try:
        if os.path.exists(CREDENTIALS_PATH):
            with open(CREDENTIALS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        return None

    return None


def save_credentials(login, password_hash):
    """
    Save admin credentials to instance JSON file.
    """

    data = {
        "login": login,
        "password_hash": password_hash
    }

    instance_dir = os.path.dirname(CREDENTIALS_PATH)

    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir, exist_ok=True)

    with open(CREDENTIALS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)


# ---------------------------------------------------
# Password Security
# ---------------------------------------------------

def is_strong_password(password: str) -> bool:
    """
    Validate strong password:
    - Minimum 8 characters
    - Uppercase
    - Lowercase
    - Digit
    - Special character
    """

    if not password or len(password) < 8:
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"\d", password):
        return False

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False

    return True


# ---------------------------------------------------
# Authentication Checks
# ---------------------------------------------------

def check_admin_auth():
    """
    Check if request is authenticated as admin.
    Supports:
    - session login
    - HTTP Basic Auth fallback
    """

    # Session login
    if session.get("admin_logged_in"):
        return True

    # HTTP Basic Auth fallback
    auth = request.authorization
    creds = load_credentials()

    if auth and creds:

        stored_login = creds.get("login")
        stored_hash = creds.get("password_hash")

        if stored_login and stored_hash:

            if (
                hmac.compare_digest(auth.username or "", stored_login)
                and check_password_hash(stored_hash, auth.password or "")
            ):
                return True

    return False


# ---------------------------------------------------
# Route Protection Decorator
# ---------------------------------------------------

def admin_required(f):
    """
    Protect admin routes.
    Redirects to admin login if not authenticated.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):

        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_bp.admin_login"))

        return f(*args, **kwargs)

    return wrapper