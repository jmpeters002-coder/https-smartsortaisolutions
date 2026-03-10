from extensions import db
from datetime import datetime


class UserCourseProgress(db.Model):
    """Track user progress in courses"""
    __tablename__ = "user_course_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    course_id = db.Column(db.Integer, nullable=False)  # Assuming course model exists
    progress_percentage = db.Column(db.Float, default=0.0)
    modules_completed = db.Column(db.Integer, default=0)
    videos_watched = db.Column(db.Integer, default=0)
    documents_accessed = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f"<UserCourseProgress user={self.user_id} course={self.course_id}>"


class SavedResource(db.Model):
    """Users can save/bookmark resources"""
    __tablename__ = "saved_resources"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    resource_type = db.Column(db.String(50), nullable=False)  # blog, news, job, course
    resource_id = db.Column(db.Integer, nullable=False, index=True)
    resource_title = db.Column(db.String(255))
    resource_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'resource_type', 'resource_id', name='uq_user_resource'),
    )

    def __repr__(self):
        return f"<SavedResource user={self.user_id} type={self.resource_type}>"


class UserSubscription(db.Model):
    """Track user subscriptions to newsletters and courses"""
    __tablename__ = "user_subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    subscription_type = db.Column(db.String(50), nullable=False)  # newsletter, premium, course
    subscription_id = db.Column(db.Integer)  # For course enrollments, newsletter subscriber id, etc.
    status = db.Column(db.String(20), default="active")  # active, paused, cancelled
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)

    def __repr__(self):
        return f"<UserSubscription user={self.user_id} type={self.subscription_type}>"
