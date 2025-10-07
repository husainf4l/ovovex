from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class AccountType(models.TextChoices):
    ASSET = 'ASSET', 'Asset'
    LIABILITY = 'LIABILITY', 'Liability'
    EQUITY = 'EQUITY', 'Equity'
    REVENUE = 'REVENUE', 'Revenue'
    EXPENSE = 'EXPENSE', 'Expense'

class Account(models.Model):
    """
    Chart of Accounts - Defines all accounts in the general ledger
    """
    code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
        db_index=True
    )
    description = models.TextField(blank=True, null=True)
    parent_account = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_accounts'
    )
    is_active = models.BooleanField(default=True)
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='accounts_created'
    )

    class Meta:
        ordering = ['code']
        indexes = [
            models.Index(fields=['code', 'account_type']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def get_balance(self):
        """Calculate the current balance based on journal entries"""
        from django.db.models import Sum, Q
        
        debit_sum = JournalEntryLine.objects.filter(
            account=self,
            journal_entry__status='POSTED'
        ).aggregate(total=Sum('debit_amount'))['total'] or Decimal('0.00')
        
        credit_sum = JournalEntryLine.objects.filter(
            account=self,
            journal_entry__status='POSTED'
        ).aggregate(total=Sum('credit_amount'))['total'] or Decimal('0.00')
        
        # For assets and expenses, debit increases balance
        # For liabilities, equity, and revenue, credit increases balance
        if self.account_type in [AccountType.ASSET, AccountType.EXPENSE]:
            return debit_sum - credit_sum
        else:
            return credit_sum - debit_sum


class JournalEntry(models.Model):
    """
    Journal Entry header - Contains metadata about the entry
    """
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        POSTED = 'POSTED', 'Posted'
        VOID = 'VOID', 'Void'

    entry_number = models.CharField(max_length=50, unique=True, db_index=True)
    entry_date = models.DateField(db_index=True)
    description = models.TextField()
    reference = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
    )
    total_debit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_credit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='journal_entries_created'
    )
    posted_at = models.DateTimeField(null=True, blank=True)
    posted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='journal_entries_posted'
    )

    class Meta:
        ordering = ['-entry_date', '-entry_number']
        verbose_name_plural = 'Journal Entries'
        indexes = [
            models.Index(fields=['entry_date', 'status']),
        ]

    def __str__(self):
        return f"{self.entry_number} - {self.description[:50]}"

    def is_balanced(self):
        """Check if debits equal credits"""
        return self.total_debit == self.total_credit

    def calculate_totals(self):
        """Recalculate total debit and credit from lines"""
        from django.db.models import Sum
        
        totals = self.lines.aggregate(
            total_debit=Sum('debit_amount'),
            total_credit=Sum('credit_amount')
        )
        
        self.total_debit = totals['total_debit'] or Decimal('0.00')
        self.total_credit = totals['total_credit'] or Decimal('0.00')
        self.save()


class JournalEntryLine(models.Model):
    """
    Journal Entry line items - Individual debits and credits
    """
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='journal_lines'
    )
    description = models.CharField(max_length=255, blank=True, null=True)
    debit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    credit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    line_number = models.IntegerField()
    
    class Meta:
        ordering = ['journal_entry', 'line_number']

    def __str__(self):
        return f"{self.journal_entry.entry_number} - Line {self.line_number}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update journal entry totals
        self.journal_entry.calculate_totals()


# ============================================================================
# INVOICES & RECEIVABLES
# ============================================================================

class Customer(models.Model):
    """Customer/Client information"""
    customer_code = models.CharField(max_length=20, unique=True, db_index=True)
    company_name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    payment_terms_days = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['company_name']
    
    def __str__(self):
        return f"{self.customer_code} - {self.company_name}"
    
    def get_outstanding_balance(self):
        """Calculate total outstanding invoices"""
        return self.invoices.filter(
            status__in=['SENT', 'OVERDUE']
        ).aggregate(
            total=models.Sum('total_amount')
        )['total'] or Decimal('0.00')


