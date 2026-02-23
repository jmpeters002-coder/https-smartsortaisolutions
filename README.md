# SmartSort AI Solutions

A production-ready Flask-based e-learning and services marketplace with secure Paystack payments, admin dashboard, and professional email automation.

---

## Features

✨ **Core Capabilities**
- 🛒 Product catalog (courses, services, e-books)
- 💳 Secure Paystack payment integration with HMAC-SHA512 webhook verification
- 📧 Professional email automation for payment confirmations
- 🔐 Automatic access control - users granted access immediately upon successful payment
- 📊 Admin dashboard with real-time order management and revenue analytics
- 🎨 Professional responsive UI with gradient design
- 🛡️ Production security (SECRET_KEY, HTTPS cookies, security headers, error handling)
- 📝 Rotating file logging for audit trails and debugging
- 🌐 Contact page with email and social media links

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Framework** | Flask 3.1.3 |
| **Database** | SQLAlchemy 2.0.46 + SQLite |
| **Payment** | Paystack API (HMAC-SHA512 verification) |
| **Email** | Flask-Mail 0.9.1 |
| **Frontend** | Jinja2 templates + custom CSS (1200+ lines) |
| **Production** | Gunicorn 21.2.0 + Nginx |
| **Logging** | RotatingFileHandler with 10MB rotation |

---

## Project Structure

```
smartsort-ai-v1/
├── app.py                      # Main Flask application (568 lines)
├── models.py                   # SQLAlchemy models (Product, Order, UserAccess)
├── .env                        # Environment configuration (Paystack, email, secrets)
├── .gitignore                  # Git ignore rules
├── requirements                # Python dependencies (23 packages)
├── DEPLOYMENT.md               # Complete deployment guide
├── README.md                   # This file
├── templates/
│   ├── base.html              # Navigation layout
│   ├── index.html             # Homepage hero
│   ├── courses.html           # Course listing
│   ├── services.html          # Services listing
│   ├── contact.html           # Contact page
│   ├── admin_dashboard.html   # Admin console (orders, revenue, filters)
│   ├── course_access.html     # Course access confirmation
│   ├── service_confirmation.html # Service confirmation
│   ├── 404.html               # Not found error page
│   ├── 403.html               # Access forbidden error page
│   └── 500.html               # Server error page
├── statics/
│   ├── css/
│   │   └── style.css          # Complete styling (1217 lines)
│   ├── js/
│   │   └── script.js          # Frontend scripts
│   └── images/
└── instance/                  # Instance folder (logs, database)
    ├── database.db            # SQLite database
    └── logs/
        └── smartsort.log      # Application logs (rotating)
```

---

## Quick Start

### Prerequisites
- Python 3.8+
- pip package manager
- Virtual environment (recommended)

### Installation

1. **Clone or download the project**
   ```bash
   cd smartsort-ai-v1
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Activate it
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements
   ```

4. **Configure environment**
   - Copy `.env.example` or create `.env`:
   ```
   PAYSTACK_PUBLIC_KEY=pk_test_xxxxxxxxx
   PAYSTACK_SECRET_KEY=sk_test_xxxxxxxxx
   SECRET_KEY=generate_with: python -c "import secrets; print(secrets.token_hex(32))"
   FLASK_ENV=development
   DEBUG=True
   
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_DEFAULT_SENDER=noreply@smartsortai.com
   ```

5. **Run application**
   ```bash
   python app.py
   ```
   
   Application runs at: `http://127.0.0.1:5000`

---

## Payment Flow

```
1. User selects product (course/service/e-book)
   ↓
2. Clicks "Pay" → Redirected to Paystack payment page
   ↓
3. Customer enters payment details (demo: 4111 1111 1111 1111)
   ↓
4. Paystack verifies payment → Sends webhook to /webhook
   ↓
5. App verifies webhook signature (HMAC-SHA512)
   ↓
6. If valid:
   - Mark Order.status = "paid"
   - Create UserAccess record (automatic fulfillment)
   - Send confirmation email with course link
   ↓
7. User can access course via /access/<payment_reference>
```

**Security**: Webhook verification prevents forged payments using secret key HMAC hashing.

---

## Database Schema

### Product
```sql
id (INT PRIMARY KEY)
title VARCHAR - Course title or service name
description TEXT - Product details
price FLOAT - Cost in NGN
product_type VARCHAR - "course", "service", or "ebook"
resource_link VARCHAR - URL to course/service material
created_at DATETIME - Creation timestamp
```

### Order
```sql
id (INT PRIMARY KEY)
customer_email VARCHAR NOT NULL - Buyer email
product_id INT FOREIGN KEY -> Product.id
payment_reference VARCHAR UNIQUE - Paystack reference ID
status VARCHAR - "pending", "paid", or "failed"
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

## Admin Dashboard

Access at: `/admin` (no auth required in development; **add authentication in production**)

**Features:**
- 📊 Stats: Total orders, revenue, pending orders, access granted
- 🔍 Filters: By status, email, product, date range
- 📋 Orders table: Email, product, amount, status, timestamps
- 💰 Revenue breakdown: By product type (courses vs services vs e-books)
- ✅ Manual fulfillment: Grant access to paid but unreceived orders
- 📝 Access logs: Recent UserAccess grants with timestamps

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
