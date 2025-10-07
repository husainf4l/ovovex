from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from accounting.models import (
    Account, BankStatement, BankReconciliation,
    ReconciliationAdjustment, FixedAsset
)
from django.contrib.auth.models import User
import random
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Seed bank reconciliation data integrated with fixed assets'

    def handle(self, *args, **options):
        self.stdout.write('Seeding bank reconciliation data...')

        # Get or create a user for audit trail
        user, created = User.objects.get_or_create(
            username='system',
            defaults={'email': 'system@ovovex.com', 'first_name': 'System'}
        )

        # Get asset-related accounts
        asset_accounts = Account.objects.filter(account_type='ASSET')
        if not asset_accounts.exists():
            self.stdout.write(self.style.WARNING('No asset accounts found. Please run seed_all_modules first.'))
            return

        # Get fixed assets
        fixed_assets = list(FixedAsset.objects.filter(is_active=True))
        if not fixed_assets:
            self.stdout.write(self.style.WARNING('No fixed assets found. Please run seed_fixed_assets first.'))
            return

        # Create bank statements for fixed asset transactions
        self.create_asset_bank_statements(user, asset_accounts, fixed_assets)

        # Create reconciliation records
        self.create_reconciliations(user, asset_accounts)

        self.stdout.write(self.style.SUCCESS('Successfully seeded bank reconciliation data'))

    def create_asset_bank_statements(self, user, asset_accounts, fixed_assets):
        """Create bank statements related to fixed asset transactions"""
        statements_created = 0

        # Get a sample of asset accounts for bank statements
        bank_accounts = asset_accounts.filter(name__icontains='bank')[:3]  # Get up to 3 bank accounts
        if not bank_accounts:
            # If no bank accounts, use first few asset accounts
            bank_accounts = asset_accounts[:3]

        for account in bank_accounts:
            # Create statements for the last 6 months
            base_date = timezone.now().date() - timedelta(days=180)

            for i in range(24):  # 2 statements per month for 12 months
                statement_date = base_date + timedelta(days=i * 15 + random.randint(0, 14))

                # Create different types of asset-related transactions
                transaction_type = random.choice([
                    'asset_purchase', 'maintenance', 'disposal', 'insurance', 'depreciation_adjustment'
                ])

                if transaction_type == 'asset_purchase':
                    # Asset purchase transaction
                    asset = random.choice(fixed_assets)
                    amount = asset.purchase_cost
                    description = f"Purchase of {asset.name} ({asset.asset_code})"
                    stmt_type = 'WITHDRAWAL'
                    asset_ref = asset
                    asset_tx_type = 'Purchase'

                elif transaction_type == 'maintenance':
                    # Maintenance payment
                    asset = random.choice(fixed_assets)
                    amount = Decimal(str(random.uniform(100, 2000)))
                    description = f"Maintenance for {asset.name} ({asset.asset_code})"
                    stmt_type = 'WITHDRAWAL'
                    asset_ref = asset
                    asset_tx_type = 'Maintenance'

                elif transaction_type == 'disposal':
                    # Asset disposal proceeds
                    asset = random.choice(fixed_assets)
                    amount = Decimal(str(random.uniform(500, 5000)))
                    description = f"Proceeds from disposal of {asset.name} ({asset.asset_code})"
                    stmt_type = 'DEPOSIT'
                    asset_ref = asset
                    asset_tx_type = 'Disposal'

                elif transaction_type == 'insurance':
                    # Insurance premium
                    asset = random.choice(fixed_assets)
                    amount = asset.insurance_premium or Decimal(str(random.uniform(200, 1000)))
                    description = f"Insurance premium for {asset.name} ({asset.asset_code})"
                    stmt_type = 'WITHDRAWAL'
                    asset_ref = asset
                    asset_tx_type = 'Insurance'

                else:  # depreciation_adjustment
                    # Depreciation adjustment or correction
                    asset = random.choice(fixed_assets)
                    amount = Decimal(str(random.uniform(50, 500)))
                    description = f"Depreciation adjustment for {asset.name} ({asset.asset_code})"
                    stmt_type = random.choice(['DEPOSIT', 'WITHDRAWAL'])
                    asset_ref = asset
                    asset_tx_type = 'Depreciation Adjustment'

                # Create transaction ID
                transaction_id = f"BS-{account.code}-{statement_date.strftime('%Y%m%d')}-{i:03d}"

                # Create bank statement
                BankStatement.objects.create(
                    account=account,
                    statement_date=statement_date,
                    description=description,
                    amount=amount,
                    statement_type=stmt_type,
                    transaction_id=transaction_id,
                    fixed_asset=asset_ref,
                    asset_transaction_type=asset_tx_type,
                    is_reconciled=random.choice([True, False, False])  # 1/3 chance of being reconciled
                )

                statements_created += 1

        self.stdout.write(f'Created {statements_created} bank statements for fixed assets')

    def create_reconciliations(self, user, asset_accounts):
        """Create bank reconciliation records"""
        reconciliations_created = 0

        # Get bank accounts
        bank_accounts = asset_accounts.filter(name__icontains='bank')[:3]
        if not bank_accounts:
            bank_accounts = asset_accounts[:3]

        for account in bank_accounts:
            # Create reconciliations for the last 6 months
            base_date = timezone.now().date() - timedelta(days=180)

            for i in range(6):
                reconciliation_date = base_date + timedelta(days=i * 30 + 15)

                # Calculate balances (simplified)
                book_balance = Decimal(str(random.uniform(50000, 200000)))
                statement_balance = book_balance + Decimal(str(random.uniform(-5000, 5000)))
                adjusted_balance = statement_balance  # Assume adjustments bring them into balance

                # Create reconciliation
                reconciliation = BankReconciliation.objects.create(
                    account=account,
                    reconciliation_date=reconciliation_date,
                    statement_date=reconciliation_date,
                    book_balance=book_balance,
                    statement_balance=statement_balance,
                    adjusted_book_balance=adjusted_balance,
                    status=random.choice(['COMPLETED', 'IN_PROGRESS', 'COMPLETED']),
                    notes=f"Monthly reconciliation for {account.name}",
                    created_by=user,
                    completed_by=user if random.choice([True, False]) else None,
                    completed_at=reconciliation_date if random.choice([True, False]) else None
                )

                # Create some adjustments
                self.create_adjustments_for_reconciliation(reconciliation, user)

                reconciliations_created += 1

        self.stdout.write(f'Created {reconciliations_created} bank reconciliations')

    def create_adjustments_for_reconciliation(self, reconciliation, user):
        """Create reconciliation adjustments"""
        adjustments_created = 0
        num_adjustments = random.randint(0, 3)  # 0-3 adjustments per reconciliation

        adjustment_types = [
            ('DEPOSIT_IN_TRANSIT', 'Deposit in transit'),
            ('OUTSTANDING_CHECK', 'Outstanding check'),
            ('BANK_FEE', 'Bank service fee'),
            ('INTEREST_EARNED', 'Interest earned'),
            ('BANK_ERROR', 'Bank error correction'),
            ('BOOK_ERROR', 'Book error correction')
        ]

        for _ in range(num_adjustments):
            adj_type, description = random.choice(adjustment_types)
            amount = Decimal(str(random.uniform(10, 1000)))
            is_addition = random.choice([True, False])

            ReconciliationAdjustment.objects.create(
                reconciliation=reconciliation,
                adjustment_type=adj_type,
                description=f"{description} - {reconciliation.account.name}",
                amount=amount,
                is_addition=is_addition,
                created_by=user
            )

            adjustments_created += 1

        if adjustments_created > 0:
            self.stdout.write(f'Created {adjustments_created} adjustments for reconciliation {reconciliation}')