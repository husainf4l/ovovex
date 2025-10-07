# Quick Start Guide - Ovovex Accounting System

## 🚀 Quick Setup (5 minutes)

### Step 1: Seed the Database
```bash
cd /home/aqlaan/Desktop/ovovex
source .venv/bin/activate
python manage.py seed_all_modules
```

### Step 2: Start the Server
```bash
python manage.py runserver 0.0.0.0:8000
```

### Step 3: Access the Application
- **Main Site**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
  - Username: `admin`
  - Password: `admin123`

## 📊 Available Modules & URLs

### Core Accounting
| Module | URL | What You'll See |
|--------|-----|-----------------|
| **General Ledger** | `/ledger/` | 39 accounts, balances, recent entries |
| **Journal Entries** | `/journal-entries/` | Double-entry transactions |
| **Balance Sheet** | `/balance-sheet/` | Assets, Liabilities, Equity |
| **P&L Statement** | `/pnl-statement/` | Revenue, Expenses, Net Profit |

### Invoicing & Receivables
| Module | URL | What You'll See |
|--------|-----|-----------------|
| **Invoices** | `/invoices/` | 3 sample invoices |
| **Accounts Receivable** | `/accounts-receivable/` | Outstanding invoices, aging |

### Payables
| Module | URL | What You'll See |
|--------|-----|-----------------|
| **Accounts Payable** | `/accounts-payable/` | 3 sample bills |

### Financial Management
| Module | URL | What You'll See |
|--------|-----|-----------------|
| **Cash Flow** | `/cash-flow/` | Cash flow analysis |
| **Budgeting** | `/budgeting/` | Budget vs Actual |
| **Fixed Assets** | `/fixed-assets/` | 4 assets with depreciation |
| **Bank Reconciliation** | `/bank-reconciliation/` | Bank statement matching |
| **Tax Center** | `/tax-center/` | Tax returns and rates |

### Operations
| Module | URL | What You'll See |
|--------|-----|-----------------|
| **Expense Management** | `/expense-management/` | 4 expense categories |
| **Purchase Orders** | `/purchase-orders/` | PO tracking |
| **Inventory** | `/inventory/` | Inventory management |

### Analytics
| Module | URL | What You'll See |
|--------|-----|-----------------|
| **Financial Ratios** | `/financial-ratios/` | Liquidity, profitability ratios |
| **AI Insights** | `/ai-insights/` | AI-powered analysis |
| **Anomaly Detection** | `/anomaly-detection/` | Unusual patterns |

## 📝 Sample Data Overview

### Customers (5)
- ABC Corporation
- XYZ Industries
- Tech Solutions Ltd
- Global Trading Inc
- Premier Services

### Vendors (5)
- Office Supplies Co
- Tech Equipment Ltd
- Utility Services Inc
- Marketing Agency
- Legal Services LLP

### Accounts (39)
- **Assets**: Cash, Receivables, Inventory, Fixed Assets
- **Liabilities**: Payables, Loans, Accrued Expenses
- **Equity**: Owner's Equity, Retained Earnings
- **Revenue**: Sales, Service Revenue, Interest Income
- **Expenses**: Salaries, Rent, Utilities, Marketing, etc.

### Transactions
- 3 Journal Entries (opening balances, salary, rent)
- 3 Invoices (with line items and payments)
- 3 Bills (vendor payables)
- 4 Expenses (office supplies, travel, etc.)
- 4 Fixed Assets (laptop, desk, vehicle, server)
- 1 Budget (FY2025 Annual)
- 2 Tax Returns (Q1-Q2 2025)

## 🔧 Common Tasks

### View Account Balances
```bash
python manage.py shell
>>> from accounting.models import Account
>>> for acc in Account.objects.all()[:5]:
...     print(f"{acc.code} - {acc.name}: ${acc.get_balance()}")
```

### Check Invoice Status
```bash
python manage.py shell
>>> from accounting.models import Invoice
>>> for inv in Invoice.objects.all():
...     print(f"{inv.invoice_number}: {inv.status} - ${inv.total_amount}")
```

