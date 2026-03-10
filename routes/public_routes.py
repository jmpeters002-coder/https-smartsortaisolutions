from flask import Blueprint, render_template, Response
from models.content import Content

public_bp = Blueprint("public_bp", __name__)

# -------------------------------
# Home / Static Pages
# -------------------------------
@public_bp.route("/")
def home():
    return render_template("index.html")

@public_bp.route("/courses")
def courses():
    return render_template("courses.html")

@public_bp.route("/services")
def services():
    return render_template("services.html")

@public_bp.route("/contact")
def contact():
    return render_template("contact.html")

@public_bp.route("/about")
def about():
    return render_template("about.html")

@public_bp.route("/refund-policy")
def refund_policy():
    return render_template("refund_policy.html")

@public_bp.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy_policy.html")

@public_bp.route("/free-resources")
def free_resources():
    return render_template("free_resources.html")

@public_bp.route("/terms-and-conditions")
def terms_conditions():
    return render_template("terms_and_conditions.html")


# -------------------------------
# Blog Routes
# -------------------------------
@public_bp.route("/blog")
def blog_index():
    # Fetch only published blog posts
    posts = Content.query.filter_by(content_type="blog", status="published")\
                         .order_by(Content.created_at.desc()).all()
    return render_template("blog/index.html", posts=posts)


@public_bp.route("/blog/<slug>")
def blog_post(slug):
    # Fetch single blog post by slug
    post = Content.query.filter_by(slug=slug, content_type="blog", status="published").first_or_404()
    return render_template("blog/post.html", post=post)


# -------------------------------
# News Routes
# -------------------------------
@public_bp.route("/news")
def news_index():
    # Fetch only published news articles
    articles = Content.query.filter_by(content_type="news", status="published")\
                            .order_by(Content.created_at.desc()).all()
    return render_template("news/index.html", articles=articles)


@public_bp.route("/news/<slug>")
def news_post(slug):
    # Fetch single news article by slug
    article = Content.query.filter_by(slug=slug, content_type="news", status="published").first_or_404()
    return render_template("news/post.html", article=article)


# -------------------------------
# Sitemap
# -------------------------------
@public_bp.route("/sitemap.xml")
def sitemap():
    pages = [
        "https://https-smartsortaisolutions.onrender.com/",
        "https://https-smartsortaisolutions.onrender.com/services",
        "https://https-smartsortaisolutions.onrender.com/courses",
        "https://https-smartsortaisolutions.onrender.com/contact",
        "https://https-smartsortaisolutions.onrender.com/blog",
        "https://https-smartsortaisolutions.onrender.com/news",
        "https://https-smartsortaisolutions.onrender.com/about"
    ]

    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""
    for page in pages:
        sitemap_xml += f"""
<url>
<loc>{page}</loc>
</url>
"""
    sitemap_xml += "</urlset>"
    return Response(sitemap_xml, mimetype="application/xml")