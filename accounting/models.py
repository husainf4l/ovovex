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


# Extend the built-in User with a lightweight profile model to store extra details
class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=50, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    job_title = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    timezone = models.CharField(max_length=64, blank=True, null=True)
    language = models.CharField(max_length=16, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user.username}"


# Automatically create profile when a User is created
from django.db.models.signals import post_save
from django.contrib.auth.models import User


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


post_save.connect(create_user_profile, sender=User)


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


# ============================================================================
# AI INSIGHTS & ANALYTICS
# ============================================================================

class AIInsight(models.Model):
    """AI-generated insights and recommendations"""
    class InsightType(models.TextChoices):
        REVENUE_OPTIMIZATION = 'REVENUE_OPTIMIZATION', 'Revenue Optimization'
        COST_REDUCTION = 'COST_REDUCTION', 'Cost Reduction'
        CASH_FLOW_IMPROVEMENT = 'CASH_FLOW_IMPROVEMENT', 'Cash Flow Improvement'
        RISK_WARNING = 'RISK_WARNING', 'Risk Warning'
        TREND_ANALYSIS = 'TREND_ANALYSIS', 'Trend Analysis'
        PERFORMANCE_METRIC = 'PERFORMANCE_METRIC', 'Performance Metric'
        COMPLIANCE_ALERT = 'COMPLIANCE_ALERT', 'Compliance Alert'
        MARKET_INSIGHT = 'MARKET_INSIGHT', 'Market Insight'
    
    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRITICAL', 'Critical'
    
    insight_id = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    insight_type = models.CharField(max_length=30, choices=InsightType.choices)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    
    # AI confidence and impact
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, help_text="AI confidence score (0-100)")
    impact_score = models.DecimalField(max_digits=15, decimal_places=2, help_text="Potential impact score (0-100)")
    potential_savings = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Related data
    related_accounts = models.ManyToManyField(Account, blank=True, related_name='ai_insights')
    related_customers = models.ManyToManyField(Customer, blank=True, related_name='ai_insights')
    related_vendors = models.ManyToManyField(Vendor, blank=True, related_name='ai_insights')
    
    # Status and tracking
    is_active = models.BooleanField(default=True)
    is_implemented = models.BooleanField(default=False)
    implemented_date = models.DateField(null=True, blank=True)
    feedback_rating = models.IntegerField(null=True, blank=True, help_text="User feedback rating (1-5)")
    
    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    ai_model_version = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        ordering = ['-generated_at', '-priority']
        indexes = [
            models.Index(fields=['insight_type', 'priority']),
            models.Index(fields=['is_active', 'generated_at']),
        ]
    
    def __str__(self):
        return f"{self.insight_id} - {self.title}"


class AIPrediction(models.Model):
    """AI predictions for future trends and values"""
    class PredictionType(models.TextChoices):
        REVENUE_FORECAST = 'REVENUE_FORECAST', 'Revenue Forecast'
        EXPENSE_FORECAST = 'EXPENSE_FORECAST', 'Expense Forecast'
        CASH_FLOW_FORECAST = 'CASH_FLOW_FORECAST', 'Cash Flow Forecast'
        PROFIT_FORECAST = 'PROFIT_FORECAST', 'Profit Forecast'
        BUDGET_VARIANCE = 'BUDGET_VARIANCE', 'Budget Variance'
        SEASONAL_TREND = 'SEASONAL_TREND', 'Seasonal Trend'
        MARKET_DEMAND = 'MARKET_DEMAND', 'Market Demand'
    
    prediction_id = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    prediction_type = models.CharField(max_length=30, choices=PredictionType.choices)
    
    # Prediction details
    predicted_value = models.DecimalField(max_digits=15, decimal_places=2)
    confidence_interval_lower = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    confidence_interval_upper = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    prediction_date = models.DateField()
    forecast_period_months = models.IntegerField(default=1)
    
    # Historical context
    actual_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    accuracy_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Related data
    related_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_predictions')
    
    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    ai_model_version = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        ordering = ['-prediction_date', '-generated_at']
        indexes = [
            models.Index(fields=['prediction_type', 'prediction_date']),
        ]
    
    def __str__(self):
        return f"{self.prediction_id} - {self.title}"


class AIModel(models.Model):
    """AI models and their performance tracking"""
    class ModelType(models.TextChoices):
        FORECASTING = 'FORECASTING', 'Forecasting'
        ANOMALY_DETECTION = 'ANOMALY_DETECTION', 'Anomaly Detection'
        CLASSIFICATION = 'CLASSIFICATION', 'Classification'
        REGRESSION = 'REGRESSION', 'Regression'
        NLP = 'NLP', 'Natural Language Processing'
    
    class Status(models.TextChoices):
        TRAINING = 'TRAINING', 'Training'
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        DEPRECATED = 'DEPRECATED', 'Deprecated'
    
    model_name = models.CharField(max_length=100, unique=True)
    model_type = models.CharField(max_length=30, choices=ModelType.choices)
    version = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    
    # Performance metrics
    accuracy_score = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    precision_score = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    recall_score = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    f1_score = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    
    # Training data
    training_data_size = models.IntegerField(null=True, blank=True)
    last_trained_at = models.DateTimeField(null=True, blank=True)
    training_duration_hours = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Usage statistics
    total_predictions = models.IntegerField(default=0)
    successful_predictions = models.IntegerField(default=0)
    
    # Metadata
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['model_name', 'version']
    
    def __str__(self):
        return f"{self.model_name} v{self.version}"
    
    def get_success_rate(self):
        """Calculate prediction success rate"""
        if self.total_predictions == 0:
            return Decimal('0.00')
        return (Decimal(self.successful_predictions) / Decimal(self.total_predictions)) * 100


