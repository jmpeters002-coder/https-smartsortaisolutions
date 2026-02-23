# SmartSort AI Solutions - Deployment Guide

## Overview
This is a production-ready Flask e-learning and services marketplace with Paystack payment integration, admin dashboard, and professional email automation.

---

## Pre-Deployment Checklist

### 1. Environment Configuration
- [ ] Generate strong SECRET_KEY: `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] Add generated key to `.env` as `SECRET_KEY=<generated_key>`
- [ ] Configure Paystack API keys in `.env`:
  - `PAYSTACK_SECRET_KEY` (get from https://dashboard.paystack.com/settings/api-keys)
  - `PAYSTACK_PUBLIC_KEY`
- [ ] Set `FLASK_ENV=production` in `.env`
- [ ] Set `DEBUG=False` in `.env`

### 2. Email Configuration
- [ ] Update SMTP credentials in `.env`:
  ```
  MAIL_SERVER=smtp.gmail.com  # or provider of choice
  MAIL_PORT=587
  MAIL_USE_TLS=True
  MAIL_USERNAME=your-email@example.com
  MAIL_PASSWORD=your-app-password  # Use app-specific password for Gmail
  MAIL_DEFAULT_SENDER=noreply@smartsortai.com
  ```
- [ ] Test email by sending a test order confirmation
- [ ] Configure professional domain email (recommended)

### 3. Database Setup
- [ ] Remove `database.db` before first production run to reinitialize with seed data
- [ ] Verify 3 sample products are created (Python Course, Consulting Service, E-book)
- [ ] Test database connectivity

### 4. Webhook Configuration
- [ ] Deploy application to production server
- [ ] Update Paystack webhook URL in dashboard:
  - Navigate to: https://dashboard.paystack.com/settings/developers
  - Add webhook: `https://yourdomain.com/webhook`
  - Select events: `charge.success`, `charge.failed`
  - Secret: Uses PAYSTACK_SECRET_KEY for verification

### Local HTTPS tunnel (ngrok) — useful for testing webhooks

For local webhook testing Paystack requires an HTTPS URL. Use `ngrok` to expose your local server over HTTPS:

1. Install ngrok: https://ngrok.com/download
2. Run ngrok on your local Flask port (default 5000):

```bash
ngrok http 5000
```

3. Copy the HTTPS URL ngrok provides (e.g. `https://abcd1234.ngrok.io`).
4. In the Paystack dashboard set the webhook URL to `<ngrok_https_url>/webhook`.
5. Also set `PUBLIC_URL` in your `.env` to the ngrok URL so callback URLs returned by the app use the same domain:

```dotenv
PUBLIC_URL=https://abcd1234.ngrok.io
```

6. Restart your Flask app so it picks up the new `PUBLIC_URL`.

Now Paystack will be able to send webhook events to your local machine over HTTPS.

