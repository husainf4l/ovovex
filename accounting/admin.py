from django.contrib import admin
from .models import (
    Account, JournalEntry, JournalEntryLine,
    Customer, Invoice, InvoiceLine, Payment,
    Vendor, Bill, BillLine, Budget, BudgetLine,
    FixedAsset, ExpenseCategory, Expense,
    TaxRate, TaxReturn
)

class JournalEntryLineInline(admin.TabularInline):
    model = JournalEntryLine
    extra = 2
    fields = ['account', 'description', 'debit_amount', 'credit_amount']

class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 1
    fields = ['description', 'quantity', 'unit_price', 'line_total']

class BillLineInline(admin.TabularInline):
    model = BillLine
    extra = 1
    fields = ['description', 'quantity', 'unit_price', 'line_total']

class BudgetLineInline(admin.TabularInline):
    model = BudgetLine
    extra = 1
    fields = ['account', 'budgeted_amount', 'actual_amount', 'variance']

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'account_type', 'balance', 'is_active']
    list_filter = ['account_type', 'is_active']
    search_fields = ['code', 'name', 'description']
    ordering = ['code']

@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['entry_number', 'entry_date', 'description', 'total_debit', 'total_credit', 'status', 'is_balanced']
    list_filter = ['status', 'entry_date']
    search_fields = ['entry_number', 'description', 'reference']
    inlines = [JournalEntryLineInline]
    readonly_fields = ['total_debit', 'total_credit', 'created_at', 'updated_at']
    
    def is_balanced(self, obj):
        return obj.is_balanced()
    is_balanced.boolean = True

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_code', 'company_name', 'contact_name', 'email', 'is_active']
    list_filter = ['is_active']
    search_fields = ['customer_code', 'company_name', 'contact_name', 'email']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer', 'invoice_date', 'due_date', 'total_amount', 'status']
    list_filter = ['status', 'invoice_date']
    search_fields = ['invoice_number', 'customer__company_name']
    inlines = [InvoiceLineInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_number', 'customer', 'payment_date', 'amount', 'payment_method']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['payment_number', 'customer__company_name']

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['vendor_code', 'company_name', 'contact_name', 'email', 'is_active']
    list_filter = ['is_active']
    search_fields = ['vendor_code', 'company_name', 'contact_name', 'email']

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['bill_number', 'vendor', 'bill_date', 'due_date', 'total_amount', 'status']
    list_filter = ['status', 'bill_date']
    search_fields = ['bill_number', 'vendor__company_name']
    inlines = [BillLineInline]

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'fiscal_year', 'period', 'start_date', 'end_date', 'total_budget', 'is_active']
    list_filter = ['fiscal_year', 'period', 'is_active']
    search_fields = ['name']
    inlines = [BudgetLineInline]

@admin.register(FixedAsset)
class FixedAssetAdmin(admin.ModelAdmin):
    list_display = ['asset_code', 'name', 'purchase_date', 'purchase_cost', 'book_value', 'is_active']
    list_filter = ['is_active', 'depreciation_method']
    search_fields = ['asset_code', 'name']

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'account', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['expense_number', 'category', 'expense_date', 'amount', 'status']
    list_filter = ['status', 'category', 'expense_date']
    search_fields = ['expense_number', 'description']

@admin.register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    list_display = ['name', 'rate', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(TaxReturn)
class TaxReturnAdmin(admin.ModelAdmin):
    list_display = ['return_number', 'tax_period_start', 'tax_period_end', 'filing_date', 'total_tax', 'status']
    list_filter = ['status']
    search_fields = ['return_number']