# ============================================================================
# ANOMALY DETECTION
# ============================================================================

class AnomalyAlert(models.Model):
    """Detected anomalies in financial data"""
    class AnomalyType(models.TextChoices):
        TRANSACTION_AMOUNT = 'TRANSACTION_AMOUNT', 'Unusual Transaction Amount'
        FREQUENCY_SPIKE = 'FREQUENCY_SPIKE', 'Transaction Frequency Spike'
        VENDOR_PATTERN = 'VENDOR_PATTERN', 'Unusual Vendor Pattern'
        CUSTOMER_PATTERN = 'CUSTOMER_PATTERN', 'Unusual Customer Pattern'
        ACCOUNT_BALANCE = 'ACCOUNT_BALANCE', 'Account Balance Anomaly'
        BUDGET_VARIANCE = 'BUDGET_VARIANCE', 'Budget Variance Anomaly'
        CASH_FLOW_IRREGULARITY = 'CASH_FLOW_IRREGULARITY', 'Cash Flow Irregularity'
        EXPENSE_SPIKE = 'EXPENSE_SPIKE', 'Expense Spike'
        REVENUE_DROP = 'REVENUE_DROP', 'Revenue Drop'
    
    class Severity(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRITICAL', 'Critical'
    
    class Status(models.TextChoices):
        DETECTED = 'DETECTED', 'Detected'
        INVESTIGATING = 'INVESTIGATING', 'Investigating'
        RESOLVED = 'RESOLVED', 'Resolved'
        FALSE_POSITIVE = 'FALSE_POSITIVE', 'False Positive'
        IGNORED = 'IGNORED', 'Ignored'
    
    alert_id = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    anomaly_type = models.CharField(max_length=30, choices=AnomalyType.choices)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DETECTED)
    
    # Anomaly details
    detected_value = models.DecimalField(max_digits=15, decimal_places=2)
    expected_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    deviation_percentage = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Related entities
    related_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='anomaly_alerts')
    related_customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='anomaly_alerts')
    related_vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='anomaly_alerts')
    related_journal_entry = models.ForeignKey(JournalEntry, on_delete=models.SET_NULL, null=True, blank=True, related_name='anomaly_alerts')
    
    # Investigation and resolution
    investigation_notes = models.TextField(blank=True, null=True)
    resolution_notes = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_anomalies')
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_anomalies')
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    detected_at = models.DateTimeField(auto_now_add=True)
    ai_model_version = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        ordering = ['-detected_at', '-severity']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['anomaly_type', 'detected_at']),
        ]
    
    def __str__(self):
        return f"{self.alert_id} - {self.title}"


class AnomalyDetectionModel(models.Model):
    """Performance tracking for anomaly detection models"""
    class ModelType(models.TextChoices):
        STATISTICAL = 'STATISTICAL', 'Statistical'
        MACHINE_LEARNING = 'MACHINE_LEARNING', 'Machine Learning'
        RULE_BASED = 'RULE_BASED', 'Rule Based'
        HYBRID = 'HYBRID', 'Hybrid'
    
    model_name = models.CharField(max_length=100, unique=True)
    model_type = models.CharField(max_length=20, choices=ModelType.choices)
    version = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    
    # Performance metrics
    total_alerts_generated = models.IntegerField(default=0)
    true_positives = models.IntegerField(default=0)
    false_positives = models.IntegerField(default=0)
    true_negatives = models.IntegerField(default=0)
    false_negatives = models.IntegerField(default=0)
    
    # Thresholds
    sensitivity_threshold = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.80'))
    specificity_threshold = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.85'))
    
    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['model_name', 'version']
    
    def __str__(self):
        return f"{self.model_name} v{self.version}"
    
    def get_precision(self):
        """Calculate precision (true positives / (true positives + false positives))"""
        denominator = self.true_positives + self.false_positives
        return (self.true_positives / denominator * 100) if denominator > 0 else Decimal('0.00')
    
    def get_recall(self):
        """Calculate recall (true positives / (true positives + false negatives))"""
        denominator = self.true_positives + self.false_negatives
        return (self.true_positives / denominator * 100) if denominator > 0 else Decimal('0.00')
    
    def get_accuracy(self):
        """Calculate accuracy"""
        total = self.true_positives + self.true_negatives + self.false_positives + self.false_negatives
        correct = self.true_positives + self.true_negatives
        return (correct / total * 100) if total > 0 else Decimal('0.00')


