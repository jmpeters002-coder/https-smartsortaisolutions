from flask import Flask, current_app
from extensions import db
from flask_mail import Mail
import os
from flask import session
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "SmartSortFallbackSecretKey2026"
)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://postgres:mnipn2026@localhost/smartsort_db"

from extensions import db
db.init_app(app)

mail = Mail(app)

# Import blueprints
def register_blueprints():
    from routes.public_routes import public_bp
    from routes.blog_routes import blog_bp
    from routes.order_routes import order_bp
    from routes.payment_routes import payment_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(blog_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(admin_bp)
register_blueprints()
def generate_csrf_token():
    token = session.get('csrf_token')

    if not token:
        token = secrets.token_urlsafe(32)
        session['csrf_token'] = token

    return token
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf_token)
    
app.config["UPLOAD_FOLDER"] = "static/uploads/news"

if __name__ == "__main__":
    app.run()