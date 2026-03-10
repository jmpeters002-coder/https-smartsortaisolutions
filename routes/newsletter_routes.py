from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from extensions import db
from models.newsletter import Subscriber
from utils.auth import admin_required
from utils.validators import validate_email
import logging

logger = logging.getLogger(__name__)

newsletter_bp = Blueprint("newsletter_bp", __name__, url_prefix="/newsletter")


# =============================
# Public Routes
# =============================

@newsletter_bp.route("/subscribe", methods=["GET", "POST"])
def subscribe():
    """Subscribe to newsletter"""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        # Validate email
        if not validate_email(email):
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"error": "Invalid email address"}), 400
            flash("Invalid email address", "danger")
            return redirect(request.referrer or "/")

        # Check if already subscribed
        existing = Subscriber.query.filter_by(email=email, status="active").first()
        if existing:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"message": "Already subscribed"}), 200
            flash("You are already subscribed", "info")
            return redirect(request.referrer or "/")

        # Create new subscriber
        subscriber = Subscriber(email=email, status="active")
        db.session.add(subscriber)
        db.session.commit()

        logger.info(f"New newsletter subscriber: {email}")
        
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"message": "Successfully subscribed"}), 201
        flash("Successfully subscribed to newsletter!", "success")
        return redirect(request.referrer or "/")

    return render_template("newsletter/subscribe.html")


@newsletter_bp.route("/unsubscribe/<email>")
def unsubscribe(email):
    """Unsubscribe from newsletter"""
    subscriber = Subscriber.query.filter_by(email=email).first()
    
    if not subscriber:
        flash("Email not found", "warning")
        return redirect("/")

    subscriber.status = "unsubscribed"
    db.session.commit()
    
    logger.info(f"Unsubscribed from newsletter: {email}")
    flash("You have been unsubscribed", "info")
    return redirect("/")


# =============================
# Admin Routes
# =============================

@newsletter_bp.route("/admin/subscribers")
@admin_required
def manage_subscribers():
    """Manage newsletter subscribers"""
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "").strip()

    query = Subscriber.query
    if search:
        query = query.filter(Subscriber.email.ilike(f"%{search}%"))

    subscribers = query.order_by(Subscriber.created_at.desc()).paginate(page=page, per_page=50)
    return render_template("admin/newsletter/subscribers.html", subscribers=subscribers)


@newsletter_bp.route("/admin/delete-subscriber/<int:subscriber_id>", methods=["POST"])
@admin_required
def delete_subscriber(subscriber_id):
    """Delete subscriber"""
    subscriber = Subscriber.query.get_or_404(subscriber_id)
    db.session.delete(subscriber)
    db.session.commit()
    logger.info(f"Deleted subscriber: {subscriber.email}")
    return jsonify({"message": "Subscriber deleted"}), 200


@newsletter_bp.route("/admin/export-subscribers")
@admin_required
def export_subscribers():
    """Export subscribers as CSV"""
    import csv
    from io import StringIO
    from flask import make_response
    
    subscribers = Subscriber.query.filter_by(status="active").all()
    
    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerow(["Email", "Subscribed Date"])
    
    for sub in subscribers:
        csv_writer.writerow([sub.email, sub.created_at.strftime("%Y-%m-%d %H:%M:%S")])
    
    response = make_response(csv_buffer.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=subscribers.csv"
    response.headers["Content-Type"] = "text/csv"
    return response
