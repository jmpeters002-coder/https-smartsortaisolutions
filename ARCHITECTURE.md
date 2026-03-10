# SmartSort AI - Architecture & Implementation Guide

## Current Structure
```
app.py                    # Main Flask app
config.py                 # Configuration classes
extensions.py             # Flask extensions (db, migrate)
requirements.txt          # Dependencies
models/                   # SQLAlchemy models
routes/                   # Flask blueprints (NEEDS REFACTOR)
services/                 # Business logic
utils/                    # Utilities (auth, logger, etc.)
templates/                # Jinja2 templates
static/                   # CSS, JS, uploads
migrations/               # Alembic database migrations
```

## Target Architecture (Modular Blueprints)

```
smartsort/
├── app/
│   ├── __init__.py                # App factory
│   ├── models/                    # SQLAlchemy models (organized by feature)
│   │   ├── __init__.py
│   │   ├── user.py               # Existing
│   │   ├── content.py            # Blogs, News (Existing)
│   │   ├── course.py             # Courses (Existing)
│   │   ├── order.py              # Orders (Existing)
│   │   ├── payment.py            # Payments (Existing)
│   │   ├── product.py            # Products (Existing)
│   │   ├── job.py                # NEW: Jobs
│   │   ├── newsletter.py         # NEW: Newsletter subscribers
│   │   ├── freelance.py          # NEW: Freelance applications
│   │   └── affiliate.py          # NEW: Affiliate program
│   │
│   ├── routes/                    # Feature-based blueprints
│   │   ├── __init__.py
│   │   ├── auth.py               # Authentication routes
│   │   ├── public.py             # Public pages (refactored)
│   │   ├── admin.py              # Admin panel → /control-panel
│   │   ├── blog.py               # Blog routes
│   │   ├── news.py               # News routes
│   │   ├── courses.py            # Course routes
│   │   ├── jobs.py               # NEW: Jobs routes
│   │   ├── newsletter.py         # NEW: Newsletter routes
│   │   ├── freelance.py          # NEW: Freelance routes
│   │   ├── affiliate.py          # NEW: Affiliate routes
│   │   ├── user_dashboard.py     # NEW: User dashboard
│   │   └── services.py           # Services routes
│   │
│   ├── services/                  # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py       # Auth logic
│   │   ├── newsletter_service.py # NEW: Email subscriptions
│   │   ├── job_service.py        # NEW: Job aggregation/filtering
│   │   ├── email_service.py      # Email templates
│   │   ├── storage_service.py    # NEW: File uploads (S3/R2)
│   │   ├── analytics_service.py  # Usage analytics
│   │   └── [others...]
│   │
│   ├── utils/                     # Utilities
│   │   ├── auth.py               # Auth helpers
│   │   ├── logger.py             # Logging
│   │   ├── validators.py         # Input validation
│   │   ├── decorators.py         # NEW: Custom decorators
│   │   └── constants.py          # NEW: App constants
│   │
│   ├── templates/                 # Jinja2 templates
│   │   ├── base.html
│   │   ├── jobs/                 # NEW
│   │   ├── newsletter/           # NEW
│   │   ├── user_dashboard/       # NEW
│   │   └── [others...]
│   │
│   └── static/                    # Static assets
│       ├── css/
│       ├── js/
│       └── uploads/
│
├── config.py                      # Config classes
├── extensions.py                  # Extensions init
└── migrations/                    # Alembic migrations
```

## Implementation Roadmap

### Phase 1: Foundation (Blueprint Refactor)
- [ ] Reorganize routes into modular blueprints
- [ ] Update app factory pattern in `__init__.py`
- [ ] Ensure all existing routes continue working

### Phase 2: Easy Wins (Low Effort, High Value)
1. **Newsletter System** ✓ Easiest
   - Single model (subscribers)
   - Email subscription form
   - Admin management
   
2. **Freelance Opportunities** ✓ Easy
   - Simple form submission
   - Database storage
   - Admin review

3. **Admin Rebranding** ✓ Easy
   - Route migration (/admin → /control-panel)
   - Add rate limiting
   - Add role verification

### Phase 3: Medium Complexity
4. **Affiliate Program**
   - Model for affiliates + referral tracking
   - Admin dashboard
   
5. **AI Jobs Aggregation**
   - Job model with filters
   - Admin CRUD for manual posting
   - Public job listing/filtering

### Phase 4: Complex Features
6. **Media Upload System**
   - Integration with AWS S3 or Cloudflare R2
   - Image serving & CDN
   
7. **User Dashboard**
   - Course progress tracking
   - Saved resources
   - Subscription management

8. **Courses Content Expansion**
   - Multiple content types (video, PDF, links)
   - Module/lesson structure

## Database Models Summary

### New Models to Create
```python
# models/newsletter.py
Subscriber(id, email, status, created_at, unsubscribed_at)

# models/freelance.py
FreelanceApplication(id, name, email, country, skills, portfolio, created_at)

# models/affiliate.py
AffiliatePartner(id, name, email, country, website, status, referral_code, created_at)
AffiliateReferral(id, affiliate_id, user_id, created_at)

# models/job.py
Job(id, title, company, location, job_type, remote, description, 
    application_link, image, source, created_at, status, slug)

# models/user_dashboard.py
UserCourseProgress(user_id, course_id, progress_percentage, last_accessed, modules_completed)
SavedResource(id, user_id, resource_type, resource_id, created_at)
```

## Security Enhancements
- [ ] Rate limiting on login (/control-panel)
- [ ] CSRF protection (already present)
- [ ] Input validation for all forms
- [ ] File upload restrictions
- [ ] Secure password hashing (bcrypt)

## Recommended Dependencies
```
Flask               # Already have
Flask-SQLAlchemy    # Already have
Flask-Migrate       # Already have
Flask-Mail          # Already have
python-dotenv       # Already have

# To add:
Flask-Limiter       # Rate limiting
Flask-WTF           # Forms & CSRF
botocore            # AWS S3 (if using)
redis               # Caching (future)
celery              # Background tasks (future)
```

## Next Steps
1. Create modular blueprint structure
2. Implement Newsletter System (easiest)
3. Implement Freelance Opportunities
4. Continue with planned features
