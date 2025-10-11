"""
Comprehensive database seeding script for Ovovex Accounting System
"""
import random
from decimal import Decimal
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounting.models import *


class Command(BaseCommand):
    help = 'Seed database with comprehensive sample data'

    def handle(self, *args, **options):
        self.stdout.write('Starting comprehensive database seeding...')

        # Create additional users
        self.create_users()

        # Create chart of accounts
        self.create_accounts()

        # Create customers and vendors
        self.create_customers_and_vendors()

        # Create inventory
        self.create_inventory()

        # Create invoices and payments
        self.create_invoices_and_payments()

        # Create bills and expenses
        self.create_bills_and_expenses()

        # Create fixed assets
        self.create_fixed_assets()

        # Create budgets
        self.create_budgets()

        # Create journal entries
        self.create_journal_entries()

        # Create purchase orders
        self.create_purchase_orders()

        # Create tax data
        self.create_tax_data()

        # Create dashboard data
        self.create_dashboard_data()

        # Create notifications
        self.create_notifications()

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))

    def create_users(self):
        """Create additional sample users"""
        self.stdout.write('Creating users...')

        users_data = [
            {'username': 'manager', 'email': 'manager@company.com', 'first_name': 'John', 'last_name': 'Manager'},
            {'username': 'accountant', 'email': 'accounting@company.com', 'first_name': 'Sarah', 'last_name': 'Accountant'},
            {'username': 'sales', 'email': 'sales@company.com', 'first_name': 'Mike', 'last_name': 'Sales'},
            {'username': 'purchasing', 'email': 'purchasing@company.com', 'first_name': 'Lisa', 'last_name': 'Purchasing'},
        ]

        for user_data in users_data:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password='password123',
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                # Create user profile if it doesn't exist
                UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'phone': f'555-{random.randint(100,999)}-{random.randint(1000,9999)}',
                        'company': 'Ovovex Corp',
                        'job_title': user_data['last_name']
                    }
                )
                self.stdout.write(f'Created user: {user.username}')

    def create_accounts(self):
        """Create comprehensive chart of accounts"""
        self.stdout.write('Creating chart of accounts...')

        accounts_data = [
            # Assets
            {'code': '1000', 'name': 'Cash', 'type': 'ASSET'},
            {'code': '1100', 'name': 'Accounts Receivable', 'type': 'ASSET'},
            {'code': '1200', 'name': 'Inventory', 'type': 'ASSET'},
            {'code': '1300', 'name': 'Prepaid Expenses', 'type': 'ASSET'},
            {'code': '1400', 'name': 'Fixed Assets', 'type': 'ASSET'},
            {'code': '1500', 'name': 'Accumulated Depreciation', 'type': 'ASSET'},

            # Liabilities
            {'code': '2000', 'name': 'Accounts Payable', 'type': 'LIABILITY'},
            {'code': '2100', 'name': 'Loans Payable', 'type': 'LIABILITY'},
            {'code': '2200', 'name': 'Taxes Payable', 'type': 'LIABILITY'},

            # Equity
            {'code': '3000', 'name': 'Common Stock', 'type': 'EQUITY'},
            {'code': '3100', 'name': 'Retained Earnings', 'type': 'EQUITY'},

            # Revenue
            {'code': '4000', 'name': 'Sales Revenue', 'type': 'REVENUE'},
            {'code': '4100', 'name': 'Service Revenue', 'type': 'REVENUE'},
            {'code': '4200', 'name': 'Interest Income', 'type': 'REVENUE'},

            # Expenses
            {'code': '5000', 'name': 'Cost of Goods Sold', 'type': 'EXPENSE'},
            {'code': '5100', 'name': 'Salaries Expense', 'type': 'EXPENSE'},
            {'code': '5200', 'name': 'Rent Expense', 'type': 'EXPENSE'},
            {'code': '5300', 'name': 'Utilities Expense', 'type': 'EXPENSE'},
            {'code': '5400', 'name': 'Office Supplies', 'type': 'EXPENSE'},
            {'code': '5500', 'name': 'Marketing Expense', 'type': 'EXPENSE'},
            {'code': '5600', 'name': 'Depreciation Expense', 'type': 'EXPENSE'},
            {'code': '5700', 'name': 'Insurance Expense', 'type': 'EXPENSE'},
        ]

        admin_user = User.objects.get(username='admin')

        for account_data in accounts_data:
            if not Account.objects.filter(code=account_data['code']).exists():
                Account.objects.create(
                    code=account_data['code'],
                    name=account_data['name'],
                    account_type=account_data['type'],
                    created_by=admin_user
                )

        self.stdout.write(f'Created {len(accounts_data)} accounts')

    def create_customers_and_vendors(self):
        """Create sample customers and vendors"""
        self.stdout.write('Creating customers and vendors...')

        customers_data = [
            {'code': 'CUST001', 'name': 'Tech Solutions Inc', 'contact': 'John Smith', 'email': 'john@techsolutions.com'},
            {'code': 'CUST002', 'name': 'Global Manufacturing', 'contact': 'Sarah Johnson', 'email': 'sarah@globalmfg.com'},
            {'code': 'CUST003', 'name': 'Retail Chain Corp', 'contact': 'Mike Davis', 'email': 'mike@retailchain.com'},
            {'code': 'CUST004', 'name': 'Healthcare Systems', 'contact': 'Lisa Brown', 'email': 'lisa@healthcare.com'},
            {'code': 'CUST005', 'name': 'Education District', 'contact': 'Tom Wilson', 'email': 'tom@education.edu'},
        ]

        vendors_data = [
            {'code': 'VEND001', 'name': 'Office Supplies Co', 'contact': 'Jane Doe', 'email': 'jane@officesupplies.com'},
            {'code': 'VEND002', 'name': 'Tech Hardware Inc', 'contact': 'Bob Wilson', 'email': 'bob@techhardware.com'},
            {'code': 'VEND003', 'name': 'Professional Services LLC', 'contact': 'Alice Green', 'email': 'alice@proservices.com'},
            {'code': 'VEND004', 'name': 'Manufacturing Supplies', 'contact': 'Charlie Brown', 'email': 'charlie@mfg.com'},
            {'code': 'VEND005', 'name': 'Software Solutions', 'contact': 'Diana Prince', 'email': 'diana@software.com'},
        ]

        admin_user = User.objects.get(username='admin')

        for customer_data in customers_data:
            if not Customer.objects.filter(customer_code=customer_data['code']).exists():
                Customer.objects.create(
                    customer_code=customer_data['code'],
                    company_name=customer_data['name'],
                    contact_name=customer_data['contact'],
                    email=customer_data['email'],
                    phone=f'555-{random.randint(100,999)}-{random.randint(1000,9999)}',
                    address=f'{random.randint(100,9999)} Main St, City, State 12345',
                    credit_limit=Decimal(str(random.randint(5000, 50000))),
                    payment_terms_days=random.choice([15, 30, 45, 60])
                )

        for vendor_data in vendors_data:
            if not Vendor.objects.filter(vendor_code=vendor_data['code']).exists():
                Vendor.objects.create(
                    vendor_code=vendor_data['code'],
                    company_name=vendor_data['name'],
                    contact_name=vendor_data['contact'],
                    email=vendor_data['email'],
                    phone=f'555-{random.randint(100,999)}-{random.randint(1000,9999)}',
                    address=f'{random.randint(100,9999)} Business Ave, City, State 12345',
                    payment_terms_days=random.choice([15, 30, 45, 60])
                )

        self.stdout.write(f'Created {len(customers_data)} customers and {len(vendors_data)} vendors')

    def create_inventory(self):
        """Create inventory categories and items"""
        self.stdout.write('Creating inventory...')

        categories_data = [
            'Office Supplies', 'Computer Equipment', 'Furniture', 'Software', 'Tools', 'Raw Materials'
        ]

        for cat_name in categories_data:
            InventoryCategory.objects.get_or_create(
                name=cat_name,
                defaults={'description': f'{cat_name} category'}
            )

        vendors = list(Vendor.objects.all())
        categories = list(InventoryCategory.objects.all())
        admin_user = User.objects.get(username='admin')

        inventory_data = [
            {'code': 'ITEM001', 'name': 'Printer Paper', 'cost': 5.99, 'price': 8.99, 'stock': 500},
            {'code': 'ITEM002', 'name': 'Office Chair', 'cost': 89.99, 'price': 149.99, 'stock': 25},
            {'code': 'ITEM003', 'name': 'Laptop Computer', 'cost': 799.99, 'price': 1199.99, 'stock': 10},
            {'code': 'ITEM004', 'name': 'Wireless Mouse', 'cost': 12.99, 'price': 24.99, 'stock': 50},
            {'code': 'ITEM005', 'name': 'Monitor 24"', 'cost': 149.99, 'price': 249.99, 'stock': 15},
            {'code': 'ITEM006', 'name': 'Software License', 'cost': 299.99, 'price': 399.99, 'stock': 20},
            {'code': 'ITEM007', 'name': 'Desk Lamp', 'cost': 19.99, 'price': 34.99, 'stock': 30},
            {'code': 'ITEM008', 'name': 'Network Cable', 'cost': 4.99, 'price': 9.99, 'stock': 100},
            {'code': 'ITEM009', 'name': 'Whiteboard Markers', 'cost': 2.49, 'price': 4.99, 'stock': 200},
            {'code': 'ITEM010', 'name': 'Conference Table', 'cost': 399.99, 'price': 699.99, 'stock': 5},
        ]

        for item_data in inventory_data:
            if not InventoryItem.objects.filter(item_code=item_data['code']).exists():
                category = random.choice(categories) if categories else None
                vendor = random.choice(vendors) if vendors else None

                item = InventoryItem.objects.create(
                    item_code=item_data['code'],
                    name=item_data['name'],
                    description=f'High quality {item_data["name"]}',
                    category=category,
                    current_stock=Decimal(str(item_data['stock'])),
                    minimum_stock=Decimal(str(random.randint(5, 20))),
                    reorder_point=Decimal(str(random.randint(10, 30))),
                    unit_cost=Decimal(str(item_data['cost'])),
                    selling_price=Decimal(str(item_data['price'])),
                    primary_vendor=vendor,
                    location='Warehouse A',
                    created_by=admin_user
                )

                # Create some inventory transactions
                for _ in range(random.randint(1, 3)):
                    days_ago = random.randint(1, 90)
                    transaction_date = datetime.now() - timedelta(days=days_ago)

                    InventoryTransaction.objects.create(
                        item=item,
                        transaction_type='RECEIPT',
                        quantity=Decimal(str(random.randint(10, 50))),
                        unit_cost=item.unit_cost,
                        reference_number=f'PO-{random.randint(1000, 9999)}',
                        notes='Initial stock receipt',
                        created_by=admin_user
                    )

        self.stdout.write(f'Created inventory categories and {len(inventory_data)} items')

    def create_invoices_and_payments(self):
        """Create sample invoices and payments"""
        self.stdout.write('Creating invoices and payments...')

        customers = list(Customer.objects.all())
        admin_user = User.objects.get(username='admin')

        for i in range(20):
            customer = random.choice(customers)
            invoice_date = datetime.now() - timedelta(days=random.randint(1, 90))
            due_date = invoice_date + timedelta(days=customer.payment_terms_days)

            # Create invoice - use higher numbers to avoid conflicts
            invoice_number = f'INV-{2000+i:04d}'
            if Invoice.objects.filter(invoice_number=invoice_number).exists():
                continue  # Skip if already exists
                
            invoice = Invoice.objects.create(
                invoice_number=invoice_number,
                customer=customer,
                invoice_date=invoice_date,
                due_date=due_date,
                subtotal=Decimal(str(random.randint(500, 5000))),
                tax_amount=Decimal('0.00'),  # Simplified
                total_amount=Decimal(str(random.randint(500, 5000))),
                status=random.choice(['DRAFT', 'SENT', 'PAID', 'OVERDUE']),
                created_by=admin_user
            )

            # Create invoice lines
            for j in range(random.randint(1, 3)):
                InvoiceLine.objects.create(
                    invoice=invoice,
                    description=f'Service/Item {j+1}',
                    quantity=Decimal(str(random.randint(1, 10))),
                    unit_price=Decimal(str(random.randint(50, 500))),
                    line_total=Decimal(str(random.randint(50, 5000))),
                    line_number=j+1
                )

            # Create payment if invoice is paid
            if invoice.status == 'PAID':
                payment_number = f'PAY-{2000+i:04d}'
                if not Payment.objects.filter(payment_number=payment_number).exists():
                    Payment.objects.create(
                        payment_number=payment_number,
                        customer=customer,
                        invoice=invoice,
                        payment_date=invoice_date + timedelta(days=random.randint(1, 30)),
                        amount=invoice.total_amount,
                        payment_method='BANK_TRANSFER',
                        reference=f'Check #{random.randint(1000, 9999)}',
                        created_by=admin_user
                    )

        self.stdout.write('Created 20 sample invoices with payments')

    def create_bills_and_expenses(self):
        """Create sample bills and expenses"""
        self.stdout.write('Creating bills and expenses...')

        vendors = list(Vendor.objects.all())
        admin_user = User.objects.get(username='admin')

        # Create expense categories
        expense_categories = [
            'Office Supplies', 'Travel', 'Meals', 'Utilities', 'Marketing', 'Professional Services'
        ]

        for cat_name in expense_categories:
            ExpenseCategory.objects.get_or_create(
                name=cat_name,
                defaults={
                    'account': Account.objects.filter(account_type='EXPENSE').first(),
                    'description': f'{cat_name} expenses'
                }
            )

        categories = list(ExpenseCategory.objects.all())

        for i in range(15):
            vendor = random.choice(vendors)
            category = random.choice(categories)
            expense_date = datetime.now() - timedelta(days=random.randint(1, 60))

            expense_number = f'EXP-{2000+i:04d}'
            if Expense.objects.filter(expense_number=expense_number).exists():
                continue  # Skip if already exists
                
            Expense.objects.create(
                expense_number=expense_number,
                category=category,
                vendor=vendor,
                expense_date=expense_date,
                amount=Decimal(str(random.randint(50, 2000))),
                description=f'{category.name} expense',
                status=random.choice(['DRAFT', 'SUBMITTED', 'APPROVED', 'PAID']),
                created_by=admin_user
            )

        self.stdout.write('Created expense categories and 15 sample expenses')

    def create_fixed_assets(self):
        """Create sample fixed assets"""
        self.stdout.write('Creating fixed assets...')

        admin_user = User.objects.get(username='admin')
        asset_account = Account.objects.filter(code='1400').first()

        assets_data = [
            {'code': 'ASSET001', 'name': 'Company Vehicle', 'cost': 25000, 'category': 'VEHICLES'},
            {'code': 'ASSET002', 'name': 'Office Building', 'cost': 500000, 'category': 'BUILDINGS'},
            {'code': 'ASSET003', 'name': 'Computer Server', 'cost': 5000, 'category': 'COMPUTER_EQUIPMENT'},
            {'code': 'ASSET004', 'name': 'Office Furniture', 'cost': 8000, 'category': 'FURNITURE'},
            {'code': 'ASSET005', 'name': 'Manufacturing Equipment', 'cost': 75000, 'category': 'MACHINERY'},
        ]

        for asset_data in assets_data:
            if not FixedAsset.objects.filter(asset_code=asset_data['code']).exists():
                purchase_date = datetime.now() - timedelta(days=random.randint(30, 365))

                asset = FixedAsset.objects.create(
                    asset_code=asset_data['code'],
                    name=asset_data['name'],
                    description=f'Company {asset_data["name"]}',
                    category=asset_data['category'],
                    account=asset_account,
                    purchase_date=purchase_date,
                    purchase_cost=Decimal(str(asset_data['cost'])),
                    salvage_value=Decimal(str(asset_data['cost'] * 0.1)),  # 10% salvage
                    useful_life_years=random.randint(3, 10),
                    depreciation_method='STRAIGHT_LINE',
                    location='Main Office',
                    book_value=Decimal(str(asset_data['cost'])),  # Initial book value = cost
                    created_by=admin_user
                )
                
                # Calculate book value
                asset.book_value = asset.purchase_cost - asset.accumulated_depreciation
                asset.save()

        self.stdout.write(f'Created {len(assets_data)} fixed assets')

    def create_budgets(self):
        """Create sample budgets"""
        self.stdout.write('Creating budgets...')

        admin_user = User.objects.get(username='admin')

        # Create budget for current year
        current_year = datetime.now().year
        start_date = datetime(current_year, 1, 1).date()
        end_date = datetime(current_year, 12, 31).date()

        budget = Budget.objects.create(
            name=f'FY{current_year} Operating Budget',
            fiscal_year=current_year,
            period='ANNUAL',
            start_date=start_date,
            end_date=end_date,
            total_budget=Decimal('500000.00'),
            created_by=admin_user
        )

        # Create budget lines for expense accounts
        expense_accounts = Account.objects.filter(account_type='EXPENSE')
        for account in expense_accounts:
            BudgetLine.objects.create(
                budget=budget,
                account=account,
                budgeted_amount=Decimal(str(random.randint(5000, 50000))),
                actual_amount=Decimal(str(random.randint(3000, 45000)))
            )

        self.stdout.write('Created annual budget with expense line items')

    def create_journal_entries(self):
        """Create sample journal entries"""
        self.stdout.write('Creating journal entries...')

        admin_user = User.objects.get(username='admin')
        accounts = list(Account.objects.all())

        for i in range(10):
            entry_date = datetime.now() - timedelta(days=random.randint(1, 60))
            entry_number = f'JE-{3000+i:04d}'

            # Create balanced journal entry
            debit_amount = Decimal(str(random.randint(1000, 10000)))
            credit_amount = debit_amount  # Keep balanced

            # Get random accounts
            debit_account = random.choice([acc for acc in accounts if acc.account_type in ['ASSET', 'EXPENSE']])
            credit_account = random.choice([acc for acc in accounts if acc.account_type in ['LIABILITY', 'EQUITY', 'REVENUE']])

            # Create journal entry
            journal_entry = JournalEntry.objects.create(
                entry_number=entry_number,
                entry_date=entry_date,
                description=f'Sample journal entry {i+1}',
                status='POSTED',
                created_by=admin_user,
                posted_by=admin_user,
                posted_at=entry_date
            )

            # Create lines
            JournalEntryLine.objects.create(
                journal_entry=journal_entry,
                account=debit_account,
                description=f'Debit to {debit_account.name}',
                debit_amount=debit_amount,
                credit_amount=Decimal('0.00'),
                line_number=1
            )

            JournalEntryLine.objects.create(
                journal_entry=journal_entry,
                account=credit_account,
                description=f'Credit to {credit_account.name}',
                debit_amount=Decimal('0.00'),
                credit_amount=credit_amount,
                line_number=2
            )

        self.stdout.write('Created 10 sample journal entries')

    def create_purchase_orders(self):
        """Create sample purchase orders"""
        self.stdout.write('Creating purchase orders...')

        vendors = list(Vendor.objects.all())
        items = list(InventoryItem.objects.all())
        admin_user = User.objects.get(username='admin')

        for i in range(8):
            vendor = random.choice(vendors)
            order_date = datetime.now() - timedelta(days=random.randint(1, 45))

            po = PurchaseOrder.objects.create(
                po_number=f'PO-{3000+i:04d}',
                vendor=vendor,
                order_date=order_date,
                required_date=order_date + timedelta(days=random.randint(7, 30)),
                status=random.choice(['DRAFT', 'APPROVED', 'ORDERED', 'RECEIVED']),
                subtotal=Decimal('0.00'),
                created_by=admin_user
            )

            # Add line items
            subtotal = Decimal('0.00')
            for j in range(random.randint(1, 3)):
                item = random.choice(items)
                quantity = Decimal(str(random.randint(1, 20)))
                unit_price = item.unit_cost

                PurchaseOrderLine.objects.create(
                    purchase_order=po,
                    item_description=item.name,
                    inventory_item=item,
                    quantity_ordered=quantity,
                    unit_price=unit_price,
                    line_total=quantity * unit_price
                )

                subtotal += quantity * unit_price

            # Update PO totals
            po.subtotal = subtotal
            po.total_amount = subtotal
            po.save()

        self.stdout.write('Created 8 sample purchase orders')

    def create_tax_data(self):
        """Create sample tax data"""
        self.stdout.write('Creating tax data...')

        admin_user = User.objects.get(username='admin')

        # Create tax rates
        tax_rates = [
            {'name': 'Sales Tax - General', 'type': 'SALES', 'rate': 8.25, 'jurisdiction': 'State'},
            {'name': 'Income Tax - Corporate', 'type': 'INCOME', 'rate': 21.0, 'jurisdiction': 'Federal'},
            {'name': 'Property Tax', 'type': 'PROPERTY', 'rate': 1.2, 'jurisdiction': 'County'},
        ]

        for tax_data in tax_rates:
            TaxRate.objects.get_or_create(
                name=tax_data['name'],
                defaults={
                    'tax_type': tax_data['type'],
                    'rate': Decimal(str(tax_data['rate'])),
                    'jurisdiction': tax_data['jurisdiction'],
                    'effective_date': datetime(2024, 1, 1).date()
                }
            )

        # Create tax return
        TaxReturn.objects.create(
            return_number='TAX-2024-001',
            return_type='FORM_1120',
            tax_period_start=datetime(2024, 1, 1).date(),
            tax_period_end=datetime(2024, 12, 31).date(),
            filing_date=datetime.now().date(),
            due_date=datetime(2025, 3, 15).date(),  # Tax due date
            jurisdiction='Federal',
            gross_income=Decimal('500000.00'),
            deductions=Decimal('150000.00'),
            taxable_income=Decimal('350000.00'),
            tax_rate=Decimal('21.00'),
            total_tax=Decimal('73500.00'),
            paid_amount=Decimal('73500.00'),
            status='PAID',
            created_by=admin_user,
            filed_by=admin_user
        )

        self.stdout.write('Created tax rates and sample tax return')

    def create_dashboard_data(self):
        """Create dashboard KPI metrics and widgets"""
        self.stdout.write('Creating dashboard data...')

        admin_user = User.objects.get(username='admin')

        # Create KPI metrics
        kpi_data = [
            {'name': 'total_revenue', 'display': 'Total Revenue', 'value': 450000, 'prev': 420000, 'type': 'CURRENCY'},
            {'name': 'total_expenses', 'display': 'Total Expenses', 'value': 320000, 'prev': 310000, 'type': 'CURRENCY'},
            {'name': 'net_profit', 'display': 'Net Profit', 'value': 130000, 'prev': 110000, 'type': 'CURRENCY'},
            {'name': 'accounts_receivable', 'display': 'A/R Balance', 'value': 45000, 'prev': 52000, 'type': 'CURRENCY'},
            {'name': 'inventory_value', 'display': 'Inventory Value', 'value': 125000, 'prev': 118000, 'type': 'CURRENCY'},
            {'name': 'cash_balance', 'display': 'Cash Balance', 'value': 85000, 'prev': 78000, 'type': 'CURRENCY'},
        ]

        for kpi in kpi_data:
            metric, created = DashboardKPIMetric.objects.get_or_create(
                name=kpi['name'],
                defaults={
                    'display_name': kpi['display'],
                    'metric_type': kpi['type'],
                    'current_value': Decimal(str(kpi['value'])),
                    'previous_value': Decimal(str(kpi['prev'])),
                    'is_active': True
                }
            )
            if created:
                metric.calculate_trend()

        # Create dashboard widgets
        widgets_data = [
            {'title': 'Revenue Overview', 'type': 'CHART', 'chart_type': 'LINE', 'pos_x': 0, 'pos_y': 0},
            {'title': 'Expense Breakdown', 'type': 'CHART', 'chart_type': 'PIE', 'pos_x': 1, 'pos_y': 0},
            {'title': 'Cash Flow', 'type': 'CHART', 'chart_type': 'BAR', 'pos_x': 0, 'pos_y': 1},
            {'title': 'Key Metrics', 'type': 'SUMMARY', 'pos_x': 1, 'pos_y': 1},
        ]

        for widget_data in widgets_data:
            DashboardWidget.objects.get_or_create(
                title=widget_data['title'],
                defaults={
                    'widget_type': widget_data['type'],
                    'chart_type': widget_data.get('chart_type'),
                    'position_x': widget_data['pos_x'],
                    'position_y': widget_data['pos_y'],
                    'width': 1,
                    'height': 1,
                    'created_by': admin_user
                }
            )

        self.stdout.write('Created dashboard KPI metrics and widgets')

    def create_notifications(self):
        """Create sample notifications"""
        self.stdout.write('Creating notifications...')

        users = list(User.objects.all())

        notification_data = [
            {'title': 'Invoice Overdue', 'message': 'Invoice INV-1005 is 15 days overdue', 'type': 'WARNING'},
            {'title': 'Low Inventory Alert', 'message': 'Printer Paper stock is below reorder point', 'type': 'WARNING'},
            {'title': 'Payment Received', 'message': 'Payment of $2,500 received from Tech Solutions Inc', 'type': 'SUCCESS'},
            {'title': 'Budget Alert', 'message': 'Marketing expenses are 85% of budgeted amount', 'type': 'INFO'},
            {'title': 'Tax Filing Due', 'message': 'Quarterly tax return due in 7 days', 'type': 'CRITICAL'},
        ]

        for notif_data in notification_data:
            for user in users[:2]:  # Send to first 2 users
                Notification.objects.create(
                    user=user,
                    title=notif_data['title'],
                    message=notif_data['message'],
                    notification_type=notif_data['type'],
                    action_url='/dashboard'
                )

        self.stdout.write('Created sample notifications')