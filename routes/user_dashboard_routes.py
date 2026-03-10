from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from extensions import db
from models import User
from models.user_dashboard import UserCourseProgress, SavedResource, UserSubscription
from models.newsletter import Subscriber
from utils.auth import admin_required
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

user_dashboard_bp = Blueprint("user_dashboard_bp", __name__, url_prefix="/dashboard")


def get_current_user():
    """Get current logged-in user"""
    user_id = session.get("user_id")
    if user_id:
        return User.query.get(user_id)
    return None


def require_user_login(f):
    """Require user to be logged in"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash("Please log in first", "warning")
            return redirect(url_for("public_bp.home"))
        return f(*args, **kwargs)
    return decorated_function


# =============================
# Dashboard Home
# =============================

@user_dashboard_bp.route("/")
@require_user_login
def dashboard():
    """Main dashboard"""
    user = get_current_user()
    
    # Get statistics
    course_progress = UserCourseProgress.query.filter_by(user_id=user.id).all()
    saved_resources = SavedResource.query.filter_by(user_id=user.id).count()
    subscriptions = UserSubscription.query.filter_by(user_id=user.id, status="active").all()
    
    stats = {
        "courses_enrolled": len(course_progress),
        "saved_resources": saved_resources,
        "active_subscriptions": len(subscriptions),
    }
    
    return render_template("user/dashboard.html", user=user, stats=stats, subscriptions=subscriptions)


# =============================
# Course Progress
# =============================

@user_dashboard_bp.route("/courses")
@require_user_login
def my_courses():
    """View enrolled courses"""
    user = get_current_user()
    
    progress_records = UserCourseProgress.query.filter_by(user_id=user.id).all()
    
    return render_template("user/my_courses.html", user=user, courses=progress_records)


@user_dashboard_bp.route("/courses/<int:course_id>")
@require_user_login
def course_progress(course_id):
    """View course progress details"""
    user = get_current_user()
    
    progress = UserCourseProgress.query.filter_by(
        user_id=user.id,
        course_id=course_id
    ).first_or_404()
    
    return render_template("user/course_progress.html", user=user, progress=progress)


@user_dashboard_bp.route("/courses/<int:course_id>/update", methods=["POST"])
@require_user_login
def update_course_progress(course_id):
    """Update course progress"""
    user = get_current_user()
    data = request.get_json()
    
    progress = UserCourseProgress.query.filter_by(
        user_id=user.id,
        course_id=course_id
    ).first_or_404()
    
    if "progress_percentage" in data:
        progress.progress_percentage = min(100, max(0, data["progress_percentage"]))
    
    if "modules_completed" in data:
        progress.modules_completed = data["modules_completed"]
    
    if "videos_watched" in data:
        progress.videos_watched = data["videos_watched"]
    
    if "documents_accessed" in data:
        progress.documents_accessed = data["documents_accessed"]
    
    progress.last_accessed = datetime.utcnow()
    
    if progress.progress_percentage >= 100:
        progress.completed_at = datetime.utcnow()
    
    db.session.commit()
    logger.info(f"Updated course progress: user={user.id}, course={course_id}")
    
    return jsonify({"message": "Progress updated"}), 200


# =============================
# Saved Resources
# =============================

@user_dashboard_bp.route("/saved")
@require_user_login
def saved_resources():
    """View saved resources"""
    user = get_current_user()
    resource_type = request.args.get("type")
    
    query = SavedResource.query.filter_by(user_id=user.id)
    if resource_type:
        query = query.filter_by(resource_type=resource_type)
    
    resources = query.order_by(SavedResource.created_at.desc()).all()
    
    return render_template("user/saved_resources.html", user=user, resources=resources, current_type=resource_type)


@user_dashboard_bp.route("/saved/<int:resource_id>/save", methods=["POST"])
@require_user_login
def save_resource(resource_id):
    """Save a resource"""
    user = get_current_user()
    data = request.get_json()
    
    resource_type = data.get("resource_type")
    resource_title = data.get("resource_title")
    resource_url = data.get("resource_url")
    
    # Check if already saved
    existing = SavedResource.query.filter_by(
        user_id=user.id,
        resource_type=resource_type,
        resource_id=resource_id
    ).first()
    
    if existing:
        return jsonify({"message": "Already saved"}), 200
    
    saved = SavedResource(
        user_id=user.id,
        resource_type=resource_type,
        resource_id=resource_id,
        resource_title=resource_title,
        resource_url=resource_url
    )
    
    db.session.add(saved)
    db.session.commit()
    
    logger.info(f"Saved resource: user={user.id}, type={resource_type}, id={resource_id}")
    return jsonify({"message": "Saved successfully"}), 201


@user_dashboard_bp.route("/saved/<int:save_id>/unsave", methods=["POST"])
@require_user_login
def unsave_resource(save_id):
    """Unsave a resource"""
    user = get_current_user()
    
    saved = SavedResource.query.get_or_404(save_id)
    
    if saved.user_id != user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    db.session.delete(saved)
    db.session.commit()
    
    logger.info(f"Unsaved resource: save_id={save_id}")
    return jsonify({"message": "Removed"}), 200


# =============================
# Subscriptions Management
# =============================

@user_dashboard_bp.route("/subscriptions")
@require_user_login
def manage_subscriptions():
    """Manage subscriptions"""
    user = get_current_user()
    
    subscriptions = UserSubscription.query.filter_by(user_id=user.id).all()
    
    # Check if subscribed to newsletter
    newsletter_subscriber = Subscriber.query.filter_by(email=user.login, status="active").first()
    
    return render_template(
        "user/subscriptions.html",
        user=user,
        subscriptions=subscriptions,
        is_newsletter_subscriber=bool(newsletter_subscriber)
    )


@user_dashboard_bp.route("/subscriptions/newsletter/toggle", methods=["POST"])
@require_user_login
def toggle_newsletter():
    """Toggle newsletter subscription"""
    user = get_current_user()
    
    subscriber = Subscriber.query.filter_by(email=user.login).first()
    
    if not subscriber:
        # Create new subscriber
        subscriber = Subscriber(email=user.login, status="active")
        db.session.add(subscriber)
        db.session.commit()
        action = "subscribed"
    elif subscriber.status == "active":
        subscriber.status = "unsubscribed"
        db.session.commit()
        action = "unsubscribed"
    else:
        subscriber.status = "active"
        db.session.commit()
        action = "subscribed"
    
    logger.info(f"Newsletter {action}: {user.login}")
    return jsonify({"message": f"Newsletter {action}"}), 200


@user_dashboard_bp.route("/subscriptions/<int:sub_id>/cancel", methods=["POST"])
@require_user_login
def cancel_subscription(sub_id):
    """Cancel a subscription"""
    user = get_current_user()
    
    subscription = UserSubscription.query.get_or_404(sub_id)
    
    if subscription.user_id != user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    subscription.status = "cancelled"
    subscription.cancelled_at = datetime.utcnow()
    db.session.commit()
    
    logger.info(f"Cancelled subscription: {sub_id}")
    return jsonify({"message": "Subscription cancelled"}), 200


# =============================
# Account Settings
# =============================

@user_dashboard_bp.route("/settings")
@require_user_login
def account_settings():
    """Account settings"""
    user = get_current_user()
    return render_template("user/settings.html", user=user)


@user_dashboard_bp.route("/settings/password", methods=["POST"])
@require_user_login
def change_password():
    """Change password"""
    user = get_current_user()
    
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")
    
    if not user.check_password(current_password):
        flash("Current password is incorrect", "danger")
        return redirect(url_for("user_dashboard_bp.account_settings"))
    
    if new_password != confirm_password:
        flash("New passwords don't match", "danger")
        return redirect(url_for("user_dashboard_bp.account_settings"))
    
    if len(new_password) < 6:
        flash("Password must be at least 6 characters", "danger")
        return redirect(url_for("user_dashboard_bp.account_settings"))
    
    user.set_password(new_password)
    db.session.commit()
    
    logger.info(f"Password changed: user={user.id}")
    flash("Password changed successfully", "success")
    return redirect(url_for("user_dashboard_bp.account_settings"))
