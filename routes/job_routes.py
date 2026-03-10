from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from extensions import db
from models.job import Job
from utils.auth import admin_required
from utils.slug import generate_slug
import os
from datetime import datetime

logger = __import__('logging').getLogger(__name__)

job_bp = Blueprint("job_bp", __name__, url_prefix="/jobs")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# =============================
# Public Routes
# =============================

@job_bp.route("/")
def jobs_list():
    """List all published jobs with filtering"""
    job_type = request.args.get("type")
    remote_only = request.args.get("remote", "false").lower() == "true"
    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)

    query = Job.query.filter_by(status="published")

    if job_type:
        query = query.filter_by(job_type=job_type)
    if remote_only:
        query = query.filter_by(remote=True)
    if search:
        query = query.filter(
            (Job.title.ilike(f"%{search}%")) |
            (Job.company.ilike(f"%{search}%")) |
            (Job.description.ilike(f"%{search}%"))
        )

    jobs = query.order_by(Job.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template("jobs/index.html", jobs=jobs, current_filter=job_type, remote_only=remote_only, search=search)


@job_bp.route("/<slug>")
def job_detail(slug):
    """View single job"""
    job = Job.query.filter_by(slug=slug, status="published").first_or_404()
    current_app.logger.info(f"Job viewed: {slug}")
    return render_template("jobs/detail.html", job=job)


# =============================
# Admin Routes
# =============================

@job_bp.route("/admin/list")
@admin_required
def admin_jobs_list():
    """Manage jobs"""
    status = request.args.get("status")
    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)

    query = Job.query
    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.filter(
            (Job.title.ilike(f"%{search}%")) |
            (Job.company.ilike(f"%{search}%"))
        )

    jobs = query.order_by(Job.created_at.desc()).paginate(page=page, per_page=50)
    return render_template("admin/jobs/list.html", jobs=jobs, current_status=status)


@job_bp.route("/admin/create", methods=["GET", "POST"])
@admin_required
def create_job():
    """Create new job"""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        company = request.form.get("company", "").strip()
        location = request.form.get("location", "").strip()
        job_type = request.form.get("job_type", "").strip()
        remote = request.form.get("remote") == "on"
        description = request.form.get("description", "").strip()
        application_link = request.form.get("application_link", "").strip()
        status = request.form.get("status", "draft")

        # Validate required fields
        if not all([title, company, job_type]):
            flash("Title, company, and job type are required", "danger")
            return redirect(url_for("job_bp.create_job"))

        # Handle image upload
        image_filename = None
        if "image" in request.files:
            image = request.files["image"]
            if image and image.filename:
                if not allowed_file(image.filename):
                    flash("Invalid image format", "danger")
                    return redirect(url_for("job_bp.create_job"))

                filename = secure_filename(image.filename)
                upload_folder = os.path.join(current_app.root_path, "static/uploads/jobs")
                os.makedirs(upload_folder, exist_ok=True)
                image.save(os.path.join(upload_folder, filename))
                image_filename = filename

        # Generate slug
        slug = generate_slug(title)
        existing = Job.query.filter_by(slug=slug).first()
        if existing:
            slug = f"{slug}-{int(datetime.utcnow().timestamp())}"

        # Create job
        job = Job(
            title=title,
            company=company,
            location=location,
            job_type=job_type,
            remote=remote,
            description=description,
            application_link=application_link,
            image=image_filename,
            slug=slug,
            source="manual",
            status=status
        )

        db.session.add(job)
        db.session.commit()

        logger.info(f"Created job: {title}")
        flash("Job created successfully", "success")
        return redirect(url_for("job_bp.admin_jobs_list"))

    return render_template("admin/jobs/create.html", job_types=["fulltime", "parttime", "internship", "freelance", "remote"])


@job_bp.route("/admin/edit/<int:job_id>", methods=["GET", "POST"])
@admin_required
def edit_job(job_id):
    """Edit job"""
    job = Job.query.get_or_404(job_id)

    if request.method == "POST":
        job.title = request.form.get("title", "").strip()
        job.company = request.form.get("company", "").strip()
        job.location = request.form.get("location", "").strip()
        job.job_type = request.form.get("job_type", "").strip()
        job.remote = request.form.get("remote") == "on"
        job.description = request.form.get("description", "").strip()
        job.application_link = request.form.get("application_link", "").strip()
        job.status = request.form.get("status", "draft")

        if "image" in request.files:
            image = request.files["image"]
            if image and image.filename and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                upload_folder = os.path.join(current_app.root_path, "static/uploads/jobs")
                os.makedirs(upload_folder, exist_ok=True)
                image.save(os.path.join(upload_folder, filename))
                job.image = filename

        job.updated_at = datetime.utcnow()
        db.session.commit()

        logger.info(f"Updated job: {job.title}")
        flash("Job updated successfully", "success")
        return redirect(url_for("job_bp.admin_jobs_list"))

    return render_template("admin/jobs/edit.html", job=job, job_types=["fulltime", "parttime", "internship", "freelance", "remote"])


@job_bp.route("/admin/delete/<int:job_id>", methods=["POST"])
@admin_required
def delete_job(job_id):
    """Delete job"""
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    logger.info(f"Deleted job: {job.title}")
    return jsonify({"message": "Job deleted"}), 200


@job_bp.route("/admin/publish/<int:job_id>", methods=["POST"])
@admin_required
def publish_job(job_id):
    """Publish job"""
    job = Job.query.get_or_404(job_id)
    job.status = "published"
    job.published_at = datetime.utcnow()
    db.session.commit()
    logger.info(f"Published job: {job.title}")
    return jsonify({"message": "Job published"}), 200
