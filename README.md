# SmartSort AI Solutions

A production-ready Flask e-learning and services marketplace with Paystack payment integration, secure admin dashboard, professional email automation, responsive design, and flexible pricing.

## Features

✅ **E-Learning & Services Marketplace**
- 🛒 Product catalog (courses, services)
- 💳 Flexible payment amounts (customers enter custom price)
- Secure Paystack payment integration with HMAC-SHA512 webhook verification
- 📧 Professional email automation for payment confirmations
- 🔐 Automatic access control - users granted access immediately upon successful payment

✅ **Admin Dashboard & Security**
- 🔐 Session-based admin login + HTTP Basic auth support
- 📊 Admin dashboard with real-time order management and revenue analytics
- 🔍 Order filters (status, email) and manual fulfillment override
- 🛡️ Production security (SECRET_KEY, HTTPS cookies, security headers, HMAC verification)

✅ **Responsive Design**
- 📱 Mobile-first UI with hamburger navigation
- 🎨 Desktop/tablet/mobile optimization
- ✨ Smooth animations and modern gradient styling

✅ **Production Ready**
- 📝 Rotating file logging for audit trails
- 🚀 Deployment-ready for Render with Gunicorn
- 🔒 Environment-based secrets management
- 📊 Revenue tracking and reporting

---

## Tech Stack

- **Backend**: Flask 3.1.3, SQLAlchemy 2.0
- **Database**: SQLite (dev) / PostgreSQL (production via Render)
- **Payment**: Paystack API
- **Email**: Flask-Mail (SMTP)
- **Deployment**: Render with Gunicorn
- **Frontend**: Responsive HTML/CSS/JavaScript
- **Environment**: Python 3.11+

---

## Installation & Setup

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/jmpeters002-coder/https-smartsortaisolutions.git
   cd https-smartsortaisolutions
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\Activate.ps1
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   # Flask Configuration
   FLASK_ENV=development
   DEBUG=True
   SECRET_KEY=your_generated_secret_key_here
   SECURITY_PASSWORD_SALT=your_generated_salt_here

   # Admin Credentials
   ADMIN_USERNAME=admin_4bbf17d1
   ADMIN_PASSWORD=POs-G96HzjFnfdTzh5U6Rgbjk847H2-E

   # Paystack API Keys
   PAYSTACK_SECRET_KEY=sk_test_your_paystack_secret_key
   PAYSTACK_PUBLIC_KEY=pk_test_your_paystack_public_key
   PUBLIC_URL=http://127.0.0.1:5000

   # Email Configuration (Gmail example)
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   MAIL_DEFAULT_SENDER=support@smartsort.ai
   ```

5. **Run the development server**
   ```bash
   python app.py
   ```
   Visit `http://127.0.0.1:5000` in your browser.

---

## Environment Variables

### Required for Production (Render)

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask session encryption key (32 bytes hex) | `6367aac0dedf098c3d16caef5a81475ea77044603d7a4654a639bdff7afcc64d` |
| `SECURITY_PASSWORD_SALT` | Password salt for security extensions (16 bytes hex) | `2d550dc96b3127d81d5bb8828bb22b73` |
| `ADMIN_USERNAME` | Admin dashboard username | `admin_4bbf17d1` |
| `ADMIN_PASSWORD` | Admin dashboard password | `POs-G96HzjFnfdTzh5U6Rgbjk847H2-E` |
| `PAYSTACK_SECRET_KEY` | Paystack API secret key | `sk_test_...` |
| `PAYSTACK_PUBLIC_KEY` | Paystack API public key | `pk_test_...` |
| `PUBLIC_URL` | Base URL for payment callbacks | `https://your-render-domain.onrender.com` |
| `MAIL_USERNAME` | Email sender address | `noreply@smartsort.ai` |
| `MAIL_PASSWORD` | Email account password/token | (app-specific password) |

---

## Admin Access

### Login Methods

1. **Session-based Login** (recommended for web)
   - Visit `/admin/login`
   - Enter `ADMIN_USERNAME` and `ADMIN_PASSWORD`
   - Session expires after 30 days (configurable)

2. **HTTP Basic Authentication** (for API/automation)
   ```bash
   curl -u admin_4bbf17d1:POs-G96HzjFnfdTzh5U6Rgbjk847H2-E https://your-domain.com/admin/dashboard
   ```

### Features
- View all orders with filters (status, email)
- Track revenue by product type
- Manual order fulfillment override
- Access grant history

---

## Deployment to Render

### 1. Connect GitHub Repository