class Invoice(models.Model):
    """Sales Invoices"""
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SENT = 'SENT', 'Sent'
        PAID = 'PAID', 'Paid'
        OVERDUE = 'OVERDUE', 'Overdue'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='invoices')
    invoice_date = models.DateField(db_index=True)
    due_date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-invoice_date', '-invoice_number']
    
    def __str__(self):
        return f"{self.invoice_number} - {self.customer.company_name}"
    
    def get_balance_due(self):
        return self.total_amount - self.paid_amount


class InvoiceLine(models.Model):
    """Invoice line items"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='lines')
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    line_total = models.DecimalField(max_digits=15, decimal_places=2)
    line_number = models.IntegerField()
    
    class Meta:
        ordering = ['invoice', 'line_number']
    
    def __str__(self):
        return f"{self.invoice.invoice_number} - Line {self.line_number}"


class Payment(models.Model):
    """Customer Payments"""
    class PaymentMethod(models.TextChoices):
        CASH = 'CASH', 'Cash'
        CHECK = 'CHECK', 'Check'
        BANK_TRANSFER = 'BANK_TRANSFER', 'Bank Transfer'
        CREDIT_CARD = 'CREDIT_CARD', 'Credit Card'
        OTHER = 'OTHER', 'Other'
    
    payment_number = models.CharField(max_length=50, unique=True, db_index=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='payments')
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name='payments', null=True, blank=True)
    payment_date = models.DateField(db_index=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    reference = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.payment_number} - ${self.amount}"


# ============================================================================
# VENDORS & PAYABLES
# ============================================================================

class Vendor(models.Model):
    """Vendor/Supplier information"""
    vendor_code = models.CharField(max_length=20, unique=True, db_index=True)
    company_name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    payment_terms_days = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['company_name']
    
    def __str__(self):
        return f"{self.vendor_code} - {self.company_name}"


class Bill(models.Model):
    """Vendor Bills (Accounts Payable)"""
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        APPROVED = 'APPROVED', 'Approved'
        PAID = 'PAID', 'Paid'
        OVERDUE = 'OVERDUE', 'Overdue'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    bill_number = models.CharField(max_length=50, unique=True, db_index=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='bills')
    bill_date = models.DateField(db_index=True)
    due_date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-bill_date', '-bill_number']
    
    def __str__(self):
        return f"{self.bill_number} - {self.vendor.company_name}"


class BillLine(models.Model):
    """Bill line items"""
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='lines')
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1.00'))
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    line_total = models.DecimalField(max_digits=15, decimal_places=2)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.bill.bill_number} - {self.description[:50]}"


# ============================================================================
# BUDGETS & FORECASTING
# ============================================================================

class Budget(models.Model):
    """Budget planning"""
    class Period(models.TextChoices):
        MONTHLY = 'MONTHLY', 'Monthly'
        QUARTERLY = 'QUARTERLY', 'Quarterly'
        ANNUAL = 'ANNUAL', 'Annual'
    
    name = models.CharField(max_length=255)
    fiscal_year = models.IntegerField()
    period = models.CharField(max_length=20, choices=Period.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    total_budget = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-fiscal_year', '-start_date']
    
    def __str__(self):
        return f"{self.name} - FY{self.fiscal_year}"


class BudgetLine(models.Model):
    """Budget line items by account"""
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='lines')
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='budget_lines')
    budgeted_amount = models.DecimalField(max_digits=15, decimal_places=2)
    actual_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    variance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['budget', 'account']
    
    def __str__(self):
        return f"{self.budget.name} - {self.account.name}"
    
    def calculate_variance(self):
        self.variance = self.actual_amount - self.budgeted_amount
        self.save()


# ============================================================================
# FIXED ASSETS
# ============================================================================

class FixedAsset(models.Model):
    """Fixed assets register"""
    class DepreciationMethod(models.TextChoices):
        STRAIGHT_LINE = 'STRAIGHT_LINE', 'Straight Line'
        DECLINING_BALANCE = 'DECLINING_BALANCE', 'Declining Balance'
        UNITS_OF_PRODUCTION = 'UNITS_OF_PRODUCTION', 'Units of Production'
    
    class AssetCategory(models.TextChoices):
        OFFICE_EQUIPMENT = 'OFFICE_EQUIPMENT', 'Office Equipment'
        FURNITURE = 'FURNITURE', 'Furniture'
        VEHICLES = 'VEHICLES', 'Vehicles'
        BUILDINGS = 'BUILDINGS', 'Buildings'
        LAND = 'LAND', 'Land'
        SOFTWARE = 'SOFTWARE', 'Software'
        LEASEHOLD_IMPROVEMENTS = 'LEASEHOLD_IMPROVEMENTS', 'Leasehold Improvements'
        MACHINERY = 'MACHINERY', 'Machinery'
        COMPUTER_EQUIPMENT = 'COMPUTER_EQUIPMENT', 'Computer Equipment'
        OTHER = 'OTHER', 'Other'
    
    class AcquisitionMethod(models.TextChoices):
        PURCHASE = 'PURCHASE', 'Purchase'
        LEASE = 'LEASE', 'Lease'
        DONATION = 'DONATION', 'Donation'
        CONSTRUCTION = 'CONSTRUCTION', 'Construction'
        CAPITALIZED_EXPENSE = 'CAPITALIZED_EXPENSE', 'Capitalized Expense'
        OTHER = 'OTHER', 'Other'
    
    # Basic Asset Information
    asset_code = models.CharField(max_length=50, unique=True, db_index=True, help_text="Unique asset identification code")
    name = models.CharField(max_length=255, help_text="Asset name/description")
    description = models.TextField(blank=True, null=True, help_text="Detailed asset description")
    
    # Classification
    category = models.CharField(max_length=30, choices=AssetCategory.choices, default=AssetCategory.OTHER, help_text="Asset category")
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='fixed_assets', help_text="GL account for this asset")
    
    # Acquisition Details
    acquisition_method = models.CharField(max_length=30, choices=AcquisitionMethod.choices, default=AcquisitionMethod.PURCHASE, help_text="How the asset was acquired")
    purchase_date = models.DateField(help_text="Date the asset was acquired")
    purchase_cost = models.DecimalField(max_digits=15, decimal_places=2, help_text="Original purchase cost")
    vendor = models.ForeignKey('Vendor', on_delete=models.SET_NULL, null=True, blank=True, related_name='supplied_assets', help_text="Vendor/supplier")
    purchase_order_number = models.CharField(max_length=100, blank=True, null=True, help_text="Purchase order reference")
    invoice_number = models.CharField(max_length=100, blank=True, null=True, help_text="Invoice reference")
    
    # Physical Details
    serial_number = models.CharField(max_length=100, blank=True, null=True, help_text="Manufacturer serial number")
    manufacturer = models.CharField(max_length=255, blank=True, null=True, help_text="Asset manufacturer")
    model = models.CharField(max_length=255, blank=True, null=True, help_text="Asset model")
    barcode = models.CharField(max_length=100, blank=True, null=True, unique=True, help_text="Barcode/RFID tag")
    
    # Location & Assignment
    location = models.CharField(max_length=255, blank=True, null=True, help_text="Physical location of the asset")
    department = models.CharField(max_length=255, blank=True, null=True, help_text="Department responsible for the asset")
    custodian = models.CharField(max_length=255, blank=True, null=True, help_text="Person responsible for the asset")
    custodian_employee_id = models.CharField(max_length=50, blank=True, null=True, help_text="Employee ID of custodian")
    
    # Financial Information
    salvage_value = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), help_text="Estimated salvage value at end of life")
    useful_life_years = models.IntegerField(help_text="Expected useful life in years")
    depreciation_method = models.CharField(max_length=30, choices=DepreciationMethod.choices, default=DepreciationMethod.STRAIGHT_LINE, help_text="Depreciation calculation method")
    accumulated_depreciation = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), help_text="Total depreciation charged to date")
    book_value = models.DecimalField(max_digits=15, decimal_places=2, help_text="Current book value (cost - accumulated depreciation)")
    
    # Funding & Insurance
    funding_source = models.CharField(max_length=255, blank=True, null=True, help_text="Source of funding for the asset")
    grant_number = models.CharField(max_length=100, blank=True, null=True, help_text="Grant or funding reference number")
    insurance_policy_number = models.CharField(max_length=100, blank=True, null=True, help_text="Insurance policy number")
    insurance_company = models.CharField(max_length=255, blank=True, null=True, help_text="Insurance company name")
    insurance_coverage_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Insurance coverage amount")
    insurance_premium = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Annual insurance premium")
    insurance_expiry_date = models.DateField(null=True, blank=True, help_text="Insurance policy expiry date")
    
    # Warranty Information
    warranty_start_date = models.DateField(null=True, blank=True, help_text="Warranty start date")
    warranty_end_date = models.DateField(null=True, blank=True, help_text="Warranty end date")
    warranty_provider = models.CharField(max_length=255, blank=True, null=True, help_text="Warranty provider")
    warranty_terms = models.TextField(blank=True, null=True, help_text="Warranty terms and conditions")
    
    # Maintenance Information
    maintenance_schedule = models.CharField(max_length=255, blank=True, null=True, help_text="Maintenance schedule (e.g., 'Monthly', 'Quarterly')")
    last_maintenance_date = models.DateField(null=True, blank=True, help_text="Date of last maintenance")
    next_maintenance_date = models.DateField(null=True, blank=True, help_text="Date of next scheduled maintenance")
    maintenance_provider = models.CharField(max_length=255, blank=True, null=True, help_text="Maintenance service provider")
    maintenance_cost_budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Annual maintenance budget")
    
    # Disposal Information
    disposal_date = models.DateField(null=True, blank=True, help_text="Date the asset was disposed")
    disposal_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Proceeds from disposal")
    disposal_method = models.CharField(max_length=255, blank=True, null=True, help_text="How the asset was disposed (sold, scrapped, etc.)")
    disposal_notes = models.TextField(blank=True, null=True, help_text="Notes about the disposal")
    
    # Status & Control
    is_active = models.BooleanField(default=True, help_text="Is the asset currently active/in use")
    is_depreciated = models.BooleanField(default=True, help_text="Should this asset be depreciated")
    is_insured = models.BooleanField(default=False, help_text="Is this asset insured")
    is_under_warranty = models.BooleanField(default=False, help_text="Is this asset under warranty")
    is_leased = models.BooleanField(default=False, help_text="Is this asset leased")
    
    # Audit Trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assets_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets_updated')
    
    # Additional Notes
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the asset")
    tags = models.CharField(max_length=500, blank=True, null=True, help_text="Tags for categorization and search")
    
    class Meta:
        ordering = ['asset_code']
        indexes = [
            models.Index(fields=['asset_code', 'category']),
            models.Index(fields=['is_active', 'category']),
            models.Index(fields=['purchase_date']),
            models.Index(fields=['department']),
            models.Index(fields=['custodian']),
        ]
    
    def __str__(self):
        return f"{self.asset_code} - {self.name}"
    
    def calculate_book_value(self):
        """Calculate current book value"""
        self.book_value = self.purchase_cost - self.accumulated_depreciation
        return self.book_value
    
    def calculate_monthly_depreciation(self):
        """Calculate monthly depreciation amount"""
        if not self.is_depreciated or self.useful_life_years <= 0:
            return Decimal('0.00')
        
        if self.depreciation_method == self.DepreciationMethod.STRAIGHT_LINE:
            annual_depr = (self.purchase_cost - self.salvage_value) / self.useful_life_years
            return annual_depr / 12
        elif self.depreciation_method == self.DepreciationMethod.DECLINING_BALANCE:
            # Double declining balance
            rate = Decimal('2.0') / self.useful_life_years
            annual_depr = self.purchase_cost * rate
            return annual_depr / 12
        else:
            # Default to straight line
            annual_depr = (self.purchase_cost - self.salvage_value) / self.useful_life_years
            return annual_depr / 12
    
    def get_depreciation_status(self):
        """Get depreciation status information"""
        if not self.is_depreciated:
            return "Not depreciated"
        
        depreciable_amount = self.purchase_cost - self.salvage_value
        if depreciable_amount <= 0:
            return "Fully depreciated"
        
        depreciation_percentage = (self.accumulated_depreciation / depreciable_amount) * 100
        if depreciation_percentage >= 100:
            return "Fully depreciated"
        elif depreciation_percentage >= 80:
            return "Nearly fully depreciated"
        else:
            return f"{depreciation_percentage:.1f}% depreciated"
    
    def is_warranty_active(self):
        """Check if warranty is currently active"""
        if not self.warranty_end_date:
            return False
        from django.utils import timezone
        return self.warranty_end_date >= timezone.now().date()
    
    def is_insurance_active(self):
        """Check if insurance is currently active"""
        if not self.insurance_expiry_date:
            return False
        from django.utils import timezone
        return self.insurance_expiry_date >= timezone.now().date()
    
    def days_until_maintenance(self):
        """Calculate days until next maintenance"""
        if not self.next_maintenance_date:
            return None
        from django.utils import timezone
        today = timezone.now().date()
        if self.next_maintenance_date < today:
            return 0  # Overdue
        return (self.next_maintenance_date - today).days
    
    def get_age_in_years(self):
        """Calculate asset age in years"""
        from django.utils import timezone
        today = timezone.now().date()
        age_days = (today - self.purchase_date).days
        return age_days / 365.25
    
    def get_remaining_life_years(self):
        """Calculate remaining useful life in years"""
        age = self.get_age_in_years()
        return max(0, self.useful_life_years - age)


# ============================================================================
# EXPENSES
# ============================================================================

class ExpenseCategory(models.Model):
    """Expense categories"""
    name = models.CharField(max_length=255)
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='expense_categories')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Expense Categories'
    
    def __str__(self):
        return self.name


class Expense(models.Model):
    """Expense tracking"""
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        PAID = 'PAID', 'Paid'
    
    expense_number = models.CharField(max_length=50, unique=True, db_index=True)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='expenses')
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    expense_date = models.DateField(db_index=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    receipt_number = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='expenses_created')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses_approved')
    
    class Meta:
        ordering = ['-expense_date', '-expense_number']
    
    def __str__(self):
        return f"{self.expense_number} - {self.description[:50]}"


# ============================================================================
# TAX
# ============================================================================

class TaxRate(models.Model):
    """Tax rates configuration"""
    class TaxType(models.TextChoices):
        INCOME = 'INCOME', 'Income Tax'
        SALES = 'SALES', 'Sales Tax'
        PROPERTY = 'PROPERTY', 'Property Tax'
        DEPRECIATION = 'DEPRECIATION', 'Depreciation Tax'
        OTHER = 'OTHER', 'Other'
    
    name = models.CharField(max_length=255)
    tax_type = models.CharField(max_length=20, choices=TaxType.choices, default=TaxType.INCOME)
    rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Tax rate as percentage")
    description = models.TextField(blank=True, null=True)
    jurisdiction = models.CharField(max_length=100, blank=True, null=True, help_text="Tax jurisdiction (state, local, federal)")
    effective_date = models.DateField(default='2024-01-01', help_text="Date when this tax rate becomes effective")
    end_date = models.DateField(null=True, blank=True, help_text="Date when this tax rate expires")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-effective_date', 'name']
        indexes = [
            models.Index(fields=['tax_type', 'jurisdiction', 'effective_date']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.rate}% ({self.jurisdiction or 'General'})"
    
    def is_current(self):
        """Check if this tax rate is currently active"""
        from django.utils import timezone
        today = timezone.now().date()
        return (self.effective_date <= today and 
                (self.end_date is None or self.end_date >= today) and 
                self.is_active)


class TaxReturn(models.Model):
    """Tax return filings"""
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        FILED = 'FILED', 'Filed'
        PAID = 'PAID', 'Paid'
        AMENDED = 'AMENDED', 'Amended'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    class ReturnType(models.TextChoices):
        FORM_1040 = 'FORM_1040', 'Form 1040 (Individual)'
        FORM_1120 = 'FORM_1120', 'Form 1120 (Corporation)'
        FORM_1120S = 'FORM_1120S', 'Form 1120S (S-Corp)'
        FORM_1065 = 'FORM_1065', 'Form 1065 (Partnership)'
        FORM_4562 = 'FORM_4562', 'Form 4562 (Depreciation)'
        FORM_4797 = 'FORM_4797', 'Form 4797 (Sales of Assets)'
        PROPERTY_TAX = 'PROPERTY_TAX', 'Property Tax Return'
        OTHER = 'OTHER', 'Other'
    
    return_number = models.CharField(max_length=50, unique=True, db_index=True)
    return_type = models.CharField(max_length=20, choices=ReturnType.choices, default=ReturnType.FORM_1120)
    tax_period_start = models.DateField(db_index=True)
    tax_period_end = models.DateField(db_index=True)
    filing_date = models.DateField(null=True, blank=True)
    due_date = models.DateField()
    jurisdiction = models.CharField(max_length=100, blank=True, null=True)
    
    # Tax calculations
    gross_income = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    deductions = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    taxable_income = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    total_tax = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    balance_due = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True, null=True)
    
    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tax_returns_created')
    filed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tax_returns_filed')
    
    class Meta:
        ordering = ['-tax_period_end', '-return_number']
        indexes = [
            models.Index(fields=['return_type', 'tax_period_end']),
            models.Index(fields=['status', 'due_date']),
        ]
    
    def __str__(self):
        return f"{self.return_type} - {self.return_number} ({self.tax_period_start} to {self.tax_period_end})"
    
    def calculate_balance_due(self):
        """Calculate balance due or refund"""
        self.balance_due = self.total_tax - self.paid_amount
        return self.balance_due
    
    def is_overdue(self):
        """Check if tax return is overdue"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.due_date < today and self.status not in [self.Status.PAID, self.Status.CANCELLED]


