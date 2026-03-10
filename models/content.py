from datetime import datetime
from extensions import db

class Content(db.Model):
    __tablename__ = "content"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    summary = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(20), nullable=False, index=True)  # blog or news
    image = db.Column(db.String(300))
    status = db.Column(db.String(20), default="draft", index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Content {self.title}>"