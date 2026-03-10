from extensions import db
from datetime import datetime


class CourseModule(db.Model):
    """Course modules/sections"""
    __tablename__ = "course_modules"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)  # Display order
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    lessons = db.relationship('CourseLesson', backref='module', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<CourseModule {self.title}>"


class CourseLesson(db.Model):
    """Individual lessons/content within a module"""
    __tablename__ = "course_lessons"

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey("course_modules.id"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    content_type = db.Column(db.String(50), nullable=False)  # video, pdf, link, text, quiz
    content_url = db.Column(db.String(500))  # URL to video, PDF, or external link
    document_url = db.Column(db.String(500))  # URL to downloadable document
    content = db.Column(db.Text)  # For text-based content
    duration_minutes = db.Column(db.Integer)  # For video content
    order = db.Column(db.Integer, default=0)  # Display order
    is_preview = db.Column(db.Boolean, default=False)  # Free preview
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CourseLesson {self.title}>"

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content_type': self.content_type,
            'duration_minutes': self.duration_minutes,
            'is_preview': self.is_preview,
        }


class CourseResource(db.Model):
    """Downloadable resources for a course"""
    __tablename__ = "course_resources"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    resource_type = db.Column(db.String(50), nullable=False)  # pdf, zip, doc, image, etc.
    file_url = db.Column(db.String(500), nullable=False)
    file_size_kb = db.Column(db.Integer)
    download_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CourseResource {self.title}>"
