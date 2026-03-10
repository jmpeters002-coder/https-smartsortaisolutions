from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, current_app
from extensions import db
from models.affiliate import AffiliatePartner, AffiliateReferral
from utils.auth import admin_required
from utils.validators import validate_email
import logging

logger = logging.getLogger(__name__)

affiliate_bp = Blueprint("affiliate_bp", __name__, url_prefix="/affiliate")


# =============================
# Public Routes
# =============================

@affiliate_bp.route("/apply", methods=["GET", "POST"])
def apply():
    """Apply to affiliate program"""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        country = request.form.get("country", "").strip()
        website = request.form.get("website", "").strip()

        # Validate
        if not name or len(name) < 2:
            flash("Please provide a valid name", "danger")
            return redirect(url_for("affiliate_bp.apply"))

        if not validate_email(email):
            flash("Invalid email address", "danger")
            return redirect(url_for("affiliate_bp.apply"))

        if not website or len(website) < 5:
            flash("Please provide your website or social media URL", "danger")
            return redirect(url_for("affiliate_bp.apply"))

        # Check if already applied
        existing = AffiliatePartner.query.filter_by(email=email).first()
        if existing:
            flash("You have already applied to the affiliate program", "info")
            return redirect(url_for("affiliate_bp.apply"))

        # Create application
        affiliate = AffiliatePartner(
            name=name,
            email=email,
            country=country,
            website=website,
            referral_code=AffiliatePartner.generate_referral_code(),
            status="pending"
        )

        db.session.add(affiliate)
        db.session.commit()

        logger.info(f"New affiliate application from: {name} ({email})")
        current_app.logger.info(f"Affiliate application: {name}")

        flash("Application submitted! We'll review it and contact you soon.", "success")
        return redirect(url_for("affiliate_bp.apply"))

    return render_template("affiliate/apply.html")


@affiliate_bp.route("/dashboard/<referral_code>")
def dashboard(referral_code):
    """Affiliate dashboard"""
    affiliate = AffiliatePartner.query.filter_by(referral_code=referral_code, status="active").first_or_404()
    referrals = AffiliateReferral.query.filter_by(affiliate_id=affiliate.id).all()
    
    stats = {
        "total_referrals": len(referrals),
        "completed_referrals": sum(1 for r in referrals if r.status == "completed"),
        "pending_referrals": sum(1 for r in referrals if r.status == "pending"),
        "total_commission": affiliate.total_commission,
    }
    
    return render_template("affiliate/dashboard.html", affiliate=affiliate, referrals=referrals, stats=stats)


# =============================
# Admin Routes
# =============================

@affiliate_bp.route("/admin/partners")
@admin_required
def manage_partners():
    """Manage affiliate partners"""
    status = request.args.get("status", "pending")
    search = request.args.get("search", "").strip()

    query = AffiliatePartner.query
    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.filter(AffiliatePartner.name.ilike(f"%{search}%") |
                            AffiliatePartner.email.ilike(f"%{search}%"))

    partners = query.order_by(AffiliatePartner.created_at.desc()).all()
    return render_template("admin/affiliate/partners.html", partners=partners, current_status=status)


@affiliate_bp.route("/admin/partner/<int:partner_id>")
@admin_required
def view_partner(partner_id):
    """View partner details"""
    partner = AffiliatePartner.query.get_or_404(partner_id)
    referrals = AffiliateReferral.query.filter_by(affiliate_id=partner_id).all()
    return render_template("admin/affiliate/view_partner.html", partner=partner, referrals=referrals)


@affiliate_bp.route("/admin/approve-partner/<int:partner_id>", methods=["POST"])
@admin_required
def approve_partner(partner_id):
    """Approve affiliate partner"""
    partner = AffiliatePartner.query.get_or_404(partner_id)
    from datetime import datetime
    partner.status = "active"
    partner.approved_at = datetime.utcnow()
    db.session.commit()
    logger.info(f"Approved affiliate partner: {partner.email}")
    return jsonify({"message": "Partner approved"}), 200


@affiliate_bp.route("/admin/reject-partner/<int:partner_id>", methods=["POST"])
@admin_required
def reject_partner(partner_id):
    """Reject affiliate partner"""
    partner = AffiliatePartner.query.get_or_404(partner_id)
    partner.status = "rejected"
    db.session.commit()
    logger.info(f"Rejected affiliate partner: {partner.email}")
    return jsonify({"message": "Partner rejected"}), 200


@affiliate_bp.route("/admin/delete-partner/<int:partner_id>", methods=["POST"])
@admin_required
def delete_partner(partner_id):
    """Delete partner"""
    partner = AffiliatePartner.query.get_or_404(partner_id)
    db.session.delete(partner)
    db.session.commit()
    logger.info(f"Deleted affiliate partner: {partner.email}")
    return jsonify({"message": "Partner deleted"}), 200
