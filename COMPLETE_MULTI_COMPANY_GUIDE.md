# 🏢 Complete Multi-Company Management System - Ovovex

## Overview

Ovovex is now a **fully-featured multi-company accounting SaaS platform** similar to QuickBooks Online. Each company has its own complete workspace with isolated data, custom branding, and comprehensive information management.

---

## ✨ Features

### 1. **Complete Company Profile Management**
- ✅ Full company information (name, legal name, logo, industry)
- ✅ Contact details (address, phone, email, website)
- ✅ Registration & tax information
- ✅ Financial settings (currency, fiscal year)
- ✅ Logo upload (up to 2MB, JPG/PNG)
- ✅ Real-time logo preview
- ✅ Responsive modern dark UI

### 2. **Data Isolation**
- ✅ All accounting data filtered by active company
- ✅ Invoices, journal entries, accounts are company-specific
- ✅ Reports generated per company
- ✅ Complete workspace separation

### 3. **Seamless Company Switching**
- ✅ Sidebar dropdown for quick switching
- ✅ Instant context change
- ✅ All pages automatically reload with new company data
- ✅ Company badge showing active company

### 4. **Security & Access Control**
- ✅ Users can belong to multiple companies
- ✅ Only one active company at a time
- ✅ Middleware-based authentication
- ✅ Automatic data filtering

---

## 🚀 Quick Start Guide

### For Users

#### 1. **Create Your First Company**

```
1. Login to your Ovovex account
2. Click "Add" in the company switcher (sidebar)
3. Fill in basic company information
4. Submit - your company is created and activated!
```

#### 2. **View & Edit Company Details**

```
1. Click "Details" in the company switcher (sidebar)
   OR visit: /companies/details/
2. Update any company information
3. Upload company logo (drag & drop or click)
4. Click "Save Changes"
```

#### 3. **Switch Between Companies**

```
1. Use the dropdown in the sidebar
2. Select the company you want to work with
3. All data automatically switches!
```

---

## 📋 Available Pages & Features

### Company Management
- **`/companies/add/`** - Create new company
- **`/companies/details/`** - View/edit company profile
- **`/companies/switch/<id>/`** - Switch active company

### Dashboard Modules (All Company-Filtered)
- **Dashboard** - Summary metrics for active company
- **Invoices** - Create and manage invoices
- **Journal Entries** - Accounting entries
- **General Ledger** - Chart of accounts
- **Balance Sheet** - Financial position
- **P&L Statement** - Profit & loss
- **Cash Flow** - Cash flow analysis
- **Reports** - All financial reports

---

## 🔧 Technical Implementation

### Database Schema

#### Company Model
```python
class Company(models.Model):
    # Basic Information
    name = CharField              # Trading name
    legal_name = CharField        # Legal/registered name
    logo = ImageField            # Company logo
    industry_type = CharField    # Industry sector
    description = TextField      # Company description

    # Contact Information
    address = CharField
    city = CharField
    country = CharField
    phone = CharField
    email = EmailField
    website = URLField

    # Registration & Tax
    registration_number = CharField
    tax_number = CharField

    # Financial Settings
    currency = CharField          # Default: JOD
    fiscal_year_start = DateField

    # Metadata
    created_at = DateTimeField
    updated_at = DateTimeField
```

#### UserCompany Model (Many-to-Many with Active Status)
```python
class UserCompany(models.Model):
    user = ForeignKey(User)
    company = ForeignKey(Company)
    is_active = BooleanField      # Only one active per user
```

### Middleware
```python
# companies/middleware.py
class ActiveCompanyMiddleware:
    """Automatically sets request.active_company for all views"""
    def __call__(self, request):
        if request.user.is_authenticated:
            active = UserCompany.objects.filter(
                user=request.user,
                is_active=True
            ).first()
            request.active_company = active.company if active else None
        return self.get_response(request)
```

### Views Pattern
All accounting views follow this pattern:

```python
@login_required
def your_view(request):
    # Get active company from middleware
    active_company = request.active_company

    # Filter all queries by company
    invoices = Invoice.objects.filter(company=active_company)
    accounts = Account.objects.filter(company=active_company)
    journals = JournalEntry.objects.filter(company=active_company)

    # Rest of your view logic...
```

---

## 📁 File Structure