1. Log in to [Render](https://render.com)
2. Click **New** → **Web Service**
3. Select **Build and deploy from a Git repository**
4. Connect your GitHub account and select `https-smartsortaisolutions`

### 2. Configure Service

| Setting | Value |
|---------|-------|
| **Name** | smartsort-ai-v1 |
| **Environment** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 3` |
| **Instance Type** | Free or Starter (upgrade as needed) |

### 3. Set Environment Variables

In Render dashboard → **Environment**, add:

```
SECRET_KEY=6367aac0dedf098c3d16caef5a81475ea77044603d7a4654a639bdff7afcc64d
SECURITY_PASSWORD_SALT=2d550dc96b3127d81d5bb8828bb22b73
ADMIN_USERNAME=admin_4bbf17d1
ADMIN_PASSWORD=POs-G96HzjFnfdTzh5U6Rgbjk847H2-E
PAYSTACK_SECRET_KEY=sk_test_your_key
PAYSTACK_PUBLIC_KEY=pk_test_your_key
PUBLIC_URL=https://your-render-domain.onrender.com
FLASK_ENV=production
DEBUG=False
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_DEFAULT_SENDER=support@smartsort.ai
```

### 4. Deploy

Click **Deploy** and wait for the build to complete. Your app will be live at `https://your-service-name.onrender.com`.

### Post-Deployment

- Verify health check: `https://your-domain.com/` should return the home page
- Test admin login: `https://your-domain.com/admin/login`
- Update Paystack webhook URL to point to your Render domain

---

## Payment Flow

### Customer Flow
1. Browse courses/services
2. Click "Enroll Now" or "Request Service"
3. Enter email and **custom payment amount**
4. Redirected to Paystack payment page
5. Complete payment
6. On success, automatic access is granted
7. Confirmation email sent

### Admin Flow
1. Log in to `/admin/dashboard`
2. View orders with revenue metrics
3. Optionally override fulfillment for pending orders

**Security**: Webhook verification prevents forged payments using secret key HMAC hashing.

---

## Project Structure

```
smartsort-ai-v1/
├── app.py                      # Main Flask application
├── models.py                   # Database models (Product, Order, UserAccess)
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git exclusions
├── .gitattributes              # Git LFS tracking
├── README.md                   # This file
├── DEPLOYMENT.md               # Deployment guide
├── templates/
│   ├── base.html              # Base template (nav, footer, responsive)
│   ├── index.html             # Home page
│   ├── courses.html           # Courses with enrollment modal
│   ├── services.html          # Services with enrollment modal
│   ├── contact.html           # Contact page
│   ├── admin_login.html       # Admin login form
│   ├── admin_dashboard.html   # Admin dashboard
│   ├── course_access.html     # Course access page
│   ├── service_confirmation.html # Service confirmation
│   ├── 403.html, 404.html, 500.html # Error pages
│   └── statics/
│       ├── css/style.css      # Responsive design
│       └── js/script.js       # Mobile nav toggle
├── logs/
│   └── smartsort.log          # Rotating log file
└── instance/
    └── database.db            # SQLite database (dev only)
```

---

## API Endpoints

### Public
- `GET /` - Home page
- `GET /courses` - Course catalog
- `GET /services` - Services catalog
- `GET /contact` - Contact page
- `POST /create-order/<product_id>` - Create order with custom amount
- `GET /verify-payment` - Paystack callback
- `POST /webhook` - Paystack webhook (HMAC verified)
- `GET /access/<reference>` - Access purchased product
- `GET /check-access/<email>/<product_id>` - Check user access
- `GET /my-access/<email>` - Get all user accesses

### Admin (Protected)
- `GET /admin/login` - Admin login form
- `POST /admin/login` - Submit login credentials
- `GET /admin/dashboard` - Admin dashboard
- `POST /admin/override/<order_id>` - Manual fulfillment override
- `GET /admin/logout` - Logout

---

## Paystack Configuration

### Webhook Setup

1. Log in to [Paystack Dashboard](https://dashboard.paystack.com)
2. Go to **Settings** → **API Keys & Webhooks**
3. Add webhook URL: `https://your-render-domain.onrender.com/webhook`
4. Select events:
   - `charge.success`
   - `charge.failed`
5. Copy your **Secret Key** and **Public Key** to Render environment variables

---

## Database Schema

### Product
```sql
id (INT PRIMARY KEY)
title VARCHAR - Course title or service name
description TEXT - Product details
price FLOAT - Suggested price (user can override)
product_type VARCHAR - "course" or "service"
resource_link VARCHAR - URL to course/service material
created_at DATETIME - Creation timestamp
```

### Order
```sql
id (INT PRIMARY KEY)
customer_email VARCHAR NOT NULL - Buyer email
product_id INT FOREIGN KEY -> Product.id
payment_reference VARCHAR UNIQUE - Paystack reference ID
status VARCHAR - "pending" or "paid"
created_at DATETIME - Order timestamp
```

### UserAccess
```sql
id (INT PRIMARY KEY)
customer_email VARCHAR NOT NULL - Buyer email
product_id INT FOREIGN KEY -> Product.id
order_id INT FOREIGN KEY -> Order.id
access_type VARCHAR - "course" or "service"
granted_at DATETIME - Access grant timestamp
UNIQUE CONSTRAINT (customer_email, product_id) - Prevent duplicates
```

---

## Security Notes

⚠️ **Never commit secrets to Git:**
- Use `.env` locally (ignored by `.gitignore`)
- Use Render environment variables for production
- Rotate passwords and API keys regularly

✅ **Best Practices:**
- Keep `SECRET_KEY` and `SECURITY_PASSWORD_SALT` random and unique
- Use HTTPS only in production (`SESSION_COOKIE_SECURE=True`)
- Enable webhook signature verification (already implemented)
- Sanitize user input (Flask handles via Jinja2 escaping)
- Rate-limit admin login attempts (optional: use fail2ban or similar)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Build fails on Render with `requirements.txt` not found** | Ensure `requirements.txt` is in repo root and pushed |
| **Admin login not working** | Verify `ADMIN_USERNAME` and `ADMIN_PASSWORD` are set in Render environment |
| **Payment webhook not received** | Check webhook URL in Paystack dashboard matches your Render domain |
| **Email not sending** | Verify SMTP credentials; use app-specific password for Gmail (not account password) |
| **Responsive design not working** | Ensure `meta viewport` tag is in `templates/base.html` |
| **Database locked** | Delete `instance/database.db` and restart app |

---

## Support & Resources

- **Paystack Docs**: https://paystack.com/docs
- **Flask Docs**: https://flask.palletsprojects.com
- **Render Docs**: https://docs.render.com
- **GitHub Repo**: https://github.com/jmpeters002-coder/https-smartsortaisolutions

---

## License

© 2026 SmartSort AI Solutions. All rights reserved.

---

## Changelog

### v1.1.0 (2026-02-23)
- ✅ Admin authentication (session + HTTP Basic auth)
- ✅ Responsive mobile-first design with hamburger nav
- ✅ Flexible payment amounts (custom pricing)
- ✅ Git LFS support for model binaries
- ✅ Render deployment ready with Gunicorn

### v1.0.0 (2026-01-15)
- Initial release
- Paystack payment integration
- Email automation
- Admin dashboard
- SQLAlchemy ORM

---

## Email Templates

### Course Confirmation
```
Subject: Your Course Access is Ready!
Body: 
  Hi [Customer Name],
  
  Thank you for purchasing [Course Title]!
  Click here to access: [Direct link to course]
  
  Happy learning!
```

### Service Confirmation
```
Subject: Your Service Request Confirmation
Body:
  Hi [Customer Name],
  
  We've received your request for [Service Name].
  Our team will contact you within 24-48 hours.
  Your order reference: [Order ID]
```

---

## Security Features

🔒 **Production Hardening**
- `SECRET_KEY`: 32-char random hex for session signing and CSRF protection
- `SESSION_COOKIE_SECURE`: HTTPS-only cookies in production
- `SESSION_COOKIE_HTTPONLY`: Prevent XSS cookie theft
- `SESSION_COOKIE_SAMESITE`: Prevent CSRF attacks (Lax mode)

🛡️ **Security Headers**
- `X-Content-Type-Options: nosniff` - Prevent MIME type sniffing
- `X-Frame-Options: SAMEORIGIN` - Prevent clickjacking
- `X-XSS-Protection: 1; mode=block` - Legacy XSS protection
- `Strict-Transport-Security: max-age=31536000` - Force HTTPS for 1 year

📝 **Logging & Monitoring**
- RotatingFileHandler: 10MB max size, 10 backup files
- Request logging: Every GET/POST to logs/smartsort.log
- Error logging: 404, 500, 403 errors tracked
- Webhook logging: All payments logged for audit trail

✔️ **Payment Security**
- HMAC-SHA512 signature verification (Paystack webhook)
- Prevents forged/replayed payment notifications
- Payment reference validation

---

## Development Commands

```bash
# Run in development (debug mode)
python app.py

# Run in production mode
FLASK_ENV=production DEBUG=False python app.py

# With Gunicorn (4 workers)
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# View logs
tail -f instance/logs/smartsort.log

# Database check
sqlite3 instance/database.db ".tables"
```

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Homepage |
| GET | `/courses` | Course catalog |
| GET | `/services` | Services catalog |
| GET | `/contact` | Contact page |
| POST | `/create-order` | Initialize payment |
| GET | `/verify-payment?reference=X` | Verify payment (internal) |
| POST | `/webhook` | Paystack webhook (external) |
| GET | `/access/<reference>` | Course access page (requires access) |
| GET | `/admin` | Admin dashboard |
| POST | `/admin/fulfill/<order_id>` | Manual fulfillment button |
| GET | `/admin/filter` | Filtered orders (query params) |
| GET/404/500/403 | Various | Error pages |

---

## Testing

### Test Payment (Development)
1. Navigate to `/courses`
2. Click "Enroll Now" on Python Course
3. Fill order form with test email
4. Pay with Paystack test card: `4111 1111 1111 1111`
5. OTP: Any 6 digits (e.g., 123456)
6. Verify order created in admin dashboard
7. Check email for confirmation (if SMTP configured)

### Test Webhook (Manual)
```bash
# From Paystack dashboard "Test Webhook" feature:
POST /webhook
Headers:
  X-Paystack-Signature: <HMAC-SHA512 of request body with SECRET_KEY>
Body (JSON):
{
  "event": "charge.success",
  "data": {
    "reference": "test_reference_123",
    "amount": 50000,
    "customer": {"email": "test@example.com"},
    "metadata": {"product_id": 1}
  }
}
```

---

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guides including:
- ✅ Pre-deployment security checklist
- ✅ Gunicorn + Nginx setup (recommended)
- ✅ Docker deployment
- ✅ PaaS deployment (Heroku, Render, Railway)
- ✅ Post-deployment verification
- ✅ Monitoring and maintenance
- ✅ Troubleshooting guide

**TL;DR:**
```bash
# Production with Gunicorn
pip install -r requirements
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Payment webhook not received** | Check webhook URL in Paystack dashboard, verify SECRET_KEY |
| **Email not sending** | Verify SMTP in .env, use app-specific password (not regular password) |
| **404 error page not showing** | Ensure `templates/404.html` exists, check DEBUG=False |
| **Database locked** | Delete `instance/database.db` and restart |
| **No logs created** | Verify `instance/logs/` directory exists and is writable |
| **Admin dashboard empty** | Run `python app.py` to seed sample products |

---

## Key Files Explained

### app.py (568 lines)
- **Lines 1-35**: Security config (SECRET_KEY, session cookies, HTTPS flags)
- **Lines 44-60**: Logging with RotatingFileHandler
- **Lines 75-120**: Database initialization and product seeding
- **Lines 170-210**: Webhook route with HMAC verification
- **Lines 225-280**: Payment initialization and Paystack redirect
- **Lines 290-330**: Payment verification and UserAccess creation
- **Lines 340-390**: Course/service access routes with guards
- **Lines 410-500**: Admin dashboard with calculations
- **Lines 540-585**: Error handlers (404, 500, 403)
- **Lines 590-620**: Security headers and request logging middleware

### models.py (75 lines)
- SQLAlchemy ORM definitions for 3-tier architecture
- Product → Order relationship (what was bought)
- Order → UserAccess relationship (who got access)
- Unique constraint prevents double-fulfillment

### style.css (1217 lines)
- Professional navy-to-cyan gradient theme
- Admin dashboard styling with stats cards
- Responsive mobile design (768px breakpoint)
- Error page styling with large typography
- Smooth animations and transitions

---

## Support & Docs

- **Flask Docs**: https://flask.palletsprojects.com/
- **Paystack API**: https://paystack.com/docs/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## Future Enhancements

- [ ] Admin authentication (currently open access)
- [ ] Student dashboard (view purchased courses)
- [ ] Progress tracking (video watched %, quiz scores)
- [ ] Referral system & affiliate commission
- [ ] Certificate generation on course completion
- [ ] Advanced analytics (cohort analysis, funnel metrics)
- [ ] Multi-currency support
- [ ] Refund processing
- [ ] Two-factor authentication

---

## License

Private - SmartSort AI Solutions

---

## Contact

📧 Email: info@smartsortai.com
🐦 Twitter: @smartsortai_sol
🔗 Website: smartsortai.com

---

**Status**: ✅ Phase 5 Complete - Production Ready
**Last Updated**: January 15, 2024
