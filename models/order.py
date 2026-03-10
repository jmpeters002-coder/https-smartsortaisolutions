from datetime import datetime
from extensions import db


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)

    customer_email = db.Column(db.String(120), nullable=False)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False
    )

    product = db.relationship("Product")

    payment_reference = db.Column(
        db.String(200),
        unique=True,
        index=True
    )

    status = db.Column(
        db.String(50),
        default="pending",
        index=True
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)