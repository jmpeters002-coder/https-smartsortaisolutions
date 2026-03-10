from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from werkzeug.utils import secure_filename
from extensions import db
from models.course_content import CourseModule, CourseLesson, CourseResource
from utils.auth import admin_required
from services.storage_service import get_storage_service
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

courses_bp = Blueprint("courses_bp", __name__, url_prefix="/courses")


# =============================
# Admin Course Management
# =============================

@courses_bp.route("/admin/list")
@admin_required
def admin_courses_list():
    """List all courses (TODO: assumes Course model exists)"""
    # This assumes a Course model exists
    return render_template("admin/courses/list.html")


# =============================
# Course Modules
# =============================

@courses_bp.route("/admin/<int:course_id>/modules")
@admin_required
def manage_modules(course_id):
    """Manage course modules"""
    modules = CourseModule.query.filter_by(course_id=course_id).order_by(CourseModule.order).all()
    return render_template("admin/courses/modules.html", course_id=course_id, modules=modules)


@courses_bp.route("/admin/<int:course_id>/modules/create", methods=["GET", "POST"])
@admin_required
def create_module(course_id):
    """Create module"""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        order = request.form.get("order", 0, type=int)
        
        if not title:
            flash("Title is required", "danger")
            return redirect(url_for("courses_bp.manage_modules", course_id=course_id))
        
        module = CourseModule(
            course_id=course_id,
            title=title,
            description=description,
            order=order
        )
        
        db.session.add(module)
        db.session.commit()
        
        logger.info(f"Created module: {title} (course={course_id})")
        flash("Module created successfully", "success")
        return redirect(url_for("courses_bp.manage_modules", course_id=course_id))
    
    return render_template("admin/courses/create_module.html", course_id=course_id)


