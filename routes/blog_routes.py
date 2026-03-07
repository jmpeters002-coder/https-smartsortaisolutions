from flask import Blueprint, render_template
from models import Blog
from services.blog_service import create_blog
from flask import request

blog_bp = Blueprint("blog_bp", __name__, url_prefix="/blog")


# Blog listing page
@blog_bp.route("/")
def blog_home():

   page = request.args.get("page", 1, type=int)

   posts = Blog.query.filter_by(status="published")\
    .order_by(Blog.created_at.desc())\
    .all()
   return render_template("blog.html", posts=posts)

# Blog detail page
@blog_bp.route("/<slug>")
def blog_post(slug):

    post = Blog.query.filter_by(slug=slug).first_or_404()

    return render_template("blog_details.html", post=post)