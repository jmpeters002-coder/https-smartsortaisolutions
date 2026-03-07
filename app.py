import os
import secrets
from flask import Flask, session
from flask_mail import Mail
from dotenv import load_dotenv

from extensions import db

load_dotenv()

app = Flask(__name__)

# =============================
# DATABASE CONFIGURATION
# =============================

database_url = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/smartsort_db"
)

# Fix Render postgres:// bug
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# =============================
# OTHER APP CONFIG
# =============================

app.config["UPLOAD_FOLDER"] = "static/uploads/news"
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

# Ensure upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# =============================
# INITIALIZE EXTENSIONS
# =============================

db.init_app(app)
mail = Mail(app)

# =============================
# CREATE DATABASE TABLES
# =============================

with app.app_context():
    db.create_all()

# =============================
# REGISTER BLUEPRINTS
# =============================

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

# =============================
# CSRF TOKEN GENERATOR
# =============================

def generate_csrf_token():
    token = session.get("csrf_token")

    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token

    return token


@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf_token)

# =============================
# RUN LOCALLY
# =============================

if __name__ == "__main__":
    app.run(debug=True)