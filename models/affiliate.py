from extensions import db
from datetime import datetime
import secrets


class AffiliatePartner(db.Model):
    """Affiliate program partner"""
    __tablename__ = "affiliate_partners"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    country = db.Column(db.String(100))
    website = db.Column(db.String(500))  # Website or social media
    referral_code = db.Column(db.String(50), unique=True, index=True)
    status = db.Column(db.String(20), default="pending")  # pending, approved, rejected, active
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    
    # Commission tracking
    total_referrals = db.Column(db.Integer, default=0)
    total_commission = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f"<AffiliatePartner {self.name}>"

    @staticmethod
    def generate_referral_code():
        """Generate unique referral code"""
        while True:
            code = secrets.token_urlsafe(12)
            if not AffiliatePartner.query.filter_by(referral_code=code).first():
                return code


class AffiliateReferral(db.Model):
    """Track referrals from affiliate partners"""
    __tablename__ = "affiliate_referrals"

    id = db.Column(db.Integer, primary_key=True)
    affiliate_id = db.Column(db.Integer, db.ForeignKey("affiliate_partners.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    commission_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default="pending")  # pending, completed, paid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    affiliate = db.relationship("AffiliatePartner", backref="referrals")

    def __repr__(self):
        return f"<AffiliateReferral {self.affiliate_id}>"
