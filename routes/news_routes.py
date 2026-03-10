from flask import Blueprint, render_template, current_app
from models.content import Content

news_bp = Blueprint("news_bp", __name__, url_prefix="/news")


# NEWS LIST PAGE
@news_bp.route("/")
def news_home():
    articles = Content.query.filter_by(
        content_type="news",
        status="published"
    ).order_by(Content.created_at.desc()).all()
    
    current_app.logger.info("News page visited")
    return render_template("news/index.html", posts=articles)


# SINGLE NEWS ARTICLE
@news_bp.route("/<slug>")
def news_post(slug):
    current_app.logger.info(f"News article viewed: {slug}")
    
    post = Content.query.filter_by(
        content_type="news",
        slug=slug,
        status="published"
    ).first_or_404()
    
    return render_template("news/post.html", post=post)