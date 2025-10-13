# 🚀 Ovovex Accounting System - Production Setup Guide

A clean, production-ready Django accounting system with automatic database setup and initialization.

---

## 📋 Prerequisites

- Python 3.10+
- PostgreSQL 13+ (or SQLite for development)
- pip (Python package manager)
- Virtual environment (recommended)

---

## 🔧 Installation Steps

### 1. Clone and Setup Environment

```bash
# Navigate to project directory
cd /path/to/ovovex

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True  # Set to False in production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
# Option 1: PostgreSQL (Recommended for production)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=accounting_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Option 2: SQLite (Development only)
# DB_ENGINE=django.db.backends.sqlite3
# DB_NAME=db.sqlite3

# AWS S3 (Production only)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_BUCKET_NAME=your_bucket
AWS_REGION=us-east-1
```

### 3. PostgreSQL Setup (If using PostgreSQL)

**Option A: Let Django create the database automatically**

The system will automatically create the PostgreSQL database when you run the initialization command. Just make sure PostgreSQL is running and your credentials are correct in `.env`.

**Option B: Manual database creation**

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE accounting_db;

# Create user (if needed)
CREATE USER your_user WITH PASSWORD 'your_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE accounting_db TO your_user;

# Exit
\q
```

---

## 🎯 Quick Start (Automated Setup)

### Single Command Setup

```bash
python manage.py init_db
```

This command will:
1. ✅ Check database connection
2. ✅ Create database if it doesn't exist (PostgreSQL only)
3. ✅ Run all migrations
4. ✅ Seed production data (chart of accounts, categories, etc.)
5. ✅ Create admin user

**Default Admin Credentials:**
- Username: `admin`
- Password: `changeme123`

⚠️ **IMPORTANT:** Change the admin password immediately after first login!

---

## 🔐 Security Steps

### 1. Change Admin Password

```bash
python manage.py changepassword admin
```

### 2. Generate New Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Update `SECRET_KEY` in `.env` with the generated key.

### 3. Production Settings

Before deploying to production, update `.env`:

```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

---

## 🏃 Running the Application

### Development Server

```bash
python manage.py runserver
```

Access the application at: `http://localhost:8000`

### Production Server (Gunicorn)

```bash
gunicorn ovovex.wsgi:application --bind 0.0.0.0:8000
```

---

## 📊 Database Management

### Manual Setup Steps

If you prefer manual control over each step:

```bash
# 1. Run migrations
python manage.py migrate

# 2. Create admin user
python manage.py createsuperuser

# 3. Seed production data
python manage.py seed_production
```

### Database Reset

⚠️ **WARNING:** This will delete all data!

**PostgreSQL:**
```bash
# Drop and recreate database
psql -U postgres -c "DROP DATABASE accounting_db;"
psql -U postgres -c "CREATE DATABASE accounting_db;"

# Re-initialize
python manage.py init_db
```

**SQLite:**
```bash
# Delete database file
rm db.sqlite3

# Re-initialize
python manage.py init_db
```

---

## 🌱 What Gets Seeded?

The `seed_production` command creates:

### ✅ Chart of Accounts
- Assets (1000-1999)
- Liabilities (2000-2999)
- Equity (3000-3999)
- Revenue (4000-4999)
- Expenses (5000-5999)

### ✅ Expense Categories
- Office Supplies
- Travel & Entertainment
- Professional Services
- Marketing & Advertising
- Utilities
- Insurance
- Maintenance & Repairs
- Rent

### ✅ Inventory Categories
- Raw Materials
- Work in Progress
- Finished Goods
- Office Supplies
- IT Equipment
- Furniture
- Maintenance Parts

### ✅ Document Categories
- Financial Statements
- Tax Documents
- Contracts
- Invoices
- Bills
- Legal Documents
- Bank Statements
- Correspondence

### ✅ Tax Rates
- Standard Sales Tax (10%)
- Federal Income Tax (21%)
- State Income Tax (5%)
- Property Tax (1.2%)

---

## 🧹 Clean Database (No Demo Data)

This system is production-ready with **NO demo/fake data**:

- ✅ No sample customers
- ✅ No fake invoices
- ✅ No mock transactions
- ✅ Only essential configuration data
- ✅ Real production structure

---

## 📁 Project Structure

```
ovovex/
├── accounting/              # Main accounting app
│   ├── management/
│   │   └── commands/
│   │       ├── init_db.py          # Database initialization
│   │       └── seed_production.py  # Production data seeding
│   ├── models.py            # Database models
│   └── views.py             # Application views
├── ovovex/                  # Project settings
│   ├── settings.py          # Django settings (with auto DB creation)
│   ├── urls.py              # URL routing
│   └── views.py             # Core views
├── templates/               # HTML templates
├── static/                  # Static files (CSS, JS, images)
├── .env                     # Environment variables (create this)
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
├── manage.py                # Django management script
└── SETUP.md                 # This file
```

---

## 🔍 Troubleshooting

### Database Connection Error

```
Error: could not connect to server
```

**Solution:**
- Ensure PostgreSQL is running: `sudo systemctl status postgresql`
- Check credentials in `.env`
- Verify database user has correct permissions

### Migration Errors

```
No migrations to apply
```

**Solution:**
```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### ImportError for psycopg2

```
ImportError: No module named 'psycopg2'
```

**Solution:**
```bash
pip install psycopg2-binary
```

### Permission Denied

```
permission denied for database
```

**Solution:**
```sql
-- In PostgreSQL
GRANT ALL PRIVILEGES ON DATABASE accounting_db TO your_user;
ALTER DATABASE accounting_db OWNER TO your_user;
```

---

## 📚 Additional Commands

### Create Additional Users

```bash
python manage.py createsuperuser
```

### Collect Static Files (Production)

```bash
python manage.py collectstatic --noinput
```

### Check Deployment Readiness

```bash
python manage.py check --deploy
```

### Database Shell

```bash
python manage.py dbshell
```

### Django Shell

```bash
python manage.py shell
```

---

## 🌐 Deployment Checklist

Before deploying to production:

- [ ] Set `DEBUG=False` in `.env`
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Change admin password
- [ ] Generate new `SECRET_KEY`
- [ ] Configure AWS S3 for static/media files
- [ ] Set up SSL certificate
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Configure monitoring/logging
- [ ] Run `python manage.py check --deploy`
- [ ] Test all critical features

---

## 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Review Django logs: Look for error messages in console output
- Check PostgreSQL logs: `/var/log/postgresql/`

---

## 📝 License

Proprietary - All rights reserved

---

**Last Updated:** 2025-01-13
**Version:** 1.0.0
