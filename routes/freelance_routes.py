from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, current_app, session
from extensions import db
from models.freelance import FreelanceApplication
from utils.auth import admin_required
from utils.validators import validate_email
import logging

logger = logging.getLogger(__name__)

freelance_bp = Blueprint("freelance_bp", __name__, url_prefix="/freelance")


# =============================
# Public Routes
# =============================

@freelance_bp.route("/apply", methods=["GET", "POST"])
def apply():
    """Apply for freelance opportunities"""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        country = request.form.get("country", "").strip()
        skills = request.form.get("skills", "").strip()
        portfolio = request.form.get("portfolio", "").strip()

        # Validate
        if not name or len(name) < 2:
            flash("Please provide a valid name", "danger")
            return redirect(url_for("freelance_bp.apply"))

        if not validate_email(email):
            flash("Invalid email address", "danger")
            return redirect(url_for("freelance_bp.apply"))

        if not skills or len(skills) < 5:
            flash("Please describe your skills", "danger")
            return redirect(url_for("freelance_bp.apply"))

        # Create application
        application = FreelanceApplication(
            name=name,
            email=email,
            country=country,
            skills=skills,
            portfolio=portfolio,
            status="pending"
        )

        db.session.add(application)
        db.session.commit()

        logger.info(f"New freelance application from: {name} ({email})")
        current_app.logger.info(f"Freelance application: {name}")

        flash("Application submitted successfully! We'll review it shortly.", "success")
        return redirect(url_for("freelance_bp.apply"))

    return render_template("freelance/apply.html")


# =============================
# Admin Routes
# =============================

@freelance_bp.route("/admin/applications")
@admin_required
def manage_applications():
    """Manage freelance applications"""
    status = request.args.get("status", "pending")
    search = request.args.get("search", "").strip()

    query = FreelanceApplication.query
    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.filter(FreelanceApplication.name.ilike(f"%{search}%") |
                           FreelanceApplication.email.ilike(f"%{search}%"))

    applications = query.order_by(FreelanceApplication.created_at.desc()).all()
    return render_template("admin/freelance/applications.html", applications=applications, current_status=status)


@freelance_bp.route("/admin/application/<int:app_id>")
@admin_required
def view_application(app_id):
    """View application details"""
    application = FreelanceApplication.query.get_or_404(app_id)
    return render_template("admin/freelance/view_application.html", application=application)


@freelance_bp.route("/admin/update-status/<int:app_id>", methods=["POST"])
@admin_required
def update_status(app_id):
    """Update application status"""
    application = FreelanceApplication.query.get_or_404(app_id)
    new_status = request.form.get("status")

    if new_status not in ["pending", "approved", "rejected"]:
        flash("Invalid status", "danger")
        return redirect(url_for("freelance_bp.manage_applications"))

    application.status = new_status
    from datetime import datetime
    application.reviewed_at = datetime.utcnow()
    application.reviewed_by = session.get("admin_id")

    db.session.commit()
    logger.info(f"Updated freelance application {app_id} status to: {new_status}")
    flash(f"Application status updated to {new_status}", "success")
    return redirect(url_for("freelance_bp.manage_applications"))


@freelance_bp.route("/admin/delete-application/<int:app_id>", methods=["POST"])
@admin_required
def delete_application(app_id):
    """Delete application"""
    application = FreelanceApplication.query.get_or_404(app_id)
    db.session.delete(application)
    db.session.commit()
    logger.info(f"Deleted freelance application: {app_id}")
    return jsonify({"message": "Application deleted"}), 200
