import re
import time


def generate_slug(title):
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def unique_slug(model, slug):
    existing = model.query.filter_by(slug=slug).first()
    if existing:
        slug = f"{slug}-{int(time.time())}"
    return slug