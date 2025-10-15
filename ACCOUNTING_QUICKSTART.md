# 🚀 Ovovex Accounting System - Quick Start Guide

## Getting Started in 5 Minutes

### Step 1: Access the Dashboard
Navigate to: `http://localhost:8000/dashboard/`

### Step 2: Select/Create Company
If no company selected, you'll be prompted to create one at `/companies/add/`

### Step 3: Access Accounting Modules

#### 📄 **Invoices**
```
URL: /accounting/invoices/
Action Buttons:
- Create Invoice → /accounting/invoices/create/
- View Invoice → /accounting/invoices/{id}/
- Edit Invoice → /accounting/invoices/{id}/edit/
- Send Invoice → /accounting/invoices/{id}/send/
- Delete Invoice → /accounting/invoices/{id}/delete/
- Record Payment → /accounting/payments/create/{invoice_id}/
```

#### 💰 **Expenses**
```
URL: /accounting/expenses/
Action Buttons:
- Record Expense → /accounting/expenses/create/
- View Expense → /accounting/expenses/{id}/
- Approve Expense → /accounting/expenses/{id}/approve/
- Delete Expense → /accounting/expenses/{id}/delete/
```

#### 📒 **Journal Entries**
```
URL: /accounting/journal-entries/
Action Buttons:
- New Journal Entry → /accounting/journal-entries/create/
- View Entry → /accounting/journal-entries/{id}/
- Post Entry → /accounting/journal-entries/{id}/post/
- Delete Entry → /accounting/journal-entries/{id}/delete/ (DRAFT only)
```

#### 📊 **Budgets**
```
URL: /accounting/budgets/
Action Buttons:
- Create Budget → /accounting/budgets/create/
- View Budget → /accounting/budgets/{id}/
- Variance Report → Auto-calculated on detail page
- Delete Budget → /accounting/budgets/{id}/delete/
```

#### 🏢 **Fixed Assets**
```
URL: /accounting/fixed-assets/
Action Buttons:
- Add Fixed Asset → /accounting/fixed-assets/create/
- View Asset → /accounting/fixed-assets/{id}/
- Edit Asset → /accounting/fixed-assets/{id}/edit/
- Delete Asset → /accounting/fixed-assets/{id}/delete/
```

#### 👥 **Customers**
```
URL: /accounting/customers/
Action Buttons:
- Add Customer → /accounting/customers/create/
- View Customer → /accounting/customers/{id}/
```

#### 🤖 **AI Insights**
```
URLs:
- Run Analysis → /accounting/ai/run-analysis/
- Trend Analysis → /accounting/ai/trend-analysis/
```

## 🔗 Dashboard Button Wiring

### Update Dashboard Templates

Add these URL links to your dashboard action buttons:

```html
<!-- Invoices Section -->
<a href="{% url 'accounting:invoice_create' %}" class="btn btn-primary">
    <i class="fas fa-plus"></i> Create Invoice
</a>
<a href="{% url 'accounting:invoice_list' %}" class="btn btn-secondary">
    <i class="fas fa-list"></i> View Invoices
</a>

<!-- Expenses Section -->
<a href="{% url 'accounting:expense_create' %}" class="btn btn-success">
    <i class="fas fa-receipt"></i> Record Expense
</a>
<a href="{% url 'accounting:expense_list' %}" class="btn btn-secondary">
    <i class="fas fa-list"></i> View Expenses
</a>

<!-- Journal Entries -->
<a href="{% url 'accounting:journal_entry_create' %}" class="btn btn-warning">
    <i class="fas fa-book"></i> New Journal Entry
</a>
<a href="{% url 'accounting:journal_entry_list' %}" class="btn btn-secondary">
    <i class="fas fa-list"></i> View Entries
</a>

<!-- Budgets -->
<a href="{% url 'accounting:budget_create' %}" class="btn btn-info">
    <i class="fas fa-chart-pie"></i> Create Budget
</a>
<a href="{% url 'accounting:budget_list' %}" class="btn btn-secondary">
    <i class="fas fa-list"></i> View Budgets
</a>

<!-- Fixed Assets -->
<a href="{% url 'accounting:fixed_asset_create' %}" class="btn btn-secondary">
    <i class="fas fa-building"></i> Add Asset
</a>
<a href="{% url 'accounting:fixed_asset_list' %}" class="btn btn-secondary">
    <i class="fas fa-list"></i> View Assets
</a>

<!-- AI Insights -->
<a href="{% url 'accounting:ai_run_analysis' %}" class="btn btn-primary">
    <i class="fas fa-robot"></i> Run AI Analysis
</a>
<a href="{% url 'accounting:ai_trend_analysis' %}" class="btn btn-secondary">
    <i class="fas fa-chart-line"></i> Trend Analysis
</a>
```

