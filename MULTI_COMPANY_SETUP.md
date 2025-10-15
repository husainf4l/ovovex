# Multi-Company Management - Ovovex

## Overview

Ovovex now supports **full multi-company management**. Users can create multiple companies, switch between them seamlessly in the dashboard sidebar, and all accounting data (Invoices, Journal Entries, Accounts, etc.) is automatically filtered by the active company.

---

## Features Implemented

✅ **Company Management**
- Create unlimited companies
- Each company has: name, tax number, address, country, currency
- Users can belong to multiple companies
- Only one company can be active at a time

✅ **Middleware Integration**
- `ActiveCompanyMiddleware` automatically sets `request.active_company` for every authenticated request
- Available in all views and templates

✅ **Data Isolation**
- All major accounting models now have a `company` ForeignKey
- Models updated:
  - `Account` (Chart of Accounts)
  - `JournalEntry`
  - `Invoice`
  - `Customer`
  - And more can be added following the same pattern

✅ **UI Integration**
- Company switcher in dashboard sidebar
- Dropdown to select active company
- "Add Company" button to create new companies
- Seamless switching without page refresh (form auto-submits)

---

## How It Works

### 1. Models

#### Company Model
Located in `companies/models.py`:

```python
class Company(models.Model):
    name = models.CharField(max_length=255)
    tax_number = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    currency = models.CharField(max_length=10, default="JOD")
    created_at = models.DateTimeField(auto_now_add=True)
```

#### UserCompany Model
Manages the many-to-many relationship with active company tracking:

```python
class UserCompany(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
```

Only **one** UserCompany per user should have `is_active=True`.

---

### 2. Middleware

`companies/middleware.py` provides the active company context:

```python
class ActiveCompanyMiddleware:
    def __call__(self, request):
        if request.user.is_authenticated:
            active = UserCompany.objects.filter(user=request.user, is_active=True).first()
            request.active_company = active.company if active else None
        else:
            request.active_company = None
        return self.get_response(request)
```

This middleware is registered in `settings.py` after `AuthenticationMiddleware`.

---

### 3. Views

#### Add Company
URL: `/companies/add/`

Creates a new company and automatically assigns it to the current user as the active company.

#### Switch Company
URL: `/companies/switch/<company_id>/`

Deactivates all companies for the user and activates the selected one.

---

### 4. Filtering Data by Company

**Example from `dashboard/views.py`:**

```python
@login_required
def dashboard_view(request):
    # Get active company from middleware
    active_company = request.active_company

    # Filter all queries by active company
    revenue_accounts = Account.objects.filter(
        company=active_company,
        account_type=AccountType.REVENUE,
        is_active=True
    )

    invoices = Invoice.objects.filter(
        company=active_company,
        status__in=["SENT", "OVERDUE"]
    )

    journal_entries = JournalEntry.objects.filter(
        company=active_company,
        status="POSTED"
    )
```

**Always filter by `request.active_company` in your views to ensure data isolation!**

---

## Adding Company Support to New Models

When creating new accounting models that should be company-specific:

1. **Add the company ForeignKey:**

```python
class YourModel(models.Model):
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="your_models"
    )
    # ... other fields
```

2. **Update unique constraints** (if applicable):

```python
class Meta:
    unique_together = [["company", "your_unique_field"]]
    indexes = [
        models.Index(fields=["company", "field1", "field2"]),
    ]
```

3. **Filter queries by active company** in views:

```python
def your_view(request):
    active_company = request.active_company
    your_data = YourModel.objects.filter(company=active_company)
```

---

## Admin Panel

Companies are registered in the Django admin:

- `/admin/companies/company/` - Manage companies
- `/admin/companies/usercompany/` - Manage user-company relationships

---

## Database Schema Changes

### New Tables
- `companies_company` - Stores company information
- `companies_usercompany` - Links users to companies with active status

