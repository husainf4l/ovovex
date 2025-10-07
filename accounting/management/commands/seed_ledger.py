from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounting.models import Account, JournalEntry, JournalEntryLine, AccountType
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Seeds the database with sample general ledger data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting database seeding...')
        
        # Get or create a default user
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@ovovex.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {user.username}'))
        
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        JournalEntryLine.objects.all().delete()
        JournalEntry.objects.all().delete()
        Account.objects.all().delete()
        
        # Create Chart of Accounts
        self.stdout.write('Creating Chart of Accounts...')
        accounts_data = [
            # Assets (1000-1999)
            {'code': '1000', 'name': 'Cash and Cash Equivalents', 'type': AccountType.ASSET, 'desc': 'Primary cash accounts'},
            {'code': '1010', 'name': 'Petty Cash', 'type': AccountType.ASSET, 'desc': 'Small cash on hand'},
            {'code': '1020', 'name': 'Bank Account - Operating', 'type': AccountType.ASSET, 'desc': 'Main operating account'},
            {'code': '1030', 'name': 'Bank Account - Savings', 'type': AccountType.ASSET, 'desc': 'Savings account'},
            {'code': '1100', 'name': 'Accounts Receivable', 'type': AccountType.ASSET, 'desc': 'Money owed by customers'},
            {'code': '1110', 'name': 'Allowance for Doubtful Accounts', 'type': AccountType.ASSET, 'desc': 'Estimated uncollectible receivables'},
            {'code': '1200', 'name': 'Inventory', 'type': AccountType.ASSET, 'desc': 'Goods held for sale'},
            {'code': '1300', 'name': 'Prepaid Expenses', 'type': AccountType.ASSET, 'desc': 'Expenses paid in advance'},
            {'code': '1400', 'name': 'Fixed Assets - Equipment', 'type': AccountType.ASSET, 'desc': 'Office equipment and machinery'},
            {'code': '1410', 'name': 'Fixed Assets - Furniture', 'type': AccountType.ASSET, 'desc': 'Office furniture'},
            {'code': '1420', 'name': 'Fixed Assets - Vehicles', 'type': AccountType.ASSET, 'desc': 'Company vehicles'},
            {'code': '1500', 'name': 'Accumulated Depreciation', 'type': AccountType.ASSET, 'desc': 'Total depreciation on fixed assets'},
            
            # Liabilities (2000-2999)
            {'code': '2000', 'name': 'Accounts Payable', 'type': AccountType.LIABILITY, 'desc': 'Money owed to suppliers'},
            {'code': '2100', 'name': 'Accrued Expenses', 'type': AccountType.LIABILITY, 'desc': 'Expenses incurred but not yet paid'},
            {'code': '2110', 'name': 'Salaries Payable', 'type': AccountType.LIABILITY, 'desc': 'Unpaid employee salaries'},
            {'code': '2120', 'name': 'Interest Payable', 'type': AccountType.LIABILITY, 'desc': 'Accrued interest on loans'},
            {'code': '2200', 'name': 'Short-term Loans', 'type': AccountType.LIABILITY, 'desc': 'Loans due within one year'},
            {'code': '2300', 'name': 'Long-term Loans', 'type': AccountType.LIABILITY, 'desc': 'Loans due after one year'},
            {'code': '2400', 'name': 'Tax Payable', 'type': AccountType.LIABILITY, 'desc': 'Taxes owed to government'},
            
            # Equity (3000-3999)
            {'code': '3000', 'name': "Owner's Equity", 'type': AccountType.EQUITY, 'desc': 'Owner investment in business'},
            {'code': '3100', 'name': 'Retained Earnings', 'type': AccountType.EQUITY, 'desc': 'Accumulated profits'},
            {'code': '3200', 'name': 'Drawings', 'type': AccountType.EQUITY, 'desc': 'Owner withdrawals'},
            
            # Revenue (4000-4999)
            {'code': '4000', 'name': 'Sales Revenue', 'type': AccountType.REVENUE, 'desc': 'Income from product sales'},
            {'code': '4100', 'name': 'Service Revenue', 'type': AccountType.REVENUE, 'desc': 'Income from services'},
            {'code': '4200', 'name': 'Interest Income', 'type': AccountType.REVENUE, 'desc': 'Interest earned on investments'},
            {'code': '4300', 'name': 'Other Income', 'type': AccountType.REVENUE, 'desc': 'Miscellaneous income'},
            
            # Expenses (5000-5999)
            {'code': '5000', 'name': 'Cost of Goods Sold', 'type': AccountType.EXPENSE, 'desc': 'Direct costs of products sold'},
            {'code': '5100', 'name': 'Salaries and Wages', 'type': AccountType.EXPENSE, 'desc': 'Employee compensation'},
            {'code': '5110', 'name': 'Employee Benefits', 'type': AccountType.EXPENSE, 'desc': 'Health insurance, retirement, etc.'},
            {'code': '5200', 'name': 'Rent Expense', 'type': AccountType.EXPENSE, 'desc': 'Office or facility rent'},
            {'code': '5210', 'name': 'Utilities Expense', 'type': AccountType.EXPENSE, 'desc': 'Electricity, water, internet, etc.'},
            {'code': '5220', 'name': 'Office Supplies', 'type': AccountType.EXPENSE, 'desc': 'Paper, pens, and office materials'},
            {'code': '5300', 'name': 'Marketing and Advertising', 'type': AccountType.EXPENSE, 'desc': 'Promotional expenses'},
            {'code': '5400', 'name': 'Insurance Expense', 'type': AccountType.EXPENSE, 'desc': 'Business insurance premiums'},
            {'code': '5500', 'name': 'Depreciation Expense', 'type': AccountType.EXPENSE, 'desc': 'Asset depreciation'},
            {'code': '5600', 'name': 'Interest Expense', 'type': AccountType.EXPENSE, 'desc': 'Interest on loans'},
            {'code': '5700', 'name': 'Professional Fees', 'type': AccountType.EXPENSE, 'desc': 'Legal, accounting, consulting'},
            {'code': '5800', 'name': 'Travel and Entertainment', 'type': AccountType.EXPENSE, 'desc': 'Business travel and meals'},
            {'code': '5900', 'name': 'Miscellaneous Expense', 'type': AccountType.EXPENSE, 'desc': 'Other operating expenses'},
        ]
        
        accounts = {}
        for acc_data in accounts_data:
            account = Account.objects.create(
                code=acc_data['code'],
                name=acc_data['name'],
                account_type=acc_data['type'],
                description=acc_data['desc'],
                created_by=user
            )
            accounts[acc_data['code']] = account
            
        self.stdout.write(self.style.SUCCESS(f'Created {len(accounts)} accounts'))
        
        # Create sample journal entries
        self.stdout.write('Creating sample journal entries...')
        
        journal_entries_data = [
            # Opening Balance Entry
            {
                'number': 'JE-2025-001',
                'date': datetime.now().date() - timedelta(days=90),
                'description': 'Opening Balances',
                'lines': [
                    {'account': '1020', 'debit': Decimal('500000.00'), 'credit': Decimal('0.00'), 'desc': 'Opening bank balance'},
                    {'account': '1400', 'debit': Decimal('150000.00'), 'credit': Decimal('0.00'), 'desc': 'Office equipment'},
                    {'account': '1410', 'debit': Decimal('75000.00'), 'credit': Decimal('0.00'), 'desc': 'Office furniture'},
                    {'account': '2300', 'debit': Decimal('0.00'), 'credit': Decimal('200000.00'), 'desc': 'Equipment loan'},
                    {'account': '3000', 'debit': Decimal('0.00'), 'credit': Decimal('525000.00'), 'desc': 'Owner initial investment'},
                ]
            },
            # Sales Transaction
            {
                'number': 'JE-2025-002',
                'date': datetime.now().date() - timedelta(days=85),
                'description': 'Sales to Customer ABC Corp',
                'lines': [
                    {'account': '1100', 'debit': Decimal('45000.00'), 'credit': Decimal('0.00'), 'desc': 'Invoice #1001'},
                    {'account': '4000', 'debit': Decimal('0.00'), 'credit': Decimal('45000.00'), 'desc': 'Product sales'},
                ]
            },
            # Payment received
            {
                'number': 'JE-2025-003',
                'date': datetime.now().date() - timedelta(days=80),
                'description': 'Payment received from ABC Corp',
                'lines': [
                    {'account': '1020', 'debit': Decimal('45000.00'), 'credit': Decimal('0.00'), 'desc': 'Bank deposit'},
                    {'account': '1100', 'debit': Decimal('0.00'), 'credit': Decimal('45000.00'), 'desc': 'Clear receivable'},
                ]
            },
            # Purchase of inventory
            {
                'number': 'JE-2025-004',
                'date': datetime.now().date() - timedelta(days=75),
                'description': 'Purchase of inventory from Supplier XYZ',
                'lines': [
                    {'account': '1200', 'debit': Decimal('25000.00'), 'credit': Decimal('0.00'), 'desc': 'Inventory purchased'},
                    {'account': '2000', 'debit': Decimal('0.00'), 'credit': Decimal('25000.00'), 'desc': 'Amount payable'},
                ]
            },
            # Salary payment
            {
                'number': 'JE-2025-005',
                'date': datetime.now().date() - timedelta(days=70),
                'description': 'Monthly salary payment',
                'lines': [
                    {'account': '5100', 'debit': Decimal('85000.00'), 'credit': Decimal('0.00'), 'desc': 'Staff salaries'},
                    {'account': '1020', 'debit': Decimal('0.00'), 'credit': Decimal('85000.00'), 'desc': 'Bank payment'},
                ]
            },
            # Rent payment
            {
                'number': 'JE-2025-006',
                'date': datetime.now().date() - timedelta(days=65),
                'description': 'Monthly rent payment',
                'lines': [
                    {'account': '5200', 'debit': Decimal('15000.00'), 'credit': Decimal('0.00'), 'desc': 'Office rent'},
                    {'account': '1020', 'debit': Decimal('0.00'), 'credit': Decimal('15000.00'), 'desc': 'Bank payment'},
                ]
            },
            # Utilities
            {
                'number': 'JE-2025-007',
                'date': datetime.now().date() - timedelta(days=60),
                'description': 'Utilities payment',
                'lines': [
                    {'account': '5210', 'debit': Decimal('3200.00'), 'credit': Decimal('0.00'), 'desc': 'Electricity and internet'},
                    {'account': '1020', 'debit': Decimal('0.00'), 'credit': Decimal('3200.00'), 'desc': 'Bank payment'},
                ]
            },
            # Service Revenue
            {
                'number': 'JE-2025-008',
                'date': datetime.now().date() - timedelta(days=55),
                'description': 'Service revenue from consulting',
                'lines': [
                    {'account': '1020', 'debit': Decimal('32000.00'), 'credit': Decimal('0.00'), 'desc': 'Cash received'},
                    {'account': '4100', 'debit': Decimal('0.00'), 'credit': Decimal('32000.00'), 'desc': 'Consulting services'},
                ]
            },
            # Office supplies
            {
                'number': 'JE-2025-009',
                'date': datetime.now().date() - timedelta(days=50),
                'description': 'Purchase of office supplies',
                'lines': [
                    {'account': '5220', 'debit': Decimal('2340.00'), 'credit': Decimal('0.00'), 'desc': 'Paper, pens, etc.'},
                    {'account': '1020', 'debit': Decimal('0.00'), 'credit': Decimal('2340.00'), 'desc': 'Cash payment'},
                ]
            },
            # Marketing expense
            {
                'number': 'JE-2025-010',
                'date': datetime.now().date() - timedelta(days=45),
                'description': 'Digital marketing campaign',
                'lines': [
                    {'account': '5300', 'debit': Decimal('12500.00'), 'credit': Decimal('0.00'), 'desc': 'Online ads'},
                    {'account': '1020', 'debit': Decimal('0.00'), 'credit': Decimal('12500.00'), 'desc': 'Bank payment'},
                ]
            },
            # Insurance payment
            {
                'number': 'JE-2025-011',
                'date': datetime.now().date() - timedelta(days=40),
                'description': 'Annual insurance premium',
                'lines': [
                    {'account': '5400', 'debit': Decimal('18000.00'), 'credit': Decimal('0.00'), 'desc': 'Business insurance'},
                    {'account': '1020', 'debit': Decimal('0.00'), 'credit': Decimal('18000.00'), 'desc': 'Bank payment'},
                ]
            },
            # Monthly depreciation
            {
                'number': 'JE-2025-012',
                'date': datetime.now().date() - timedelta(days=35),
                'description': 'Monthly depreciation expense',
                'lines': [
                    {'account': '5500', 'debit': Decimal('3200.00'), 'credit': Decimal('0.00'), 'desc': 'Equipment depreciation'},
                    {'account': '1500', 'debit': Decimal('0.00'), 'credit': Decimal('3200.00'), 'desc': 'Accumulated depreciation'},
                ]
            },
            # Interest on loan
            {
                'number': 'JE-2025-013',
                'date': datetime.now().date() - timedelta(days=30),
                'description': 'Interest payment on loan',
                'lines': [
                    {'account': '5600', 'debit': Decimal('4200.00'), 'credit': Decimal('0.00'), 'desc': 'Loan interest'},
                    {'account': '1020', 'debit': Decimal('0.00'), 'credit': Decimal('4200.00'), 'desc': 'Bank payment'},
                ]
            },
            # Sales transaction
            {
                'number': 'JE-2025-014',
                'date': datetime.now().date() - timedelta(days=25),
                'description': 'Sales to Customer DEF Ltd',
                'lines': [
                    {'account': '1020', 'debit': Decimal('67500.00'), 'credit': Decimal('0.00'), 'desc': 'Cash sale'},
                    {'account': '4000', 'debit': Decimal('0.00'), 'credit': Decimal('67500.00'), 'desc': 'Product sales'},
                ]
            },
            # Employee benefits
            {
                'number': 'JE-2025-015',
                'date': datetime.now().date() - timedelta(days=20),
                'description': 'Employee health insurance',
                'lines': [
                    {'account': '5110', 'debit': Decimal('8500.00'), 'credit': Decimal('0.00'), 'desc': 'Health insurance premium'},
                    {'account': '1020', 'debit': Decimal('0.00'), 'credit': Decimal('8500.00'), 'desc': 'Bank payment'},
                ]
            },
            # Professional fees
            {
                'number': 'JE-2025-016',
                'date': datetime.now().date() - timedelta(days=15),
                'description': 'Accounting services',
                'lines': [
                    {'account': '5700', 'debit': Decimal('5200.00'), 'credit': Decimal('0.00'), 'desc': 'Monthly accounting fees'},
                    {'account': '1020', 'debit': Decimal('0.00'), 'credit': Decimal('5200.00'), 'desc': 'Bank payment'},
                ]
            },
            # Interest income
            {
                'number': 'JE-2025-017',
                'date': datetime.now().date() - timedelta(days=10),
                'description': 'Interest earned on savings',
                'lines': [
                    {'account': '1030', 'debit': Decimal('850.00'), 'credit': Decimal('0.00'), 'desc': 'Savings interest'},
                    {'account': '4200', 'debit': Decimal('0.00'), 'credit': Decimal('850.00'), 'desc': 'Interest income'},
                ]
            },
            # Travel expense
            {
                'number': 'JE-2025-018',
                'date': datetime.now().date() - timedelta(days=5),
                'description': 'Business travel expenses',
                'lines': [
                    {'account': '5800', 'debit': Decimal('4750.00'), 'credit': Decimal('0.00'), 'desc': 'Flight and hotel'},
                    {'account': '1020', 'debit': Decimal('0.00'), 'credit': Decimal('4750.00'), 'desc': 'Cash payment'},
                ]
            },
            # Recent sales
            {
                'number': 'JE-2025-019',
                'date': datetime.now().date() - timedelta(days=2),
                'description': 'Sales to Customer GHI Inc',
                'lines': [
                    {'account': '1100', 'debit': Decimal('28900.00'), 'credit': Decimal('0.00'), 'desc': 'Invoice #1025'},
                    {'account': '4000', 'debit': Decimal('0.00'), 'credit': Decimal('28900.00'), 'desc': 'Product sales'},
                ]
            },
        ]
        
        for entry_data in journal_entries_data:
            # Create journal entry
            journal_entry = JournalEntry.objects.create(
                entry_number=entry_data['number'],
                entry_date=entry_data['date'],
                description=entry_data['description'],
                status=JournalEntry.Status.POSTED,
                created_by=user,
                posted_by=user,
                posted_at=timezone.now()
            )
            
            # Create journal entry lines
            for i, line_data in enumerate(entry_data['lines'], start=1):
                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=accounts[line_data['account']],
                    description=line_data['desc'],
                    debit_amount=line_data['debit'],
                    credit_amount=line_data['credit'],
                    line_number=i
                )
            
            # Recalculate totals
            journal_entry.calculate_totals()
            
        self.stdout.write(self.style.SUCCESS(f'Created {len(journal_entries_data)} journal entries'))
        
        # Update account balances
        self.stdout.write('Updating account balances...')
        for account in Account.objects.all():
            account.balance = account.get_balance()
            account.save()
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
