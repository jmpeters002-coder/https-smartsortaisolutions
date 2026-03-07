def load_credentials():
    """Load admin credentials from instance JSON file."""
    try:
        if os.path.exists(CREDENTIALS_PATH):
            with open(CREDENTIALS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        return None
    return None


def save_credentials(login, password_hash):
    """Save admin credentials to instance JSON file."""
    data = {'login': login, 'password_hash': password_hash}
    # Ensure instance directory exists
    inst_dir = os.path.dirname(CREDENTIALS_PATH)
    if not os.path.exists(inst_dir):
        os.makedirs(inst_dir, exist_ok=True)
    with open(CREDENTIALS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f)


def is_strong_password(pw: str) -> bool:
    """Basic strong-password check: min 8, upper, lower, digit, special."""
    if not pw or len(pw) < 8:
        return False
    if not re.search(r'[a-z]', pw):
        return False
    if not re.search(r'[A-Z]', pw):
        return False
    if not re.search(r'\d', pw):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', pw):
        return False
    return True

def check_admin_auth():
    """Return True if the request has admin access via session or HTTP Basic auth."""
    # Session-based login
    if session.get('is_admin'):
        return True
     # HTTP Basic auth using stored credentials
    auth = request.authorization
    creds = load_credentials()
    if auth and creds:
        stored_login = creds.get('login')
        stored_hash = creds.get('password_hash')
        if stored_login and stored_hash:
            if hmac.compare_digest(auth.username or "", stored_login) and check_password_hash(stored_hash, auth.password or ""):
                return True

    return False
from functools import wraps
from flask import session, redirect, url_for

def admin_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if not session.get("is_admin"):
            return redirect(url_for("admin_bp.admin_login"))

        return f(*args, **kwargs)

    return wrapper