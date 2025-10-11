# DJANGO APP SETUP GUIDE
# ======================

"""
This guide provides the step-by-step commands to create all recommended Django apps
for the Ovovex Accounting Platform.

Run these commands from your project root directory.
"""

# Core Apps
python manage.py startapp accounts
python manage.py startapp accounting
python manage.py startapp invoicing
python manage.py startapp receivables
python manage.py startapp payables
python manage.py startapp banking
python manage.py startapp financials
python manage.py startapp assets
python manage.py startapp operations
python manage.py startapp tax
python manage.py startapp compliance
python manage.py startapp analytics
python manage.py startapp ai_engine
python manage.py startapp workflows
python manage.py startapp integrations
python manage.py startapp documents
python manage.py startapp notifications
python manage.py startapp portal
python manage.py startapp multicompany
python manage.py startapp website
python manage.py startapp dashboard
python manage.py startapp api

# ============================================================================
# SETTINGS.PY CONFIGURATION
# ============================================================================

"""
Add these apps to your INSTALLED_APPS in settings.py:
"""

INSTALLED_APPS = [
    # Django Core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party Apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    'crispy_forms',
    'crispy_tailwind',
    'channels',  # For WebSockets/real-time features
    'celery',  # For background tasks
    'storages',  # For S3-compatible storage
    'django_extensions',
    'debug_toolbar',  # Development only
    
    # Your Apps - Core
    'accounts',
    'accounting',
    'invoicing',
    'receivables',
    'payables',
    'banking',
    'financials',
    'assets',
    'operations',
    
    # Your Apps - Advanced
    'tax',
    'compliance',
    'analytics',
    'ai_engine',
    'workflows',
    'integrations',
    'documents',
    'notifications',
    'portal',
    'multicompany',
    
    # Your Apps - Frontend
    'website',
    'dashboard',
    'api',
]


# ============================================================================
# TEMPLATE DIRECTORY STRUCTURE
# ============================================================================

"""
Recommended template structure for the project:

templates/
├── base.html                          # Master template
├── base_auth.html                     # Authenticated layout
├── base_public.html                   # Public site layout
│
├── website/                           # Public marketing site
│   ├── home.html
│   ├── solutions/
│   │   ├── small_business.html
│   │   ├── mid_market.html
│   │   ├── enterprise.html
│   │   ├── accounting_firms.html
│   │   └── startups.html
│   ├── industries/
│   │   ├── retail_ecommerce.html
│   │   ├── manufacturing.html
│   │   ├── professional_services.html
│   │   ├── healthcare.html
│   │   ├── real_estate.html
│   │   ├── technology_saas.html
│   │   └── non_profit.html
│   ├── features/
│   │   ├── smart_invoicing.html
│   │   ├── ai_bookkeeping.html
│   │   ├── expense_management.html
│   │   ├── real_time_analytics.html
│   │   └── ...
│   ├── resources/
│   │   ├── documentation.html
│   │   ├── blog_list.html
│   │   ├── blog_detail.html
│   │   ├── case_studies.html
│   │   └── help_center.html
│   ├── pricing.html
│   ├── start_free_trial.html
│   └── request_demo.html
│
├── dashboard/                         # Main dashboard
│   ├── home.html
│   ├── quick_actions.html
│   ├── recent_activity.html
│   └── help_center.html
│
├── accounting/                        # Core accounting
│   ├── general_ledger.html
│   ├── chart_of_accounts.html
│   ├── account_form.html
│   ├── journal_entries.html
│   ├── journal_entry_form.html
│   ├── journal_entry_detail.html
│   ├── trial_balance.html
│   └── reconciliation.html
│
├── invoicing/                         # Invoicing & billing
│   ├── invoice_list.html
│   ├── invoice_form.html
│   ├── invoice_detail.html
│   ├── invoice_pdf.html
│   ├── recurring_invoices.html
│   ├── quotes.html
│   ├── credit_notes.html
│   └── payment_links.html
│
├── receivables/                       # AR management
│   ├── dashboard.html
│   ├── aging_report.html
│   ├── customer_list.html
│   ├── customer_form.html
│   ├── customer_detail.html
│   ├── payment_list.html
│   └── collections.html
│
├── payables/                          # AP management
│   ├── dashboard.html
│   ├── vendor_list.html
│   ├── vendor_form.html
│   ├── bill_list.html
│   ├── bill_form.html
│   ├── payment_process.html
│   └── three_way_match.html
│
├── banking/                           # Banking & treasury
│   ├── account_list.html
│   ├── reconciliation.html
│   ├── bank_feeds.html
│   ├── treasury.html
│   └── multi_currency.html
│
├── financials/                        # Financial management
│   ├── balance_sheet.html
│   ├── income_statement.html
│   ├── cash_flow_statement.html
│   ├── budgeting.html
│   ├── budget_form.html
│   ├── cash_flow_forecast.html
│   └── scenario_planning.html
│
├── assets/                            # Fixed assets
│   ├── asset_list.html
│   ├── asset_form.html
│   ├── asset_detail.html
│   └── depreciation.html
│
├── operations/                        # Operations
│   ├── expense_list.html
│   ├── expense_form.html
│   ├── receipt_scanner.html
│   ├── purchase_orders.html
│   ├── inventory.html
│   ├── projects.html
│   └── time_tracking.html
│
├── tax/                               # Tax management
│   ├── tax_center.html
│   ├── tax_reports.html
│   ├── vat_returns.html
│   └── compliance_calendar.html
│
├── compliance/                        # Compliance
│   ├── dashboard.html
│   ├── audit_trail.html
│   ├── regulatory_filing.html
│   └── compliance_reports.html
│
├── analytics/                         # Analytics & insights
│   ├── financial_dashboard.html
│   ├── financial_ratios.html
│   ├── kpi_tracking.html
│   ├── custom_reports.html
│   └── benchmarking.html
│
├── ai_engine/                         # AI features
│   ├── ai_chat.html
│   ├── ai_insights.html
│   ├── anomaly_detection.html
│   ├── predictive_analytics.html
│   ├── smart_recommendations.html
│   └── report_generator.html
│
├── workflows/                         # Workflows & automation
│   ├── approvals.html
│   ├── pending_approvals.html
│   ├── workflow_list.html
│   ├── automation_rules.html
│   ├── email_templates.html
│   └── scheduled_reports.html
│
├── integrations/                      # Integrations
│   ├── integration_hub.html
│   ├── bank_connections.html
│   ├── payment_processors.html
│   ├── ecommerce.html
│   ├── payroll.html
│   ├── crm.html
│   ├── erp.html
│   └── api_webhooks.html
│
├── documents/                         # Document management
│   ├── document_list.html
│   ├── document_detail.html
│   └── document_upload.html
│
├── notifications/                     # Notifications
│   ├── notification_list.html
│   └── notification_settings.html
│
├── portal/                            # Customer portal
│   ├── dashboard.html
│   ├── invoices.html
│   ├── payments.html
│   ├── documents.html
│   └── support.html
│
├── multicompany/                      # Multi-company
│   ├── company_selector.html
│   ├── consolidation.html
│   ├── inter_company.html
│   └── group_reporting.html
│
├── settings/                          # Settings
│   ├── company_settings.html
│   ├── user_management.html
│   ├── roles_permissions.html
│   ├── security_settings.html
│   ├── two_factor_auth.html
│   ├── audit_logs.html
│   ├── backup_recovery.html
│   ├── billing_subscription.html
│   └── preferences.html
│
├── components/                        # Reusable components
│   ├── navbar.html
│   ├── sidebar.html
│   ├── footer.html
│   ├── breadcrumbs.html
│   ├── pagination.html
│   ├── search.html
│   ├── filters.html
│   ├── modals/
│   ├── forms/
│   └── cards/
│
└── emails/                            # Email templates
    ├── base_email.html
    ├── invoice_email.html
    ├── payment_confirmation.html
    ├── reminder_email.html
    └── welcome_email.html
"""