class AssetTaxInfo(models.Model):
    """Tax-specific information for fixed assets"""
    class TaxDepreciationMethod(models.TextChoices):
        MACRS = 'MACRS', 'MACRS (Modified Accelerated Cost Recovery System)'
        STRAIGHT_LINE = 'STRAIGHT_LINE', 'Straight Line'
        DECLINING_BALANCE = 'DECLINING_BALANCE', 'Declining Balance'
        SECTION_179 = 'SECTION_179', 'Section 179 Deduction'
        BONUS_DEPRECIATION = 'BONUS_DEPRECIATION', 'Bonus Depreciation'
    
    class PropertyClass(models.TextChoices):
        CLASS_3 = 'CLASS_3', '3-year property'
        CLASS_5 = 'CLASS_5', '5-year property'
        CLASS_7 = 'CLASS_7', '7-year property'
        CLASS_10 = 'CLASS_10', '10-year property'
        CLASS_15 = 'CLASS_15', '15-year property'
        CLASS_20 = 'CLASS_20', '20-year property'
        CLASS_27_5 = 'CLASS_27_5', '27.5-year property'
        CLASS_39 = 'CLASS_39', '39-year property'
        NON_DEPRECIABLE = 'NON_DEPRECIABLE', 'Non-depreciable'
    
    asset = models.OneToOneField(FixedAsset, on_delete=models.CASCADE, related_name='tax_info')
    
    # Tax depreciation settings
    tax_depreciation_method = models.CharField(
        max_length=30, 
        choices=TaxDepreciationMethod.choices, 
        default=TaxDepreciationMethod.MACRS,
        help_text="Depreciation method for tax purposes"
    )
    property_class = models.CharField(
        max_length=20, 
        choices=PropertyClass.choices, 
        default=PropertyClass.CLASS_5,
        help_text="IRS property class for depreciation"
    )
    tax_useful_life_years = models.IntegerField(
        null=True, 
        blank=True, 
        help_text="Useful life for tax depreciation (may differ from book life)"
    )
    
    # Tax basis and adjustments
    tax_basis = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        help_text="Tax basis for depreciation calculations"
    )
    section_179_deduction = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Section 179 deduction taken"
    )
    bonus_depreciation = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Bonus depreciation taken"
    )
    
    # Tax depreciation tracking
    tax_accumulated_depreciation = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Accumulated depreciation for tax purposes"
    )
    tax_book_value = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        help_text="Tax book value (basis - accumulated tax depreciation)"
    )
    
    # Property tax information
    assessed_value = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Assessed value for property tax"
    )
    property_tax_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        null=True, 
        blank=True,
        help_text="Property tax rate (as decimal, e.g., 0.0125 for 1.25%)"
    )
    property_tax_jurisdiction = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Property tax jurisdiction"
    )
    
    # Tax lots (for tracking multiple purchase lots)
    tax_lot_number = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Tax lot number for property records"
    )
    
    # Tax reporting flags
    reported_on_form_4562 = models.BooleanField(
        default=False,
        help_text="Has this asset been reported on Form 4562"
    )
    reported_on_form_4797 = models.BooleanField(
        default=False,
        help_text="Has this asset been reported on Form 4797 (sales)"
    )
    
    # Notes
    tax_notes = models.TextField(blank=True, null=True, help_text="Tax-specific notes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Asset Tax Information"
        verbose_name_plural = "Asset Tax Information"
    
    def __str__(self):
        return f"Tax Info for {self.asset.asset_code}"
    
    def calculate_tax_depreciation_schedule(self, year=None):
        """Calculate tax depreciation schedule for a specific year or all years"""
        from decimal import Decimal
        from django.utils import timezone
        
        if year is None:
            year = timezone.now().year
        
        # This is a simplified MACRS calculation
        # In a real system, this would be much more complex
        schedule = []
        
        if self.tax_depreciation_method == self.TaxDepreciationMethod.MACRS:
            # Simplified MACRS rates (half-year convention)
            macrs_rates = {
                self.PropertyClass.CLASS_3: [0.3333, 0.4445, 0.1481, 0.0741],
                self.PropertyClass.CLASS_5: [0.2000, 0.3200, 0.1920, 0.1152, 0.1152, 0.0576],
                self.PropertyClass.CLASS_7: [0.1429, 0.2449, 0.1749, 0.1249, 0.0893, 0.0892, 0.0893, 0.0446],
                self.PropertyClass.CLASS_10: [0.1000, 0.1800, 0.1440, 0.1152, 0.0922, 0.0737, 0.0655, 0.0655, 0.0656, 0.0328],
                self.PropertyClass.CLASS_15: [0.0500, 0.0950, 0.0855, 0.0770, 0.0693, 0.0623, 0.0590, 0.0590, 0.0591, 0.0590, 0.0591, 0.0590, 0.0591, 0.0590, 0.0295],
                self.PropertyClass.CLASS_20: [0.0375, 0.0722, 0.0668, 0.0618, 0.0571, 0.0529, 0.0489, 0.0452, 0.0416, 0.0383, 0.0351, 0.0323, 0.0295, 0.0269, 0.0244, 0.0224, 0.0205, 0.0188, 0.0172, 0.0094],
            }
            
            rates = macrs_rates.get(self.property_class, [0.2000, 0.3200, 0.1920, 0.1152, 0.1152, 0.0576])
            
            # Calculate depreciation for each year
            basis = self.tax_basis - self.section_179_deduction - self.bonus_depreciation
            
            for i, rate in enumerate(rates):
                dep_year = self.asset.purchase_date.year + i
                if dep_year > year:
                    break
                    
                annual_depr = basis * Decimal(str(rate))
                schedule.append({
                    'year': dep_year,
                    'rate': rate,
                    'annual_depreciation': annual_depr,
                    'accumulated_depreciation': sum(s['annual_depreciation'] for s in schedule)
                })
        
        return schedule
    
    def calculate_property_tax(self):
        """Calculate annual property tax"""
        if not self.assessed_value or not self.property_tax_rate:
            return Decimal('0.00')
        return self.assessed_value * self.property_tax_rate
    
    def get_tax_depreciation_status(self):
        """Get tax depreciation status"""
        if not self.asset.is_depreciated:
            return "Not depreciated for tax purposes"
        
        basis = self.tax_basis - self.section_179_deduction - self.bonus_depreciation
        if basis <= 0:
            return "Fully depreciated for tax purposes"
        
        depreciation_percentage = (self.tax_accumulated_depreciation / basis) * 100
        if depreciation_percentage >= 100:
            return "Fully depreciated for tax purposes"
        else:
            return f"{depreciation_percentage:.1f}% depreciated for tax purposes"


# ============================================================================
# BANK RECONCILIATION
# ============================================================================

class BankStatement(models.Model):
    """Bank statement entries for reconciliation"""
    class StatementType(models.TextChoices):
        DEPOSIT = 'DEPOSIT', 'Deposit'
        WITHDRAWAL = 'WITHDRAWAL', 'Withdrawal'
        CHECK = 'CHECK', 'Check'
        TRANSFER = 'TRANSFER', 'Transfer'
        FEE = 'FEE', 'Bank Fee'
        INTEREST = 'INTEREST', 'Interest'
        ADJUSTMENT = 'ADJUSTMENT', 'Adjustment'
    
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='bank_statements')
    statement_date = models.DateField(db_index=True)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    statement_type = models.CharField(max_length=20, choices=StatementType.choices)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    check_number = models.CharField(max_length=50, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, unique=True, db_index=True)
    
    # Reconciliation status
    is_reconciled = models.BooleanField(default=False)
    reconciled_date = models.DateField(null=True, blank=True)
    reconciled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reconciled_statements')
    
    # Link to related journal entry if reconciled
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.SET_NULL, null=True, blank=True, related_name='bank_statements')
    
    # Fixed Asset specific fields
    fixed_asset = models.ForeignKey(FixedAsset, on_delete=models.SET_NULL, null=True, blank=True, related_name='bank_statements')
    asset_transaction_type = models.CharField(max_length=50, blank=True, null=True, help_text="Purchase, Maintenance, Disposal, etc.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-statement_date', '-created_at']
        indexes = [
            models.Index(fields=['account', 'statement_date']),
            models.Index(fields=['is_reconciled', 'statement_date']),
            models.Index(fields=['transaction_id']),
        ]
    
    def __str__(self):
        return f"{self.account.code} - {self.statement_date} - ${self.amount}"


class BankReconciliation(models.Model):
    """Bank reconciliation records"""
    class Status(models.TextChoices):
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='reconciliations')
    reconciliation_date = models.DateField(db_index=True)
    statement_date = models.DateField()
    
    # Balances
    book_balance = models.DecimalField(max_digits=15, decimal_places=2)
    statement_balance = models.DecimalField(max_digits=15, decimal_places=2)
    adjusted_book_balance = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Reconciliation details
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    notes = models.TextField(blank=True, null=True)
    
    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reconciliations_created')
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reconciliations_completed')
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-reconciliation_date']
        unique_together = ['account', 'reconciliation_date']
        indexes = [
            models.Index(fields=['account', 'status']),
            models.Index(fields=['reconciliation_date']),
        ]
    
    def __str__(self):
        return f"{self.account.code} - {self.reconciliation_date}"
    
    def get_unreconciled_statements(self):
        """Get bank statements that are not yet reconciled for this period"""
        return BankStatement.objects.filter(
            account=self.account,
            statement_date__lte=self.statement_date,
            is_reconciled=False
        )
    
    def get_reconciled_statements(self):
        """Get bank statements that are reconciled for this period"""
        return BankStatement.objects.filter(
            account=self.account,
            statement_date__lte=self.statement_date,
            is_reconciled=True,
            reconciled_date__lte=self.reconciliation_date
        )
    
    def calculate_adjustments_total(self):
        """Calculate total adjustments needed"""
        return self.adjusted_book_balance - self.book_balance
    
    def is_balanced(self):
        """Check if reconciliation is balanced"""
        return self.adjusted_book_balance == self.statement_balance