# ============================================================================
# NOTIFICATIONS
# ============================================================================

class Notification(models.Model):
    """System notifications for users"""
    class NotificationType(models.TextChoices):
        CRITICAL = 'CRITICAL', 'Critical'
        WARNING = 'WARNING', 'Warning'
        INFO = 'INFO', 'Info'
        SUCCESS = 'SUCCESS', 'Success'
        AI_INSIGHT = 'AI_INSIGHT', 'AI Insight'
        SYSTEM = 'SYSTEM', 'System'
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.INFO
    )
    is_read = models.BooleanField(default=False)
    action_url = models.CharField(max_length=500, blank=True, null=True)
    action_text = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
            models.Index(fields=['notification_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

# ============================================================================
# DOCUMENT MANAGEMENT
# ============================================================================

class DocumentCategory(models.Model):
    """Document categories for organization"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    color_code = models.CharField(max_length=7, default='#3498db', help_text="Hex color code for UI")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Document Categories'
    
    def __str__(self):
        return self.name


class Document(models.Model):
    """Document management system"""
    class DocumentType(models.TextChoices):
        INVOICE = 'INVOICE', 'Invoice'
        RECEIPT = 'RECEIPT', 'Receipt'
        CONTRACT = 'CONTRACT', 'Contract'
        STATEMENT = 'STATEMENT', 'Financial Statement'
        TAX_DOCUMENT = 'TAX_DOCUMENT', 'Tax Document'
        LEGAL_DOCUMENT = 'LEGAL_DOCUMENT', 'Legal Document'
        CORRESPONDENCE = 'CORRESPONDENCE', 'Correspondence'
        REPORT = 'REPORT', 'Report'
        OTHER = 'OTHER', 'Other'
    
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        FINAL = 'FINAL', 'Final'
        ARCHIVED = 'ARCHIVED', 'Archived'
        DELETED = 'DELETED', 'Deleted'
    
    document_id = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    document_type = models.CharField(max_length=20, choices=DocumentType.choices, default=DocumentType.OTHER)
    category = models.ForeignKey(DocumentCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    
    # File information
    file_name = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='documents/%Y/%m/')
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    mime_type = models.CharField(max_length=100)
    
    # Version control
    version = models.CharField(max_length=20, default='1.0')
    parent_document = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='versions')
    
    # Status and security
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.FINAL)
    is_confidential = models.BooleanField(default=False)
    retention_period_years = models.IntegerField(default=7, help_text="Document retention period in years")
    
    # Related entities
    related_customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    related_vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    related_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    related_invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    related_bill = models.ForeignKey(Bill, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    
    # Tags and search
    tags = models.CharField(max_length=500, blank=True, null=True, help_text="Comma-separated tags")
    
    # Audit trail
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='modified_documents')
    last_modified_at = models.DateTimeField(auto_now=True)
    
    # Access control
    view_permissions = models.ManyToManyField(User, blank=True, related_name='viewable_documents', help_text="Users who can view this document")
    edit_permissions = models.ManyToManyField(User, blank=True, related_name='editable_documents', help_text="Users who can edit this document")
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['document_type', 'status']),
            models.Index(fields=['category', 'uploaded_at']),
            models.Index(fields=['uploaded_by', 'uploaded_at']),
        ]
    
    def __str__(self):
        return f"{self.document_id} - {self.title}"
    
    def get_file_size_display(self):
        """Return human-readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def is_expired(self):
        """Check if document has expired based on retention period"""
        from django.utils import timezone
        expiry_date = self.uploaded_at + timezone.timedelta(days=self.retention_period_years * 365)
        return timezone.now() > expiry_date


class DocumentShare(models.Model):
    """Document sharing and collaboration"""
    class AccessLevel(models.TextChoices):
        VIEW = 'VIEW', 'View Only'
        COMMENT = 'COMMENT', 'View and Comment'
        EDIT = 'EDIT', 'Edit'
        FULL = 'FULL', 'Full Access'
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='shares')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_documents')
    access_level = models.CharField(max_length=20, choices=AccessLevel.choices, default=AccessLevel.VIEW)
    
    # Sharing details
    shared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='shared_by_documents')
    shared_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    message = models.TextField(blank=True, null=True, help_text="Message from sharer")
    
    # Access tracking
    last_accessed_at = models.DateTimeField(null=True, blank=True)
    access_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['document', 'shared_with']
        ordering = ['-shared_at']
    
    def __str__(self):
        return f"{self.document.title} shared with {self.shared_with.username}"
    
    def is_expired(self):
        """Check if share has expired"""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at


# ============================================================================
# PURCHASE ORDERS
# ============================================================================

