from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounting.models import FixedAsset, AssetTaxInfo, TaxRate
from django.db import models
from decimal import Decimal
from datetime import datetime
import random

class Command(BaseCommand):
    help = 'Seeds tax-related data for the Tax Center Module'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('Starting Tax Data Seeding'))
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
            self.stdout.write(self.style.SUCCESS('✓ Created admin user'))

        # Seed tax rates
        self.stdout.write('\nSeeding tax rates...')
        tax_rates = self._seed_tax_rates(user)

        # Seed asset tax information
        self.stdout.write('\nSeeding asset tax information...')
        tax_infos = self._seed_asset_tax_info(user)

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Tax data seeding completed successfully!'))
        self.stdout.write(self.style.SUCCESS('='*60))

        # Show summary
        self._show_summary(tax_rates, tax_infos)

    def _seed_tax_rates(self, user):
        """Seed comprehensive tax rates"""
        tax_rates_data = [
            # Income Tax Rates
            {'name': 'Corporate Income Tax Rate', 'tax_type': 'INCOME', 'rate': 21.00, 'jurisdiction': 'Federal', 'description': 'Federal corporate income tax rate'},
            {'name': 'State Income Tax - CA', 'tax_type': 'INCOME', 'rate': 8.84, 'jurisdiction': 'California', 'description': 'California state income tax rate'},
            {'name': 'State Income Tax - NY', 'tax_type': 'INCOME', 'rate': 6.50, 'jurisdiction': 'New York', 'description': 'New York state income tax rate'},
            {'name': 'State Income Tax - TX', 'tax_type': 'INCOME', 'rate': 0.00, 'jurisdiction': 'Texas', 'description': 'Texas has no state income tax'},

            # Sales Tax Rates
            {'name': 'Sales Tax - CA', 'tax_type': 'SALES', 'rate': 8.25, 'jurisdiction': 'California', 'description': 'California state sales tax'},
            {'name': 'Sales Tax - NY', 'tax_type': 'SALES', 'rate': 4.00, 'jurisdiction': 'New York', 'description': 'New York state sales tax'},
            {'name': 'Sales Tax - TX', 'tax_type': 'SALES', 'rate': 6.25, 'jurisdiction': 'Texas', 'description': 'Texas state sales tax'},

            # Property Tax Rates
            {'name': 'Property Tax - CA Average', 'tax_type': 'PROPERTY', 'rate': 0.75, 'jurisdiction': 'California', 'description': 'Average California property tax rate (0.75%)'},
            {'name': 'Property Tax - NY Average', 'tax_type': 'PROPERTY', 'rate': 1.20, 'jurisdiction': 'New York', 'description': 'Average New York property tax rate (1.20%)'},
            {'name': 'Property Tax - TX Average', 'tax_type': 'PROPERTY', 'rate': 1.80, 'jurisdiction': 'Texas', 'description': 'Average Texas property tax rate (1.80%)'},
        ]

        tax_rates = []
        for rate_data in tax_rates_data:
            tax_rate, created = TaxRate.objects.get_or_create(
                name=rate_data['name'],
                defaults={
                    'tax_type': rate_data['tax_type'],
                    'rate': Decimal(str(rate_data['rate'])),
                    'jurisdiction': rate_data['jurisdiction'],
                    'description': rate_data['description'],
                    'effective_date': '2024-01-01',
                    'is_active': True
                }
            )
            tax_rates.append(tax_rate)
            if created:
                self.stdout.write(f'  Created tax rate: {tax_rate.name} - {tax_rate.rate}%')

        return tax_rates

    def _seed_asset_tax_info(self, user):
        """Seed tax information for existing fixed assets"""
        assets = FixedAsset.objects.filter(is_active=True)
        tax_infos = []

        # Property tax rates by jurisdiction
        property_tax_rates = {
            'California': Decimal('0.0075'),  # 0.75%
            'New York': Decimal('0.0120'),    # 1.20%
            'Texas': Decimal('0.0180'),       # 1.80%
        }

        for asset in assets:
            # Skip if tax info already exists
            if hasattr(asset, 'tax_info') and asset.tax_info:
                continue

            # Determine property class based on asset category
            property_class = AssetTaxInfo.PropertyClass.CLASS_5  # Default
            if asset.category in ['COMPUTER_EQUIPMENT', 'OFFICE_EQUIPMENT', 'SOFTWARE']:
                property_class = AssetTaxInfo.PropertyClass.CLASS_5  # 5-year property
            elif asset.category in ['FURNITURE', 'LEASEHOLD_IMPROVEMENTS']:
                property_class = AssetTaxInfo.PropertyClass.CLASS_7  # 7-year property
            elif asset.category == 'VEHICLES':
                property_class = AssetTaxInfo.PropertyClass.CLASS_5  # 5-year property
            elif asset.category == 'BUILDINGS':
                property_class = AssetTaxInfo.PropertyClass.CLASS_39  # 39-year property
            elif asset.category == 'LAND':
                property_class = AssetTaxInfo.PropertyClass.NON_DEPRECIABLE

            # Determine tax depreciation method
            tax_method = AssetTaxInfo.TaxDepreciationMethod.MACRS
            if asset.category == 'LAND':
                tax_method = AssetTaxInfo.TaxDepreciationMethod.STRAIGHT_LINE

            # Set tax basis (same as purchase cost initially)
            tax_basis = asset.purchase_cost

            # Random Section 179 deduction for qualifying assets (under $1M limit)
            section_179 = Decimal('0.00')
            if asset.category in ['COMPUTER_EQUIPMENT', 'OFFICE_EQUIPMENT', 'SOFTWARE'] and asset.purchase_cost <= 1000000:
                section_179 = min(asset.purchase_cost * Decimal('0.5'), Decimal('50000'))  # Up to 50% or $50k

            # Random bonus depreciation
            bonus_depr = Decimal('0.00')
            if random.choice([True, False]):  # 50% chance
                bonus_depr = (tax_basis - section_179) * Decimal('0.8')  # 80% bonus depreciation

            # Property tax information (for buildings and land)
            assessed_value = None
            property_tax_rate = None
            property_jurisdiction = None

            if asset.category in ['BUILDINGS', 'LAND']:
                # Random jurisdiction
                jurisdiction = random.choice(['California', 'New York', 'Texas'])
                assessed_value = asset.purchase_cost * Decimal(str(random.uniform(0.8, 1.2)))  # 80-120% of cost
                property_tax_rate = property_tax_rates[jurisdiction]
                property_jurisdiction = jurisdiction

            # Create tax info
            tax_info = AssetTaxInfo(
                asset=asset,
                tax_depreciation_method=tax_method,
                property_class=property_class,
                tax_basis=tax_basis,
                section_179_deduction=section_179,
                bonus_depreciation=bonus_depr,
                assessed_value=assessed_value,
                property_tax_rate=property_tax_rate,
                property_tax_jurisdiction=property_jurisdiction,
                tax_notes=f"Tax information for {asset.asset_code}. Property class: {property_class}. Tax method: {tax_method}."
            )

            # Calculate initial tax depreciation and book value
            tax_info.tax_accumulated_depreciation = sum(
                d['annual_depreciation'] for d in tax_info.calculate_tax_depreciation_schedule()
            )
            tax_info.tax_book_value = tax_info.tax_basis - tax_info.section_179_deduction - tax_info.bonus_depreciation - tax_info.tax_accumulated_depreciation
            tax_info.save()

            tax_infos.append(tax_info)
            self.stdout.write(f'  Created tax info for: {asset.asset_code} - {asset.name[:30]}...')

        return tax_infos

    def _show_summary(self, tax_rates, tax_infos):
        """Show summary of seeded tax data"""
        self.stdout.write('\nTax Data Summary:')
        self.stdout.write('-' * 40)

        # Tax rates by type
        rate_types = TaxRate.objects.values('tax_type').annotate(
            count=models.Count('id')
        ).order_by('tax_type')

        self.stdout.write('\nTax Rates by Type:')
        for rate_type in rate_types:
            self.stdout.write(f"  {rate_type['tax_type']}: {rate_type['count']} rates")

        # Asset tax info summary
        total_assets = FixedAsset.objects.filter(is_active=True).count()
        assets_with_tax_info = AssetTaxInfo.objects.count()

        self.stdout.write(f"\nAsset Tax Information:")
        self.stdout.write(f"  Total Assets: {total_assets}")
        self.stdout.write(f"  Assets with Tax Info: {assets_with_tax_info}")
        self.stdout.write(f"  Coverage: {assets_with_tax_info/total_assets*100:.1f}%" if total_assets > 0 else "  Coverage: 0%")

        # Tax depreciation summary
        tax_summary = AssetTaxInfo.objects.aggregate(
            total_tax_basis=models.Sum('tax_basis'),
            total_section_179=models.Sum('section_179_deduction'),
            total_bonus=models.Sum('bonus_depreciation'),
            total_tax_depr=models.Sum('tax_accumulated_depreciation'),
            total_tax_book_value=models.Sum('tax_book_value')
        )

        self.stdout.write(f"\nTax Depreciation Summary:")
        self.stdout.write(f"  Total Tax Basis: ${tax_summary['total_tax_basis'] or 0:,.2f}")
        self.stdout.write(f"  Section 179 Deductions: ${tax_summary['total_section_179'] or 0:,.2f}")
        self.stdout.write(f"  Bonus Depreciation: ${tax_summary['total_bonus'] or 0:,.2f}")
        self.stdout.write(f"  Accumulated Tax Depreciation: ${tax_summary['total_tax_depr'] or 0:,.2f}")
        self.stdout.write(f"  Total Tax Book Value: ${tax_summary['total_tax_book_value'] or 0:,.2f}")

        # Property tax summary
        property_assets = AssetTaxInfo.objects.filter(assessed_value__isnull=False)
        if property_assets.exists():
            property_summary = property_assets.aggregate(
                total_assessed=models.Sum('assessed_value'),
                avg_tax_rate=models.Avg('property_tax_rate')
            )

            total_property_tax = sum(asset.calculate_property_tax() for asset in property_assets)

            self.stdout.write(f"\nProperty Tax Summary:")
            self.stdout.write(f"  Assets with Property Tax: {property_assets.count()}")
            self.stdout.write(f"  Total Assessed Value: ${property_summary['total_assessed'] or 0:,.2f}")
            self.stdout.write(f"  Average Tax Rate: {(property_summary['avg_tax_rate'] or 0)*100:.2f}%")
            self.stdout.write(f"  Total Property Tax: ${total_property_tax:,.2f}")