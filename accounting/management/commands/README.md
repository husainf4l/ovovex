"""
Seed General Ledger Data

# Accounting Management Commands

This directory contains Django management commands for seeding the database with sample accounting data.

## Available Commands

### `seed_ledger`
Seeds the database with basic general ledger data including:
- Chart of accounts (assets, liabilities, equity, revenue, expenses)
- Sample journal entries
- Account balances

### `seed_all_modules`
Comprehensive seeding command that populates all accounting modules with sample data:
- Chart of accounts
- Customers and vendors
- Invoices and bills
- Journal entries
- Fixed assets
- Expenses and budgets
- Tax data

### `seed_fixed_assets`
Seeds the database with comprehensive fixed assets data including:
- **Office Equipment**: Laptops, printers, phones, servers, projectors
- **Furniture**: Desks, cubicles, conference tables, reception furniture
- **Vehicles**: Company cars and vans
- **Buildings & Land**: Office building and land
- **Software**: Accounting software, office suites, antivirus
- **Leasehold Improvements**: Office renovations and HVAC upgrades

#### Features:
- **20 diverse fixed assets** across 7 categories
- **Realistic depreciation calculations** using both straight-line and declining balance methods
- **Detailed asset information** including location, description, and useful life
- **Automatic depreciation** based on purchase date and current date
- **Comprehensive reporting** with totals by category and depreciation method

#### Sample Data Includes:
- Asset codes, names, and detailed descriptions
- Purchase costs ranging from $1,200 to $750,000
- Various useful lives (3-99 years)
- Multiple depreciation methods
- Location tracking
- Salvage values

#### Usage:
```bash
python manage.py seed_fixed_assets
```

#### Output:
- Creates 20 fixed assets
- Calculates accumulated depreciation
- Shows summary by category
- Displays overall totals
- Reports depreciation methods used

## Running Commands

All commands can be run from the project root:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run a specific command
python manage.py <command_name>

# Example
python manage.py seed_fixed_assets
```

## Notes

- Commands will create an admin user if one doesn't exist (username: admin, password: admin123)
- Existing data may be cleared depending on the command
- All monetary values are in USD
- Dates are randomized within reasonable ranges
- Chart of Accounts (39 accounts across all types)
- Sample Journal Entries (19 transactions covering 90 days)
- Calculated account balances

Usage:
    python manage.py seed_ledger

The command will:
1. Create an admin user (username: admin, password: admin123) if not exists
2. Clear all existing accounting data
3. Create a complete chart of accounts
4. Generate realistic journal entries
5. Calculate and update account balances

Account Types Created:
- Assets (1000-1999): 12 accounts
- Liabilities (2000-2999): 7 accounts
- Equity (3000-3999): 3 accounts
- Revenue (4000-4999): 4 accounts
- Expenses (5000-5999): 13 accounts

Sample Transactions Include:
- Opening balances
- Sales and customer payments
- Inventory purchases
- Salary and benefit payments
- Rent and utilities
- Office supplies and equipment
- Marketing expenses
- Depreciation and interest
- Professional fees
- Travel expenses

After running, visit http://localhost:8000/ledger/ to view the general ledger.
"""