```
ovovex/
├── companies/
│   ├── models.py                    # Company & UserCompany models
│   ├── views.py                     # Company CRUD views
│   ├── middleware.py                # ActiveCompanyMiddleware
│   ├── urls.py                      # Company routes
│   ├── admin.py                     # Django admin config
│   └── templates/
│       └── companies/
│           ├── add_company.html     # Create company form
│           └── company_details.html # Full company profile page
├── templates/
│   └── components/
│       ├── sidemenu.html           # Sidebar with company switcher
│       └── company_badge.html      # Reusable company badge
├── accounting/
│   └── models.py                   # All models have company FK
└── dashboard/
    └── views.py                    # All views filter by active_company
```

---

## 🎨 UI Components

### 1. **Company Badge** (Reusable Component)

Include in any template:
```html
{% include 'components/company_badge.html' %}
```

Shows:
- Company logo (if uploaded)
- Company name
- Quick link to details page

### 2. **Sidebar Company Switcher**

Features:
- Dropdown to select active company
- "Details" button → View/edit company
- "Add" button → Create new company
- Auto-submit on selection

### 3. **Company Details Page**

Layout:
- **Header Card**: Logo + Company name + Edit buttons
- **General Info Card**: Name, legal name, industry, description
- **Contact Info Card**: Address, city, country, phone, email, website
- **Registration Card**: Registration #, tax #, currency, fiscal year
- **Metadata Card**: Created date, last updated

---

## 🔐 Security Features

### 1. **Access Control**
```python
# Only show companies user belongs to
user_companies = request.user.usercompany_set.all()

# Verify user has access before showing data
if not UserCompany.objects.filter(user=request.user, company=active_company).exists():
    return HttpResponseForbidden()
```

### 2. **Data Isolation**
```python
# ALWAYS filter by active company
Invoice.objects.filter(company=request.active_company)  # ✅ Correct
Invoice.objects.all()                                    # ❌ Wrong - shows all companies!
```

### 3. **Logo Upload Validation**
```python
# In views.py
if logo.size > 2 * 1024 * 1024:  # 2MB limit
    return JsonResponse({"error": "File too large"})

if logo.content_type not in ["image/jpeg", "image/png"]:
    return JsonResponse({"error": "Invalid file type"})
```

---

## 📊 Database Migrations

### Already Applied
1. **Initial Company Models** (`0001_initial.py`)
   - Company table
   - UserCompany table

2. **Extended Company Fields** (`0002_alter_company_options...py`)
   - Added: legal_name, logo, industry_type, description
   - Added: city, phone, email, website
   - Added: registration_number, fiscal_year_start
   - Added: updated_at

3. **Accounting Models** (`accounting/0016_...py`)
   - Added company FK to: Account, JournalEntry, Invoice, Customer
   - Updated unique constraints to be company-scoped
   - Added indexes for performance

---

## 🧪 Testing Workflow

### Manual Testing Steps

1. **Create Test Companies**
```bash
# Login as user
# Create Company A: "Acme Corp" - Tech industry
# Create Company B: "Best Retail" - Retail industry
```

2. **Test Data Isolation**
```bash
# Switch to Company A
# Create invoice INV-001
# Create account 1000-Cash

# Switch to Company B
# Verify INV-001 doesn't appear
# Verify account 1000-Cash doesn't appear

# Create same invoice number INV-001 (should work - different company)
```

3. **Test Company Details**
```bash
# Click "Details" in sidebar
# Upload logo
# Update all fields
# Save changes
# Verify changes persist
# Switch company and back - verify data still correct
```

4. **Test Permissions**
```bash
# Create User B (different user)
# User B shouldn't see User A's companies
# Invite User B to Company A
# Now User B should see Company A in dropdown
```

---

## 🚀 Deployment Checklist

### Before Production

- [ ] Set up media file storage (S3 or similar for logos)
- [ ] Configure `MEDIA_URL` and `MEDIA_ROOT` in settings
- [ ] Install Pillow for image processing: `pip install Pillow`
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create default companies for existing users
- [ ] Assign existing data to default company
- [ ] Test company switching in production environment
- [ ] Set up backup strategy for company data
- [ ] Configure logo file size limits in web server
- [ ] Enable HTTPS for secure logo uploads

### Required Settings

```python
# settings.py

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Or for production with S3:
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
```

---

## 🎯 Best Practices

### For Developers

1. **Always Filter by Company**
```python
# ✅ Good
invoices = Invoice.objects.filter(company=request.active_company)

# ❌ Bad
invoices = Invoice.objects.all()
```