## 📝 Common Workflows

### Workflow 1: Create and Send Invoice
```
1. Click "Create Invoice" button
2. Select customer, enter amounts
3. Save as DRAFT
4. Review invoice details
5. Click "Send Invoice"
6. Status changes to SENT
7. When customer pays, click "Record Payment"
8. Invoice auto-updates to PAID
```

### Workflow 2: Record and Approve Expense
```
1. Click "Record Expense" button
2. Enter expense details
3. Save as DRAFT or SUBMITTED
4. Manager reviews and clicks "Approve"
5. Status changes to APPROVED
6. Process payment (status → PAID)
```

### Workflow 3: Create Budget and Track Variance
```
1. Click "Create Budget" button
2. Enter fiscal year, period, dates
3. Add budget lines per account
4. Save budget
5. System auto-calculates variance
6. View budget detail for variance report
```

### Workflow 4: Register Fixed Asset
```
1. Click "Add Asset" button
2. Enter asset code, name, category
3. Enter purchase cost, useful life
4. Select depreciation method
5. Save asset
6. System auto-calculates book value
7. View depreciation schedule on detail page
```

## 🎯 Testing Instructions

### Test Invoice Creation
```bash
# 1. Create customer first
http://localhost:8000/accounting/customers/create/

# 2. Create invoice
http://localhost:8000/accounting/invoices/create/

# 3. Record payment
http://localhost:8000/accounting/payments/create/
```

### Test Journal Entry
```bash
# Create journal entry with balanced debits/credits
http://localhost:8000/accounting/journal-entries/create/

# Example entry:
Debit:  Cash (1000)         $5,000
Credit: Revenue (4000)               $5,000
```

### Test Expense Approval
```bash
# Create expense
http://localhost:8000/accounting/expenses/create/

# Approve expense
http://localhost:8000/accounting/expenses/1/approve/
```

## 🐛 Troubleshooting

### Issue: "No reverse for 'accounting:invoice_create'"
**Solution**: Ensure accounting URLs are included in main `urls.py`:
```python
path("accounting/", include("accounting.urls", namespace="accounting")),
```

### Issue: "Company matching query does not exist"
**Solution**: Create a company first at `/companies/add/`

### Issue: "Invoice list is empty"
**Solution**: Create your first invoice at `/accounting/invoices/create/`

### Issue: "Journal entry cannot be posted"
**Solution**: Ensure debits equal credits before posting

### Issue: "Cannot delete journal entry"
**Solution**: Only DRAFT entries can be deleted. POSTED entries are permanent.

## 📊 Statistics Tracking

The system automatically tracks:
- Total invoices, revenue, paid/overdue counts
- Total expenses, approval status counts
- Budget vs actual, variance calculations
- Asset book values, depreciation totals
- Customer outstanding balances

## 🔐 Security Notes

- All operations require login (`@login_required`)
- All data filtered by active company
- CSRF protection on all forms
- No SQL injection (Django ORM)
- Transaction integrity for journal entries

## 📈 Next Actions

1. ✅ **Test Invoice Creation**
2. ✅ **Test Payment Recording**
3. ✅ **Test Journal Entry Posting**
4. ✅ **Test Expense Approval**
5. ✅ **Test Budget Creation**
6. ✅ **Test Asset Registration**
7. ✅ **Verify Multi-Company Isolation**
8. ✅ **Check Dashboard Integration**

## 🎉 Success Criteria

You'll know everything is working when:
- ✅ Dashboard buttons navigate to correct pages
- ✅ Forms save data successfully
- ✅ Data appears in list views
- ✅ Company switching filters data correctly
- ✅ Statistics cards show accurate numbers
- ✅ Status changes work (DRAFT → SENT → PAID)
- ✅ Validations prevent invalid data
- ✅ Success messages appear after saves
- ✅ Delete confirmations work
- ✅ Multi-company isolation verified

---

**Ready to go!** Start by creating your first invoice at:
`http://localhost:8000/accounting/invoices/create/`

**Support**: Check [ACCOUNTING_CRUD_COMPLETE.md](./ACCOUNTING_CRUD_COMPLETE.md) for detailed documentation.
