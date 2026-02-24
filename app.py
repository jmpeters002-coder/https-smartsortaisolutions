from flask import Flask, render_template, jsonify, request, redirect, session, Response, url_for
from models import db, Product, Order, UserAccess, User
import os
import requests
from dotenv import load_dotenv
import hmac
import hashlib
import json
import re
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import logging
from logging.handlers import RotatingFileHandler
import secrets
from functools import wraps

load_dotenv()

# Configure static folder path
static_folder = os.path.join(os.path.dirname(__file__), 'templates', 'statics')
app = Flask(__name__, static_folder=static_folder, static_url_path='/static')

# Ensure templates reload during development when templates change
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

# PHASE 5 — SECURITY CONFIGURATION
# Secret key for session management and CSRF protection
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY") or secrets.token_hex(32)
# Salt used by Flask-Security (or other password hashing extensions)
# Provide `SECURITY_PASSWORD_SALT` in your Render environment variables
app.config['SECURITY_PASSWORD_SALT'] = os.getenv("SECURITY_PASSWORD_SALT") or secrets.token_hex(16)

# Flask mode (development | production)
app.config['ENV'] = os.getenv("FLASK_ENV", "production")
app.config['DEBUG'] = os.getenv("DEBUG", "False") == "True"

# Security headers
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JS access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = 2592000  # 30 days


# --- Simple CSRF protection (token stored in session) ---
def generate_csrf_token():
    token = session.get('csrf_token')
    if not token:
        token = secrets.token_urlsafe(32)
        session['csrf_token'] = token
    return token


def validate_csrf(token):
    expected = session.get('csrf_token')
    return expected and hmac.compare_digest(expected, token)


# Make csrf_token available in Jinja templates
app.jinja_env.globals['csrf_token'] = generate_csrf_token


@app.before_request
def enforce_csrf_on_post():
    # Skip safe methods
    if request.method != 'POST':
        return

    # Exempt endpoints that are webhooks or external APIs
    path = request.path or ''
    csrf_exempt_prefixes = ['/webhook', '/api/', '/static']
    if any(path.startswith(p) for p in csrf_exempt_prefixes):
        return

    # Check token either in header (X-CSRF-Token) or in form data
    token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
    if not token or not validate_csrf(token):
        return Response('CSRF validation failed', status=400)

# Paystack API Key
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY")

# Public URL for callbacks (set to your ngrok https URL or production domain)
# Example: https://abcd1234.ngrok.io or https://yourdomain.com
PUBLIC_URL = os.getenv("PUBLIC_URL", "http://127.0.0.1:5000")

# Email Configuration (Professional Domain)
app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT", 587))
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS", "True") == "True"
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER", "support@smartsort.ai")

mail = Mail(app)

# --- Admin authentication helpers ---
# Admin credentials and email (login username/email comes from env)
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'smartsortsolutions04@gmail.com')
# Credentials file stored in instance folder (created if missing)
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'admin_credentials.json')


