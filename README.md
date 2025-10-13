# Ovovex Accounting System

A production-ready, feature-rich Django-based accounting and financial management system with bilingual support (English/Arabic).

---

## ✨ Features

### 📊 Core Accounting
- **General Ledger** - Complete chart of accounts with real-time balance tracking
- **Journal Entries** - Manual entries with automatic balancing verification
- **Financial Statements** - Balance Sheet, P&L Statement, Cash Flow
- **Trial Balance** - Real-time trial balance with drill-down capabilities

### 💰 Accounts Management
- **Accounts Receivable** - Customer invoicing and payment tracking
- **Accounts Payable** - Vendor bill management and payment processing
- **Bank Reconciliation** - Automated statement matching and reconciliation

### 📈 Financial Analysis
- **Financial Ratios** - Liquidity, profitability, efficiency, and leverage ratios
- **Trend Analysis** - Historical financial performance tracking
- **Cash Flow Analysis** - Operating, investing, and financing activities

### 🏢 Business Operations
- **Inventory Management** - Stock tracking with reorder point alerts
- **Purchase Orders** - PO creation and fulfillment tracking
- **Fixed Assets** - Asset tracking with depreciation schedules
- **Expense Management** - Employee expense tracking and approval

### 🤖 AI & Analytics
- **AI Insights** - Revenue optimization and cost reduction recommendations
- **Anomaly Detection** - Unusual transaction and pattern detection
- **Predictive Analytics** - Revenue and expense forecasting

### 🔐 Compliance & Security
- **Audit Trail** - Complete activity logging
- **Compliance Checks** - SOX, IFRS, GDPR compliance monitoring
- **Document Management** - Secure document storage and categorization
- **Tax Center** - Tax calculation and reporting

### 🌍 Internationalization
- **Bilingual Support** - Full English and Arabic language support
- **RTL Support** - Right-to-left layout for Arabic
- **Localized Formatting** - Currency, dates, and numbers

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 13+ (or SQLite for development)
- pip and virtualenv

### One-Command Setup

```bash
# Clone repository
git clone <repository-url>
cd ovovex

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Initialize database (creates DB, runs migrations, seeds production data)
python manage.py init_db

# Start server
python manage.py runserver
```

Access at: `http://localhost:8000`

**Default Login:**
- Username: `admin`
- Password: `changeme123` (change immediately!)

---

## 📖 Documentation

- **[SETUP.md](SETUP.md)** - Comprehensive setup and deployment guide
- **[accounting/management/commands/README.md](accounting/management/commands/README.md)** - Management commands documentation

---

## 🗂️ Project Structure

```
ovovex/
├── accounting/              # Main accounting application
│   ├── models.py           # Database models
│   ├── views.py            # Business logic
│   ├── management/
│   │   └── commands/       # Custom Django commands
│   └── migrations/         # Database migrations
├── ovovex/                  # Project configuration
│   ├── settings.py         # Django settings
│   ├── urls.py             # URL routing
│   └── views.py            # Core application views
├── templates/               # HTML templates
│   ├── auth/               # Authentication pages
│   ├── dashboard/          # Dashboard pages
│   ├── modules/            # Feature modules
│   ├── pages/              # Public pages
│   └── components/         # Reusable components
├── static/                  # Static files (CSS, JS, images)
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript
│   └── images/             # Images and icons
├── locale/                  # Translation files
│   ├── en/                 # English translations
│   └── ar/                 # Arabic translations
├── .env                     # Environment variables (create from .env.example)
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
├── manage.py                # Django management script
├── SETUP.md                 # Setup guide
└── README.md                # This file
```

---

## 💾 Database

### Automatic Database Creation

The system automatically creates the PostgreSQL database on first run. Just configure your `.env` file:

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=accounting_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Manual Database Management

```bash
# Initialize database
python manage.py init_db

# Run migrations only
python manage.py migrate

# Seed production data only
python manage.py seed_production

# Create admin user
python manage.py createsuperuser
```

---

## 🌱 Data Seeding

### Production Data (Safe for production)
```bash
python manage.py seed_production
```

Seeds essential data:
- Chart of accounts (50+ accounts)
- Expense categories
- Inventory categories
- Document categories
- Tax rates

