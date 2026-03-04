from flask import Blueprint, render_template, abort
from models import Blog

blog_bp = Blueprint("blog_bp", __name__, url_prefix="/blog")


# Blog listing page

@blog_bp.route("/")
def blog_home():

    from flask import current_app

    with current_app.app_context():
        posts = Blog.query.order_by(Blog.created_at.desc()).all()

    return render_template("blog.html", posts=posts)

# Blog detail page
@blog_bp.route("/<slug>")
def blog_post(slug):

    post = Blog.query.filter_by(slug=slug).first()

    if not post:
        abort(404)

    return render_template("blog_post.html", post=post)