### View Customer Outstanding Balance
```bash
python manage.py shell
>>> from accounting.models import Customer
>>> for customer in Customer.objects.all():
...     print(f"{customer.company_name}: ${customer.get_outstanding_balance()}")
```

### Generate Balance Sheet Report
Navigate to: http://localhost:8000/balance-sheet/

### Generate P&L Statement
Navigate to: http://localhost:8000/pnl-statement/

## 🎨 UI Features

- **Dark Mode**: Toggle between light and dark themes
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Statistics**: Live KPIs on every page
- **Interactive Tables**: Sortable and filterable data
- **Quick Actions**: One-click access to common tasks

## 🔐 Admin Panel Features

Access: http://localhost:8000/admin/
Login: admin / admin123

### What You Can Do:
- ✅ Create/Edit Accounts
- ✅ Post Journal Entries (with inline lines)
- ✅ Manage Customers & Vendors
- ✅ Create Invoices & Bills
- ✅ Track Payments
- ✅ Manage Fixed Assets
- ✅ Create Budgets
- ✅ Submit Expenses
- ✅ File Tax Returns

## 📊 Key Reports Available

### 1. General Ledger Report
- All accounts with balances
- Filter by account type
- Real-time balance calculation

### 2. Balance Sheet
- Assets = Liabilities + Equity
- Current vs Fixed Assets
- Short-term vs Long-term Liabilities

### 3. Income Statement (P&L)
- Total Revenue
- Cost of Goods Sold
- Gross Profit
- Operating Expenses
- Net Profit
- Profit Margin %

### 4. Accounts Receivable Aging
- Current (not due)
- 1-30 days overdue
- 31-60 days overdue
- 61-90 days overdue
- 90+ days overdue

### 5. Budget vs Actual
- Budgeted amounts by account
- Actual spending
- Variance analysis
- % of budget used

### 6. Financial Ratios
- **Liquidity**: Current Ratio
- **Leverage**: Debt-to-Equity Ratio
- **Profitability**: Profit Margin, ROA, ROE

## 🐛 Troubleshooting

### Problem: No data showing
**Solution**: Run the seeding command
```bash
python manage.py seed_all_modules
```

### Problem: Balances are zero
**Solution**: Recalculate balances
```bash
python manage.py shell
>>> from accounting.models import Account
>>> for acc in Account.objects.all():
...     acc.balance = acc.get_balance()
...     acc.save()
```

### Problem: Can't login to admin
**Solution**: Reset admin password
```bash
python manage.py changepassword admin
# Or create new superuser:
python manage.py createsuperuser
```

### Problem: Server won't start
**Solution**: Check if another process is using port 8000
```bash
lsof -i :8000
# Kill the process if needed
kill -9 <PID>
# Then restart
python manage.py runserver
```

## 📚 Next Steps

### Learning Path
1. ✅ Explore the General Ledger (`/ledger/`)
2. ✅ Create a test invoice in Admin Panel
3. ✅ View Balance Sheet report
4. ✅ Check Financial Ratios
5. ✅ Create a budget entry
6. ✅ Submit an expense

### Development Tasks
1. Customize account codes for your business
2. Add your real customers and vendors
3. Configure tax rates for your jurisdiction
4. Set up your fiscal year budget
5. Import historical transactions
6. Customize reports for your needs

## 🎯 Pro Tips

1. **Always Balance Journal Entries**: Debits must equal credits
2. **Use Status Workflow**: Draft → Approved → Posted
3. **Regular Reconciliation**: Match bank statements monthly
4. **Budget Tracking**: Update actuals regularly
5. **Backup Data**: Export reports periodically

## 📞 Support

- **Documentation**: Check markdown files in `/home/aqlaan/Desktop/ovovex/`
- **Model Reference**: See `accounting/models.py` docstrings
- **Admin Guide**: Access admin panel for CRUD operations

## 🎉 You're Ready!

Your accounting system is fully set up with:
- ✅ 39 Chart of Accounts
- ✅ 5 Customers & 5 Vendors
- ✅ Sample transactions across all modules
- ✅ Real-time reporting
- ✅ Full double-entry bookkeeping
- ✅ Financial analysis tools

**Start exploring**: http://localhost:8000/dashboard/

---
*Last Updated: October 7, 2025*
