from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os

from extensions import db
from models import News, Order, UserAccess
from utils.auth import admin_required
from services.fulfillment import fulfill_order
from flask import request, session

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# -----------------------------
# Admin News Management
# -----------------------------

@admin_bp.route("/news", methods=["GET", "POST"])
@admin_required
def admin_news():

    if request.method == "POST":

        article = News(
            title=request.form.get("title"),
            slug=request.form.get("slug"),
            summary=request.form.get("summary"),
            content=request.form.get("content"),
            post_type=request.form.get("post_type"),
            source_name=request.form.get("source_name"),
            source_link=request.form.get("source_link")
        )

        image = request.files.get("image")

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)

            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            image.save(os.path.join(UPLOAD_FOLDER, filename))
            article.image_filename = filename

        db.session.add(article)
        db.session.commit()

        return redirect(url_for("admin_bp.admin_news"))

    articles = News.query.order_by(News.created_at.desc()).all()

    return render_template("admin_news.html", articles=articles)


# -----------------------------
# Admin Dashboard
# -----------------------------

@admin_bp.route("/dashboard")
@admin_required
def admin_dashboard():

    status_filter = request.args.get('status', '')
    email_filter = request.args.get('email', '')

    query = Order.query

    if status_filter:
        query = query.filter_by(status=status_filter)

    if email_filter:
        query = query.filter(Order.customer_email.ilike(f"%{email_filter}%"))

    orders = query.order_by(Order.created_at.desc()).all()

    all_orders = Order.query.all()

    total_orders = len(all_orders)
    paid_orders = len([o for o in all_orders if o.status == 'paid'])
    pending_orders = len([o for o in all_orders if o.status == 'pending'])

    total_revenue = sum(
        o.product.price for o in all_orders
        if o.status == 'paid' and o.product
    )

    revenue_by_type = {}
    revenue_by_status = {}

    for order in all_orders:
        if order.status == 'paid' and order.product:

            ptype = order.product.product_type
            revenue_by_type[ptype] = revenue_by_type.get(ptype, 0) + order.product.price

        if order.product:
            revenue_by_status[order.status] = revenue_by_status.get(
                order.status, 0
            ) + order.product.price

    recent_access = UserAccess.query.order_by(
        UserAccess.granted_at.desc()
    ).limit(10).all()

    return render_template(
        'admin_dashboard.html',
        orders=orders,
        total_orders=total_orders,
        paid_orders=paid_orders,
        pending_orders=pending_orders,
        total_revenue=total_revenue,
        revenue_by_type=revenue_by_type,
        revenue_by_status=revenue_by_status,
        recent_access=recent_access
    )


# -----------------------------
# Dashboard API Data
# -----------------------------

@admin_bp.route("/dashboard-data")
@admin_required
def admin_dashboard_data():

    all_orders = Order.query.order_by(
        Order.created_at.desc()
    ).all()

    orders_payload = [
        {
            'id': o.id,
            'customer_email': o.customer_email,
            'product_title': o.product.title if o.product else None,
            'price': o.product.price if o.product else 0,
            'status': o.status,
            'payment_reference': o.payment_reference,
            'created_at': o.created_at.isoformat() if o.created_at else None
        }
        for o in all_orders
    ]

    total_orders = len(all_orders)
    paid_orders = len([o for o in all_orders if o.status == 'paid'])
    pending_orders = len([o for o in all_orders if o.status == 'pending'])

    total_revenue = sum(
        o.product.price for o in all_orders
        if o.status == 'paid' and o.product
    )

    revenue_by_type = {}
    revenue_by_status = {}

    for o in all_orders:
        if o.status == 'paid' and o.product:
            revenue_by_type[o.product.product_type] = revenue_by_type.get(
                o.product.product_type, 0
            ) + o.product.price

        if o.product:
            revenue_by_status[o.status] = revenue_by_status.get(
                o.status, 0
            ) + o.product.price

    recent_access = UserAccess.query.order_by(
        UserAccess.granted_at.desc()
    ).limit(10).all()

    recent_access_payload = [
        {
            'email': a.customer_email,
            'product_title': a.product.title if a.product else None,
            'type': a.access_type,
            'granted_at': a.granted_at.isoformat() if a.granted_at else None
        }
        for a in recent_access
    ]

    return jsonify({
        'orders': orders_payload,
        'total_orders': total_orders,
        'paid_orders': paid_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'revenue_by_type': revenue_by_type,
        'revenue_by_status': revenue_by_status,
        'recent_access': recent_access_payload
    })


# -----------------------------
# Override Payment
# -----------------------------

@admin_bp.route("/override/<int:order_id>", methods=["POST"])
@admin_required
def admin_override(order_id):

    order = Order.query.get(order_id)

    if not order:
        return "Order not found", 404

    if order.status == 'paid':
        return redirect('/admin/dashboard?success=already_paid')

    order.status = 'paid'

    fulfill_order(order)

    return redirect('/admin/dashboard?success=override_complete')

@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        login = request.form.get("login")
        password = request.form.get("password")

        # Your authentication logic here
        # Example session auth:

        if login and password:
            session["is_admin"] = True
            return redirect(url_for("admin_bp.admin_dashboard"))

        return render_template("admin_login.html", error="Invalid credentials")

    return render_template("admin_login.html")