### 5. Domain & SSL
- [ ] Purchase domain name (e.g., smartsortai.com)
- [ ] Obtain SSL certificate (Let's Encrypt recommended)
- [ ] Configure HTTPS on web server
- [ ] All SESSION_COOKIE_SECURE flags require HTTPS

---

## Production Deployment

### Option 1: Gunicorn + Nginx (Recommended)

#### 1. Install Production Server
```bash
pip install gunicorn
```

#### 2. Create Systemd Service File
Create `/etc/systemd/system/smartsort.service`:
```ini
[Unit]
Description=SmartSort AI Flask Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/smartsort-ai-v1
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3. Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl start smartsort
sudo systemctl enable smartsort
```

#### 4. Configure Nginx
Create `/etc/nginx/sites-available/smartsort`:
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

#### 5. Enable Nginx Site
```bash
sudo ln -s /etc/nginx/sites-available/smartsort /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 2: Docker Deployment

#### 1. Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

#### 2. Create docker-compose.yml
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DEBUG=False
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
```

#### 3. Deploy
```bash
docker-compose up -d
```

### Option 3: PaaS Deployment (Heroku, Render, Railway)
Use built-in Python buildpack, configure environment variables via dashboard, set buildpack to Python.

---

## Post-Deployment Verification

### 1. Health Checks
```bash
# Check if application is running
curl https://yourdomain.com/
curl https://yourdomain.com/courses

# Check error handling
curl https://yourdomain.com/nonexistent  # Should return 404 with custom page
```

### 2. Security Headers Verification
```bash
curl -I https://yourdomain.com/
# Should show:
# X-Content-Type-Options: nosniff
# X-Frame-Options: SAMEORIGIN
# Strict-Transport-Security: max-age=31536000
```

### 3. Logging Verification
```bash
# Check logs directory
tail -f logs/smartsort.log

# Should show request logs like:
# 2024-01-15 10:30:45 INFO GET /courses
# 2024-01-15 10:30:50 INFO POST /create-order
```

### 4. Payment Testing
- Use Paystack test keys (start with `sk_test_` and `pk_test_`)
- Test transaction: Create order → Pay with test card (4111 1111 1111 1111) → Verify webhook received
- Check database for new Order and UserAccess records

### 5. Email Testing
- Complete a test payment
- Verify confirmation email received at customer email address
- Check that course access link is correct
- Verify sender shows as configured MAIL_DEFAULT_SENDER

---

## Monitoring & Maintenance

### Log Management
- Logs rotate at 10MB, keeping 10 backups
- Located at: `logs/smartsort.log`
- Check daily for errors: `grep ERROR logs/smartsort.log`

### Database Backup
```bash
# Daily backup (add to crontab)
0 2 * * * cp /path/to/database.db /path/to/backups/database-$(date +\%Y\%m\%d).db
```

### Performance Monitoring
- Monitor Gunicorn worker processes: `ps aux | grep gunicorn`
- Monitor server resources: `top`, `htop`, cloud provider dashboard
- Consider adding APM (Application Performance Monitoring) like Sentry for error tracking

### Regular Updates
- Keep Python packages updated: `pip list --outdated`
- Review security advisories: `pip install --upgrade pip`
- Update Paystack API as needed

---

## Troubleshooting

### Payment Webhook Not Received
1. Check webhook URL in Paystack dashboard
2. Verify PAYSTACK_SECRET_KEY matches dashboard settings
3. Check application logs: `grep webhook logs/smartsort.log`
4. Test webhook manually via Paystack dashboard "Test webhook" feature

### Email Not Sending
1. Verify SMTP credentials in .env
2. Check email logs: `grep MAIL logs/smartsort.log`
3. Verify app-specific password is used (not regular Gmail password)
4. Check firewall allows SMTP port (587 or 465)

### Database Errors
1. Check database.db exists and is readable
2. Verify no file lock conflicts
3. Restart application to reinitialize schema

### 404/500 Error Pages Not Showing
1. Verify error template files exist in templates/ directory
2. Check Flask is not in debug mode (DEBUG=False in .env)
3. Review app.py error handlers are registered

---

## Security Checklist

- [ ] DEBUG=False in production
- [ ] SECRET_KEY is strong (32+ character random hex)
- [ ] SSL/HTTPS enabled for entire domain
- [ ] SESSION_COOKIE_SECURE=True enforced
- [ ] Paystack webhook verification enabled (HMAC-SHA512)
- [ ] .env file is NOT committed to git (check .gitignore)
- [ ] Database credentials separate from code
- [ ] Email credentials use app-specific passwords
- [ ] Regular backups configured
- [ ] Logs monitored for suspicious activity
- [ ] CORS configured if frontend is separate domain

---

## Support & Documentation

**Framework**: Flask (https://flask.palletsprojects.com/)
**Payment**: Paystack (https://paystack.com/docs/)
**Deployment**: Gunicorn (https://gunicorn.org/)
**Database**: SQLAlchemy (https://sqlalchemy.org/)

---

*Last Updated: 2024-01-15*
*Phase 5 Production Deployment Ready*