@courses_bp.route("/admin/modules/<int:module_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_module(module_id):
    """Edit module"""
    module = CourseModule.query.get_or_404(module_id)
    
    if request.method == "POST":
        module.title = request.form.get("title", "").strip()
        module.description = request.form.get("description", "").strip()
        module.order = request.form.get("order", module.order, type=int)
        
        db.session.commit()
        logger.info(f"Updated module: {module.title}")
        flash("Module updated", "success")
        return redirect(url_for("courses_bp.manage_modules", course_id=module.course_id))
    
    return render_template("admin/courses/edit_module.html", module=module)


@courses_bp.route("/admin/modules/<int:module_id>/delete", methods=["POST"])
@admin_required
def delete_module(module_id):
    """Delete module"""
    module = CourseModule.query.get_or_404(module_id)
    course_id = module.course_id
    
    db.session.delete(module)
    db.session.commit()
    
    logger.info(f"Deleted module: {module_id}")
    flash("Module deleted", "info")
    return redirect(url_for("courses_bp.manage_modules", course_id=course_id))


# =============================
# Course Lessons
# =============================

@courses_bp.route("/admin/modules/<int:module_id>/lessons")
@admin_required
def manage_lessons(module_id):
    """Manage course lessons"""
    module = CourseModule.query.get_or_404(module_id)
    lessons = CourseLesson.query.filter_by(module_id=module_id).order_by(CourseLesson.order).all()
    
    return render_template("admin/courses/lessons.html", module=module, lessons=lessons)


@courses_bp.route("/admin/modules/<int:module_id>/lessons/create", methods=["GET", "POST"])
@admin_required
def create_lesson(module_id):
    """Create lesson"""
    module = CourseModule.query.get_or_404(module_id)
    
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        content_type = request.form.get("content_type", "text")
        content_url = request.form.get("content_url", "").strip()
        document_url = request.form.get("document_url", "").strip()
        content = request.form.get("content", "").strip()
        duration_minutes = request.form.get("duration_minutes", 0, type=int)
        is_preview = request.form.get("is_preview") == "on"
        order = request.form.get("order", 0, type=int)
        
        if not title or not content_type:
            flash("Title and content type are required", "danger")
            return redirect(url_for("courses_bp.manage_lessons", module_id=module_id))
        
        lesson = CourseLesson(
            module_id=module_id,
            title=title,
            description=description,
            content_type=content_type,
            content_url=content_url,
            document_url=document_url,
            content=content,
            duration_minutes=duration_minutes,
            is_preview=is_preview,
            order=order
        )
        
        db.session.add(lesson)
        db.session.commit()
        
        logger.info(f"Created lesson: {title} (module={module_id})")
        flash("Lesson created successfully", "success")
        return redirect(url_for("courses_bp.manage_lessons", module_id=module_id))
    
    content_types = ["video", "pdf", "link", "text", "quiz"]
    return render_template("admin/courses/create_lesson.html", module=module, content_types=content_types)


@courses_bp.route("/admin/lessons/<int:lesson_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_lesson(lesson_id):
    """Edit lesson"""
    lesson = CourseLesson.query.get_or_404(lesson_id)
    
    if request.method == "POST":
        lesson.title = request.form.get("title", "").strip()
        lesson.description = request.form.get("description", "").strip()
        lesson.content_type = request.form.get("content_type", lesson.content_type)
        lesson.content_url = request.form.get("content_url", "").strip()
        lesson.document_url = request.form.get("document_url", "").strip()
        lesson.content = request.form.get("content", "").strip()
        lesson.duration_minutes = request.form.get("duration_minutes", lesson.duration_minutes, type=int)
        lesson.is_preview = request.form.get("is_preview") == "on"
        lesson.order = request.form.get("order", lesson.order, type=int)
        lesson.updated_at = datetime.utcnow()
        
        db.session.commit()
        logger.info(f"Updated lesson: {lesson.title}")
        flash("Lesson updated", "success")
        return redirect(url_for("courses_bp.manage_lessons", module_id=lesson.module_id))
    
    content_types = ["video", "pdf", "link", "text", "quiz"]
    return render_template("admin/courses/edit_lesson.html", lesson=lesson, content_types=content_types)


@courses_bp.route("/admin/lessons/<int:lesson_id>/delete", methods=["POST"])
@admin_required
def delete_lesson(lesson_id):
    """Delete lesson"""
    lesson = CourseLesson.query.get_or_404(lesson_id)
    module_id = lesson.module_id
    
    db.session.delete(lesson)
    db.session.commit()
    
    logger.info(f"Deleted lesson: {lesson_id}")
    flash("Lesson deleted", "info")
    return redirect(url_for("courses_bp.manage_lessons", module_id=module_id))


@courses_bp.route("/admin/lessons/reorder", methods=["POST"])
@admin_required
def reorder_lessons():
    """Reorder lessons"""
    data = request.get_json()
    
    for index, lesson_id in enumerate(data.get("lesson_ids", [])):
        lesson = CourseLesson.query.get(lesson_id)
        if lesson:
            lesson.order = index
    
    db.session.commit()
    logger.info("Lessons reordered")
    return jsonify({"message": "Reordered"}), 200


# =============================
# Course Resources
# =============================

@courses_bp.route("/admin/<int:course_id>/resources")
@admin_required
def manage_resources(course_id):
    """Manage course resources"""
    resources = CourseResource.query.filter_by(course_id=course_id).all()
    return render_template("admin/courses/resources.html", course_id=course_id, resources=resources)


@courses_bp.route("/admin/<int:course_id>/resources/upload", methods=["GET", "POST"])
@admin_required
def upload_resource(course_id):
    """Upload course resource"""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        file = request.files.get("file")
        
        if not title or not file:
            flash("Title and file are required", "danger")
            return redirect(url_for("courses_bp.manage_resources", course_id=course_id))
        
        try:
            # Use storage service (defaults to local storage)
            storage = get_storage_service("local")
            upload_result = storage.upload(file, folder=f"courses/{course_id}")
            
            resource_type = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else "file"
            
            resource = CourseResource(
                course_id=course_id,
                title=title,
                description=description,
                resource_type=resource_type,
                file_url=upload_result["url"],
                file_size_kb=int(upload_result["size_mb"] * 1024)
            )
            
            db.session.add(resource)
            db.session.commit()
            
            logger.info(f"Uploaded resource: {title} (course={course_id})")
            flash("Resource uploaded successfully", "success")
            return redirect(url_for("courses_bp.manage_resources", course_id=course_id))
        
        except Exception as e:
            logger.error(f"Upload error: {e}")
            flash(f"Upload failed: {str(e)}", "danger")
            return redirect(url_for("courses_bp.manage_resources", course_id=course_id))
    
    return render_template("admin/courses/upload_resource.html", course_id=course_id)


@courses_bp.route("/admin/resources/<int:resource_id>/delete", methods=["POST"])
@admin_required
def delete_resource(resource_id):
    """Delete course resource"""
    resource = CourseResource.query.get_or_404(resource_id)
    course_id = resource.course_id
    
    db.session.delete(resource)
    db.session.commit()
    
    logger.info(f"Deleted resource: {resource_id}")
    flash("Resource deleted", "info")
    return redirect(url_for("courses_bp.manage_resources", course_id=course_id))
