from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounting.models import *
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Seeds the database with comprehensive accounting data for all modules'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('Starting Comprehensive Database Seeding'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        # Get or create admin user
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
            self.stdout.write(self.style.SUCCESS(f'✓ Created admin user'))
        else:
            self.stdout.write(f'✓ Using existing admin user')
        
        # Clear existing data (in reverse order of dependencies)
        self.stdout.write('\nClearing existing data...')
        models_to_clear = [
            TaxReturn, TaxRate, Expense, ExpenseCategory,
            FixedAsset, BudgetLine, Budget, Bill, Vendor,
            Payment, InvoiceLine, Invoice, Customer,
            JournalEntryLine, JournalEntry, Account
        ]
        for model in models_to_clear:
            count = model.objects.count()
            model.objects.all().delete()
            if count > 0:
                self.stdout.write(f'  Cleared {count} {model.__name__} records')
        
        # Seed Chart of Accounts
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SEEDING: Chart of Accounts')
        self.stdout.write('='*60)
        accounts = self._seed_accounts(user)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(accounts)} accounts'))
        
        # Seed Customers
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SEEDING: Customers')
        self.stdout.write('='*60)
        customers = self._seed_customers()
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(customers)} customers'))
        
        # Seed Vendors
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SEEDING: Vendors')
        self.stdout.write('='*60)
        vendors = self._seed_vendors()
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(vendors)} vendors'))
        
        # Seed Invoices
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SEEDING: Invoices & Payments')
        self.stdout.write('='*60)
        invoices = self._seed_invoices(customers, user)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(invoices)} invoices'))
        
        # Seed Bills
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SEEDING: Bills (Payables)')
        self.stdout.write('='*60)
        bills = self._seed_bills(vendors, user)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(bills)} bills'))
        
        # Seed Journal Entries
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SEEDING: Journal Entries')
        self.stdout.write('='*60)
        entries = self._seed_journal_entries(accounts, user)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(entries)} journal entries'))
        
        # Seed Fixed Assets
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SEEDING: Fixed Assets')
        self.stdout.write('='*60)
        assets = self._seed_fixed_assets(accounts)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(assets)} fixed assets'))
        
        # Seed Expenses
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SEEDING: Expenses')
        self.stdout.write('='*60)
        expense_cats = self._seed_expense_categories(accounts)
        expenses = self._seed_expenses(expense_cats, vendors, user)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(expense_cats)} expense categories'))
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(expenses)} expenses'))
        
        # Seed Budgets
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SEEDING: Budgets')
        self.stdout.write('='*60)
        budgets = self._seed_budgets(accounts, user)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(budgets)} budgets'))
        
        # Seed Tax
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SEEDING: Tax Data')
        self.stdout.write('='*60)
        tax_rates = self._seed_tax_rates()
        tax_returns = self._seed_tax_returns(user)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(tax_rates)} tax rates'))
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(tax_returns)} tax returns'))
        
        # Update account balances
        self.stdout.write('\n' + '='*60)
        self.stdout.write('Updating account balances...')
        self.stdout.write('='*60)
        for account in Account.objects.all():
            account.balance = account.get_balance()
            account.save()
        self.stdout.write(self.style.SUCCESS('✓ Account balances updated'))
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write('\nQuick Stats:')
        self.stdout.write(f'  Accounts: {Account.objects.count()}')
        self.stdout.write(f'  Customers: {Customer.objects.count()}')
        self.stdout.write(f'  Vendors: {Vendor.objects.count()}')
        self.stdout.write(f'  Invoices: {Invoice.objects.count()}')
        self.stdout.write(f'  Bills: {Bill.objects.count()}')
        self.stdout.write(f'  Journal Entries: {JournalEntry.objects.count()}')
        self.stdout.write(f'  Fixed Assets: {FixedAsset.objects.count()}')
        self.stdout.write(f'  Expenses: {Expense.objects.count()}')
        self.stdout.write(f'  Budgets: {Budget.objects.count()}')
        self.stdout.write('')

    def _seed_accounts(self, user):
        """Seed chart of accounts"""
        accounts_data = [
            # Assets (1000-1999)
            {'code': '1000', 'name': 'Cash and Cash Equivalents', 'type': AccountType.ASSET},
            {'code': '1010', 'name': 'Petty Cash', 'type': AccountType.ASSET},
            {'code': '1020', 'name': 'Bank Account - Operating', 'type': AccountType.ASSET},
            {'code': '1030', 'name': 'Bank Account - Savings', 'type': AccountType.ASSET},
            {'code': '1100', 'name': 'Accounts Receivable', 'type': AccountType.ASSET},
            {'code': '1110', 'name': 'Allowance for Doubtful Accounts', 'type': AccountType.ASSET},
            {'code': '1200', 'name': 'Inventory', 'type': AccountType.ASSET},
            {'code': '1300', 'name': 'Prepaid Expenses', 'type': AccountType.ASSET},
            {'code': '1400', 'name': 'Fixed Assets - Equipment', 'type': AccountType.ASSET},
            {'code': '1410', 'name': 'Fixed Assets - Furniture', 'type': AccountType.ASSET},
            {'code': '1420', 'name': 'Fixed Assets - Vehicles', 'type': AccountType.ASSET},
            {'code': '1500', 'name': 'Accumulated Depreciation', 'type': AccountType.ASSET},
            
            # Liabilities (2000-2999)
            {'code': '2000', 'name': 'Accounts Payable', 'type': AccountType.LIABILITY},
            {'code': '2100', 'name': 'Accrued Expenses', 'type': AccountType.LIABILITY},
            {'code': '2110', 'name': 'Salaries Payable', 'type': AccountType.LIABILITY},
            {'code': '2120', 'name': 'Interest Payable', 'type': AccountType.LIABILITY},
            {'code': '2200', 'name': 'Short-term Loans', 'type': AccountType.LIABILITY},
            {'code': '2300', 'name': 'Long-term Loans', 'type': AccountType.LIABILITY},
            {'code': '2400', 'name': 'Tax Payable', 'type': AccountType.LIABILITY},
            
            # Equity (3000-3999)
            {'code': '3000', 'name': "Owner's Equity", 'type': AccountType.EQUITY},
            {'code': '3100', 'name': 'Retained Earnings', 'type': AccountType.EQUITY},
            {'code': '3200', 'name': 'Drawings', 'type': AccountType.EQUITY},
            
            # Revenue (4000-4999)
            {'code': '4000', 'name': 'Sales Revenue', 'type': AccountType.REVENUE},
            {'code': '4100', 'name': 'Service Revenue', 'type': AccountType.REVENUE},
            {'code': '4200', 'name': 'Interest Income', 'type': AccountType.REVENUE},
            {'code': '4300', 'name': 'Other Income', 'type': AccountType.REVENUE},
            
            # Expenses (5000-5999)
            {'code': '5000', 'name': 'Cost of Goods Sold', 'type': AccountType.EXPENSE},
            {'code': '5100', 'name': 'Salaries and Wages', 'type': AccountType.EXPENSE},
            {'code': '5110', 'name': 'Employee Benefits', 'type': AccountType.EXPENSE},
            {'code': '5200', 'name': 'Rent Expense', 'type': AccountType.EXPENSE},
            {'code': '5210', 'name': 'Utilities Expense', 'type': AccountType.EXPENSE},
            {'code': '5220', 'name': 'Office Supplies', 'type': AccountType.EXPENSE},
            {'code': '5300', 'name': 'Marketing and Advertising', 'type': AccountType.EXPENSE},
            {'code': '5400', 'name': 'Insurance Expense', 'type': AccountType.EXPENSE},
            {'code': '5500', 'name': 'Depreciation Expense', 'type': AccountType.EXPENSE},
            {'code': '5600', 'name': 'Interest Expense', 'type': AccountType.EXPENSE},
            {'code': '5700', 'name': 'Professional Fees', 'type': AccountType.EXPENSE},
            {'code': '5800', 'name': 'Travel and Entertainment', 'type': AccountType.EXPENSE},
            {'code': '5900', 'name': 'Miscellaneous Expense', 'type': AccountType.EXPENSE},
        ]
        
        accounts = {}
        for acc_data in accounts_data:
            account = Account.objects.create(
                code=acc_data['code'],
                name=acc_data['name'],
                account_type=acc_data['type'],
                created_by=user
            )
            accounts[acc_data['code']] = account
        
        return accounts

    def _seed_customers(self):
        """Seed customer data"""
        customers_data = [
            {'code': 'C001', 'company': 'ABC Corporation', 'contact': 'John Smith', 'email': 'john@abc.com', 'limit': 50000},
            {'code': 'C002', 'company': 'XYZ Industries', 'contact': 'Jane Doe', 'email': 'jane@xyz.com', 'limit': 75000},
            {'code': 'C003', 'company': 'Tech Solutions Ltd', 'contact': 'Mike Johnson', 'email': 'mike@techsol.com', 'limit': 100000},
            {'code': 'C004', 'company': 'Global Trading Inc', 'contact': 'Sarah Wilson', 'email': 'sarah@global.com', 'limit': 60000},
            {'code': 'C005', 'company': 'Premier Services', 'contact': 'David Brown', 'email': 'david@premier.com', 'limit': 40000},
        ]
        
        customers = []
        for data in customers_data:
            customer = Customer.objects.create(
                customer_code=data['code'],
                company_name=data['company'],
                contact_name=data['contact'],
                email=data['email'],
                phone=f'+1-555-{random.randint(1000,9999)}',
                credit_limit=Decimal(str(data['limit'])),
                payment_terms_days=30
            )
            customers.append(customer)
        
        return customers

    def _seed_vendors(self):
        """Seed vendor data"""
        vendors_data = [
            {'code': 'V001', 'company': 'Office Supplies Co', 'contact': 'Tom Anderson', 'email': 'tom@officesupplies.com'},
            {'code': 'V002', 'company': 'Tech Equipment Ltd', 'contact': 'Lisa Chen', 'email': 'lisa@techequip.com'},
            {'code': 'V003', 'company': 'Utility Services Inc', 'contact': 'Bob Martinez', 'email': 'bob@utilityserv.com'},
            {'code': 'V004', 'company': 'Marketing Agency', 'contact': 'Emma Davis', 'email': 'emma@marketing.com'},
            {'code': 'V005', 'company': 'Legal Services LLP', 'contact': 'James Taylor', 'email': 'james@legal.com'},
        ]
        
        vendors = []
        for data in vendors_data:
            vendor = Vendor.objects.create(
                vendor_code=data['code'],
                company_name=data['company'],
                contact_name=data['contact'],
                email=data['email'],
                phone=f'+1-555-{random.randint(1000,9999)}',
                payment_terms_days=30
            )
            vendors.append(vendor)
        
        return vendors

    def _seed_invoices(self, customers, user):
        """Seed invoices and payments"""
        invoices = []
        base_date = timezone.now().date()
        
        for i, customer in enumerate(customers[:3]):  # Create 3 invoices
            invoice_date = base_date - timedelta(days=random.randint(10, 60))
            due_date = invoice_date + timedelta(days=30)
            
            invoice = Invoice.objects.create(
                invoice_number=f'INV-2025-{str(i+1).zfill(3)}',
                customer=customer,
                invoice_date=invoice_date,
                due_date=due_date,
                status=random.choice(['SENT', 'PAID', 'OVERDUE']),
                created_by=user
            )
            
            # Create invoice lines
            subtotal = Decimal('0')
            for line_num in range(1, random.randint(2, 4)):
                qty = Decimal(str(random.randint(1, 10)))
                price = Decimal(str(random.randint(100, 1000)))
                line_total = qty * price
                subtotal += line_total
                
                InvoiceLine.objects.create(
                    invoice=invoice,
                    description=f'Product/Service {line_num}',
                    quantity=qty,
                    unit_price=price,
                    line_total=line_total,
                    line_number=line_num
                )
            
            invoice.subtotal = subtotal
            invoice.tax_amount = subtotal * Decimal('0.10')  # 10% tax
            invoice.total_amount = invoice.subtotal + invoice.tax_amount
            
            if invoice.status == 'PAID':
                invoice.paid_amount = invoice.total_amount
                # Create payment
                Payment.objects.create(
                    payment_number=f'PAY-2025-{str(i+1).zfill(3)}',
                    customer=customer,
                    invoice=invoice,
                    payment_date=invoice_date + timedelta(days=15),
                    amount=invoice.total_amount,
                    payment_method='BANK_TRANSFER',
                    created_by=user
                )
            
            invoice.save()
            invoices.append(invoice)
        
        return invoices

    def _seed_bills(self, vendors, user):
        """Seed vendor bills"""
        bills = []
        base_date = timezone.now().date()
        
        for i, vendor in enumerate(vendors[:3]):
            bill_date = base_date - timedelta(days=random.randint(10, 45))
            due_date = bill_date + timedelta(days=30)
            
            subtotal = Decimal(str(random.randint(1000, 5000)))
            tax = subtotal * Decimal('0.10')
            
            bill = Bill.objects.create(
                bill_number=f'BILL-2025-{str(i+1).zfill(3)}',
                vendor=vendor,
                bill_date=bill_date,
                due_date=due_date,
                status=random.choice(['APPROVED', 'PAID']),
                subtotal=subtotal,
                tax_amount=tax,
                total_amount=subtotal + tax,
                paid_amount=subtotal + tax if random.choice([True, False]) else Decimal('0'),
                created_by=user
            )
            bills.append(bill)
        
        return bills

    def _seed_journal_entries(self, accounts, user):
        """Seed journal entries"""
        entries_data = [
            {
                'number': 'JE-2025-001',
                'date': timezone.now().date() - timedelta(days=90),
                'description': 'Opening Balances',
                'lines': [
                    {'account': '1020', 'debit': Decimal('500000.00'), 'credit': Decimal('0.00')},
                    {'account': '1400', 'debit': Decimal('150000.00'), 'credit': Decimal('0.00')},
                    {'account': '2300', 'debit': Decimal('0.00'), 'credit': Decimal('200000.00')},
                    {'account': '3000', 'debit': Decimal('0.00'), 'credit': Decimal('450000.00')},
                ]
            },
            {
                'number': 'JE-2025-002',
                'date': timezone.now().date() - timedelta(days=60),
                'description': 'Monthly Salary Payment',
                'lines': [
                    {'account': '5100', 'debit': Decimal('85000.00'), 'credit': Decimal('0.00')},
                    {'account': '1020', 'debit': Decimal('0.00'), 'credit': Decimal('85000.00')},
                ]
            },
            {
                'number': 'JE-2025-003',
                'date': timezone.now().date() - timedelta(days=30),
                'description': 'Rent Payment',
                'lines': [
                    {'account': '5200', 'debit': Decimal('15000.00'), 'credit': Decimal('0.00')},
                    {'account': '1020', 'debit': Decimal('0.00'), 'credit': Decimal('15000.00')},
                ]
            },
        ]
        
        entries = []
        for entry_data in entries_data:
            journal_entry = JournalEntry.objects.create(
                entry_number=entry_data['number'],
                entry_date=entry_data['date'],
                description=entry_data['description'],
                status=JournalEntry.Status.POSTED,
                created_by=user,
                posted_by=user,
                posted_at=timezone.now()
            )
            
            for i, line_data in enumerate(entry_data['lines'], start=1):
                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=accounts[line_data['account']],
                    debit_amount=line_data['debit'],
                    credit_amount=line_data['credit'],
                    line_number=i
                )
            
            journal_entry.calculate_totals()
            entries.append(journal_entry)
        
        return entries

    def _seed_fixed_assets(self, accounts):
        """Seed fixed assets"""
        assets_data = [
            {'code': 'FA-001', 'name': 'Dell Laptop', 'cost': 1500, 'life': 3, 'account': '1400'},
            {'code': 'FA-002', 'name': 'Office Desk', 'cost': 800, 'life': 5, 'account': '1410'},
            {'code': 'FA-003', 'name': 'Company Vehicle', 'cost': 35000, 'life': 5, 'account': '1420'},
            {'code': 'FA-004', 'name': 'Server Equipment', 'cost': 5000, 'life': 3, 'account': '1400'},
        ]
        
        assets = []
        base_date = timezone.now().date() - timedelta(days=365)
        
        for data in assets_data:
            purchase_cost = Decimal(str(data['cost']))
            asset = FixedAsset.objects.create(
                asset_code=data['code'],
                name=data['name'],
                account=accounts[data['account']],
                purchase_date=base_date,
                purchase_cost=purchase_cost,
                salvage_value=purchase_cost * Decimal('0.1'),
                useful_life_years=data['life'],
                depreciation_method=FixedAsset.DepreciationMethod.STRAIGHT_LINE,
                accumulated_depreciation=purchase_cost * Decimal('0.2'),  # 20% depreciated
                book_value=purchase_cost * Decimal('0.8')
            )
            assets.append(asset)
        
        return assets

    def _seed_expense_categories(self, accounts):
        """Seed expense categories"""
        categories_data = [
            {'name': 'Office Supplies', 'account': '5220'},
            {'name': 'Travel', 'account': '5800'},
            {'name': 'Marketing', 'account': '5300'},
            {'name': 'Professional Services', 'account': '5700'},
        ]
        
        categories = []
        for data in categories_data:
            category = ExpenseCategory.objects.create(
                name=data['name'],
                account=accounts[data['account']]
            )
            categories.append(category)
        
        return categories

    def _seed_expenses(self, categories, vendors, user):
        """Seed expenses"""
        expenses = []
        base_date = timezone.now().date()
        
        for i, category in enumerate(categories):
            expense = Expense.objects.create(
                expense_number=f'EXP-2025-{str(i+1).zfill(3)}',
                category=category,
                vendor=vendors[i % len(vendors)],
                expense_date=base_date - timedelta(days=random.randint(5, 30)),
                amount=Decimal(str(random.randint(100, 2000))),
                description=f'{category.name} expense',
                status=random.choice(['APPROVED', 'PAID']),
                created_by=user,
                approved_by=user
            )
            expenses.append(expense)
        
        return expenses

    def _seed_budgets(self, accounts, user):
        """Seed budgets"""
        budget = Budget.objects.create(
            name='FY2025 Annual Budget',
            fiscal_year=2025,
            period=Budget.Period.ANNUAL,
            start_date=timezone.now().date().replace(month=1, day=1),
            end_date=timezone.now().date().replace(month=12, day=31),
            created_by=user
        )
        
        # Create budget lines for expense accounts
        expense_accounts = [acc for acc in accounts.values() if acc.account_type == AccountType.EXPENSE]
        total_budget = Decimal('0')
        
        for account in expense_accounts[:5]:  # Budget for first 5 expense accounts
            budgeted = Decimal(str(random.randint(50000, 200000)))
            actual = budgeted * Decimal(str(random.uniform(0.5, 1.2)))
            
            BudgetLine.objects.create(
                budget=budget,
                account=account,
                budgeted_amount=budgeted,
                actual_amount=actual,
                variance=actual - budgeted
            )
            total_budget += budgeted
        
        budget.total_budget = total_budget
        budget.save()
        
        return [budget]

    def _seed_tax_rates(self):
        """Seed tax rates"""
        rates_data = [
            {'name': 'Standard VAT', 'rate': '10.00'},
            {'name': 'Reduced VAT', 'rate': '5.00'},
            {'name': 'Sales Tax', 'rate': '8.00'},
        ]
        
        rates = []
        for data in rates_data:
            rate = TaxRate.objects.create(
                name=data['name'],
                rate=Decimal(data['rate'])
            )
            rates.append(rate)
        
        return rates

    def _seed_tax_returns(self, user):
        """Seed tax returns"""
        base_date = timezone.now().date()
        returns = []
        
        for quarter in range(1, 3):  # 2 quarters
            start_date = base_date.replace(month=((quarter-1)*3)+1, day=1)
            end_date = start_date + timedelta(days=89)
            
            tax_return = TaxReturn.objects.create(
                return_number=f'TAX-2025-Q{quarter}',
                tax_period_start=start_date,
                tax_period_end=end_date,
                due_date=end_date + timedelta(days=30),
                total_tax=Decimal(str(random.randint(5000, 15000))),
                status='FILED' if quarter == 1 else 'DRAFT',
                created_by=user
            )
            returns.append(tax_return)
        
        return returns
