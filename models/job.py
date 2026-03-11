from extensions import db
from datetime import datetime


class Job(db.Model):
    """AI Job listing"""
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    job_type = db.Column(db.String(50), nullable=False)  # fulltime, parttime, internship, freelance, remote
    remote = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)
    application_link = db.Column(db.String(500))  # External apply URL
    image = db.Column(db.String(255))  # Company logo/image
    source = db.Column(db.String(100))  # manual, scraper, api, etc.
    slug = db.Column(db.String(255), unique=True, index=True)
    status = db.Column(db.String(20), default="draft")  # draft, published, archived
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Job {self.title}>"

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'job_type': self.job_type,
            'remote': self.remote,
            'description': self.description,
            'slug': self.slug,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
        }