### Test Data (Development only)
```bash
python manage.py seed_dashboard    # Dashboard test data
python manage.py seed_ledger       # Ledger test data
python manage.py seed_all_modules  # Comprehensive test data
```

⚠️ **Never use test seed commands in production!**

---

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=accounting_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# AWS S3 (Production)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_BUCKET_NAME=your_bucket
AWS_REGION=us-east-1
```

### Security

**Before production deployment:**

1. Generate new secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

2. Update `.env`:
```env
SECRET_KEY=<generated-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

3. Change admin password:
```bash
python manage.py changepassword admin
```

---

## 🏃 Running the Application

### Development Server
```bash
python manage.py runserver
```

### Production Server (Gunicorn)
```bash
gunicorn ovovex.wsgi:application --bind 0.0.0.0:8000
```

### With Custom Port
```bash
python manage.py runserver 0.0.0.0:3006
```

---

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounting

# Check for issues
python manage.py check

# Check deployment readiness
python manage.py check --deploy
```

---

## 🌐 Language Support

Switch languages by accessing:
- English: `http://localhost:8000/en/`
- Arabic: `http://localhost:8000/ar/`

To update translations:
```bash
# Extract translatable strings
python manage.py makemessages -l ar

# Compile translations
python manage.py compilemessages
```

---

## 📊 What's Included (Production-Ready)

✅ **Clean Database Structure**
- No demo/fake data
- Production-ready chart of accounts
- Standard expense categories
- Tax rate templates

✅ **Real Data Models**
- Customers & Vendors
- Invoices & Bills
- Journal Entries
- Fixed Assets
- Inventory Items
- Documents
- Audit Trail

✅ **Security Features**
- User authentication
- Permission-based access
- Audit logging
- CSRF protection
- SQL injection prevention

✅ **Production Features**
- PostgreSQL database support
- AWS S3 integration
- Static file optimization
- Error logging
- Database auto-creation

---

## 🚫 What's NOT Included (Clean System)

❌ No demo customers
❌ No fake invoices
❌ No mock transactions
❌ No sample data
❌ No hardcoded test accounts

---

## 🔍 Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Verify credentials in .env
cat .env | grep DB_
```

### Migration Issues
```bash
# Reset migrations (⚠️ deletes all data!)
python manage.py migrate <app_name> zero
python manage.py migrate
```

### Permission Errors
```sql
-- Grant database permissions
GRANT ALL PRIVILEGES ON DATABASE accounting_db TO your_user;
```

See [SETUP.md](SETUP.md) for detailed troubleshooting.

---

## 📦 Dependencies

### Core
- Django 5.2.7
- psycopg2-binary 2.9.10
- python-dotenv 1.1.1

### AWS Integration
- boto3 1.40.45
- django-storages 1.14.6

See `requirements.txt` for complete list.

---

## 🛠️ Development

### Adding New Features

1. Create models in `accounting/models.py`
2. Create views in `accounting/views.py` or `ovovex/views.py`
3. Add URL routes in `ovovex/urls.py`
4. Create templates in `templates/modules/`
5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Creating Management Commands

Add new commands to `accounting/management/commands/`:

```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Your command description'

    def handle(self, *args, **options):
        # Your logic here
        self.stdout.write(self.style.SUCCESS('Done!'))
```

---

## 📈 Roadmap

- [ ] API endpoints (REST/GraphQL)
- [ ] Mobile app support
- [ ] Advanced reporting
- [ ] Multi-company support
- [ ] Cryptocurrency support
- [ ] Integration with banks
- [ ] Automated backups
- [ ] Advanced AI predictions

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Proprietary - All rights reserved

---

## 📞 Support

For issues, questions, or feature requests:
- Check the documentation in [SETUP.md](SETUP.md)
- Review troubleshooting section above
- Check command documentation in `accounting/management/commands/README.md`

---

## 🙏 Acknowledgments

Built with:
- Django Framework
- PostgreSQL
- Tailwind CSS
- Alpine.js
- Font Awesome

---

**Version:** 1.0.0
**Last Updated:** 2025-01-13
**Status:** Production-Ready ✅
