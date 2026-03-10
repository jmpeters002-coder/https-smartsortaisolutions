from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from werkzeug.utils import secure_filename
from extensions import db
from models import User, Order, UserAccess
from models.content import Content
from utils.auth import admin_required
from services.fulfillment import fulfill_order
import os, re, time
from utils.slug import generate_slug


admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")

# -------------------------------
# Helpers
# -------------------------------
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_slug(title):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug

def ensure_unique_slug(model, slug):
    existing = model.query.filter_by(slug=slug).first()
    if existing:
        slug = f"{slug}-{int(time.time())}"
    return slug

# -------------------------------
# Content Stats Helper (fixed)
# -------------------------------
def get_content_stats():
    total_content = Content.query.count()
    published_content = Content.query.filter_by(status="published").count()
    draft_content = Content.query.filter_by(status="draft").count()
    return total_content, published_content, draft_content

# -------------------------------
# Admin Login
# -------------------------------
@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")

        user = User.query.filter_by(login=login).first()

        if user and user.check_password(password) and user.is_admin:
            session["admin_id"] = user.id
            session["admin_logged_in"] = True
            current_app.logger.info(f"Admin {login} logged in")
            return redirect(url_for("admin_bp.admin_dashboard"))
        else:
            flash("Invalid credentials", "danger")
            current_app.logger.warning(f"Failed admin login attempt: {login}")

    return render_template("admin/login.html")

# -------------------------------
# Admin Dashboard
# -------------------------------
@admin_bp.route("/dashboard")
@admin_required
def admin_dashboard():
    status_filter = request.args.get("status")
    email_filter = request.args.get("email")

    query = Order.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if email_filter:
        query = query.filter(Order.customer_email.ilike(f"%{email_filter}%"))

    orders = query.order_by(Order.created_at.desc()).all()
    all_orders = Order.query.all()

    total_orders = len(all_orders)
    paid_orders = sum(1 for o in all_orders if o.status == "paid")
    pending_orders = sum(1 for o in all_orders if o.status == "pending")
    total_revenue = sum(o.product.price for o in all_orders if o.status == "paid" and o.product)

    revenue_by_type = {}
    revenue_by_status = {}
    for order in all_orders:
        if not order.product:
            continue
        revenue_by_status[order.status] = revenue_by_status.get(order.status, 0) + order.product.price
        if order.status == "paid":
            ptype = order.product.product_type
            revenue_by_type[ptype] = revenue_by_type.get(ptype, 0) + order.product.price

    recent_access = UserAccess.query.order_by(UserAccess.granted_at.desc()).limit(10).all()

    # ✅ Get content stats safely inside the route
    total_content, published_content, draft_content = get_content_stats()

    return render_template(
        "admin/dashboard.html",
        orders=orders,
        total_orders=total_orders,
        paid_orders=paid_orders,
        pending_orders=pending_orders,
        total_revenue=total_revenue,
        revenue_by_type=revenue_by_type,
        revenue_by_status=revenue_by_status,
        recent_access=recent_access,
        total_content=total_content,
        published_content=published_content,
        draft_content=draft_content
    )


# -------------------------------
# Content Manager
# -------------------------------
@admin_bp.route("/content")
@admin_required
def content_manager():
    search = request.args.get("search")
    ctype = request.args.get("type")

    query = Content.query
    if search:
        query = query.filter(Content.title.ilike(f"%{search}%"))
    if ctype:
        query = query.filter_by(content_type=ctype)

    contents = query.order_by(Content.created_at.desc()).all()
    return render_template("admin/content_manager.html", contents=contents)

# -------------------------------
# Create Content
# -------------------------------
@admin_bp.route("/create-content", methods=["GET","POST"])
@admin_required
def create_content():
    if request.method == "POST":
        content_type = request.form.get("content_type")
        title = request.form.get("title")
        summary = request.form.get("summary")
        content_body = request.form.get("content")
        status = request.form.get("status") or "draft"

        image = request.files.get("image")
        image_filename = None

        if image and image.filename != "":
            filename = secure_filename(image.filename)
            
            # Create folder dynamically by content type
            upload_folder = os.path.join(current_app.root_path, "static/uploads", content_type)
            os.makedirs(upload_folder, exist_ok=True)

            image_path = os.path.join(upload_folder, filename)
            image.save(image_path)
            image_filename = filename

        # Ensure slug is unique
        slug = generate_unique_slug(title)

        new_content = Content(
            title=title,
            slug=slug,
            summary=summary,
            content=content_body,
            content_type=content_type,
            image=image_filename,
            status=status
        )

        db.session.add(new_content)
        db.session.commit()

        flash(f"{content_type.capitalize()} created successfully!", "success")
        return redirect(url_for("admin_bp.content_manager"))

    return render_template("admin/create_content.html")
# -------------------------------
# Edit Content
# -------------------------------
@admin_bp.route("/edit-content/<int:content_id>", methods=["GET", "POST"])
@admin_required
def edit_content(content_id):
    content = Content.query.get_or_404(content_id)

    if request.method == "POST":
        content.title = request.form.get("title")
        content.summary = request.form.get("summary")
        content.content = request.form.get("content")
        content.status = request.form.get("status")

        image = request.files.get("image")
        if image and image.filename != "":
            filename = secure_filename(image.filename)
            upload_folder = os.path.join(current_app.root_path, "static/uploads", content.content_type)
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, filename)
            image.save(image_path)
            content.image = filename

        db.session.commit()
        flash("Content updated successfully", "success")
        return redirect(url_for("admin_bp.content_manager"))

    return render_template("admin/edit_content.html", content=content)

# -------------------------------
# Delete Content
# -------------------------------
@admin_bp.route("/delete-content/<int:content_id>")
@admin_required
def delete_content(content_id):
    content = Content.query.get_or_404(content_id)
    db.session.delete(content)
    db.session.commit()
    flash("Content deleted", "info")
    return redirect(url_for("admin_bp.content_manager"))