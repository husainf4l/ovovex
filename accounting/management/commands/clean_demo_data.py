"""
Django management command to clean all demo/placeholder data from the accounting system.
This prepares the database for production use by removing all test data while keeping
the core accounting structure intact.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.apps import apps


class Command(BaseCommand):
    help = 'Remove all demo/placeholder data from the accounting system for production'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all demo data',
        )
        parser.add_argument(
            '--keep-accounts',
            action='store_true',
            help='Keep the chart of accounts structure (only delete transactions)',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  WARNING: This will delete ALL accounting data!\n'
                    'This action cannot be undone.\n\n'
                    'To proceed, run:\n'
                    'python manage.py clean_demo_data --confirm\n'
                )
            )
            return

        self.stdout.write(self.style.WARNING('\n🧹 Starting database cleanup...\n'))

        try:
            with transaction.atomic():
                from accounting.models import Account

                # Get all models from accounting app
                accounting_models = apps.get_app_config('accounting').get_models()

                # Models to preserve (structure/configuration)
                preserve_models = set()
                if options['keep_accounts']:
                    preserve_models.add('Account')

                # Always preserve these configuration models
                preserve_models.update([
                    'ExpenseCategory',
                    'TaxRate',
                    'AIModel',
                    'AnomalyDetectionModel',
                    'DocumentCategory',
                    'InventoryCategory',
                    'PricingPlan',
                    'AccountType',  # If it exists
                    'PaymentTerm',  # If it exists
                ])

                # Count all records
                self.stdout.write('\n📊 Records to be deleted:\n')
                counts = {}
                for model in accounting_models:
                    model_name = model.__name__
                    if model_name not in preserve_models:
                        count = model.objects.count()
                        if count > 0:
                            counts[model_name] = count
                            self.stdout.write(f'  • {model_name}: {count}')

                if not counts:
                    self.stdout.write(self.style.SUCCESS('\n✅ No demo data found. Database is already clean!\n'))
                    return

                # Delete in reverse dependency order
                self.stdout.write(self.style.WARNING('\n🗑️  Deleting records...\n'))

                # Order models by dependency (child models first)
                deletion_order = [
                    'DashboardAlert',
                    'DashboardActivity',
                    'DashboardKPIMetric',
                    'DashboardWidget',
                    'ComplianceViolation',
                    'ComplianceCheck',
                    'AuditTrail',
                    'AnomalyAlert',
                    'AIPrediction',
                    'AIInsight',
                    'TaxReturn',
                    'DocumentImage',
                    'Document',
                    'InventoryTransaction',
                    'InventoryItem',
                    'PurchaseOrderLine',
                    'PurchaseOrder',
                    'BankReconciliation',
                    'BudgetLine',
                    'Budget',
                    'FixedAsset',
                    'Expense',
                    'BillLine',
                    'Bill',
                    'Payment',
                    'InvoiceLine',
                    'Invoice',
                    'JournalEntryLine',
                    'JournalEntry',
                    'Vendor',
                    'Customer',
                    'UserProfile',
                    'Notification',
                ]

                # Delete models in order
                for model_name in deletion_order:
                    try:
                        model = apps.get_model('accounting', model_name)
                        if model_name not in preserve_models:
                            deleted, _ = model.objects.all().delete()
                            if deleted > 0:
                                self.stdout.write(self.style.SUCCESS(f'  ✓ Deleted {deleted} {model_name}'))
                    except LookupError:
                        # Model doesn't exist
                        pass
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'  ⚠ Skipping {model_name}: {str(e)}'))

                # Delete any remaining models not in the list
                for model in accounting_models:
                    model_name = model.__name__
                    if model_name not in preserve_models and model_name not in deletion_order:
                        try:
                            deleted, _ = model.objects.all().delete()
                            if deleted > 0:
                                self.stdout.write(self.style.SUCCESS(f'  ✓ Deleted {deleted} {model_name}'))
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'  ⚠ Skipping {model_name}: {str(e)}'))

                # Handle Account model specially
                if options['keep_accounts']:
                    # Reset account balances to zero
                    Account = apps.get_model('accounting', 'Account')
                    for account in Account.objects.all():
                        account.balance = 0
                        account.save(update_fields=['balance'])
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Reset balances for {Account.objects.count()} accounts to zero'
                        )
                    )
                else:
                    try:
                        Account = apps.get_model('accounting', 'Account')
                        deleted, _ = Account.objects.all().delete()
                        if deleted > 0:
                            self.stdout.write(self.style.SUCCESS(f'  ✓ Deleted {deleted} Accounts'))
                        self.stdout.write(
                            self.style.WARNING(
                                '\n⚠️  Note: Chart of Accounts was deleted. '
                                'You may need to recreate your account structure.\n'
                            )
                        )
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'  ⚠ Could not delete Accounts: {str(e)}'))

                self.stdout.write(
                    self.style.SUCCESS(
                        '\n✅ Database cleanup completed successfully!\n'
                        'Your accounting system is now ready for production use.\n'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'\n❌ Error during cleanup: {str(e)}\n'
                    'All changes have been rolled back.\n'
                )
            )
            import traceback
            traceback.print_exc()
            raise
