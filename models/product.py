from datetime import datetime
from extensions import db


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)

    description = db.Column(db.Text, nullable=False)

    price = db.Column(db.Float, nullable=False)

    product_type = db.Column(db.String(50))
    # course | ebook | service

    resource_link = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Integrity rule
    __table_args__ = (
        db.CheckConstraint("price >= 0", name="check_product_price_positive"),
    )