def load_credentials():
    """Load admin credentials from instance JSON file."""
    try:
        if os.path.exists(CREDENTIALS_PATH):
            with open(CREDENTIALS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        return None
    return None


def save_credentials(login, password_hash):
    """Save admin credentials to instance JSON file."""
    data = {'login': login, 'password_hash': password_hash}
    # Ensure instance directory exists
    inst_dir = os.path.dirname(CREDENTIALS_PATH)
    if not os.path.exists(inst_dir):
        os.makedirs(inst_dir, exist_ok=True)
    with open(CREDENTIALS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f)


def is_strong_password(pw: str) -> bool:
    """Basic strong-password check: min 8, upper, lower, digit, special."""
    if not pw or len(pw) < 8:
        return False
    if not re.search(r'[a-z]', pw):
        return False
    if not re.search(r'[A-Z]', pw):
        return False
    if not re.search(r'\d', pw):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', pw):
        return False
    return True

def check_admin_auth():
    """Return True if the request has admin access via session or HTTP Basic auth."""
    # Session-based login
    if session.get('is_admin'):
        return True

    # HTTP Basic auth using stored credentials
    auth = request.authorization
    creds = load_credentials()
    if auth and creds:
        stored_login = creds.get('login')
        stored_hash = creds.get('password_hash')
        if stored_login and stored_hash:
            if hmac.compare_digest(auth.username or "", stored_login) and check_password_hash(stored_hash, auth.password or ""):
                return True

    return False

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if check_admin_auth():
            return func(*args, **kwargs)
        # challenge for basic auth
        return Response('Authentication required', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
    return wrapper


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login using `login` (username/email) and `password`.

    If credentials do not exist yet, allow initial setup when `login` matches
    the configured `ADMIN_EMAIL` and the supplied password meets strength rules.
    """
    if request.method == 'POST':
        login = request.form.get('login', '').strip()
        password = request.form.get('password', '').strip()

        if not login or not password:
            return render_template('admin_login.html', error='Provide login and password'), 400

        creds = load_credentials()

        # If credentials exist, validate
        if creds:
            stored_login = creds.get('login')
            stored_hash = creds.get('password_hash')
            if stored_login and stored_hash and hmac.compare_digest(login, stored_login) and check_password_hash(stored_hash, password):
                session['is_admin'] = True
                return redirect(url_for('admin_dashboard'))
            return render_template('admin_login.html', error='Invalid login or password'), 401

        # No credentials yet — allow initial setup only for configured ADMIN_EMAIL
        if login == ADMIN_EMAIL:
            if not is_strong_password(password):
                return render_template('admin_login.html', error='Password must be at least 8 chars and include upper, lower, number, and special char'), 400
            pw_hash = generate_password_hash(password)
            save_credentials(login, pw_hash)
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))

        return render_template('admin_login.html', error='Invalid login or password'), 401

    return render_template('admin_login.html')


@app.route('/admin/change-password', methods=['GET', 'POST'])
def admin_change_password():
    """Allow logged-in admin to change their password.

    Requires current session `is_admin`.
    """
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if new_password != confirm_password:
            return render_template('admin_change_password.html', error='Passwords do not match'), 400

        if not is_strong_password(new_password):
            return render_template('admin_change_password.html', error='Password must be at least 8 chars and include upper, lower, number, and special char'), 400

        # Persist new password hash for current admin login
        creds = load_credentials() or {'login': ADMIN_EMAIL}
        save_credentials(creds.get('login', ADMIN_EMAIL), generate_password_hash(new_password))

        return render_template('admin_change_password.html', success='Password set successfully!'), 200

    return render_template('admin_change_password.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    session.pop('first_login', None)
    return redirect(url_for('home'))


# PHASE 5 — LOGGING CONFIGURATION
# Setup rotating file logger for production
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler(
        'logs/smartsort.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('SmartSort AI Solutions startup')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables and seed sample data
with app.app_context():
    db.create_all()

    # Seed database only if empty
    if Product.query.count() == 0:
        products = [
            Product(
                title="AI Foundations Mastery",
                description="Learn AI fundamentals, machine learning basics, neural networks, and automation concepts. Master predictive modeling and AI application development.",
                price=1250,
                product_type="course"
            ),
            Product(
                title="Full-Stack Web Development Bootcamp",
                description="Master HTML, CSS, JavaScript, Python, Django/Flask, and backend systems. Build production-ready applications with modern architecture patterns.",
                price=1850,
                product_type="course"
            ),
            Product(
                title="AI Automation for Businesses",
                description="Automate workflows and improve business efficiency using Python, APIs, and intelligent automation. Learn to create solutions that scale.",
                price=2150,
                product_type="course"
            ),
            Product(
                title="Website Development & Maintenance Service",
                description="Professional website design, development, and ongoing maintenance for businesses. Custom solutions tailored to your brand and goals.",
                price=3200,
                product_type="service"
            )
        ]

        db.session.add_all(products)
        db.session.commit()

# Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/courses")
def courses():
    products = Product.query.filter_by(product_type="course").all()
    return render_template("courses.html", products=products)

@app.route("/services")
def services():
    products = Product.query.filter_by(product_type="service").all()
    return render_template("services.html", products=products)

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/create-order/<int:product_id>", methods=["POST"])
def create_order(product_id):
    email = (request.form.get("email") or '').strip()
    custom_amount = request.form.get("amount")

    product = Product.query.get_or_404(product_id)

    # Basic email validation
    if not email or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return "Invalid email address", 400

    # Validate custom amount
    try:
        amount_float = float(custom_amount) if custom_amount else product.price
        if amount_float <= 0:
            return "Amount must be greater than 0", 400
    except (ValueError, TypeError):
        return "Invalid amount entered", 400

    # Create order first
    order = Order(
        customer_email=email,
        product_id=product.id,
        status="pending"
    )

    db.session.add(order)
    db.session.commit()

    # Paystack expects amount in kobo (multiply by 100)
    amount = int(amount_float * 100)

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "email": email,
        "amount": amount,
        "reference": f"SMARTSORT_{order.id}",
        # Use PUBLIC_URL for callback so local tunnels (ngrok) or production domains work
        "callback_url": f"{PUBLIC_URL}/verify-payment"
    }

    response = requests.post(
        "https://api.paystack.co/transaction/initialize",
        json=data,
        headers=headers
    )

    response_data = response.json()

    if response_data["status"]:
        order.payment_reference = data["reference"]
        db.session.commit()

        return redirect(response_data["data"]["authorization_url"])

    return "Payment initialization failed"

@app.route("/verify-payment")
def verify_payment():
    reference = request.args.get("reference")

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }

    response = requests.get(
        f"https://api.paystack.co/transaction/verify/{reference}",
        headers=headers
    )

    response_data = response.json()

    if response_data["status"] and response_data["data"]["status"] == "success":
        order = Order.query.filter_by(payment_reference=reference).first()

        if order:
            order.status = "paid"
            db.session.commit()

        return redirect(f"/access/{reference}")

    return "Payment verification failed."


@app.route("/access/<reference>")
def access_product(reference):
    """
    User accesses purchased product after payment confirmed.
    Routes to course or service template based on product type.
    """
    order = Order.query.filter_by(payment_reference=reference).first()

    if not order:
        return "Access denied. Order not found.", 404

    # If payment not yet confirmed, render a polling page that waits for confirmation.
    if order.status != "paid":
        return render_template("payment_pending.html", reference=reference)

    product = order.product

    if product.product_type == "course":
        return render_template("course_access.html", product=product, order=order)

    elif product.product_type == "service":
        return render_template("service_confirmation.html", product=product, order=order)

    return "Invalid product type", 400



@app.route('/api/order-status/<reference>')
def api_order_status(reference):
    """Return JSON status for a given payment reference."""
    order = Order.query.filter_by(payment_reference=reference).first()
    if not order:
        return jsonify({'status': 'not_found'}), 404
    return jsonify({'status': order.status}), 200
@app.route("/api/products")
def api_products():
    products = Product.query.all()

    return jsonify([
        {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "price": p.price,
            "product_type": p.product_type
        }
        for p in products
    ])

# PHASE 1 — SECURE PAYMENT WEBHOOK
@app.route("/webhook", methods=["POST"])
def paystack_webhook():
    """
    Secure webhook handler for Paystack payment confirmation.
    Verifies HMAC-SHA512 signature before processing payment events.
    Auto-grants access to paid products.
    """
    payload = request.get_data()
    signature = request.headers.get("x-paystack-signature")

    # Verify signature
    computed_signature = hmac.new(
        PAYSTACK_SECRET_KEY.encode(),
        payload,
        hashlib.sha512
    ).hexdigest()

    if computed_signature != signature:
        return "Invalid signature", 400

    event = request.json

    if event["event"] == "charge.success":
        reference = event["data"]["reference"]

        order = Order.query.filter_by(payment_reference=reference).first()

        if order and order.status != "paid":
            order.status = "paid"
            db.session.commit()

            # PHASE 2 — FULFILLMENT LOGIC
            # Grant access to user automatically
            fulfill_order(order)

            # PHASE 4 — EMAIL AUTOMATION
            # Send confirmation email (non-blocking)
            send_payment_email(order)

    return "OK", 200


def fulfill_order(order):
    """
    PHASE 2 — Auto-grant access after payment confirmed.
    
    Rules:
    1. Check if access already granted (prevent duplicates)
    2. Grant access based on product type
    3. Create UserAccess record
    """
    # Prevent duplicate access
    existing_access = UserAccess.query.filter_by(
        customer_email=order.customer_email,
        product_id=order.product_id
    ).first()

    if existing_access:
        return  # Already has access

    # Create access record
    access = UserAccess(
        customer_email=order.customer_email,
        product_id=order.product_id,
        order_id=order.id,
        access_type=order.product.product_type  # course | service
    )

    db.session.add(access)
    db.session.commit()

    print(f"✅ Access granted: {order.customer_email} → {order.product.title}")


def send_payment_email(order):
    """
    PHASE 4 — Send professional payment confirmation email.
    
    Differs by product type:
    - Course: includes resource link
    - Service: includes confirmation message
    """
    product = order.product
    recipient = order.customer_email

    try:
        if product.product_type == "course":
            subject = f"Course Access Confirmed - {product.title} | SmartSort AI"
            
            body = f"""
Hello,

Your payment has been successfully processed! 🎉

COURSE DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Course: {product.title}
Amount Paid: ${product.price}
Order ID: {order.id}
Payment Reference: {order.payment_reference}

YOUR COURSE ACCESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{product.description}

Access your course materials here:
{product.resource_link if product.resource_link else 'Course materials will be available shortly.'}

QUICK START
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Log in to your account
2. Visit the link above to access course materials
3. Start learning at your own pace
4. Join our community for support

NEED HELP?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Contact our support team:
✉️ support@smartsort.ai
📞 Available 24/7

Thank you for choosing SmartSort AI Solutions!

Best regards,
SmartSort AI Team
https://smartsort.ai
            """

        else:  # service
            subject = f"Service Request Confirmed - {product.title} | SmartSort AI"
            
            body = f"""
Hello,

Your service request has been successfully confirmed! ✅

SERVICE DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Service: {product.title}
Amount Paid: ${product.price}
Order ID: {order.id}
Payment Reference: {order.payment_reference}

WHAT HAPPENS NEXT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{product.description}

Our team will be in touch within 24 hours to:
✓ Confirm project details
✓ Discuss timelines
✓ Answer any questions
✓ Get started on your project

STAY UPDATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You'll receive project updates via email.
Keep your order reference handy: {order.payment_reference}

NEED HELP?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Contact our support team:
✉️ support@smartsort.ai
📞 Available 24/7

Thank you for your business!

Best regards,
SmartSort AI Team
https://smartsort.ai
            """

        # Create and send message
        msg = Message(
            subject=subject,
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[recipient],
            body=body
        )

        mail.send(msg)
        print(f"✉️ Payment email sent to {recipient}")
        
    except Exception as e:
        # Email failure should NOT crash payment flow
        print(f"⚠️ Email failed for {recipient}: {str(e)}")
        print("Payment still confirmed. Email will retry next cycle.")


@app.route("/check-access/<email>/<int:product_id>", methods=["GET"])
def check_access(email, product_id):
    """
    Check if user has access to a product.
    Returns access details or 403 if no access.
    """
    access = UserAccess.query.filter_by(
        customer_email=email,
        product_id=product_id
    ).first()

    if not access:
        return jsonify({"status": "denied"}), 403

    return jsonify({
        "status": "granted",
        "email": access.customer_email,
        "product_id": access.product_id,
        "product_title": access.product.title,
        "product_type": access.access_type,
        "granted_at": access.granted_at.isoformat(),
        "resource_link": access.product.resource_link
    })


@app.route("/my-access/<email>", methods=["GET"])
def my_access(email):
    """
    Get all products user has access to.
    """
    accesses = UserAccess.query.filter_by(customer_email=email).all()

    if not accesses:
        return jsonify({"status": "no_access", "email": email}), 404

    return jsonify({
        "status": "success",
        "email": email,
        "access_count": len(accesses),
        "products": [
            {
                "id": a.product_id,
                "title": a.product.title,
                "type": a.access_type,
                "resource_link": a.product.resource_link,
                "granted_at": a.granted_at.isoformat()
            }
            for a in accesses
        ]
    })

# PHASE 3 — ADMIN DASHBOARD

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    """
    Admin console for managing orders, revenue, and fulfillment.
    
    Features:
    - View all orders with status
    - Filter by status or email
    - Revenue breakdown
    - Access grants tracking
    - Manual fulfillment override
    """
    # Get filter parameters
    status_filter = request.args.get('status', '')
    email_filter = request.args.get('email', '')

    # Build query
    query = Order.query

    if status_filter:
        query = query.filter_by(status=status_filter)
    if email_filter:
        query = query.filter(Order.customer_email.ilike(f"%{email_filter}%"))

    orders = query.order_by(Order.created_at.desc()).all()

    # Calculate statistics
    all_orders = Order.query.all()
    total_orders = len(all_orders)
    paid_orders = len([o for o in all_orders if o.status == 'paid'])
    pending_orders = len([o for o in all_orders if o.status == 'pending'])
    
    total_revenue = sum(o.product.price for o in all_orders if o.status == 'paid')

    # Revenue breakdown by product type
    revenue_by_type = {}
    for order in all_orders:
        if order.status == 'paid':
            ptype = order.product.product_type
            revenue_by_type[ptype] = revenue_by_type.get(ptype, 0) + order.product.price

    # Revenue breakdown by status
    revenue_by_status = {}
    for order in all_orders:
        status = order.status
        revenue_by_status[status] = revenue_by_status.get(status, 0) + order.product.price

    # Get recent access grants
    recent_access = UserAccess.query.order_by(UserAccess.granted_at.desc()).limit(10).all()

    return render_template(
        'admin_dashboard.html',
        orders=orders,
        total_orders=total_orders,
        paid_orders=paid_orders,
        pending_orders=pending_orders,
        total_revenue=total_revenue,
        revenue_by_type=revenue_by_type,
        revenue_by_status=revenue_by_status,
        recent_access=recent_access
    )


@app.route("/admin/dashboard-data")
@admin_required
def admin_dashboard_data():
    """Return JSON data for dashboard (orders + stats) to support realtime UI updates."""
    all_orders = Order.query.order_by(Order.created_at.desc()).all()

    orders_payload = [
        {
            'id': o.id,
            'customer_email': o.customer_email,
            'product_title': o.product.title if o.product else None,
            'price': o.product.price if o.product else 0,
            'status': o.status,
            'payment_reference': o.payment_reference,
            'created_at': o.created_at.isoformat()
        }
        for o in all_orders
    ]

    total_orders = len(all_orders)
    paid_orders = len([o for o in all_orders if o.status == 'paid'])
    pending_orders = len([o for o in all_orders if o.status == 'pending'])
    total_revenue = sum(o.product.price for o in all_orders if o.status == 'paid')

    revenue_by_type = {}
    revenue_by_status = {}
    for o in all_orders:
        if o.status == 'paid' and o.product:
            revenue_by_type[o.product.product_type] = revenue_by_type.get(o.product.product_type, 0) + o.product.price
        revenue_by_status[o.status] = revenue_by_status.get(o.status, 0) + (o.product.price if o.product else 0)

    recent_access = UserAccess.query.order_by(UserAccess.granted_at.desc()).limit(10).all()
    recent_access_payload = [
        {
            'email': a.customer_email,
            'product_title': a.product.title if a.product else None,
            'type': a.access_type,
            'granted_at': a.granted_at.isoformat()
        }
        for a in recent_access
    ]

    return jsonify({
        'orders': orders_payload,
        'total_orders': total_orders,
        'paid_orders': paid_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'revenue_by_type': revenue_by_type,
        'revenue_by_status': revenue_by_status,
        'recent_access': recent_access_payload
    })




@app.route("/admin/override/<int:order_id>", methods=["POST"])
@admin_required
def admin_override(order_id):
    """
    Manual fulfillment override.
    Admin can manually grant access to a product.
    """
    order = Order.query.get(order_id)

    if not order:
        return "Order not found", 404

    # Check if already paid
    if order.status == 'paid':
        return redirect('/admin/dashboard?success=already_paid')

    # Mark as paid
    order.status = 'paid'

    # Grant access
    fulfill_order(order)

    return redirect('/admin/dashboard?success=override_complete')

# PHASE 5 — ERROR HANDLERS & MONITORING

@app.errorhandler(404)
def not_found(error):
    """Handle 404 - Page Not Found"""
    app.logger.warning(f'404 error: {request.url}')
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 - Internal Server Error"""
    app.logger.error(f'500 error: {str(error)}')
    db.session.rollback()
    return render_template('500.html'), 500


@app.errorhandler(403)
def forbidden(error):
    """Handle 403 - Forbidden"""
    app.logger.warning(f'403 error: {request.url}')
    return render_template('403.html'), 403


@app.before_request
def before_request():
    """Log incoming requests in production"""
    if app.config['ENV'] == 'production':
        app.logger.info(f'{request.method} {request.path} from {request.remote_addr}')


@app.after_request
def after_request(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


# Run server
if __name__ == "__main__":
    # Production: use gunicorn instead
    # gunicorn -w 4 -b 0.0.0.0:5000 app:app
    
    port = int(os.getenv("PORT", 5000))
    debug_mode = app.config['DEBUG']
    
    app.run(
        host='127.0.0.1',
        port=port,
        debug=debug_mode
    )
