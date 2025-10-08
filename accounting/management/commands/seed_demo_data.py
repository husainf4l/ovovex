from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounting.models import *
from decimal import Decimal
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Seed database with comprehensive demo data for all dashboard modules'

    def handle(self, *args, **options):
        self.stdout.write('Starting database seeding...')

        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@ovovex.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write('Created admin user')

        admin_user = User.objects.get(username='admin')

        # Seed data
        self.seed_accounts(admin_user)
        self.seed_customers(admin_user)
        self.seed_vendors(admin_user)
        self.seed_expense_categories(admin_user)
        self.seed_inventory_categories(admin_user)
        self.seed_document_categories(admin_user)
        self.seed_tax_rates(admin_user)
        self.seed_ai_insights(admin_user)
        self.seed_ai_predictions(admin_user)
        self.seed_ai_models(admin_user)
        self.seed_anomaly_alerts(admin_user)
        self.seed_anomaly_detection_models(admin_user)
        self.seed_inventory_items(admin_user)
        self.seed_inventory_transactions(admin_user)
        self.seed_documents(admin_user)
        self.seed_purchase_orders(admin_user)
        self.seed_audit_trail(admin_user)
        self.seed_compliance_checks(admin_user)
        self.seed_compliance_violations(admin_user)

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))

    def seed_accounts(self, user):
        """Seed chart of accounts"""
        accounts_data = [
            # Assets
            {'code': '1000', 'name': 'Cash and Cash Equivalents', 'type': 'ASSET'},
            {'code': '1100', 'name': 'Accounts Receivable', 'type': 'ASSET'},
            {'code': '1200', 'name': 'Inventory', 'type': 'ASSET'},
            {'code': '1300', 'name': 'Prepaid Expenses', 'type': 'ASSET'},
            {'code': '1400', 'name': 'Property, Plant and Equipment', 'type': 'ASSET'},
            {'code': '1500', 'name': 'Accumulated Depreciation', 'type': 'ASSET'},

            # Liabilities
            {'code': '2000', 'name': 'Accounts Payable', 'type': 'LIABILITY'},
            {'code': '2100', 'name': 'Accrued Expenses', 'type': 'LIABILITY'},
            {'code': '2200', 'name': 'Loans Payable', 'type': 'LIABILITY'},

            # Equity
            {'code': '3000', 'name': 'Common Stock', 'type': 'EQUITY'},
            {'code': '3100', 'name': 'Retained Earnings', 'type': 'EQUITY'},

            # Revenue
            {'code': '4000', 'name': 'Sales Revenue', 'type': 'REVENUE'},
            {'code': '4100', 'name': 'Service Revenue', 'type': 'REVENUE'},

            # Expenses
            {'code': '5000', 'name': 'Cost of Goods Sold', 'type': 'EXPENSE'},
            {'code': '5100', 'name': 'Operating Expenses', 'type': 'EXPENSE'},
            {'code': '5200', 'name': 'Marketing Expenses', 'type': 'EXPENSE'},
            {'code': '5300', 'name': 'Administrative Expenses', 'type': 'EXPENSE'},
            {'code': '5400', 'name': 'Depreciation Expense', 'type': 'EXPENSE'},
        ]

        for account_data in accounts_data:
            Account.objects.get_or_create(
                code=account_data['code'],
                defaults={
                    'name': account_data['name'],
                    'account_type': account_data['type'],
                    'created_by': user
                }
            )

        self.stdout.write(f'Created {len(accounts_data)} accounts')

    def seed_customers(self, user):
        """Seed customer data"""
        customers_data = [
            {'code': 'CUST001', 'name': 'TechCorp Solutions', 'contact': 'John Smith', 'email': 'john@techcorp.com'},
            {'code': 'CUST002', 'name': 'Global Industries Ltd', 'contact': 'Sarah Johnson', 'email': 'sarah@globalind.com'},
            {'code': 'CUST003', 'name': 'Metro Services Inc', 'contact': 'Mike Davis', 'email': 'mike@metroservices.com'},
            {'code': 'CUST004', 'name': 'Innovate Systems', 'contact': 'Lisa Brown', 'email': 'lisa@innovatesys.com'},
            {'code': 'CUST005', 'name': 'Prime Logistics', 'contact': 'David Wilson', 'email': 'david@primelog.com'},
        ]

        for customer_data in customers_data:
            Customer.objects.get_or_create(
                customer_code=customer_data['code'],
                defaults={
                    'company_name': customer_data['name'],
                    'contact_name': customer_data['contact'],
                    'email': customer_data['email'],
                    'phone': f'+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}',
                    'address': f'{random.randint(100,9999)} Business St, City, State {random.randint(10000,99999)}',
                    'credit_limit': Decimal(str(random.randint(50000, 500000))),
                    'payment_terms_days': random.choice([15, 30, 45, 60]),
                }
            )

        self.stdout.write(f'Created {len(customers_data)} customers')

    def seed_vendors(self, user):
        """Seed vendor data"""
        vendors_data = [
            {'code': 'VEND001', 'name': 'Office Supplies Plus', 'contact': 'Robert Chen', 'email': 'robert@officesup.com'},
            {'code': 'VEND002', 'name': 'Tech Equipment Corp', 'contact': 'Maria Garcia', 'email': 'maria@techequip.com'},
            {'code': 'VEND003', 'name': 'Professional Services LLC', 'contact': 'James Taylor', 'email': 'james@profserv.com'},
            {'code': 'VEND004', 'name': 'Manufacturing Parts Inc', 'contact': 'Anna Lee', 'email': 'anna@manufparts.com'},
            {'code': 'VEND005', 'name': 'Logistics Solutions', 'contact': 'Tom Anderson', 'email': 'tom@logisticsol.com'},
        ]

        for vendor_data in vendors_data:
            Vendor.objects.get_or_create(
                vendor_code=vendor_data['code'],
                defaults={
                    'company_name': vendor_data['name'],
                    'contact_name': vendor_data['contact'],
                    'email': vendor_data['email'],
                    'phone': f'+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}',
                    'address': f'{random.randint(100,9999)} Vendor Ave, City, State {random.randint(10000,99999)}',
                    'payment_terms_days': random.choice([15, 30, 45, 60]),
                }
            )

        self.stdout.write(f'Created {len(vendors_data)} vendors')

    def seed_expense_categories(self, user):
        """Seed expense categories"""
        categories_data = [
            {'name': 'Office Supplies', 'account_code': '5100'},
            {'name': 'Travel & Entertainment', 'account_code': '5200'},
            {'name': 'Professional Services', 'account_code': '5300'},
            {'name': 'Marketing & Advertising', 'account_code': '5200'},
            {'name': 'Utilities', 'account_code': '5100'},
            {'name': 'Insurance', 'account_code': '5300'},
            {'name': 'Maintenance & Repairs', 'account_code': '5400'},
        ]

        for category_data in categories_data:
            account = Account.objects.get(code=category_data['account_code'])
            ExpenseCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'account': account,
                    'description': f'Expenses related to {category_data["name"].lower()}'
                }
            )

        self.stdout.write(f'Created {len(categories_data)} expense categories')

    def seed_inventory_categories(self, user):
        """Seed inventory categories"""
        categories_data = [
            {'name': 'Office Supplies'},
            {'name': 'IT Equipment'},
            {'name': 'Furniture'},
            {'name': 'Raw Materials'},
            {'name': 'Finished Goods'},
            {'name': 'Maintenance Parts'},
        ]

        for category_data in categories_data:
            InventoryCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={'description': f'Inventory items for {category_data["name"].lower()}'}
            )

        self.stdout.write(f'Created {len(categories_data)} inventory categories')

    def seed_document_categories(self, user):
        """Seed document categories"""
        categories_data = [
            {'name': 'Financial Statements', 'color': '#e74c3c'},
            {'name': 'Tax Documents', 'color': '#3498db'},
            {'name': 'Contracts', 'color': '#2ecc71'},
            {'name': 'Invoices', 'color': '#f39c12'},
            {'name': 'Legal Documents', 'color': '#9b59b6'},
            {'name': 'Correspondence', 'color': '#1abc9c'},
        ]

        for category_data in categories_data:
            DocumentCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': f'{category_data["name"]} documents',
                    'color_code': category_data['color']
                }
            )

        self.stdout.write(f'Created {len(categories_data)} document categories')

    def seed_tax_rates(self, user):
        """Seed tax rates"""
        tax_rates_data = [
            {'name': 'Federal Income Tax', 'type': 'INCOME', 'rate': 21.0, 'jurisdiction': 'Federal'},
            {'name': 'State Sales Tax', 'type': 'SALES', 'rate': 6.0, 'jurisdiction': 'State'},
            {'name': 'Property Tax', 'type': 'PROPERTY', 'rate': 1.2, 'jurisdiction': 'Local'},
        ]

        for tax_data in tax_rates_data:
            TaxRate.objects.get_or_create(
                name=tax_data['name'],
                defaults={
                    'tax_type': tax_data['type'],
                    'rate': Decimal(str(tax_data['rate'])),
                    'jurisdiction': tax_data['jurisdiction'],
                    'description': f'{tax_data["name"]} rate'
                }
            )

        self.stdout.write(f'Created {len(tax_rates_data)} tax rates')

    def seed_ai_insights(self, user):
        """Seed AI insights"""
        insights_data = [
            {
                'id': 'INS001',
                'title': 'Revenue Optimization Opportunity',
                'description': 'Analysis shows 15% potential revenue increase through pricing optimization',
                'type': 'REVENUE_OPTIMIZATION',
                'priority': 'HIGH',
                'confidence': 85.0,
                'impact': 150000.0,
                'savings': 22500.0
            },
            {
                'id': 'INS002',
                'title': 'Cost Reduction Alert',
                'description': 'Vendor contract renegotiation could save $12,000 annually',
                'type': 'COST_REDUCTION',
                'priority': 'MEDIUM',
                'confidence': 78.0,
                'impact': 12000.0,
                'savings': 12000.0
            },
            {
                'id': 'INS003',
                'title': 'Cash Flow Improvement',
                'description': 'Optimizing payment terms could improve cash flow by $45,000',
                'type': 'CASH_FLOW_IMPROVEMENT',
                'priority': 'HIGH',
                'confidence': 92.0,
                'impact': 45000.0,
                'savings': 4500.0
            },
            {
                'id': 'INS004',
                'title': 'Expense Anomaly Detected',
                'description': 'Travel expenses 40% above normal - requires review',
                'type': 'RISK_WARNING',
                'priority': 'MEDIUM',
                'confidence': 95.0,
                'impact': 8000.0
            },
            {
                'id': 'INS005',
                'title': 'Seasonal Trend Analysis',
                'description': 'Q4 revenue typically 25% higher - prepare for increased demand',
                'type': 'TREND_ANALYSIS',
                'priority': 'LOW',
                'confidence': 88.0,
                'impact': 75000.0
            },
        ]

        for insight_data in insights_data:
            AIInsight.objects.get_or_create(
                insight_id=insight_data['id'],
                defaults={
                    'title': insight_data['title'],
                    'description': insight_data['description'],
                    'insight_type': insight_data['type'],
                    'priority': insight_data['priority'],
                    'confidence_score': Decimal(str(insight_data['confidence'])),
                    'impact_score': Decimal(str(insight_data['impact'])),
                    'potential_savings': Decimal(str(insight_data.get('savings', 0))),
                    'ai_model_version': '1.2.3'
                }
            )

        self.stdout.write(f'Created {len(insights_data)} AI insights')

    def seed_ai_predictions(self, user):
        """Seed AI predictions"""
        predictions_data = [
            {
                'id': 'PRED001',
                'title': 'Q4 Revenue Forecast',
                'type': 'REVENUE_FORECAST',
                'value': 285000.0,
                'lower': 265000.0,
                'upper': 305000.0,
                'date': datetime.now() + timedelta(days=90),
                'period': 3
            },
            {
                'id': 'PRED002',
                'title': 'Monthly Expense Forecast',
                'type': 'EXPENSE_FORECAST',
                'value': 45000.0,
                'lower': 42000.0,
                'upper': 48000.0,
                'date': datetime.now() + timedelta(days=30),
                'period': 1
            },
            {
                'id': 'PRED003',
                'title': 'Cash Flow Projection',
                'type': 'CASH_FLOW_FORECAST',
                'value': 125000.0,
                'lower': 115000.0,
                'upper': 135000.0,
                'date': datetime.now() + timedelta(days=60),
                'period': 2
            },
        ]

        for pred_data in predictions_data:
            AIPrediction.objects.get_or_create(
                prediction_id=pred_data['id'],
                defaults={
                    'title': pred_data['title'],
                    'prediction_type': pred_data['type'],
                    'predicted_value': Decimal(str(pred_data['value'])),
                    'confidence_interval_lower': Decimal(str(pred_data['lower'])),
                    'confidence_interval_upper': Decimal(str(pred_data['upper'])),
                    'prediction_date': pred_data['date'],
                    'forecast_period_months': pred_data['period'],
                    'ai_model_version': '1.2.3'
                }
            )

        self.stdout.write(f'Created {len(predictions_data)} AI predictions')

    def seed_ai_models(self, user):
        """Seed AI models"""
        models_data = [
            {
                'name': 'RevenuePredictor',
                'type': 'FORECASTING',
                'version': '2.1.0',
                'accuracy': 87.5,
                'total_pred': 150,
                'successful_pred': 131
            },
            {
                'name': 'AnomalyDetector',
                'type': 'ANOMALY_DETECTION',
                'version': '1.8.3',
                'accuracy': 94.2,
                'total_pred': 200,
                'successful_pred': 188
            },
            {
                'name': 'ExpenseAnalyzer',
                'type': 'CLASSIFICATION',
                'version': '3.0.1',
                'accuracy': 91.8,
                'total_pred': 300,
                'successful_pred': 275
            },
        ]

        for model_data in models_data:
            AIModel.objects.get_or_create(
                model_name=model_data['name'],
                defaults={
                    'model_type': model_data['type'],
                    'version': model_data['version'],
                    'accuracy_score': Decimal(str(model_data['accuracy'])),
                    'total_predictions': model_data['total_pred'],
                    'successful_predictions': model_data['successful_pred'],
                    'description': f'{model_data["name"]} AI model for {model_data["type"].lower()}'
                }
            )

        self.stdout.write(f'Created {len(models_data)} AI models')

    def seed_anomaly_alerts(self, user):
        """Seed anomaly alerts"""
        alerts_data = [
            {
                'id': 'ANOM001',
                'title': 'Unusual Transaction Amount',
                'description': 'Transaction of $50,000 exceeds normal range by 300%',
                'type': 'TRANSACTION_AMOUNT',
                'severity': 'HIGH',
                'status': 'INVESTIGATING',
                'value': 50000.0,
                'expected': 12500.0,
                'deviation': 300.0,
                'confidence': 98.5
            },
            {
                'id': 'ANOM002',
                'title': 'Vendor Payment Frequency Spike',
                'description': 'Vendor payment frequency increased by 250% this month',
                'type': 'FREQUENCY_SPIKE',
                'severity': 'MEDIUM',
                'status': 'DETECTED',
                'value': 25.0,
                'expected': 7.0,
                'deviation': 250.0,
                'confidence': 89.2
            },
            {
                'id': 'ANOM003',
                'title': 'Account Balance Anomaly',
                'description': 'Cash account balance dropped 40% below expected level',
                'type': 'ACCOUNT_BALANCE',
                'severity': 'CRITICAL',
                'status': 'RESOLVED',
                'value': 25000.0,
                'expected': 41666.67,
                'deviation': -40.0,
                'confidence': 95.8
            },
        ]

        for alert_data in alerts_data:
            AnomalyAlert.objects.get_or_create(
                alert_id=alert_data['id'],
                defaults={
                    'title': alert_data['title'],
                    'description': alert_data['description'],
                    'anomaly_type': alert_data['type'],
                    'severity': alert_data['severity'],
                    'status': alert_data['status'],
                    'detected_value': Decimal(str(alert_data['value'])),
                    'expected_value': Decimal(str(alert_data.get('expected', 0))),
                    'deviation_percentage': Decimal(str(alert_data.get('deviation', 0))),
                    'confidence_score': Decimal(str(alert_data['confidence'])),
                    'ai_model_version': '1.8.3'
                }
            )

        self.stdout.write(f'Created {len(alerts_data)} anomaly alerts')

    def seed_anomaly_detection_models(self, user):
        """Seed anomaly detection models"""
        models_data = [
            {
                'name': 'StatisticalAnomalyDetector',
                'type': 'STATISTICAL',
                'version': '2.0.1',
                'total_alerts': 47,
                'true_pos': 42,
                'false_pos': 5,
                'sensitivity': 0.89,
                'specificity': 0.94
            },
            {
                'name': 'MachineLearningAnomalyDetector',
                'type': 'MACHINE_LEARNING',
                'version': '1.5.2',
                'total_alerts': 38,
                'true_pos': 35,
                'false_pos': 3,
                'sensitivity': 0.92,
                'specificity': 0.96
            },
        ]

        for model_data in models_data:
            AnomalyDetectionModel.objects.get_or_create(
                model_name=model_data['name'],
                defaults={
                    'model_type': model_data['type'],
                    'version': model_data['version'],
                    'total_alerts_generated': model_data['total_alerts'],
                    'true_positives': model_data['true_pos'],
                    'false_positives': model_data['false_pos'],
                    'sensitivity_threshold': Decimal(str(model_data['sensitivity'])),
                    'specificity_threshold': Decimal(str(model_data['specificity']))
                }
            )

        self.stdout.write(f'Created {len(models_data)} anomaly detection models')

    def seed_inventory_items(self, user):
        """Seed inventory items"""
        categories = list(InventoryCategory.objects.all())
        vendors = list(Vendor.objects.all())

        items_data = [
            {
                'code': 'ITEM001',
                'name': 'Office Chair',
                'category': categories[2] if categories else None,
                'stock': 25,
                'min_stock': 5,
                'cost': 150.00,
                'price': 299.99,
                'vendor': vendors[0] if vendors else None
            },
            {
                'code': 'ITEM002',
                'name': 'Laptop Computer',
                'category': categories[1] if len(categories) > 1 else None,
                'stock': 12,
                'min_stock': 3,
                'cost': 800.00,
                'price': 1299.99,
                'vendor': vendors[1] if len(vendors) > 1 else None
            },
            {
                'code': 'ITEM003',
                'name': 'Printer Paper (Case)',
                'category': categories[0] if categories else None,
                'stock': 45,
                'min_stock': 10,
                'cost': 25.00,
                'price': 45.00,
                'vendor': vendors[0] if vendors else None
            },
            {
                'code': 'ITEM004',
                'name': 'Network Cable (100ft)',
                'category': categories[1] if len(categories) > 1 else None,
                'stock': 8,
                'min_stock': 5,
                'cost': 35.00,
                'price': 65.00,
                'vendor': vendors[1] if len(vendors) > 1 else None
            },
            {
                'code': 'ITEM005',
                'name': 'Desk Organizer',
                'category': categories[0] if categories else None,
                'stock': 3,
                'min_stock': 8,
                'cost': 12.00,
                'price': 24.99,
                'vendor': vendors[0] if vendors else None
            },
        ]

        for item_data in items_data:
            InventoryItem.objects.get_or_create(
                item_code=item_data['code'],
                defaults={
                    'name': item_data['name'],
                    'category': item_data['category'],
                    'current_stock': Decimal(str(item_data['stock'])),
                    'minimum_stock': Decimal(str(item_data['min_stock'])),
                    'unit_cost': Decimal(str(item_data['cost'])),
                    'selling_price': Decimal(str(item_data['price'])),
                    'primary_vendor': item_data['vendor'],
                    'created_by': user
                }
            )

        self.stdout.write(f'Created {len(items_data)} inventory items')

    def seed_inventory_transactions(self, user):
        """Seed inventory transactions"""
        items = list(InventoryItem.objects.all())

        if not items:
            return

        transactions_data = [
            {'item': items[0], 'type': 'RECEIPT', 'quantity': 10, 'cost': 150.00},
            {'item': items[1], 'type': 'RECEIPT', 'quantity': 5, 'cost': 800.00},
            {'item': items[2], 'type': 'ISSUE', 'quantity': -15, 'cost': 25.00},
            {'item': items[3], 'type': 'RECEIPT', 'quantity': 20, 'cost': 35.00},
            {'item': items[4], 'type': 'ADJUSTMENT', 'quantity': -2, 'cost': 12.00},
        ]

        for trans_data in transactions_data:
            InventoryTransaction.objects.create(
                item=trans_data['item'],
                transaction_type=trans_data['type'],
                quantity=Decimal(str(trans_data['quantity'])),
                unit_cost=Decimal(str(trans_data['cost'])),
                created_by=user,
                notes=f'{trans_data["type"]} transaction for {trans_data["item"].name}'
            )

        self.stdout.write(f'Created {len(transactions_data)} inventory transactions')

    def seed_documents(self, user):
        """Seed documents"""
        categories = list(DocumentCategory.objects.all())
        customers = list(Customer.objects.all())
        vendors = list(Vendor.objects.all())

        documents_data = [
            {
                'id': 'DOC001',
                'title': 'Q3 Financial Statement',
                'type': 'STATEMENT',
                'category': categories[0] if categories else None,
                'file_name': 'q3_financial_statement.pdf',
                'file_size': 2457600,
                'mime_type': 'application/pdf'
            },
            {
                'id': 'DOC002',
                'title': 'Tax Return 2024',
                'type': 'TAX_DOCUMENT',
                'category': categories[1] if len(categories) > 1 else None,
                'file_name': 'tax_return_2024.pdf',
                'file_size': 1843200,
                'mime_type': 'application/pdf'
            },
            {
                'id': 'DOC003',
                'title': 'Service Agreement - TechCorp',
                'type': 'CONTRACT',
                'category': categories[2] if len(categories) > 2 else None,
                'customer': customers[0] if customers else None,
                'file_name': 'service_agreement_techcorp.pdf',
                'file_size': 1536000,
                'mime_type': 'application/pdf'
            },
            {
                'id': 'DOC004',
                'title': 'Invoice INV-2024-001',
                'type': 'INVOICE',
                'category': categories[3] if len(categories) > 3 else None,
                'customer': customers[0] if customers else None,
                'file_name': 'invoice_2024_001.pdf',
                'file_size': 512000,
                'mime_type': 'application/pdf'
            },
            {
                'id': 'DOC005',
                'title': 'Legal Notice - Compliance',
                'type': 'LEGAL_DOCUMENT',
                'category': categories[4] if len(categories) > 4 else None,
                'file_name': 'legal_notice_compliance.pdf',
                'file_size': 768000,
                'mime_type': 'application/pdf'
            },
        ]

        for doc_data in documents_data:
            Document.objects.get_or_create(
                document_id=doc_data['id'],
                defaults={
                    'title': doc_data['title'],
                    'description': f'{doc_data["title"]} document',
                    'document_type': doc_data['type'],
                    'category': doc_data['category'],
                    'file_name': doc_data['file_name'],
                    'file_path': f'documents/2024/10/{doc_data["file_name"]}',
                    'file_size': doc_data['file_size'],
                    'mime_type': doc_data['mime_type'],
                    'related_customer': doc_data.get('customer'),
                    'uploaded_by': user
                }
            )

        self.stdout.write(f'Created {len(documents_data)} documents')

    def seed_purchase_orders(self, user):
        """Seed purchase orders"""
        vendors = list(Vendor.objects.all())
        items = list(InventoryItem.objects.all())

        if not vendors:
            return

        pos_data = [
            {
                'number': 'PO2024001',
                'vendor': vendors[0],
                'status': 'APPROVED',
                'subtotal': 1500.00,
                'tax': 90.00,
                'total': 1590.00,
                'lines': [
                    {'desc': 'Office Chairs', 'qty': 10, 'price': 150.00, 'item': items[0] if items else None}
                ]
            },
            {
                'number': 'PO2024002',
                'vendor': vendors[1] if len(vendors) > 1 else vendors[0],
                'status': 'ORDERED',
                'subtotal': 4000.00,
                'tax': 240.00,
                'total': 4240.00,
                'lines': [
                    {'desc': 'Laptop Computers', 'qty': 5, 'price': 800.00, 'item': items[1] if len(items) > 1 else None}
                ]
            },
            {
                'number': 'PO2024003',
                'vendor': vendors[0],
                'status': 'RECEIVED',
                'subtotal': 500.00,
                'tax': 30.00,
                'total': 530.00,
                'lines': [
                    {'desc': 'Printer Paper', 'qty': 20, 'price': 25.00, 'item': items[2] if len(items) > 2 else None}
                ]
            },
        ]

        for po_data in pos_data:
            po, created = PurchaseOrder.objects.get_or_create(
                po_number=po_data['number'],
                defaults={
                    'vendor': po_data['vendor'],
                    'order_date': datetime.now().date(),
                    'status': po_data['status'],
                    'subtotal': Decimal(str(po_data['subtotal'])),
                    'tax_amount': Decimal(str(po_data['tax'])),
                    'total_amount': Decimal(str(po_data['total'])),
                    'created_by': user
                }
            )

            if created:
                for line_data in po_data['lines']:
                    PurchaseOrderLine.objects.create(
                        purchase_order=po,
                        item_description=line_data['desc'],
                        inventory_item=line_data['item'],
                        quantity_ordered=Decimal(str(line_data['qty'])),
                        unit_price=Decimal(str(line_data['price'])),
                        line_total=Decimal(str(line_data['qty'] * line_data['price']))
                    )

        self.stdout.write(f'Created {len(pos_data)} purchase orders')

    def seed_audit_trail(self, user):
        """Seed audit trail entries"""
        audit_entries = [
            {
                'user': user,
                'action': 'CREATE',
                'entity': 'INVOICE',
                'entity_id': 'INV001',
                'entity_name': 'Invoice for TechCorp',
                'changes': {'amount': 5000.00, 'customer': 'TechCorp Solutions'}
            },
            {
                'user': user,
                'action': 'UPDATE',
                'entity': 'ACCOUNT',
                'entity_id': '1000',
                'entity_name': 'Cash Account',
                'changes': {'balance': 25000.00}
            },
            {
                'user': user,
                'action': 'LOGIN',
                'entity': 'USER',
                'entity_id': str(user.id),
                'entity_name': user.username,
                'changes': {}
            },
        ]

        for entry_data in audit_entries:
            AuditTrail.objects.create(
                user=entry_data['user'],
                action_type=entry_data['action'],
                entity_type=entry_data['entity'],
                entity_id=entry_data['entity_id'],
                entity_name=entry_data['entity_name'],
                changes_description=str(entry_data['changes']),
                success=True
            )

        self.stdout.write(f'Created {len(audit_entries)} audit trail entries')

    def seed_compliance_checks(self, user):
        """Seed compliance checks"""
        checks_data = [
            {
                'id': 'COMP001',
                'title': 'SOX Section 404 Compliance',
                'description': 'Internal controls over financial reporting',
                'type': 'SOX',
                'status': 'COMPLIANT',
                'due_date': datetime.now() + timedelta(days=90)
            },
            {
                'id': 'COMP002',
                'title': 'IFRS 15 Revenue Recognition',
                'description': 'Revenue from contracts with customers',
                'type': 'IFRS',
                'status': 'IN_PROGRESS',
                'due_date': datetime.now() + timedelta(days=30)
            },
            {
                'id': 'COMP003',
                'title': 'GDPR Data Privacy Compliance',
                'description': 'Personal data protection and privacy rights',
                'type': 'DATA_PRIVACY',
                'status': 'COMPLIANT',
                'due_date': datetime.now() + timedelta(days=180)
            },
        ]

        for check_data in checks_data:
            ComplianceCheck.objects.get_or_create(
                check_id=check_data['id'],
                defaults={
                    'title': check_data['title'],
                    'description': check_data['description'],
                    'compliance_type': check_data['type'],
                    'status': check_data['status'],
                    'due_date': check_data['due_date'],
                    'created_by': user
                }
            )

        self.stdout.write(f'Created {len(checks_data)} compliance checks')

    def seed_compliance_violations(self, user):
        """Seed compliance violations"""
        violations_data = [
            {
                'id': 'VIOL001',
                'title': 'Late Financial Reporting',
                'description': 'Q3 financial statements filed 5 days after deadline',
                'severity': 'MINOR',
                'status': 'REMEDIATED'
            },
            {
                'id': 'VIOL002',
                'title': 'Data Access Without Authorization',
                'description': 'Unauthorized access to customer financial data',
                'severity': 'MAJOR',
                'status': 'INVESTIGATING'
            },
        ]

        for viol_data in violations_data:
            ComplianceViolation.objects.get_or_create(
                violation_id=viol_data['id'],
                defaults={
                    'title': viol_data['title'],
                    'description': viol_data['description'],
                    'severity': viol_data['severity'],
                    'status': viol_data['status'],
                    'reported_by': user
                }
            )

        self.stdout.write(f'Created {len(violations_data)} compliance violations')