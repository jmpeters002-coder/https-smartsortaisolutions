from flask import Blueprint, render_template
from models import News

news_bp = Blueprint("news_bp", __name__, url_prefix="/news")

@news_bp.route("/")
def news_home():

    articles = News.query.order_by(
        News.created_at.desc()
    ).all()

    return render_template("news.html", articles=articles)


@news_bp.route("/<slug>")
def news_post(slug):

    article = News.query.filter_by(slug=slug).first_or_404()

    return render_template("news_details.html", post=article)

@news_bp.route("/blog")
def blog():
    articles = News.query.filter_by(post_type="blog")\
        .order_by(News.created_at.desc()).all()

    return render_template("news.html", articles=articles)

