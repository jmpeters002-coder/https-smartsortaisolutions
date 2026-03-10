from extensions import db
from datetime import datetime


class Subscriber(db.Model):
    """Newsletter subscriber"""
    __tablename__ = "subscribers"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    status = db.Column(db.String(20), default="active")  # active, unsubscribed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    unsubscribed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Subscriber {self.email}>"