# ============================================================================
# RECOMMENDED PACKAGES TO INSTALL
# ============================================================================

"""
requirements.txt additions:

# Core Django
Django>=5.2.0
psycopg2-binary>=2.9.0
python-decouple>=3.8

# REST API
djangorestframework>=3.14.0
django-cors-headers>=4.0.0
django-filter>=23.0

# Forms & UI
django-crispy-forms>=2.0
crispy-tailwind>=0.5.0

# Async & Real-time
channels>=4.0.0
channels-redis>=4.0.0
celery>=5.3.0
redis>=4.5.0

# Storage
django-storages>=1.13.0
boto3>=1.26.0

# Authentication & Security
PyJWT>=2.8.0
cryptography>=41.0.0
django-two-factor-auth>=1.15.0

# File Processing
Pillow>=10.0.0
python-magic>=0.4.27
PyPDF2>=3.0.0

# Data Processing
pandas>=2.0.0
openpyxl>=3.1.0
xlsxwriter>=3.1.0

# AI/ML
openai>=1.0.0
langchain>=0.1.0
scikit-learn>=1.3.0
tensorflow>=2.13.0  # Optional
prophet>=1.1.0  # For forecasting

# OCR
pytesseract>=0.3.10
pdf2image>=1.16.0

# Payment Processing
stripe>=5.5.0

# Utilities
python-dateutil>=2.8.0
pytz>=2023.3
django-extensions>=3.2.0
django-debug-toolbar>=4.1.0  # Development only

# Testing
pytest>=7.4.0
pytest-django>=4.5.0
factory-boy>=3.3.0
faker>=19.0.0

# Documentation
drf-yasg>=1.21.0  # API documentation
"""


# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

"""
Recommended middleware in settings.py:
"""

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Custom middleware
    'accounts.middleware.CompanyMiddleware',  # Multi-company support
    'accounts.middleware.AuditLogMiddleware',  # Audit logging
    'debug_toolbar.middleware.DebugToolbarMiddleware',  # Development only
]


# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

"""
PostgreSQL configuration in settings.py:
"""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='ovovex_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,
    }
}


# ============================================================================
# CELERY CONFIGURATION
# ============================================================================

"""
Celery configuration for background tasks:
"""

# celery.py in project root
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ovovex.settings')

app = Celery('ovovex')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# settings.py
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'


# ============================================================================
# REST FRAMEWORK CONFIGURATION
# ============================================================================

"""
Django REST Framework settings:
"""

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}


# ============================================================================
# STATIC & MEDIA FILES
# ============================================================================

"""
Static and media files configuration:
"""

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# For S3 storage (production)
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
# AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')


# ============================================================================
# SECURITY SETTINGS
# ============================================================================

"""
Security configuration:
"""

# HTTPS
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content Security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Session
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 86400  # 24 hours

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

"""
Comprehensive logging setup:
"""

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'ovovex': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    },
}