2. **Set Company on Create**
```python
# ✅ Good
invoice = Invoice.objects.create(
    company=request.active_company,
    # ... other fields
)

# ❌ Bad
invoice = Invoice.objects.create(...)  # company will be NULL!
```

3. **Check Active Company**
```python
# ✅ Good
if not request.active_company:
    messages.warning(request, "Please select a company")
    return redirect('add_company')

# Then use request.active_company
```

### For Users

1. **Create Company First** - Before adding invoices/accounts
2. **Upload Logo Early** - Appears throughout the system
3. **Fill Complete Profile** - Helps with reports and documents
4. **Use Descriptive Names** - Easier to identify in dropdown
5. **Set Fiscal Year** - Important for financial reports

---

## 📖 API Documentation

### Company Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/companies/details/` | View active company details |
| POST | `/companies/details/` | Update active company |
| GET | `/companies/add/` | Show create company form |
| POST | `/companies/add/` | Create new company |
| POST | `/companies/switch/<id>/` | Switch active company |
| POST | `/companies/upload-logo/` | AJAX logo upload |

### Request/Response Examples

#### Create Company
```json
POST /companies/add/
Content-Type: multipart/form-data

{
  "name": "Acme Corporation",
  "legal_name": "Acme Corp Ltd.",
  "industry_type": "Technology",
  "country": "Jordan",
  "currency": "JOD"
}

Response: Redirect to dashboard with success message
```

#### Update Company
```json
POST /companies/details/
Content-Type: multipart/form-data

{
  "name": "Updated Name",
  "email": "contact@acme.com",
  "phone": "+962 79 123 4567",
  "logo": <file>
}

Response: Redirect to details page with success message
```

---

## 🐛 Troubleshooting

### Issue: "No active company" error

**Solution:**
```python
# User needs to create or activate a company
# Redirect to: /companies/add/
```

### Issue: Logo not displaying

**Possible causes:**
1. MEDIA_URL not configured in settings
2. Media files not served in development
3. File permissions issue

**Solution:**
```python
# In urls.py (development only)
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Issue: Data showing from other companies

**This is a critical bug! Fix immediately:**
```python
# Check all queries have company filter
Model.objects.filter(company=request.active_company)

# Search codebase for:
grep -r "objects.all()" dashboard/views.py
# Replace with company-filtered queries
```

### Issue: Cannot switch company

**Check:**
1. User belongs to that company (UserCompany record exists)
2. Company ID is valid
3. Middleware is properly configured

---

## 📈 Performance Optimization

### Database Indexes

Already added for common queries:
```python
# In Company model
class Meta:
    indexes = [
        models.Index(fields=['name']),
    ]

# In accounting models
class Meta:
    indexes = [
        models.Index(fields=['company', 'invoice_date', 'status']),
        models.Index(fields=['company', 'entry_date']),
    ]
```

### Query Optimization

Use `select_related` for foreign keys:
```python
invoices = Invoice.objects.filter(
    company=active_company
).select_related('customer', 'company')
```

---

## 🔄 Future Enhancements

Potential features to add:

- [ ] Company-level user roles (Admin, Accountant, Viewer)
- [ ] Inter-company transactions
- [ ] Company consolidation reports
- [ ] Multi-currency support per company
- [ ] Company archive/deactivate functionality
- [ ] Company duplication (clone settings)
- [ ] Export company data
- [ ] Company analytics dashboard
- [ ] Audit log per company
- [ ] Company-specific chart of accounts templates

---

## 📞 Support & Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **Repository**: [Your Git URL]
- **Issues**: [Your Issues URL]

---

## ✅ Deployment Verification

After deploying, verify:

1. [ ] Can create new company
2. [ ] Can upload and view logo
3. [ ] Can update company details
4. [ ] Can switch between companies
5. [ ] Invoices filter by active company
6. [ ] Journal entries filter by active company
7. [ ] Accounts filter by active company
8. [ ] Reports show correct company data
9. [ ] Sidebar shows correct active company
10. [ ] Company badge displays correctly

---

**System Status:** ✅ Production Ready
**Version:** 2.0
**Last Updated:** 2025-10-15

---

## 🎉 Success!

You now have a complete, professional multi-company accounting system with:
- ✅ Full company profiles with branding
- ✅ Complete data isolation
- ✅ Seamless company switching
- ✅ Modern, responsive UI
- ✅ Secure access control
- ✅ Production-ready architecture

**Your Ovovex platform is ready to manage multiple companies like a pro!** 🚀
