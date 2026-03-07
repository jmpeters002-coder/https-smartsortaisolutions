from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, session, current_app
from werkzeug.utils import secure_filename
import os
import re
import time

from extensions import db
from models import News, Order, UserAccess, Blog
from utils.auth import admin_required
from services.fulfillment import fulfill_order

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


# ---------------------------------
# Helpers
# ---------------------------------

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_slug(title):
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


def ensure_unique_slug(model, slug):
    existing = model.query.filter_by(slug=slug).first()
    if existing:
        slug = f"{slug}-{int(time.time())}"
    return slug


# ---------------------------------
# Admin Login
# ---------------------------------

@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        login = request.form.get("login")
        password = request.form.get("password")

    if login == os.getenv("ADMIN_USER") and password == os.getenv("ADMIN_PASS"):

       session["is_admin"] = True
       session.modified = True

    return redirect(url_for("admin_bp.admin_dashboard"))

    return render_template("admin_login.html", error="Invalid credentials")

    return render_template("admin_login.html")


# ---------------------------------
# Admin Dashboard
# ---------------------------------

@admin_bp.route("/dashboard")
@admin_required
def admin_dashboard():

    status_filter = request.args.get("status", "")
    email_filter = request.args.get("email", "")

    query = Order.query

    if status_filter:
        query = query.filter_by(status=status_filter)

    if email_filter:
        query = query.filter(Order.customer_email.ilike(f"%{email_filter}%"))

    orders = query.order_by(Order.created_at.desc()).all()

    all_orders = Order.query.all()

    total_orders = len(all_orders)
    paid_orders = len([o for o in all_orders if o.status == "paid"])
    pending_orders = len([o for o in all_orders if o.status == "pending"])

    total_revenue = sum(
        o.product.price for o in all_orders
        if o.status == "paid" and o.product
    )

    revenue_by_type = {}
    revenue_by_status = {}

    for order in all_orders:

        if order.product:

            revenue_by_status[order.status] = revenue_by_status.get(
                order.status, 0
            ) + order.product.price

            if order.status == "paid":
                ptype = order.product.product_type
                revenue_by_type[ptype] = revenue_by_type.get(
                    ptype, 0
                ) + order.product.price

    recent_access = UserAccess.query.order_by(
        UserAccess.granted_at.desc()
    ).limit(10).all()

    return render_template(
        "admin_dashboard.html",
        orders=orders,
        total_orders=total_orders,
        paid_orders=paid_orders,
        pending_orders=pending_orders,
        total_revenue=total_revenue,
        revenue_by_type=revenue_by_type,
        revenue_by_status=revenue_by_status,
        recent_access=recent_access
    )


# ---------------------------------
# Dashboard API
# ---------------------------------

@admin_bp.route("/dashboard-data")
@admin_required
def admin_dashboard_data():

    orders = Order.query.order_by(Order.created_at.desc()).all()

    payload = [
        {
            "id": o.id,
            "customer_email": o.customer_email,
            "product_title": o.product.title if o.product else None,
            "price": o.product.price if o.product else 0,
            "status": o.status,
            "payment_reference": o.payment_reference,
            "created_at": o.created_at.isoformat() if o.created_at else None
        }
        for o in orders
    ]

    return jsonify({
        "orders": payload,
        "total_orders": len(orders),
        "paid_orders": len([o for o in orders if o.status == "paid"]),
        "pending_orders": len([o for o in orders if o.status == "pending"])
    })


# ---------------------------------
# Override Payment
# ---------------------------------

@admin_bp.route("/override/<int:order_id>", methods=["POST"])
@admin_required
def admin_override(order_id):

    order = Order.query.get_or_404(order_id)

    if order.status == "paid":
        return redirect(url_for("admin_bp.admin_dashboard", success="already_paid"))

    order.status = "paid"
    db.session.commit()

    fulfill_order(order)

    return redirect("/admin/dashboard?success=override_complete")


# ---------------------------------
# Blog Creation
# ---------------------------------

@admin_bp.route("/blog/create", methods=["GET", "POST"])
@admin_required
def create_blog():

    if request.method == "POST":

        title = request.form.get("title")
        summary = request.form.get("summary")
        content = request.form.get("content")

        slug = generate_slug(title)
        slug = ensure_unique_slug(Blog, slug)

        post = Blog(
            title=title,
            slug=slug,
            summary=summary,
            content=content
        )

        db.session.add(post)
        db.session.commit()

        flash("Blog created successfully!", "success")

        return redirect(url_for("admin_bp.content_manager"))

    return render_template("admin/create_blog.html")


# ---------------------------------
# News Creation
# ---------------------------------

@admin_bp.route("/news/create", methods=["GET", "POST"])
@admin_required
def create_news():

    if request.method == "POST":

        title = request.form.get("title")
        summary = request.form.get("summary")
        content = request.form.get("content")
        status = request.form.get("status", "draft")

        slug = generate_slug(title)
        slug = ensure_unique_slug(News, slug)

        news = News(
            title=title,
            slug=slug,
            summary=summary,
            content=content,
            status=status
        )

        db.session.add(news)
        db.session.commit()

        flash("News created successfully!", "success")

        return redirect(url_for("admin_bp.content_manager"))

    return render_template("admin/create_news.html")


# ---------------------------------
# Content Manager
# ---------------------------------

@admin_bp.route("/content")
@admin_required
def content_manager():

    blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    news_list = News.query.order_by(News.created_at.desc()).all()

    return render_template(
        "admin/content_manager.html",
        blogs=blogs,
        news_list=news_list
    )


# ---------------------------------
# Delete Blog
# ---------------------------------

@admin_bp.route("/blog/delete/<int:blog_id>", methods=["POST"])
@admin_required
def delete_blog(blog_id):

    blog = Blog.query.get_or_404(blog_id)

    blog.status = "deleted"
    db.session.commit()

    flash("Blog deleted", "success")

    return redirect(url_for("admin_bp.content_manager"))


# ---------------------------------
# Delete News
# ---------------------------------

@admin_bp.route("/news/delete/<int:news_id>", methods=["POST"])
@admin_required
def delete_news(news_id):

    news = News.query.get_or_404(news_id)

    news.status = "deleted"
    db.session.commit()

    flash("News deleted", "success")

    return redirect(url_for("admin_bp.content_manager"))

@admin_bp.route("/blog/edit/<int:blog_id>", methods=["GET", "POST"])
@admin_required
def edit_blog(blog_id):

    blog = Blog.query.get_or_404(blog_id)

    if request.method == "POST":

        blog.title = request.form.get("title")
        blog.summary = request.form.get("summary")
        blog.content = request.form.get("content")

        db.session.commit()

        flash("Blog updated successfully!", "success")

        return redirect(url_for("admin_bp.content_manager"))

    return render_template("admin/edit_blog.html", blog=blog)

@admin_bp.route("/news/edit/<int:news_id>", methods=["GET", "POST"])
@admin_required
def edit_news(news_id):

    news = News.query.get_or_404(news_id)

    if request.method == "POST":

        news.title = request.form.get("title")
        news.summary = request.form.get("summary")
        news.content = request.form.get("content")
        news.status = request.form.get("status")

        db.session.commit()

        flash("News updated successfully!", "success")

        return redirect(url_for("admin_bp.content_manager"))

    return render_template("admin/edit_news.html", news=news)