class PurchaseOrder(models.Model):
    """Purchase orders for procurement"""
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PENDING_APPROVAL = 'PENDING_APPROVAL', 'Pending Approval'
        APPROVED = 'APPROVED', 'Approved'
        ORDERED = 'ORDERED', 'Ordered'
        PARTIALLY_RECEIVED = 'PARTIALLY_RECEIVED', 'Partially Received'
        RECEIVED = 'RECEIVED', 'Received'
        CANCELLED = 'CANCELLED', 'Cancelled'
        CLOSED = 'CLOSED', 'Closed'
    
    po_number = models.CharField(max_length=50, unique=True, db_index=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='purchase_orders')
    order_date = models.DateField(db_index=True)
    required_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    
    # Financial details
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Shipping and delivery
    ship_to_address = models.TextField(blank=True, null=True)
    shipping_method = models.CharField(max_length=100, blank=True, null=True)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    delivery_terms = models.TextField(blank=True, null=True)
    
    # Approval workflow
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='requested_pos')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_pos')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Notes and references
    notes = models.TextField(blank=True, null=True)
    vendor_po_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-order_date', '-po_number']
        indexes = [
            models.Index(fields=['vendor', 'status']),
            models.Index(fields=['status', 'order_date']),
        ]
    
    def __str__(self):
        return f"PO-{self.po_number} - {self.vendor.company_name}"


class PurchaseOrderLine(models.Model):
    """Purchase order line items"""
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='lines')
    item_description = models.CharField(max_length=255)
    
    # Item details (can link to inventory or be free-form)
    inventory_item = models.ForeignKey('InventoryItem', on_delete=models.SET_NULL, null=True, blank=True, related_name='po_lines')
    
    # Quantities and pricing
    quantity_ordered = models.DecimalField(max_digits=12, decimal_places=2)
    quantity_received = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Delivery tracking
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.purchase_order.po_number} - {self.item_description[:50]}"
    
    def get_quantity_remaining(self):
        """Get remaining quantity to be received"""
        return self.quantity_ordered - self.quantity_received


# ============================================================================
# AUDIT & COMPLIANCE
# ============================================================================

class AuditTrail(models.Model):
    """Comprehensive audit trail for all system activities"""
    class ActionType(models.TextChoices):
        CREATE = 'CREATE', 'Create'
        UPDATE = 'UPDATE', 'Update'
        DELETE = 'DELETE', 'Delete'
        VIEW = 'VIEW', 'View'
        EXPORT = 'EXPORT', 'Export'
        IMPORT = 'IMPORT', 'Import'
        APPROVE = 'APPROVE', 'Approve'
        REJECT = 'REJECT', 'Reject'
        LOGIN = 'LOGIN', 'Login'
        LOGOUT = 'LOGOUT', 'Logout'
    
    class EntityType(models.TextChoices):
        ACCOUNT = 'ACCOUNT', 'Account'
        JOURNAL_ENTRY = 'JOURNAL_ENTRY', 'Journal Entry'
        INVOICE = 'INVOICE', 'Invoice'
        BILL = 'BILL', 'Bill'
        CUSTOMER = 'CUSTOMER', 'Customer'
        VENDOR = 'VENDOR', 'Vendor'
        USER = 'USER', 'User'
        FIXED_ASSET = 'FIXED_ASSET', 'Fixed Asset'
        BUDGET = 'BUDGET', 'Budget'
        EXPENSE = 'EXPENSE', 'Expense'
        TAX_RETURN = 'TAX_RETURN', 'Tax Return'
        DOCUMENT = 'DOCUMENT', 'Document'
        INVENTORY = 'INVENTORY', 'Inventory'
        PURCHASE_ORDER = 'PURCHASE_ORDER', 'Purchase Order'
        OTHER = 'OTHER', 'Other'
    
    # Audit details
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_actions')
    action_type = models.CharField(max_length=20, choices=ActionType.choices)
    entity_type = models.CharField(max_length=20, choices=EntityType.choices)
    entity_id = models.CharField(max_length=100, db_index=True)
    entity_name = models.CharField(max_length=255, blank=True, null=True)
    
    # Change details
    old_values = models.JSONField(null=True, blank=True, help_text="Previous values (JSON)")
    new_values = models.JSONField(null=True, blank=True, help_text="New values (JSON)")
    changes_description = models.TextField(blank=True, null=True)
    
    # Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['action_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username if self.user else 'System'} - {self.action_type} - {self.entity_type} - {self.timestamp}"


