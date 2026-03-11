from extensions import db
from datetime import datetime


class FreelanceApplication(db.Model):
    """Freelance service application"""
    __tablename__ = "freelance_applications"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, index=True)
    country = db.Column(db.String(100))
    skills = db.Column(db.Text)  # Comma-separated or JSON
    portfolio = db.Column(db.String(500))  # URL to portfolio
    status = db.Column(db.String(20), default="pending")  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f"<FreelanceApplication {self.name}>"
