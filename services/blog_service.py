from models import Blog
from extensions import db
import re
import time


def generate_slug(title):
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def ensure_unique_slug(slug):
    existing = Blog.query.filter_by(slug=slug).first()
    if existing:
        slug = f"{slug}-{int(time.time())}"
    return slug


def create_blog(title, summary, content):
    slug = ensure_unique_slug(generate_slug(title))

    post = Blog(
        title=title,
        slug=slug,
        summary=summary,
        content=content
    )

    db.session.add(post)
    db.session.commit()

    return post


def update_blog(blog, title, summary, content):
    blog.title = title
    blog.summary = summary
    blog.content = content
    db.session.commit()