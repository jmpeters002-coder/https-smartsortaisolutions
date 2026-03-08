from flask import Blueprint, render_template, current_app
from models.blog import Blog

blog_bp = Blueprint("blog", __name__)

# BLOG LIST PAGE
@blog_bp.route("/blog/")
def blog_home():

    current_app.logger.info("Blog page visited")

    posts = Blog.query.filter_by(status="published") \
                      .order_by(Blog.created_at.desc()) \
                      .all()

    return render_template("blog/index.html", posts=posts)


# SINGLE ARTICLE PAGE
@blog_bp.route("/blog/<slug>")
def blog_post(slug):

    current_app.logger.info(f"Blog post viewed: {slug}")

    post = Blog.query.filter_by(slug=slug, status="published").first_or_404()

    return render_template("blog/post.html", post=post)