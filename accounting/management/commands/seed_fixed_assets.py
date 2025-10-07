from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounting.models import FixedAsset, Account, AccountType
from django.db import models
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Seeds the database with comprehensive fixed assets data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('Starting Fixed Assets Database Seeding'))
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

        # Get or create required accounts
        self.stdout.write('\nEnsuring required accounts exist...')
        accounts = self._ensure_accounts(user)

        # Clear existing fixed assets
        self.stdout.write('\nClearing existing fixed assets...')
        count = FixedAsset.objects.count()
        FixedAsset.objects.all().delete()
        if count > 0:
            self.stdout.write(f'✓ Cleared {count} existing fixed assets')

        # Seed comprehensive fixed assets
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SEEDING: Fixed Assets')
        self.stdout.write('='*60)
        assets = self._seed_fixed_assets(accounts)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(assets)} fixed assets'))

        # Calculate depreciation for all assets
        self.stdout.write('\nCalculating depreciation...')
        self._calculate_depreciation(assets)

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Fixed Assets seeding completed successfully!'))
        self.stdout.write(self.style.SUCCESS('='*60))

        # Show summary
        self._show_summary()

    def _ensure_accounts(self, user):
        """Ensure required accounts exist"""
        accounts_data = [
            {'code': '1400', 'name': 'Fixed Assets - Equipment', 'type': AccountType.ASSET},
            {'code': '1410', 'name': 'Fixed Assets - Furniture', 'type': AccountType.ASSET},
            {'code': '1420', 'name': 'Fixed Assets - Vehicles', 'type': AccountType.ASSET},
            {'code': '1430', 'name': 'Fixed Assets - Buildings', 'type': AccountType.ASSET},
            {'code': '1440', 'name': 'Fixed Assets - Land', 'type': AccountType.ASSET},
            {'code': '1450', 'name': 'Fixed Assets - Software', 'type': AccountType.ASSET},
            {'code': '1460', 'name': 'Fixed Assets - Leasehold Improvements', 'type': AccountType.ASSET},
            {'code': '1500', 'name': 'Accumulated Depreciation', 'type': AccountType.ASSET},
        ]

        accounts = {}
        for acc_data in accounts_data:
            account, created = Account.objects.get_or_create(
                code=acc_data['code'],
                defaults={
                    'name': acc_data['name'],
                    'account_type': acc_data['type'],
                    'created_by': user
                }
            )
            accounts[acc_data['code']] = account
            if created:
                self.stdout.write(f'  Created account: {account.code} - {account.name}')

        return accounts

    def _seed_fixed_assets(self, accounts):
        """Seed comprehensive fixed assets data"""
        base_date = timezone.now().date()

        assets_data = [
            # Office Equipment
            {
                'code': 'EQ-001', 'name': 'Dell Latitude 5420 Laptop', 'category': FixedAsset.AssetCategory.COMPUTER_EQUIPMENT,
                'account': '1400', 'acquisition_method': FixedAsset.AcquisitionMethod.PURCHASE,
                'cost': 1850.00, 'salvage': 185.00, 'life': 3, 'method': FixedAsset.DepreciationMethod.STRAIGHT_LINE,
                'location': 'Main Office - IT Department', 'department': 'Information Technology', 'custodian': 'John Smith',
                'description': 'High-performance business laptop for accounting team',
                'manufacturer': 'Dell', 'model': 'Latitude 5420', 'serial_number': 'DL5420-2023-001',
                'funding_source': 'Company Budget', 'is_insured': True, 'is_under_warranty': True,
                'warranty_end_date': base_date.replace(year=base_date.year + 3), 'maintenance_schedule': 'Annual',
                'tags': 'laptop,computer,office,accounting'
            },
            {
                'code': 'EQ-002', 'name': 'HP LaserJet Pro MFP M182nw', 'category': FixedAsset.AssetCategory.OFFICE_EQUIPMENT,
                'account': '1400', 'acquisition_method': FixedAsset.AcquisitionMethod.PURCHASE,
                'cost': 450.00, 'salvage': 45.00, 'life': 5, 'method': FixedAsset.DepreciationMethod.STRAIGHT_LINE,
                'location': 'Main Office - Admin Area', 'department': 'Administration', 'custodian': 'Jane Doe',
                'description': 'Multi-function printer for office use',
                'manufacturer': 'HP', 'model': 'LaserJet Pro MFP M182nw', 'serial_number': 'HP182NW-2023-045',
                'funding_source': 'Office Supplies Budget', 'is_insured': False, 'is_under_warranty': True,
                'warranty_end_date': base_date.replace(year=base_date.year + 1), 'maintenance_schedule': 'Semi-annual',
                'tags': 'printer,mfp,office,administration'
            },
            {
                'code': 'EQ-003', 'name': 'Cisco IP Phone System', 'category': FixedAsset.AssetCategory.OFFICE_EQUIPMENT,
                'account': '1400', 'acquisition_method': FixedAsset.AcquisitionMethod.PURCHASE,
                'cost': 1200.00, 'salvage': 120.00, 'life': 7, 'method': FixedAsset.DepreciationMethod.STRAIGHT_LINE,
                'location': 'Main Office - Reception', 'department': 'Administration', 'custodian': 'Mike Johnson',
                'description': 'VOIP phone system with 4 handsets',
                'manufacturer': 'Cisco', 'model': 'IP Phone 7841', 'serial_number': 'CISCO7841-2023-078',
                'funding_source': 'IT Budget', 'is_insured': True, 'is_under_warranty': True,
                'warranty_end_date': base_date.replace(year=base_date.year + 2), 'maintenance_schedule': 'Annual',
                'tags': 'phone,voip,communication,reception'
            },
            {
                'code': 'EQ-004', 'name': 'Server Rack and UPS', 'category': FixedAsset.AssetCategory.COMPUTER_EQUIPMENT,
                'account': '1400', 'acquisition_method': FixedAsset.AcquisitionMethod.PURCHASE,
                'cost': 3500.00, 'salvage': 350.00, 'life': 5, 'method': FixedAsset.DepreciationMethod.DECLINING_BALANCE,
                'location': 'Server Room', 'department': 'Information Technology', 'custodian': 'John Smith',
                'description': '19" server rack with backup power supply',
                'manufacturer': 'APC', 'model': 'Smart-UPS SRT 1000VA', 'serial_number': 'APC-SRT-2023-100',
                'funding_source': 'IT Infrastructure Budget', 'is_insured': True, 'is_under_warranty': True,
                'warranty_end_date': base_date.replace(year=base_date.year + 3), 'maintenance_schedule': 'Quarterly',
                'insurance_policy_number': 'INS-IT-2023-001', 'insurance_coverage_amount': 5000.00,
                'tags': 'server,rack,ups,power,backup'
            },
            {
                'code': 'EQ-005', 'name': 'Projector and Screen', 'category': FixedAsset.AssetCategory.OFFICE_EQUIPMENT,
                'account': '1400', 'acquisition_method': FixedAsset.AcquisitionMethod.PURCHASE,
                'cost': 2200.00, 'salvage': 220.00, 'life': 7, 'method': FixedAsset.DepreciationMethod.STRAIGHT_LINE,
                'location': 'Conference Room', 'department': 'Administration', 'custodian': 'Sarah Wilson',
                'description': '4K projector with motorized screen for presentations',
                'manufacturer': 'Epson', 'model': 'PowerLite Pro G6970WU', 'serial_number': 'EPSON-G6970-2023-069',
                'funding_source': 'Office Equipment Budget', 'is_insured': False, 'is_under_warranty': True,
                'warranty_end_date': base_date.replace(year=base_date.year + 2), 'maintenance_schedule': 'Annual',
                'tags': 'projector,screen,presentation,conference'
            },

            # Furniture
            {
                'code': 'FN-001', 'name': 'Executive Desk Set', 'category': FixedAsset.AssetCategory.FURNITURE,
                'account': '1410', 'acquisition_method': FixedAsset.AcquisitionMethod.PURCHASE,
                'cost': 3200.00, 'salvage': 320.00, 'life': 10, 'method': FixedAsset.DepreciationMethod.STRAIGHT_LINE,
                'location': 'CEO Office', 'department': 'Executive', 'custodian': 'CEO',
                'description': 'Mahogany executive desk with matching credenza and chair',
                'manufacturer': 'Herman Miller', 'model': 'Aeron Executive Set', 'serial_number': 'HM-AERON-2022-042',
                'funding_source': 'Executive Budget', 'is_insured': True, 'is_under_warranty': False,
                'maintenance_schedule': 'Annual', 'insurance_policy_number': 'INS-FURN-2023-001',
                'insurance_coverage_amount': 4000.00, 'tags': 'desk,chair,executive,furniture,mahogany'
            },
            {
                'code': 'FN-002', 'name': 'Cubicle Workstation (x10)', 'category': FixedAsset.AssetCategory.FURNITURE,
                'account': '1410', 'acquisition_method': FixedAsset.AcquisitionMethod.PURCHASE,
                'cost': 15000.00, 'salvage': 1500.00, 'life': 7, 'method': FixedAsset.DepreciationMethod.STRAIGHT_LINE,
                'location': 'Open Office Area', 'department': 'Operations', 'custodian': 'Operations Manager',
                'description': 'Modular cubicle system for 10 employees',
                'manufacturer': 'Haworth', 'model': 'Compose Workstations', 'serial_number': 'HW-COMPOSE-2023-010',
                'funding_source': 'Office Renovation Budget', 'is_insured': True, 'is_under_warranty': True,
                'warranty_end_date': base_date.replace(year=base_date.year + 5), 'maintenance_schedule': 'Semi-annual',
                'insurance_policy_number': 'INS-FURN-2023-002', 'insurance_coverage_amount': 18000.00,
                'tags': 'cubicle,workstation,office,furniture,modular'
            },
            {
                'code': 'FN-003', 'name': 'Conference Room Table', 'category': FixedAsset.AssetCategory.FURNITURE,
                'account': '1410', 'acquisition_method': FixedAsset.AcquisitionMethod.PURCHASE,
                'cost': 4800.00, 'salvage': 480.00, 'life': 10, 'method': FixedAsset.DepreciationMethod.STRAIGHT_LINE,
                'location': 'Conference Room', 'department': 'Administration', 'custodian': 'Sarah Wilson',
                'description': '12-person oval conference table with leather chairs',
                'manufacturer': 'Knoll', 'model': 'Reff Oval Table', 'serial_number': 'KNOLL-REFF-2023-012',
                'funding_source': 'Office Equipment Budget', 'is_insured': True, 'is_under_warranty': False,
                'maintenance_schedule': 'Annual', 'insurance_policy_number': 'INS-FURN-2023-003',
                'insurance_coverage_amount': 6000.00, 'tags': 'table,conference,chairs,leather,meeting'
            },
            {
                'code': 'FN-004', 'name': 'Reception Area Furniture', 'category': FixedAsset.AssetCategory.FURNITURE,
                'account': '1410', 'acquisition_method': FixedAsset.AcquisitionMethod.PURCHASE,
                'cost': 5200.00, 'salvage': 520.00, 'life': 8, 'method': FixedAsset.DepreciationMethod.STRAIGHT_LINE,
                'location': 'Reception Area', 'department': 'Administration', 'custodian': 'Mike Johnson',
                'description': 'Sofa set, coffee tables, and reception desk',
                'manufacturer': 'Steelcase', 'model': 'Reception Suite', 'serial_number': 'SC-RECEP-2023-005',
                'funding_source': 'Office Renovation Budget', 'is_insured': True, 'is_under_warranty': True,
                'warranty_end_date': base_date.replace(year=base_date.year + 3), 'maintenance_schedule': 'Annual',
                'insurance_policy_number': 'INS-FURN-2023-004', 'insurance_coverage_amount': 6500.00,
                'tags': 'reception,sofa,desk,furniture,lobby'
            },
            {
                'code': 'FN-005', 'name': 'Filing Cabinets (x5)', 'category': FixedAsset.AssetCategory.FURNITURE,
                'account': '1410', 'acquisition_method': FixedAsset.AcquisitionMethod.PURCHASE,
                'cost': 2500.00, 'salvage': 250.00, 'life': 15, 'method': FixedAsset.DepreciationMethod.STRAIGHT_LINE,
                'location': 'Records Room', 'department': 'Administration', 'custodian': 'Records Manager',
                'description': 'Fire-rated filing cabinets for document storage',
                'manufacturer': 'HON', 'model': 'FireKing Filing Cabinets', 'serial_number': 'HON-FK-2023-005',
                'funding_source': 'Records Management Budget', 'is_insured': True, 'is_under_warranty': True,
                'warranty_end_date': base_date.replace(year=base_date.year + 10), 'maintenance_schedule': 'Annual',
                'insurance_policy_number': 'INS-FURN-2023-005', 'insurance_coverage_amount': 3000.00,
                'tags': 'filing,cabinets,storage,fire-rated,records'
            },

            # Vehicles
            {
                'code': 'VH-001', 'name': 'Toyota Camry 2023', 'category': FixedAsset.AssetCategory.VEHICLES,
                'account': '1420', 'acquisition_method': FixedAsset.AcquisitionMethod.PURCHASE,
                'cost': 28500.00, 'salvage': 2850.00, 'life': 5, 'method': FixedAsset.DepreciationMethod.STRAIGHT_LINE,
                'location': 'Company Garage', 'department': 'Executive', 'custodian': 'CEO',
                'description': 'Executive sedan for business travel and client meetings',
                'manufacturer': 'Toyota', 'model': 'Camry XSE', 'serial_number': 'JTNB11HK803500123',
                'funding_source': 'Vehicle Budget', 'is_insured': True, 'is_under_warranty': True,
                'warranty_end_date': base_date.replace(year=base_date.year + 3), 'maintenance_schedule': 'Monthly',
                'insurance_policy_number': 'AUTO-2023-001', 'insurance_coverage_amount': 35000.00,
                'insurance_company': 'State Farm', 'insurance_expiry_date': base_date.replace(year=base_date.year + 1),
                'tags': 'vehicle,car,sedan,executive,toyota'
            },
            {
                'code': 'VH-002', 'name': 'Ford Transit Van', 'category': FixedAsset.AssetCategory.VEHICLES,
                'account': '1420', 'acquisition_method': FixedAsset.AcquisitionMethod.LEASE,
                'cost': 42000.00, 'salvage': 4200.00, 'life': 7, 'method': FixedAsset.DepreciationMethod.STRAIGHT_LINE,
                'location': 'Company Garage', 'department': 'Operations', 'custodian': 'Fleet Manager',
                'description': 'Cargo van for equipment transport and deliveries',
                'manufacturer': 'Ford', 'model': 'Transit T-150', 'serial_number': '1FTBW1YG8FKA01234',
                'funding_source': 'Operations Budget', 'is_insured': True, 'is_leased': True, 'is_under_warranty': True,
                'warranty_end_date': base_date.replace(year=base_date.year + 5), 'maintenance_schedule': 'Monthly',
                'insurance_policy_number': 'AUTO-2023-002', 'insurance_coverage_amount': 50000.00,
                'insurance_company': 'Progressive', 'insurance_expiry_date': base_date.replace(year=base_date.year + 1),
                'tags': 'vehicle,van,cargo,delivery,ford'
            },
            {
                'code': 'VH-003', 'name': 'Honda Civic Hybrid', 'category': FixedAsset.AssetCategory.VEHICLES,
                'account': '1420', 'acquisition_method': FixedAsset.AcquisitionMethod.PURCHASE,
                'cost': 26500.00, 'salvage': 2650.00, 'life': 5, 'method': FixedAsset.DepreciationMethod.DECLINING_BALANCE,
                'location': 'Company Garage', 'department': 'Sales', 'custodian': 'Sales Manager',
                'description': 'Fuel-efficient vehicle for sales team',
                'manufacturer': 'Honda', 'model': 'Civic Sport Hybrid', 'serial_number': '19XFC2F5XGE000567',
                'funding_source': 'Sales Budget', 'is_insured': True, 'is_under_warranty': True,
                'warranty_end_date': base_date.replace(year=base_date.year + 3), 'maintenance_schedule': 'Monthly',
                'insurance_policy_number': 'AUTO-2023-003', 'insurance_coverage_amount': 30000.00,
                'insurance_company': 'Geico', 'insurance_expiry_date': base_date.replace(year=base_date.year + 1),
                'tags': 'vehicle,car,hybrid,sales,honda'
            },

            # Buildings and Land
            {
                'code': 'BLD-001', 'name': 'Office Building', 'category': FixedAsset.AssetCategory.BUILDINGS,
                'account': '1430', 'acquisition_method': FixedAsset.AcquisitionMethod.PURCHASE,
                'cost': 750000.00, 'salvage': 75000.00, 'life': 39, 'method': FixedAsset.DepreciationMethod.STRAIGHT_LINE,
                'location': '123 Business Ave, City, State', 'department': 'Facilities', 'custodian': 'Facilities Manager',
                'description': '3-story office building with 15,000 sq ft',
                'funding_source': 'Capital Investment', 'is_insured': True, 'is_depreciated': True,
                'maintenance_schedule': 'Quarterly', 'insurance_policy_number': 'PROP-2023-001',
                'insurance_coverage_amount': 1000000.00, 'insurance_company': 'Allstate',
                'insurance_expiry_date': base_date.replace(year=base_date.year + 1),
                'tags': 'building,office,property,commercial'
            },
            {
                'code': 'LAND-001', 'name': 'Office Land', 'category': FixedAsset.AssetCategory.LAND,
                'account': '1440', 'acquisition_method': FixedAsset.AcquisitionMethod.PURCHASE,
                'cost': 150000.00, 'salvage': 150000.00, 'life': 99, 'method': FixedAsset.DepreciationMethod.STRAIGHT_LINE,
                'location': '123 Business Ave, City, State', 'department': 'Facilities', 'custodian': 'Facilities Manager',
                'description': '0.5 acre land parcel (land is not depreciated)',
                'funding_source': 'Capital Investment', 'is_insured': False, 'is_depreciated': False,
                'insurance_policy_number': 'LAND-2023-001', 'insurance_coverage_amount': 200000.00,
                'insurance_company': 'Farmers', 'insurance_expiry_date': base_date.replace(year=base_date.year + 1),
                'tags': 'land,property,parcel,real-estate'
            },

            # Software
            {
                'code': 'SW-001', 'name': 'Accounting Software License', 'category': FixedAsset.AssetCategory.SOFTWARE,
                'account': '1450', 'acquisition_method': FixedAsset.AcquisitionMethod.PURCHASE,
                'cost': 25000.00, 'salvage': 0.00, 'life': 5, 'method': FixedAsset.DepreciationMethod.STRAIGHT_LINE,
                'location': 'IT Systems', 'department': 'Information Technology', 'custodian': 'IT Manager',
                'description': 'Enterprise accounting software suite with annual maintenance',
                'manufacturer': 'SAP', 'model': 'Business One Professional', 'serial_number': 'SAP-B1-2023-001',
                'funding_source': 'IT Budget', 'is_insured': False, 'is_under_warranty': False,
                'maintenance_schedule': 'Annual', 'tags': 'software,accounting,sap,enterprise'
            },
            {
                'code': 'SW-002', 'name': 'Microsoft Office 365', 'category': FixedAsset.AssetCategory.SOFTWARE,
                'account': '1450', 'acquisition_method': FixedAsset.AcquisitionMethod.PURCHASE,
                'cost': 4800.00, 'salvage': 0.00, 'life': 3, 'method': FixedAsset.DepreciationMethod.STRAIGHT_LINE,
                'location': 'All Computers', 'department': 'Information Technology', 'custodian': 'IT Manager',
                'description': 'Office productivity suite for 50 users',
                'manufacturer': 'Microsoft', 'model': 'Office 365 Enterprise E3', 'serial_number': 'MS-O365-2023-050',
                'funding_source': 'Office Supplies Budget', 'is_insured': False, 'is_under_warranty': False,
                'maintenance_schedule': 'Monthly (subscription)', 'tags': 'software,office,microsoft,productivity'
            },
            {
                'code': 'SW-003', 'name': 'Antivirus Software', 'category': FixedAsset.AssetCategory.SOFTWARE,
                'account': '1450', 'acquisition_method': FixedAsset.AcquisitionMethod.PURCHASE,
                'cost': 3600.00, 'salvage': 0.00, 'life': 3, 'method': FixedAsset.DepreciationMethod.STRAIGHT_LINE,
                'location': 'All Computers', 'department': 'Information Technology', 'custodian': 'IT Manager',
                'description': 'Enterprise antivirus protection for all devices',
                'manufacturer': 'Symantec', 'model': 'Endpoint Protection Enterprise', 'serial_number': 'SYM-EP-2023-100',
                'funding_source': 'IT Security Budget', 'is_insured': False, 'is_under_warranty': False,
                'maintenance_schedule': 'Monthly', 'tags': 'software,security,antivirus,symantec'
            },

            # Leasehold Improvements
            {
                'code': 'LI-001', 'name': 'Office Renovation', 'category': FixedAsset.AssetCategory.LEASEHOLD_IMPROVEMENTS,
                'account': '1460', 'acquisition_method': FixedAsset.AcquisitionMethod.CAPITALIZED_EXPENSE,
                'cost': 85000.00, 'salvage': 0.00, 'life': 10, 'method': FixedAsset.DepreciationMethod.STRAIGHT_LINE,
                'location': 'Main Office Building', 'department': 'Facilities', 'custodian': 'Facilities Manager',
                'description': 'Complete office renovation including flooring, painting, and lighting',
                'funding_source': 'Renovation Budget', 'is_insured': False, 'is_depreciated': True,
                'maintenance_schedule': 'Annual', 'tags': 'renovation,improvements,office,flooring,lighting'
            },
            {
                'code': 'LI-002', 'name': 'HVAC System Upgrade', 'category': FixedAsset.AssetCategory.LEASEHOLD_IMPROVEMENTS,
                'account': '1460', 'acquisition_method': FixedAsset.AcquisitionMethod.CAPITALIZED_EXPENSE,
                'cost': 45000.00, 'salvage': 0.00, 'life': 15, 'method': FixedAsset.DepreciationMethod.STRAIGHT_LINE,
                'location': 'Main Office Building', 'department': 'Facilities', 'custodian': 'Facilities Manager',
                'description': 'Energy-efficient HVAC system replacement',
                'manufacturer': 'Carrier', 'model': 'Infinity System', 'serial_number': 'CARRIER-INF-2023-001',
                'funding_source': 'Facilities Budget', 'is_insured': True, 'is_depreciated': True,
                'warranty_end_date': base_date.replace(year=base_date.year + 10), 'maintenance_schedule': 'Semi-annual',
                'insurance_policy_number': 'HVAC-2023-001', 'insurance_coverage_amount': 55000.00,
                'tags': 'hvac,heating,cooling,energy-efficient,upgrade'
            },
        ]

        assets = []

        for data in assets_data:
            # Randomize purchase date within last 3 years
            days_back = random.randint(0, 1095)  # 0-3 years
            purchase_date = base_date - timedelta(days=days_back)

            purchase_cost = Decimal(str(data['cost']))
            salvage_value = Decimal(str(data['salvage']))

            asset = FixedAsset.objects.create(
                asset_code=data['code'],
                name=data['name'],
                description=data.get('description', ''),
                category=data.get('category', FixedAsset.AssetCategory.OFFICE_EQUIPMENT),
                account=accounts[data['account']],
                acquisition_method=data.get('acquisition_method', FixedAsset.AcquisitionMethod.PURCHASE),
                purchase_date=purchase_date,
                purchase_cost=purchase_cost,
                salvage_value=salvage_value,
                useful_life_years=data['life'],
                depreciation_method=data['method'],
                location=data.get('location', ''),
                department=data.get('department', ''),
                custodian=data.get('custodian', ''),
                manufacturer=data.get('manufacturer', ''),
                model=data.get('model', ''),
                serial_number=data.get('serial_number', ''),
                funding_source=data.get('funding_source', ''),
                is_insured=data.get('is_insured', False),
                is_under_warranty=data.get('is_under_warranty', False),
                is_leased=data.get('is_leased', False),
                is_depreciated=data.get('is_depreciated', True),
                warranty_end_date=data.get('warranty_end_date'),
                maintenance_schedule=data.get('maintenance_schedule', ''),
                insurance_policy_number=data.get('insurance_policy_number', ''),
                insurance_coverage_amount=data.get('insurance_coverage_amount', Decimal('0.00')),
                insurance_company=data.get('insurance_company', ''),
                insurance_expiry_date=data.get('insurance_expiry_date'),
                tags=data.get('tags', ''),
                accumulated_depreciation=Decimal('0.00'),  # Start with no depreciation
                book_value=purchase_cost,  # Initially equals purchase cost
                is_active=True
            )
            assets.append(asset)

        return assets

    def _calculate_depreciation(self, assets):
        """Calculate accumulated depreciation for all assets"""
        today = timezone.now().date()

        for asset in assets:
            # Calculate months since purchase
            months_elapsed = (today.year - asset.purchase_date.year) * 12 + (today.month - asset.purchase_date.month)

            if months_elapsed > 0:
                if asset.depreciation_method == FixedAsset.DepreciationMethod.STRAIGHT_LINE:
                    # Straight line depreciation
                    annual_depr = (asset.purchase_cost - asset.salvage_value) / asset.useful_life_years
                    monthly_depr = annual_depr / 12
                    accumulated_depr = min(monthly_depr * months_elapsed, asset.purchase_cost - asset.salvage_value)

                elif asset.depreciation_method == FixedAsset.DepreciationMethod.DECLINING_BALANCE:
                    # Declining balance (double declining for simplicity)
                    rate = Decimal('2.0') / Decimal(str(asset.useful_life_years))  # Double declining
                    book_value = asset.purchase_cost

                    for year in range(min(int(months_elapsed / 12) + 1, asset.useful_life_years)):
                        annual_depr = book_value * rate
                        if year == asset.useful_life_years - 1:  # Last year
                            annual_depr = max(annual_depr, book_value - asset.salvage_value)
                        book_value -= annual_depr

                    # Adjust for partial year
                    partial_year_factor = Decimal(str((months_elapsed % 12) / 12))
                    if partial_year_factor > 0 and int(months_elapsed / 12) < asset.useful_life_years:
                        additional_depr = (book_value + annual_depr) * rate * partial_year_factor
                        book_value -= additional_depr

                    accumulated_depr = asset.purchase_cost - book_value
                    accumulated_depr = min(accumulated_depr, asset.purchase_cost - asset.salvage_value)

                else:
                    # Default to straight line
                    annual_depr = (asset.purchase_cost - asset.salvage_value) / asset.useful_life_years
                    monthly_depr = annual_depr / 12
                    accumulated_depr = min(monthly_depr * months_elapsed, asset.purchase_cost - asset.salvage_value)

                asset.accumulated_depreciation = Decimal(str(round(float(accumulated_depr), 2)))
                asset.book_value = asset.purchase_cost - asset.accumulated_depreciation
                asset.save()

    def _show_summary(self):
        """Show summary of seeded assets"""
        self.stdout.write('\nFixed Assets Summary:')
        self.stdout.write('-' * 40)

        # By category
        categories = FixedAsset.objects.values('account__name').annotate(
            count=models.Count('id'),
            total_cost=models.Sum('purchase_cost'),
            total_depr=models.Sum('accumulated_depreciation'),
            total_book=models.Sum('book_value')
        ).order_by('account__name')

        for cat in categories:
            self.stdout.write(f"{cat['account__name']}:")
            self.stdout.write(f"  Count: {cat['count']}")
            self.stdout.write(f"  Total Cost: ${cat['total_cost']:,.2f}")
            self.stdout.write(f"  Accumulated Depreciation: ${cat['total_depr']:,.2f}")
            self.stdout.write(f"  Net Book Value: ${cat['total_book']:,.2f}")
            self.stdout.write('')

        # Overall totals
        totals = FixedAsset.objects.aggregate(
            total_cost=models.Sum('purchase_cost'),
            total_depr=models.Sum('accumulated_depreciation'),
            total_book=models.Sum('book_value')
        )

        self.stdout.write('Overall Totals:')
        self.stdout.write(f"  Total Assets: {FixedAsset.objects.count()}")
        self.stdout.write(f"  Total Cost: ${totals['total_cost']:,.2f}")
        self.stdout.write(f"  Total Accumulated Depreciation: ${totals['total_depr']:,.2f}")
        self.stdout.write(f"  Total Net Book Value: ${totals['total_book']:,.2f}")

        # Depreciation methods
        methods = FixedAsset.objects.values('depreciation_method').annotate(
            count=models.Count('id')
        ).order_by('depreciation_method')

        self.stdout.write('\nDepreciation Methods:')
        for method in methods:
            method_name = method['depreciation_method']
            count = method['count']
            self.stdout.write(f"  {method_name}: {count} assets")