class ComplianceCheck(models.Model):
    """Compliance checks and regulatory requirements"""
    class ComplianceType(models.TextChoices):
        SOX = 'SOX', 'Sarbanes-Oxley Act'
        IFRS = 'IFRS', 'International Financial Reporting Standards'
        GAAP = 'GAAP', 'Generally Accepted Accounting Principles'
        TAX_COMPLIANCE = 'TAX_COMPLIANCE', 'Tax Compliance'
        DATA_PRIVACY = 'DATA_PRIVACY', 'Data Privacy (GDPR/CCPA)'
        INTERNAL_CONTROLS = 'INTERNAL_CONTROLS', 'Internal Controls'
        INDUSTRY_SPECIFIC = 'INDUSTRY_SPECIFIC', 'Industry Specific'
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLIANT = 'COMPLIANT', 'Compliant'
        NON_COMPLIANT = 'NON_COMPLIANT', 'Non-Compliant'
        EXEMPT = 'EXEMPT', 'Exempt'
    
    check_id = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    compliance_type = models.CharField(max_length=20, choices=ComplianceType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # Requirements and deadlines
    requirement_details = models.TextField(blank=True, null=True)
    due_date = models.DateField(null=True, blank=True)
    frequency = models.CharField(max_length=50, blank=True, null=True, help_text="Monthly, Quarterly, Annual, etc.")
    
    # Assessment details
    risk_level = models.CharField(max_length=20, choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('CRITICAL', 'Critical')], default='MEDIUM')
    last_assessed_at = models.DateTimeField(null=True, blank=True)
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='compliance_assessments')
    assessment_notes = models.TextField(blank=True, null=True)
    
    # Remediation
    remediation_required = models.BooleanField(default=False)
    remediation_plan = models.TextField(blank=True, null=True)
    remediation_due_date = models.DateField(null=True, blank=True)
    remediation_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Related entities
    related_accounts = models.ManyToManyField(Account, blank=True, related_name='compliance_checks')
    related_documents = models.ManyToManyField(Document, blank=True, related_name='compliance_checks')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-due_date', '-created_at']
        indexes = [
            models.Index(fields=['compliance_type', 'status']),
            models.Index(fields=['due_date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.check_id} - {self.title}"
    
    def is_overdue(self):
        """Check if compliance check is overdue"""
        if not self.due_date:
            return False
        from django.utils import timezone
        return timezone.now().date() > self.due_date and self.status not in [self.Status.COMPLIANT, self.Status.EXEMPT]


class ComplianceViolation(models.Model):
    """Compliance violations and issues"""
    class Severity(models.TextChoices):
        MINOR = 'MINOR', 'Minor'
        MODERATE = 'MODERATE', 'Moderate'
        MAJOR = 'MAJOR', 'Major'
        CRITICAL = 'CRITICAL', 'Critical'
    
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        INVESTIGATING = 'INVESTIGATING', 'Investigating'
        REMEDIATED = 'REMEDIATED', 'Remediated'
        CLOSED = 'CLOSED', 'Closed'
        DISMISSED = 'DISMISSED', 'Dismissed'
    
    violation_id = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MODERATE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    
    # Related compliance check
    compliance_check = models.ForeignKey(ComplianceCheck, on_delete=models.SET_NULL, null=True, blank=True, related_name='violations')
    
    # Violation details
    detected_at = models.DateTimeField(auto_now_add=True)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_violations')
    
    # Investigation and resolution
    investigation_notes = models.TextField(blank=True, null=True)
    root_cause = models.TextField(blank=True, null=True)
    remediation_actions = models.TextField(blank=True, null=True)
    preventive_measures = models.TextField(blank=True, null=True)
    
    # Resolution tracking
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_violations')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_violations')
    
    # Financial impact
    financial_impact = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    regulatory_fine = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Related entities
    related_accounts = models.ManyToManyField(Account, blank=True, related_name='compliance_violations')
    related_documents = models.ManyToManyField(Document, blank=True, related_name='compliance_violations')
    
    class Meta:
        ordering = ['-detected_at', '-severity']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['compliance_check', 'status']),
        ]
    
    def __str__(self):
        return f"{self.violation_id} - {self.title}"


# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

