from flask import Blueprint, render_template, current_app
from requests import post
from models.content import Content

blog_bp = Blueprint("blog", __name__)




# SINGLE ARTICLE PAGE
@blog_bp.route("/blog/<slug>")
def blog_post(slug):

    current_app.logger.info(f"Blog post viewed: {slug}")

    post=Content.query.filter_by(
    content_type="blog",
    status="published"
    ).order_by(Content.created_at.desc()) \
    .limit(5).all()
    return render_template("blog/post.html", post=post)

@blog_bp.route("/")
def blog_home():

    posts = Content.query.filter_by(
        content_type="blog",
        status="published"
    ).order_by(Content.created_at.desc()).all()

    return render_template("blog/index.html", posts=posts)