from flask import Blueprint, render_template, Response

public_bp = Blueprint("public_bp", __name__)


# Home
@public_bp.route("/")
def home():
    return render_template("index.html")


# Courses
@public_bp.route("/courses")
def courses():
    return render_template("courses.html")


# Services
@public_bp.route("/services")
def services():
    return render_template("services.html")


# Contact
@public_bp.route("/contact")
def contact():
    return render_template("contact.html")


# News
@public_bp.route("/news")
def news():
    return render_template("news.html")


# About
@public_bp.route("/about")
def about():
    return render_template("about.html")


# Policies
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


# Sitemap
@public_bp.route("/sitemap.xml")
def sitemap():

    pages = [
        "https://https-smartsortaisolutions.onrender.com/",
        "https://https-smartsortaisolutions.onrender.com/services",
        "https://https-smartsortaisolutions.onrender.com/courses",
        "https://https-smartsortaisolutions.onrender.com/contact",
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