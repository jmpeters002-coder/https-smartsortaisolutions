"""
User Authentication Routes
Handles signup, login, logout, password reset, etc.
"""

from flask import (
    Blueprint, render_template, request, redirect, 
    url_for, flash, session, current_app
)
from extensions import db
from models.user import User
from services.auth_service import AuthService
from utils.decorators import login_rate_limit

auth_bp = Blueprint("auth_bp", __name__)

# =============================
# Signup
# =============================

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """User registration page"""
    if request.method == "POST":
        login = request.form.get("login", "").strip()
        email = request.form.get("email", "").strip()
        name = request.form.get("name", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validate password match
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for("auth_bp.signup"))

        # Attempt signup
        user, error = AuthService.signup(login, email, name, password)
        
        if error:
            flash(error, "danger")
            return redirect(url_for("auth_bp.signup"))
        
        # Set session
        session["user_id"] = user.id
        session["user_login"] = user.login
        flash(f"Welcome {user.name}! Please verify your email.", "success")
        
        return redirect(url_for("user_dashboard_bp.dashboard"))
    
    return render_template("auth/signup.html")


# =============================
# Login
# =============================

@auth_bp.route("/login", methods=["GET", "POST"])
@login_rate_limit(max_attempts=5, window_seconds=900)
def login():
    """User login page"""
    if request.method == "POST":
        login_or_email = request.form.get("login_or_email", "").strip()
        password = request.form.get("password", "")

        # Attempt login
        user, error = AuthService.login(login_or_email, password)
        
        if error:
            flash(error, "danger")
            return redirect(url_for("auth_bp.login"))
        
        # Set session
        session["user_id"] = user.id
        session["user_login"] = user.login
        current_app.logger.info(f"User logged in: {user.login}")
        
        # Redirect to dashboard or next page
        next_page = request.args.get("next")
        if next_page and next_page.startswith("/"):
            return redirect(next_page)
        
        return redirect(url_for("user_dashboard_bp.dashboard"))
    
    return render_template("auth/login.html")


# =============================
# Logout
# =============================

@auth_bp.route("/logout")
def logout():
    """User logout"""
    if "user_id" in session:
        user_login = session.get("user_login", "User")
        current_app.logger.info(f"User logged out: {user_login}")
    
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("public_bp.home"))


# =============================
# Password Reset Request
# =============================

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Request password reset"""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        
        if not email:
            flash("Please enter your email address", "danger")
            return redirect(url_for("auth_bp.forgot_password"))
        
        user, error, token = AuthService.request_password_reset(email)
        
        # Always show success message (security best practice)
        flash("If an account exists with this email, a password reset link has been sent.", "info")
        return redirect(url_for("auth_bp.login"))
    
    return render_template("auth/forgot_password.html")


# =============================
# Password Reset
# =============================

@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Reset password with token"""
    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for("auth_bp.reset_password", token=token))
        
        user, error = AuthService.reset_password(token, password)
        
        if error:
            flash(error, "danger")
            return redirect(url_for("auth_bp.forgot_password"))
        
        flash("Your password has been reset. Please log in.", "success")
        return redirect(url_for("auth_bp.login"))
    
    return render_template("auth/reset_password.html", token=token)


# =============================
# Email Verification
# =============================

@auth_bp.route("/verify-email/<int:user_id>/<token>")
def verify_email(user_id, token):
    """Verify user email"""
    user, error = AuthService.verify_email(user_id, token)
    
    if error:
        flash(error, "danger")
        return redirect(url_for("public_bp.home"))
    
    flash("Email verified successfully!", "success")
    return redirect(url_for("user_dashboard_bp.dashboard"))
