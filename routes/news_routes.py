from alembic.util import status
from flask import Blueprint, app, render_template, request
from models import News
from routes.admin_routes import generate_slug

news_bp = Blueprint("news_bp", __name__, url_prefix="/news")

@public_bp.route("/news")
def news_page():

    app.logger.info("News page visited")
    posts = News.query.filter(
    News.status == "published"
    ).order_by(
    News.created_at.desc()
    ).all()

    return render_template("news.html", posts=posts)

@admin_bp.route("/news/create", methods=["GET", "POST"])
def create_news():

    if request.method == "POST":
        title = request.form.get("title")
        summary = request.form.get("summary")
        content = request.form.get("content")
        status = request.form.get("status", "draft")
        slug = generate_slug(title)

        new_news = News(
            title=title,
            slug=slug,
            summary=summary,
            content=content,
            status=status   
        )

        db.session.add(new_news)
        db.session.commit()

        flash("News created successfully!", "success")
        return redirect(url_for("admin_bp.admin_dashboard"))

    return render_template("admin/create_news.html")

@news_bp.route("/<slug>")
def news_post(slug):

    article = News.query.filter_by(slug=slug).first_or_404()

    return render_template("news_details.html", post=article)

@news_bp.route("/blog")
def blog():
    app.logger.info("Blog page visited")

    articles = News.query.filter_by(post_type="blog")\
        .order_by(News.created_at.desc()).all()

    return render_template("news.html", articles=articles)
