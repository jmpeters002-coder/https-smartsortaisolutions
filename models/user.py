from datetime import datetime
from extensions import db
from sqlalchemy import event
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    login = db.Column(db.String(120), unique=True, nullable=False, index=True)

    password_hash = db.Column(db.String(255), nullable=False)

    is_admin = db.Column(db.Boolean, default=False)

    failed_attempts = db.Column(db.Integer, default=0)

    last_failed_login = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

    def __repr__(self):
        return f"<User {self.login}>"

# Normalize login before saving
@event.listens_for(User, "before_insert")
def normalize_login(mapper, connection, target):
    if target.login:
        target.login = target.login.lower().strip()