class InventoryCategory(models.Model):
    """Inventory item categories"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Inventory Categories'
    
    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    """Inventory items tracking"""
    class UnitOfMeasure(models.TextChoices):
        EACH = 'EACH', 'Each'
        KG = 'KG', 'Kilogram'
        LB = 'LB', 'Pound'
        LITER = 'LITER', 'Liter'
        GALLON = 'GALLON', 'Gallon'
        METER = 'METER', 'Meter'
        FOOT = 'FOOT', 'Foot'
        SQUARE_METER = 'SQUARE_METER', 'Square Meter'
        CUBIC_METER = 'CUBIC_METER', 'Cubic Meter'
        BOX = 'BOX', 'Box'
        CASE = 'CASE', 'Case'
        PALLET = 'PALLET', 'Pallet'
    
    item_code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(InventoryCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    
    # Stock levels
    current_stock = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    minimum_stock = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    maximum_stock = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    reorder_point = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Pricing
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    unit_of_measure = models.CharField(max_length=20, choices=UnitOfMeasure.choices, default=UnitOfMeasure.EACH)
    
    # Supplier information
    primary_vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='supplied_items')
    vendor_item_code = models.CharField(max_length=50, blank=True, null=True)
    
    # Location and tracking
    location = models.CharField(max_length=255, blank=True, null=True)
    barcode = models.CharField(max_length=100, blank=True, null=True, unique=True)
    serial_number_required = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_taxable = models.BooleanField(default=True)
    
    # Financial tracking
    total_value = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['item_code']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['current_stock', 'minimum_stock']),
        ]
    
    def __str__(self):
        return f"{self.item_code} - {self.name}"
    
    def get_stock_status(self):
        """Get stock status based on current levels"""
        if self.current_stock <= 0:
            return "Out of Stock"
        elif self.current_stock <= self.reorder_point:
            return "Low Stock"
        elif self.maximum_stock and self.current_stock >= self.maximum_stock:
            return "Overstock"
        else:
            return "In Stock"
    
    def get_total_value(self):
        """Calculate total inventory value"""
        return self.current_stock * self.unit_cost
    
    def needs_reorder(self):
        """Check if item needs reordering"""
        return self.current_stock <= self.reorder_point


class InventoryTransaction(models.Model):
    """Inventory transactions (in/out/adjustments)"""
    class TransactionType(models.TextChoices):
        RECEIPT = 'RECEIPT', 'Stock Receipt'
        ISSUE = 'ISSUE', 'Stock Issue'
        ADJUSTMENT = 'ADJUSTMENT', 'Stock Adjustment'
        TRANSFER = 'TRANSFER', 'Stock Transfer'
        RETURN = 'RETURN', 'Stock Return'
        DAMAGE = 'DAMAGE', 'Damage/Loss'
    
    item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # References
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    related_bill = models.ForeignKey(Bill, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_transactions')
    related_invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_transactions')
    
    # Location tracking
    from_location = models.CharField(max_length=255, blank=True, null=True)
    to_location = models.CharField(max_length=255, blank=True, null=True)
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['item', 'created_at']),
            models.Index(fields=['transaction_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.item.item_code} - {self.transaction_type} - {self.quantity}"


# Dashboard Models
class DashboardKPIMetric(models.Model):
    """Key Performance Indicators for dashboard"""
    class MetricType(models.TextChoices):
        CURRENCY = 'CURRENCY', 'Currency'
        PERCENTAGE = 'PERCENTAGE', 'Percentage'
        NUMBER = 'NUMBER', 'Number'
        RATIO = 'RATIO', 'Ratio'
    
    class TrendDirection(models.TextChoices):
        UP = 'UP', 'Increasing'
        DOWN = 'DOWN', 'Decreasing'
        STABLE = 'STABLE', 'Stable'
    
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    metric_type = models.CharField(max_length=20, choices=MetricType.choices, default=MetricType.CURRENCY)
    
    # Current values
    current_value = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    previous_value = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Trend calculation
    trend_direction = models.CharField(max_length=10, choices=TrendDirection.choices, default=TrendDirection.STABLE)
    trend_percentage = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    
    # Formatting
    prefix = models.CharField(max_length=10, blank=True, null=True)  # e.g., "$", "€"
    suffix = models.CharField(max_length=10, blank=True, null=True)  # e.g., "%", "units"
    
    # Update settings
    auto_update = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Display settings
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Dashboard KPI Metric'
        verbose_name_plural = 'Dashboard KPI Metrics'
    
    def __str__(self):
        return self.display_name
    
    def calculate_trend(self):
        """Calculate trend direction and percentage"""
        if self.previous_value == 0:
            self.trend_percentage = Decimal('0.00')
            self.trend_direction = self.TrendDirection.STABLE
        else:
            change = ((self.current_value - self.previous_value) / self.previous_value) * 100
            self.trend_percentage = change
            
            if change > 5:
                self.trend_direction = self.TrendDirection.UP
            elif change < -5:
                self.trend_direction = self.TrendDirection.DOWN
            else:
                self.trend_direction = self.TrendDirection.STABLE
    
    def get_formatted_value(self):
        """Return formatted value with prefix/suffix"""
        if self.metric_type == self.MetricType.CURRENCY:
            formatted = f"{self.prefix or '$'}{self.current_value:,.2f}{self.suffix or ''}"
        elif self.metric_type == self.MetricType.PERCENTAGE:
            formatted = f"{self.current_value:.1f}{self.suffix or '%'}"
        elif self.metric_type == self.MetricType.RATIO:
            formatted = f"{self.current_value:.2f}{self.suffix or ''}"
        else:
            formatted = f"{self.prefix or ''}{int(self.current_value)}{self.suffix or ''}"
        
        return formatted


class DashboardWidget(models.Model):
    """Dashboard widgets/cards"""
    class WidgetType(models.TextChoices):
        KPI_CARD = 'KPI_CARD', 'KPI Card'
        CHART = 'CHART', 'Chart'
        TABLE = 'TABLE', 'Data Table'
        SUMMARY = 'SUMMARY', 'Summary Card'
        ALERT = 'ALERT', 'Alert/Notification'
    
    class ChartType(models.TextChoices):
        LINE = 'LINE', 'Line Chart'
        BAR = 'BAR', 'Bar Chart'
        PIE = 'PIE', 'Pie Chart'
        AREA = 'AREA', 'Area Chart'
        DONUT = 'DONUT', 'Donut Chart'
    
    title = models.CharField(max_length=200)
    widget_type = models.CharField(max_length=20, choices=WidgetType.choices)
    chart_type = models.CharField(max_length=10, choices=ChartType.choices, blank=True, null=True)
    
    # Position and layout
    position_x = models.PositiveIntegerField(default=0)
    position_y = models.PositiveIntegerField(default=0)
    width = models.PositiveIntegerField(default=1)  # Grid columns
    height = models.PositiveIntegerField(default=1)  # Grid rows
    
    # Data source
    data_source = models.CharField(max_length=100, blank=True, null=True)  # Model or API endpoint
    data_filter = models.JSONField(blank=True, null=True)  # Filter parameters
    
    # Configuration
    config = models.JSONField(blank=True, null=True)  # Widget-specific settings
    refresh_interval = models.PositiveIntegerField(default=300)  # seconds
    
    # Status
    is_active = models.BooleanField(default=True)
    is_visible = models.BooleanField(default=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['position_y', 'position_x']
        verbose_name = 'Dashboard Widget'
        verbose_name_plural = 'Dashboard Widgets'
    
    def __str__(self):
        return f"{self.title} ({self.widget_type})"


class DashboardChartData(models.Model):
    """Chart data points for dashboard charts"""
    widget = models.ForeignKey(DashboardWidget, on_delete=models.CASCADE, related_name='chart_data')
    
    # Data point
    label = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    category = models.CharField(max_length=100, blank=True, null=True)
    
    # Time series data
    date = models.DateField(blank=True, null=True)
    period = models.CharField(max_length=20, blank=True, null=True)  # 'daily', 'weekly', 'monthly'
    
    # Additional metadata
    color = models.CharField(max_length=7, blank=True, null=True)  # Hex color
    metadata = models.JSONField(blank=True, null=True)
    
    # Ordering
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['sort_order', 'date', 'label']
        unique_together = ['widget', 'label', 'date']
        verbose_name = 'Dashboard Chart Data'
        verbose_name_plural = 'Dashboard Chart Data'
    
    def __str__(self):
        return f"{self.widget.title} - {self.label}: {self.value}"


class DashboardAlert(models.Model):
    """Dashboard alerts and notifications"""
    class AlertType(models.TextChoices):
        INFO = 'INFO', 'Information'
        WARNING = 'WARNING', 'Warning'
        ERROR = 'ERROR', 'Error'
        SUCCESS = 'SUCCESS', 'Success'
    
    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRITICAL', 'Critical'
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    alert_type = models.CharField(max_length=10, choices=AlertType.choices, default=AlertType.INFO)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    
    # Related data
    related_model = models.CharField(max_length=100, blank=True, null=True)  # e.g., 'Invoice', 'Bill'
    related_id = models.PositiveIntegerField(blank=True, null=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Auto-dismiss
    auto_dismiss = models.BooleanField(default=False)
    dismiss_after_hours = models.PositiveIntegerField(default=24)
    
    # Recipients
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboard_alerts')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)
    dismissed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Dashboard Alert'
        verbose_name_plural = 'Dashboard Alerts'
    
    def __str__(self):
        return f"{self.alert_type} - {self.title}"


class DashboardActivity(models.Model):
    """Recent activity feed for dashboard"""
    class ActivityType(models.TextChoices):
        INVOICE_CREATED = 'INVOICE_CREATED', 'Invoice Created'
        INVOICE_PAID = 'INVOICE_PAID', 'Invoice Paid'
        BILL_CREATED = 'BILL_CREATED', 'Bill Created'
        BILL_PAID = 'BILL_PAID', 'Bill Paid'
        PAYMENT_RECEIVED = 'PAYMENT_RECEIVED', 'Payment Received'
        PAYMENT_MADE = 'PAYMENT_MADE', 'Payment Made'
        JOURNAL_POSTED = 'JOURNAL_POSTED', 'Journal Entry Posted'
        EXPENSE_APPROVED = 'EXPENSE_APPROVED', 'Expense Approved'
        ASSET_ADDED = 'ASSET_ADDED', 'Asset Added'
        BUDGET_CREATED = 'BUDGET_CREATED', 'Budget Created'
        TAX_RETURN_FILED = 'TAX_RETURN_FILED', 'Tax Return Filed'
    
    activity_type = models.CharField(max_length=30, choices=ActivityType.choices)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Related objects
    related_model = models.CharField(max_length=100, blank=True, null=True)
    related_id = models.PositiveIntegerField(blank=True, null=True)
    
    # Amounts (if applicable)
    amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, default='USD')
    
    # User who performed the activity
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='dashboard_activities')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Dashboard Activity'
        verbose_name_plural = 'Dashboard Activities'
    
    def __str__(self):
        return f"{self.activity_type} - {self.title}"


class DashboardSettings(models.Model):
    """User-specific dashboard settings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard_settings')
    
    # Layout preferences
    layout_columns = models.PositiveIntegerField(default=4)
    theme = models.CharField(max_length=20, default='light')
    
    # Widget visibility
    visible_widgets = models.JSONField(default=list)  # List of widget IDs
    hidden_widgets = models.JSONField(default=list)  # List of hidden widget IDs
    
    # Refresh settings
    auto_refresh = models.BooleanField(default=True)
    refresh_interval = models.PositiveIntegerField(default=300)  # seconds
    
    # Notification preferences
    email_alerts = models.BooleanField(default=True)
    browser_notifications = models.BooleanField(default=True)
    
    # Date range preferences
    default_date_range = models.CharField(max_length=20, default='last_30_days')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Dashboard Settings'
        verbose_name_plural = 'Dashboard Settings'
    
    def __str__(self):
        return f"Dashboard settings for {self.user.username}"


