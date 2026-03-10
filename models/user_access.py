from datetime import datetime
from extensions import db


class UserAccess(db.Model):
    __tablename__ = "user_access"

    id = db.Column(db.Integer, primary_key=True)

    customer_email = db.Column(db.String(120), nullable=False)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False
    )

    product = db.relationship("Product")

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id"),
        nullable=False
    )

    access_type = db.Column(db.String(50))
    # course | service

    granted_at = db.Column(db.DateTime, default=datetime.utcnow)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint(
            "customer_email",
            "product_id",
            name="unique_user_product_access"
        ),
    )

    def __repr__(self):
        return f"<UserAccess {self.customer_email} → {self.product_id}>"