### Modified Tables
The following accounting tables now have a `company_id` ForeignKey:
- `accounting_account`
- `accounting_journalentry`
- `accounting_invoice`
- `accounting_customer`

**Note:** Existing data will have `company_id = NULL`. You should create a default company and assign existing records to it.

---

## Migration Strategy for Existing Data

If you have existing data, you'll need to:

1. Create a default company:
```python
python manage.py shell
>>> from companies.models import Company, UserCompany
>>> from django.contrib.auth.models import User
>>> company = Company.objects.create(name="Default Company", currency="JOD")
>>> for user in User.objects.all():
...     UserCompany.objects.create(user=user, company=company, is_active=True)
```

2. Assign existing records to the default company:
```python
>>> from accounting.models import Account, Invoice, JournalEntry, Customer
>>> company = Company.objects.first()
>>> Account.objects.update(company=company)
>>> Invoice.objects.update(company=company)
>>> JournalEntry.objects.update(company=company)
>>> Customer.objects.update(company=company)
```

---

## UI Components

### Sidebar Company Switcher

Located in `templates/components/sidemenu.html` at the bottom, above the Logout button:

```html
<li class="pt-4 mt-4 space-y-2 border-t border-gray-200 dark:border-gray-700">
    <div class="px-2">
        <label class="text-xs font-semibold text-gray-500 uppercase dark:text-gray-400">Company</label>
        <form method="post" action="{% url 'switch_company' 0 %}" id="companyForm" class="mt-2">
            {% csrf_token %}
            <select name="company_id" class="w-full px-3 py-2 text-sm..."
                onchange="this.form.action='/companies/switch/'+this.value+'/';this.form.submit();">
                {% for uc in request.user.usercompany_set.all %}
                    <option value="{{ uc.company.id }}" {% if uc.is_active %}selected{% endif %}>
                        {{ uc.company.name }}
                    </option>
                {% endfor %}
            </select>
        </form>
        <a href="{% url 'add_company' %}" class="mt-2 flex items-center justify-center...">
            Add Company
        </a>
    </div>
</li>
```

---

## Testing the Feature

1. **Create a test user and company:**
```bash
python manage.py createsuperuser
```

2. **Login and navigate to:** `/companies/add/`

3. **Create multiple companies** with different names

4. **Switch between companies** using the dropdown in the sidebar

5. **Verify data isolation** by creating accounts/invoices for each company

---

## API Considerations

If you have API endpoints, ensure they also filter by the active company:

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_invoices(request):
    active_company = request.active_company
    if not active_company:
        return Response({"error": "No active company"}, status=400)

    invoices = Invoice.objects.filter(company=active_company)
    # ... serialize and return
```

---

## Security Notes

⚠️ **Important Security Considerations:**

1. **Always filter by `request.active_company`** in views
2. **Never trust company_id from client input** - always use `request.active_company`
3. **Validate permissions** - ensure users can only access companies they belong to
4. **Audit trail** - log company switches for security monitoring

---

## Troubleshooting

### "No companies" in dropdown
- User hasn't created any companies yet
- Direct them to `/companies/add/`

### Data not filtering correctly
- Ensure `request.active_company` is being used in query filters
- Check that middleware is properly configured in `settings.py`

### Company switcher not appearing
- Verify `templates/components/sidemenu.html` has been updated
- Clear browser cache and refresh

---

## Future Enhancements

Potential improvements to consider:

- [ ] Company-level permissions and roles
- [ ] Inter-company transactions
- [ ] Company consolidation reports
- [ ] Company-specific settings (fiscal year, tax rates, etc.)
- [ ] Company logo upload
- [ ] Multi-currency support per company

---

## Support

For questions or issues with multi-company features, please refer to:
- Django documentation: https://docs.djangoproject.com/
- Project repository issues

---

**Last Updated:** 2025-10-15
**Feature Version:** 1.0
**Status:** ✅ Production Ready
