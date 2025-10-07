# General Ledger Implementation

## Overview
A complete General Ledger module has been implemented with database models, seeding functionality, and a dynamic view displaying real data from the database.

## What Was Created

### 1. Django App: `accounting`
A new Django app containing all the accounting-related functionality.

### 2. Models (`accounting/models.py`)

#### Account Model
- **Purpose**: Chart of Accounts - defines all accounts in the general ledger
- **Fields**:
  - `code`: Unique account code (e.g., "1000", "2000")
  - `name`: Account name (e.g., "Cash and Cash Equivalents")
  - `account_type`: Type of account (ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE)
  - `description`: Detailed description of the account
  - `parent_account`: For hierarchical account structures
  - `is_active`: Whether the account is active
  - `balance`: Current account balance
  - `created_at`, `updated_at`: Timestamps
  - `created_by`: User who created the account

#### JournalEntry Model
- **Purpose**: Journal Entry header containing metadata
- **Fields**:
  - `entry_number`: Unique entry number (e.g., "JE-2025-001")
  - `entry_date`: Date of the transaction
  - `description`: Entry description
  - `reference`: Optional reference number
  - `status`: DRAFT, POSTED, or VOID
  - `total_debit`, `total_credit`: Total amounts
  - `created_at`, `updated_at`, `posted_at`: Timestamps
  - `created_by`, `posted_by`: User tracking

#### JournalEntryLine Model
- **Purpose**: Individual debit/credit lines in a journal entry
- **Fields**:
  - `journal_entry`: Foreign key to JournalEntry
  - `account`: Foreign key to Account
  - `description`: Line description
  - `debit_amount`, `credit_amount`: Transaction amounts
  - `line_number`: Line order in the entry

### 3. Database Seeding Command
**Command**: `python manage.py seed_ledger`

This management command creates:
- **39 Accounts** across all account types:
  - Assets (1000-1999): Cash, Receivables, Inventory, Fixed Assets, etc.
  - Liabilities (2000-2999): Payables, Loans, Tax Payable, etc.
  - Equity (3000-3999): Owner's Equity, Retained Earnings, etc.
  - Revenue (4000-4999): Sales Revenue, Service Revenue, Interest Income, etc.
  - Expenses (5000-5999): Salaries, Rent, Utilities, Marketing, etc.

- **19 Journal Entries** with realistic transactions:
  - Opening balances
  - Sales and payment transactions
  - Expense entries (salaries, rent, utilities, supplies)
  - Asset purchases and depreciation
  - Interest payments and income

### 4. Updated View (`ovovex/views.py`)
The `general_ledger_view` function now:
- Fetches all active accounts from the database
- Calculates real-time balances using the `get_balance()` method
- Provides filtering by account type
- Retrieves statistics:
  - Total active accounts
  - Journal entries posted this month
  - Unbalanced/draft entries count
  - Total posted entries
- Calculates balance summary by account type
- Shows recent journal entries
- Computes net balance (Assets - Liabilities)

### 5. Updated Template (`templates/modules/general_ledger.html`)
The template now displays:
- **Dynamic KPI Cards**: Real statistics from the database
- **Chart of Accounts Table**: 
  - All accounts with their codes, names, types, and balances
  - Color-coded balances (green for positive, red for negative)
  - Active/inactive status indicators
  - Filterable by account type
- **Recent Journal Entries**: Last 5 posted entries with details
- **Balance Summary**: Totals for each account type (Assets, Liabilities, Equity, Revenue, Expenses)
- **Net Balance**: Calculated net position

### 6. Admin Interface (`accounting/admin.py`)
Configured Django admin for:
- Account management with search and filtering
- Journal Entry management with inline entry lines
- Balance checking and validation

## Usage

### 1. Access the General Ledger
Navigate to: `http://localhost:8000/ledger/`

### 2. Filter Accounts
Use the dropdown filter to view accounts by type:
- All Types
- Assets
- Liabilities
- Equity
- Revenue
- Expenses

### 3. View Account Details
The table displays:
- Account Code
- Account Name
- Account Type
- Current Balance (color-coded)
- Status

### 4. Monitor Recent Activity
The sidebar shows:
- Recent journal entries
- Balance summary by account type
- Net balance calculation

### 5. Reseed the Database
To clear and recreate sample data:
```bash
python manage.py seed_ledger
```

## Database Schema

### Relationships
```
Account
  └── JournalEntryLine (many-to-one)
        └── JournalEntry (many-to-one)
              └── User (created_by, posted_by)
```

### Key Features
- **Double-entry bookkeeping**: Every journal entry must have balanced debits and credits
- **Balance calculation**: Account balances are calculated dynamically from posted journal entries
- **Account type logic**: 
  - Assets & Expenses: Debit increases, Credit decreases
  - Liabilities, Equity & Revenue: Credit increases, Debit decreases
- **Status tracking**: Draft, Posted, and Void states for journal entries
- **Audit trail**: Tracks who created and posted entries with timestamps

## Sample Data Summary

After running `seed_ledger`, you'll have:
- 39 accounts spanning all major categories
- 19 posted journal entries covering common transactions
- Realistic balances calculated from transactions
- Data covering the last 90 days

## Future Enhancements

Potential improvements:
1. Add account detail view showing all transactions
2. Implement trial balance report
3. Add journal entry creation form
4. Implement account reconciliation
5. Add period closing functionality
6. Export to PDF/Excel
7. Advanced filtering and search
8. Multi-currency support
9. Budget vs. actual comparison
10. Financial statement generation

## Technical Notes

- Uses Django ORM for all database operations
- Implements proper indexing on frequently queried fields
- Uses DecimalField for accurate financial calculations
- Follows accounting best practices for double-entry bookkeeping
- Includes data validation at model level
- Timezone-aware datetime handling
- Responsive dark/light mode UI with Tailwind CSS

## Admin Access

Access the Django admin panel at: `http://localhost:8000/admin/`
- Username: `admin`
- Password: `admin123` (created by seed_ledger command)

Through the admin, you can:
- Create, edit, and delete accounts
- Create journal entries with multiple lines
- View balance calculations
- Check if entries are balanced
