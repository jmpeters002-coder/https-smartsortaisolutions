import os
import secrets
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, session, request
from flask_mail import Mail
from dotenv import load_dotenv

from extensions import db, migrate

# =============================
# LOAD ENV VARIABLES
# =============================

load_dotenv()

# =============================
# CREATE FLASK APP
# =============================

app = Flask(__name__)

# =============================
# LOGGING CONFIGURATION
# =============================

if not os.path.exists("logs"):
    os.mkdir("logs")

file_handler = RotatingFileHandler(
    "logs/smartsort.log", maxBytes=10240, backupCount=10
)

file_handler.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
))

file_handler.setLevel(logging.INFO)

app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

app.logger.info("SmartSort AI startup")
werkzeug_logger = logging.getLogger("werkzeug")
werkzeug_logger.setLevel(logging.INFO)
werkzeug_logger.addHandler(file_handler)    

streamhandler = logging.StreamHandler()
streamhandler.setLevel(logging.INFO)
app.logger.addHandler(streamhandler)    

# =============================
# DATABASE CONFIGURATION
# =============================

database_url = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/smartsort_db"
)

# Fix Render postgres bug
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# =============================
# OTHER APP CONFIG
# =============================
app.config["SECRET_KEY"] = "super-secret-key"
app.secret_key = os.getenv("SECRET_KEY")

app.config["UPLOAD_FOLDER"] = "static/uploads/news"

# Ensure upload folder exists

# =============================
# INITIALIZE EXTENSIONS
# =============================

db.init_app(app)
mail = Mail(app)
migrate.init_app(app, db)

# =============================
# CREATE DATABASE TABLES
# =============================


# =============================
# REGISTER BLUEPRINTS
# =============================

def register_blueprints():
    # Auth blueprints
    from routes.auth_routes import auth_bp
    
    # Existing blueprints
    from routes.public_routes import public_bp
    from routes.order_routes import order_bp
    from routes.payment_routes import payment_bp
    from routes.admin_routes import admin_bp
    from routes.blog_routes import blog_bp
    from routes.news_routes import news_bp
    
    # New blueprints
    from routes.newsletter_routes import newsletter_bp
    from routes.freelance_routes import freelance_bp
    from routes.affiliate_routes import affiliate_bp
    from routes.job_routes import job_bp
    from routes.user_dashboard_routes import user_dashboard_bp
    from routes.courses_management_routes import courses_bp
    
    # Register auth blueprint (no prefix - uses /login, /signup, etc.)
    app.register_blueprint(auth_bp)
    
    # Register all other blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(blog_bp, url_prefix="/blog")
    app.register_blueprint(news_bp)
    app.register_blueprint(newsletter_bp)
    app.register_blueprint(freelance_bp)
    app.register_blueprint(affiliate_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(user_dashboard_bp)
    app.register_blueprint(courses_bp)

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
# REQUEST LOGGER
# =============================

@app.before_request
def log_request():
    app.logger.info(
        f"{request.method} {request.path} from{request.path}")



import click
from models import User

@app.cli.command("create-admin")
@click.argument("username")
@click.argument("password")
def create_admin(username, password):

    admin = User(
        login=username,
        is_admin=True
    )

    admin.set_password(password)

    db.session.add(admin)
    db.session.commit()

    print("Admin created successfully!")
# =============================
# RUN APP
# =============================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    
    # Print dev link
    print("\n" + "="*70)
    print("✨ SmartSort AI Server Started")
    print("="*70)
    print(f"🌐 Development Link: http://localhost:{port}")
    print(f"🔗 Full URL: http://127.0.0.1:{port}")
    print(f"🐛 Debug Mode: {'✓ ON' if debug else '✗ OFF'}")
    print("="*70)
    print("💡 Tip: Press Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    app.run(
        host="0.0.0.0", 
        port=port, 
        debug=debug,
        use_reloader=False
    )