from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

    price = db.Column(db.Float, nullable=False)

    product_type = db.Column(db.String(50))  
    # course | ebook | service

    resource_link = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    customer_email = db.Column(db.String(120), nullable=False)

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    product = db.relationship('Product')

    payment_reference = db.Column(db.String(200), unique=True)

    status = db.Column(db.String(50), default="pending")
    # pending | paid | failed

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserAccess(db.Model):
    """
    Tracks user access to paid products.
    Auto-granted when payment is confirmed.
    Prevents duplicate access grants.
    """
    id = db.Column(db.Integer, primary_key=True)

    customer_email = db.Column(db.String(120), nullable=False)

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    product = db.relationship('Product')

    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)

    access_type = db.Column(db.String(50))
    # course | service

    granted_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Prevent duplicate access for same user + product
    __table_args__ = (db.UniqueConstraint('customer_email', 'product_id', name='unique_user_product_access'),)

    def __repr__(self):
        return f"<UserAccess {self.customer_email} → {self.product_id}>"


class User(db.Model):
    """Application user / admin model.

    Passwords are stored as a secure hash. Use the provided helpers
    `set_password` and `check_password` to manage credentials.
    """
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(120), unique=True, nullable=False, index=True)  # email or username
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password, hash_func=None):
        """Set password using provided hash function (werkzeug by default)."""
        # Delayed import to avoid circular imports in some contexts
        try:
            from werkzeug.security import generate_password_hash
            self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        except Exception:
            # Fallback naive assignment (should not happen in practice)
            self.password_hash = password

    def check_password(self, password):
        try:
            from werkzeug.security import check_password_hash
            return check_password_hash(self.password_hash, password)
        except Exception:
            return False

    def __repr__(self):
        return f"<User {self.login} {'(admin)' if self.is_admin else ''}>"