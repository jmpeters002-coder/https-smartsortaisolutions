from datetime import datetime
from extensions import db
from sqlalchemy import event
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Authentication
    login = db.Column(db.String(120), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200))
    password_hash = db.Column(db.String(255), nullable=False)

    # Account Status
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime)

    # Security
    failed_attempts = db.Column(db.Integer, default=0)
    last_failed_login = db.Column(db.DateTime)
    password_reset_token = db.Column(db.String(255))
    password_reset_expires = db.Column(db.DateTime)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    # Password handling
    def set_password(self, password):
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        self.password_hash = generate_password_hash(
            password,
            method="pbkdf2:sha256",
            salt_length=16
        )

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def record_login(self):
        """Record successful login attempt"""
        self.last_login = datetime.utcnow()
        self.failed_attempts = 0
        db.session.commit()

    def record_failed_login(self):
        """Record failed login attempt"""
        self.failed_attempts += 1
        self.last_failed_login = datetime.utcnow()
        db.session.commit()

    def is_locked(self):
        """Check if account is locked due to failed login attempts"""
        return self.failed_attempts >= 5

    def __repr__(self):
        return f"<User {self.login} ({self.email})>"

# Normalize login and email before saving
@event.listens_for(User, "before_insert")
def normalize_user_data(mapper, connection, target):
    if target.login:
        target.login = target.login.lower().strip()
    if target.email:
        target.email = target.email.lower().strip()