# Pricing and Billing Models

class PricingPlan(models.Model):
    """
    Defines pricing plans available to users
    """
    PLAN_TYPES = [
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]

    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    name = models.CharField(max_length=50, unique=True)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField()
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES, default='monthly')

    # Plan limits
    max_users = models.PositiveIntegerField(default=1)
    max_invoices_per_month = models.PositiveIntegerField(default=5)
    max_storage_gb = models.PositiveIntegerField(default=1)
    api_access = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)
    advanced_analytics = models.BooleanField(default=False)
    custom_integrations = models.BooleanField(default=False)

    # Features
    features = models.JSONField(default=dict, help_text="JSON object containing plan features")

    # Trial settings
    trial_days = models.PositiveIntegerField(default=14)
    is_active = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['price_monthly']
        verbose_name = 'Pricing Plan'
        verbose_name_plural = 'Pricing Plans'

    def __str__(self):
        return f"{self.display_name} (${self.price_monthly}/month)"

    def get_yearly_price(self):
        """Calculate yearly price with discount"""
        if self.price_yearly > 0:
            return self.price_yearly
        # 20% discount for yearly billing
        return self.price_monthly * 12 * Decimal('0.8')

    @property
    def is_free_plan(self):
        return self.plan_type == 'free'


class Subscription(models.Model):
    """
    Tracks user subscriptions to pricing plans
    """
    STATUS_CHOICES = [
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('expired', 'Expired'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(PricingPlan, on_delete=models.PROTECT, related_name='subscriptions')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
    billing_cycle = models.CharField(max_length=20, choices=PricingPlan.BILLING_CYCLE_CHOICES, default='monthly')

    # Trial tracking
    trial_start_date = models.DateTimeField(auto_now_add=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)

    # Subscription dates
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)

    # Usage tracking
    invoices_used_this_month = models.PositiveIntegerField(default=0)
    storage_used_gb = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    canceled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

    def __str__(self):
        return f"{self.user.username} - {self.plan.display_name} ({self.status})"

    def is_trial_active(self):
        """Check if trial is still active"""
        if self.status != 'trial':
            return False
        return self.trial_end_date > models.timezone.now() if self.trial_end_date else False

    def days_left_in_trial(self):
        """Return days left in trial"""
        if not self.is_trial_active():
            return 0
        return (self.trial_end_date - models.timezone.now()).days

    def can_create_invoice(self):
        """Check if user can create more invoices this month"""
        if self.plan.max_invoices_per_month == 0:  # Unlimited
            return True
        return self.invoices_used_this_month < self.plan.max_invoices_per_month


class PaymentMethod(models.Model):
    """
    Stores user payment methods
    """
    PAYMENT_TYPES = [
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
        ('bank', 'Bank Transfer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)

    # Card details (encrypted in production)
    card_last4 = models.CharField(max_length=4, blank=True, null=True)
    card_brand = models.CharField(max_length=20, blank=True, null=True)
    card_exp_month = models.PositiveIntegerField(null=True, blank=True)
    card_exp_year = models.PositiveIntegerField(null=True, blank=True)

    # PayPal details
    paypal_email = models.EmailField(blank=True, null=True)

    # Bank details
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_last4 = models.CharField(max_length=4, blank=True, null=True)

    # Stripe/Payment processor IDs
    payment_processor_id = models.CharField(max_length=100, unique=True)
    is_default = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'

    def __str__(self):
        if self.payment_type == 'card':
            return f"{self.card_brand} ****{self.card_last4}"
        elif self.payment_type == 'paypal':
            return f"PayPal ({self.paypal_email})"
        else:
            return f"Bank ****{self.account_last4}"


class BillingHistory(models.Model):
    """
    Tracks all billing transactions and invoices
    """
    TRANSACTION_TYPES = [
        ('subscription', 'Subscription Payment'),
        ('upgrade', 'Plan Upgrade'),
        ('downgrade', 'Plan Downgrade'),
        ('addon', 'Add-on Purchase'),
        ('refund', 'Refund'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('disputed', 'Disputed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='billing_history')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)

    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Amounts
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Payment details
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    payment_processor_transaction_id = models.CharField(max_length=100, blank=True, null=True)

    # Billing period
    billing_period_start = models.DateTimeField(null=True, blank=True)
    billing_period_end = models.DateTimeField(null=True, blank=True)

    # Invoice details
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_pdf_url = models.URLField(blank=True, null=True)

    # Description and notes
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Billing History'
        verbose_name_plural = 'Billing History'

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - ${self.amount} ({self.status})"

    @property
    def total_amount(self):
        """Calculate total amount including tax and discount"""
        return self.amount + self.tax_amount - self.discount_amount
