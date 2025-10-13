from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounting.models import *
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed database with production-ready initial data (no demo/fake data)'

    def handle(self, *args, **options):
        self.stdout.write('Starting production database seeding...')

        # Create default admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@ovovex.com',
                password='changeme123',  # User should change this immediately
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('✅ Created admin user (username: admin, password: changeme123)'))
            self.stdout.write(self.style.WARNING('⚠️  Please change the admin password immediately!'))

        admin_user = User.objects.get(username='admin')

        # Seed essential production data
        self.seed_chart_of_accounts(admin_user)
        self.seed_expense_categories(admin_user)
        self.seed_inventory_categories(admin_user)
        self.seed_document_categories(admin_user)
        self.seed_tax_rates(admin_user)

        self.stdout.write(self.style.SUCCESS('✅ Production database seeding completed successfully!'))
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('Next steps:'))
        self.stdout.write('1. Run migrations: python manage.py migrate')
        self.stdout.write('2. Change admin password: python manage.py changepassword admin')
        self.stdout.write('3. Start server: python manage.py runserver')

    def seed_chart_of_accounts(self, user):
        """Seed standard chart of accounts"""
        accounts_data = [
            # ASSETS (1000-1999)
            {'code': '1000', 'name': 'Cash and Cash Equivalents', 'type': 'ASSET', 'description': 'Cash on hand and in banks'},
            {'code': '1010', 'name': 'Petty Cash', 'type': 'ASSET', 'description': 'Cash for small expenses'},
            {'code': '1100', 'name': 'Accounts Receivable', 'type': 'ASSET', 'description': 'Amounts owed by customers'},
            {'code': '1110', 'name': 'Allowance for Doubtful Accounts', 'type': 'ASSET', 'description': 'Estimated uncollectible receivables'},
            {'code': '1200', 'name': 'Inventory', 'type': 'ASSET', 'description': 'Goods for sale'},
            {'code': '1300', 'name': 'Prepaid Expenses', 'type': 'ASSET', 'description': 'Expenses paid in advance'},
            {'code': '1310', 'name': 'Prepaid Insurance', 'type': 'ASSET', 'description': 'Insurance premiums paid in advance'},
            {'code': '1400', 'name': 'Property, Plant and Equipment', 'type': 'ASSET', 'description': 'Fixed assets'},
            {'code': '1410', 'name': 'Land', 'type': 'ASSET', 'description': 'Land owned'},
            {'code': '1420', 'name': 'Buildings', 'type': 'ASSET', 'description': 'Buildings owned'},
            {'code': '1430', 'name': 'Equipment', 'type': 'ASSET', 'description': 'Equipment owned'},
            {'code': '1440', 'name': 'Vehicles', 'type': 'ASSET', 'description': 'Vehicles owned'},
            {'code': '1450', 'name': 'Furniture and Fixtures', 'type': 'ASSET', 'description': 'Office furniture'},
            {'code': '1500', 'name': 'Accumulated Depreciation', 'type': 'ASSET', 'description': 'Cumulative depreciation on assets'},
            {'code': '1600', 'name': 'Intangible Assets', 'type': 'ASSET', 'description': 'Non-physical assets'},
            {'code': '1610', 'name': 'Goodwill', 'type': 'ASSET', 'description': 'Goodwill from acquisitions'},

            # LIABILITIES (2000-2999)
            {'code': '2000', 'name': 'Accounts Payable', 'type': 'LIABILITY', 'description': 'Amounts owed to suppliers'},
            {'code': '2100', 'name': 'Accrued Expenses', 'type': 'LIABILITY', 'description': 'Expenses incurred but not yet paid'},
            {'code': '2110', 'name': 'Salaries Payable', 'type': 'LIABILITY', 'description': 'Unpaid employee salaries'},
            {'code': '2120', 'name': 'Interest Payable', 'type': 'LIABILITY', 'description': 'Accrued interest on loans'},
            {'code': '2130', 'name': 'Taxes Payable', 'type': 'LIABILITY', 'description': 'Taxes owed but not yet paid'},
            {'code': '2200', 'name': 'Unearned Revenue', 'type': 'LIABILITY', 'description': 'Advance payments from customers'},
            {'code': '2300', 'name': 'Loans Payable - Current', 'type': 'LIABILITY', 'description': 'Short-term loans'},
            {'code': '2400', 'name': 'Loans Payable - Long Term', 'type': 'LIABILITY', 'description': 'Long-term loans'},

            # EQUITY (3000-3999)
            {'code': '3000', 'name': 'Common Stock', 'type': 'EQUITY', 'description': 'Owner equity - common stock'},
            {'code': '3100', 'name': 'Retained Earnings', 'type': 'EQUITY', 'description': 'Cumulative net income'},
            {'code': '3200', 'name': 'Dividends', 'type': 'EQUITY', 'description': 'Distributions to owners'},

            # REVENUE (4000-4999)
            {'code': '4000', 'name': 'Sales Revenue', 'type': 'REVENUE', 'description': 'Revenue from product sales'},
            {'code': '4100', 'name': 'Service Revenue', 'type': 'REVENUE', 'description': 'Revenue from services'},
            {'code': '4200', 'name': 'Interest Income', 'type': 'REVENUE', 'description': 'Interest earned'},
            {'code': '4300', 'name': 'Other Income', 'type': 'REVENUE', 'description': 'Miscellaneous income'},

            # EXPENSES (5000-5999)
            {'code': '5000', 'name': 'Cost of Goods Sold', 'type': 'EXPENSE', 'description': 'Direct costs of products sold'},
            {'code': '5100', 'name': 'Salaries and Wages', 'type': 'EXPENSE', 'description': 'Employee compensation'},
            {'code': '5110', 'name': 'Payroll Taxes', 'type': 'EXPENSE', 'description': 'Employer payroll taxes'},
            {'code': '5120', 'name': 'Employee Benefits', 'type': 'EXPENSE', 'description': 'Health insurance, retirement, etc.'},
            {'code': '5200', 'name': 'Rent Expense', 'type': 'EXPENSE', 'description': 'Office and facility rent'},
            {'code': '5210', 'name': 'Utilities', 'type': 'EXPENSE', 'description': 'Electricity, water, gas, internet'},
            {'code': '5300', 'name': 'Marketing and Advertising', 'type': 'EXPENSE', 'description': 'Marketing costs'},
            {'code': '5400', 'name': 'Office Supplies', 'type': 'EXPENSE', 'description': 'Stationery and supplies'},
            {'code': '5500', 'name': 'Insurance Expense', 'type': 'EXPENSE', 'description': 'Business insurance'},
            {'code': '5600', 'name': 'Professional Fees', 'type': 'EXPENSE', 'description': 'Legal, accounting, consulting'},
            {'code': '5700', 'name': 'Depreciation Expense', 'type': 'EXPENSE', 'description': 'Asset depreciation'},
            {'code': '5800', 'name': 'Interest Expense', 'type': 'EXPENSE', 'description': 'Interest on loans'},
            {'code': '5900', 'name': 'Travel and Entertainment', 'type': 'EXPENSE', 'description': 'Business travel costs'},
            {'code': '5910', 'name': 'Repairs and Maintenance', 'type': 'EXPENSE', 'description': 'Equipment and facility repairs'},
            {'code': '5920', 'name': 'Bank Charges', 'type': 'EXPENSE', 'description': 'Banking fees'},
            {'code': '5930', 'name': 'Bad Debt Expense', 'type': 'EXPENSE', 'description': 'Uncollectible accounts'},
        ]

        created_count = 0
        for account_data in accounts_data:
            account, created = Account.objects.get_or_create(
                code=account_data['code'],
                defaults={
                    'name': account_data['name'],
                    'account_type': account_data['type'],
                    'description': account_data.get('description', ''),
                    'is_active': True,
                    'created_by': user
                }
            )
            if created:
                created_count += 1

        self.stdout.write(f'✅ Created {created_count} accounts (Chart of Accounts)')

    def seed_expense_categories(self, user):
        """Seed standard expense categories"""
        categories_data = [
            {'name': 'Office Supplies', 'code': '5400', 'description': 'Stationery, pens, paper, etc.'},
            {'name': 'Travel & Entertainment', 'code': '5900', 'description': 'Business travel and meals'},
            {'name': 'Professional Services', 'code': '5600', 'description': 'Legal, accounting, consulting'},
            {'name': 'Marketing & Advertising', 'code': '5300', 'description': 'Marketing campaigns and ads'},
            {'name': 'Utilities', 'code': '5210', 'description': 'Electricity, water, internet'},
            {'name': 'Insurance', 'code': '5500', 'description': 'Business insurance premiums'},
            {'name': 'Maintenance & Repairs', 'code': '5910', 'description': 'Equipment and facility repairs'},
            {'name': 'Rent', 'code': '5200', 'description': 'Office and facility rent'},
        ]

        created_count = 0
        for category_data in categories_data:
            account = Account.objects.filter(code=category_data['code']).first()
            if account:
                category, created = ExpenseCategory.objects.get_or_create(
                    name=category_data['name'],
                    defaults={
                        'account': account,
                        'description': category_data['description'],
                        'is_active': True
                    }
                )
                if created:
                    created_count += 1

        self.stdout.write(f'✅ Created {created_count} expense categories')

    def seed_inventory_categories(self, user):
        """Seed standard inventory categories"""
        categories_data = [
            {'name': 'Raw Materials', 'description': 'Materials used in manufacturing'},
            {'name': 'Work in Progress', 'description': 'Partially completed goods'},
            {'name': 'Finished Goods', 'description': 'Completed products ready for sale'},
            {'name': 'Office Supplies', 'description': 'Supplies for office use'},
            {'name': 'IT Equipment', 'description': 'Computers and technology'},
            {'name': 'Furniture', 'description': 'Office furniture'},
            {'name': 'Maintenance Parts', 'description': 'Parts for equipment maintenance'},
        ]

        created_count = 0
        for category_data in categories_data:
            category, created = InventoryCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1

        self.stdout.write(f'✅ Created {created_count} inventory categories')

    def seed_document_categories(self, user):
        """Seed standard document categories"""
        categories_data = [
            {'name': 'Financial Statements', 'color': '#e74c3c', 'description': 'Balance sheet, P&L, cash flow'},
            {'name': 'Tax Documents', 'color': '#3498db', 'description': 'Tax returns and related documents'},
            {'name': 'Contracts', 'color': '#2ecc71', 'description': 'Business contracts and agreements'},
            {'name': 'Invoices', 'color': '#f39c12', 'description': 'Customer invoices'},
            {'name': 'Bills', 'color': '#9b59b6', 'description': 'Vendor bills and receipts'},
            {'name': 'Legal Documents', 'color': '#1abc9c', 'description': 'Legal filings and notices'},
            {'name': 'Bank Statements', 'color': '#34495e', 'description': 'Bank account statements'},
            {'name': 'Correspondence', 'color': '#95a5a6', 'description': 'Business correspondence'},
        ]

        created_count = 0
        for category_data in categories_data:
            category, created = DocumentCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'color_code': category_data['color'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1

        self.stdout.write(f'✅ Created {created_count} document categories')

    def seed_tax_rates(self, user):
        """Seed standard tax rates (customize for your jurisdiction)"""
        tax_rates_data = [
            {
                'name': 'Standard Sales Tax',
                'type': 'SALES',
                'rate': Decimal('10.0'),
                'jurisdiction': 'Default',
                'description': 'Standard sales tax rate'
            },
            {
                'name': 'Federal Income Tax',
                'type': 'INCOME',
                'rate': Decimal('21.0'),
                'jurisdiction': 'Federal',
                'description': 'Federal corporate income tax'
            },
            {
                'name': 'State Income Tax',
                'type': 'INCOME',
                'rate': Decimal('5.0'),
                'jurisdiction': 'State',
                'description': 'State corporate income tax'
            },
            {
                'name': 'Property Tax',
                'type': 'PROPERTY',
                'rate': Decimal('1.2'),
                'jurisdiction': 'Local',
                'description': 'Annual property tax rate'
            },
        ]

        created_count = 0
        for tax_data in tax_rates_data:
            tax_rate, created = TaxRate.objects.get_or_create(
                name=tax_data['name'],
                tax_type=tax_data['type'],
                defaults={
                    'rate': tax_data['rate'],
                    'jurisdiction': tax_data['jurisdiction'],
                    'description': tax_data['description'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1

        self.stdout.write(f'✅ Created {created_count} tax rates')