class ReconciliationAdjustment(models.Model):
    """Adjustments made during bank reconciliation"""
    class AdjustmentType(models.TextChoices):
        DEPOSIT_IN_TRANSIT = 'DEPOSIT_IN_TRANSIT', 'Deposit in Transit'
        OUTSTANDING_CHECK = 'OUTSTANDING_CHECK', 'Outstanding Check'
        BANK_ERROR = 'BANK_ERROR', 'Bank Error'
        BOOK_ERROR = 'BOOK_ERROR', 'Book Error'
        INTEREST_EARNED = 'INTEREST_EARNED', 'Interest Earned'
        BANK_FEE = 'BANK_FEE', 'Bank Fee'
        OTHER = 'OTHER', 'Other'
    
    reconciliation = models.ForeignKey(BankReconciliation, on_delete=models.CASCADE, related_name='adjustments')
    adjustment_type = models.CharField(max_length=30, choices=AdjustmentType.choices)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    is_addition = models.BooleanField(default=True, help_text="True if adding to book balance, False if subtracting")
    
    # Link to journal entry if adjustment is posted
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.SET_NULL, null=True, blank=True, related_name='reconciliation_adjustments')
    
    # Fixed Asset specific
    fixed_asset = models.ForeignKey(FixedAsset, on_delete=models.SET_NULL, null=True, blank=True, related_name='reconciliation_adjustments')
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.reconciliation} - {self.adjustment_type} - ${self.amount}"
