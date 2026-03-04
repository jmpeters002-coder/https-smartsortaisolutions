from flask import Blueprint, render_template
from models import News

news_bp = Blueprint("news", __name__)

@news_bp.route("/news")
def news():
    articles = News.query.filter_by(post_type="news")\
        .order_by(News.created_at.desc()).all()

    return render_template("news.html", articles=articles)


@news_bp.route("/blog")
def blog():
    articles = News.query.filter_by(post_type="blog")\
        .order_by(News.created_at.desc()).all()

    return render_template("news.html", articles=articles)


@news_bp.route("/news/<slug>")
def news_detail(slug):
    article = News.query.filter_by(slug=slug).first_or_404()

    return render_template("news_detail.html", article=article)