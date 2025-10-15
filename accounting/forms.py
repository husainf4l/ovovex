"""
Forms for Accounting Module - Full CRUD Support
Multi-company aware forms for all accounting entities
"""

from django import forms
from django.contrib.auth.models import User
from .models import (
    Invoice,
    InvoiceLine,
    Payment,
    JournalEntry,
    JournalEntryLine,
    Account,
    Customer,
    Expense,
    ExpenseCategory,
    Budget,
    BudgetLine,
    FixedAsset,
    Bill,
    BillLine,
    Vendor,
)
from decimal import Decimal


# ============================================================================
# INVOICE FORMS
# ============================================================================


class InvoiceForm(forms.ModelForm):
    """Form for creating and editing invoices"""

    class Meta:
        model = Invoice
        fields = [
            "customer",
            "invoice_number",
            "invoice_date",
            "due_date",
            "status",
            "subtotal",
            "tax_amount",
            "discount_amount",
            "total_amount",
            "notes",
        ]
        widgets = {
            "customer": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500"
                }
            ),
            "invoice_number": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "placeholder": "INV-0001",
                }
            ),
            "invoice_date": forms.DateInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "type": "date",
                }
            ),
            "due_date": forms.DateInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "type": "date",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500"
                }
            ),
            "subtotal": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "step": "0.01",
                    "readonly": True,
                }
            ),
            "tax_amount": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "step": "0.01",
                }
            ),
            "discount_amount": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "step": "0.01",
                }
            ),
            "total_amount": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "step": "0.01",
                    "readonly": True,
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)
        if company:
            self.fields["customer"].queryset = Customer.objects.filter(
                company=company, is_active=True
            )


class InvoiceLineForm(forms.ModelForm):
    """Form for invoice line items"""

    class Meta:
        model = InvoiceLine
        fields = ["description", "quantity", "unit_price", "line_number"]
        widgets = {
            "description": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Item description",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "w-24 px-3 py-2 bg-gray-800 border border-gray-700 rounded focus:ring-2 focus:ring-blue-500",
                    "step": "0.01",
                    "min": "0.01",
                }
            ),
            "unit_price": forms.NumberInput(
                attrs={
                    "class": "w-32 px-3 py-2 bg-gray-800 border border-gray-700 rounded focus:ring-2 focus:ring-blue-500",
                    "step": "0.01",
                    "min": "0.00",
                }
            ),
            "line_number": forms.HiddenInput(),
        }


# ============================================================================
# PAYMENT FORMS
# ============================================================================


class PaymentForm(forms.ModelForm):
    """Form for recording customer payments"""

    class Meta:
        model = Payment
        fields = [
            "customer",
            "invoice",
            "payment_number",
            "payment_date",
            "amount",
            "payment_method",
            "reference",
            "notes",
        ]
        widgets = {
            "customer": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500"
                }
            ),
            "invoice": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500"
                }
            ),
            "payment_number": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "placeholder": "PAY-0001",
                }
            ),
            "payment_date": forms.DateInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "type": "date",
                }
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "step": "0.01",
                    "min": "0.01",
                }
            ),
            "payment_method": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500"
                }
            ),
            "reference": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Check number or transaction ID",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)
        if company:
            # Filter customers by company
            self.fields["customer"].queryset = Customer.objects.filter(
                company=company, is_active=True
            )
            # Filter invoices by company (only unpaid or partially paid)
            from .models import Invoice
            self.fields["invoice"].queryset = Invoice.objects.filter(
                company=company
            ).exclude(status="PAID").select_related("customer")
            self.fields["invoice"].required = False


# ============================================================================
# JOURNAL ENTRY FORMS
# ============================================================================


class JournalEntryForm(forms.ModelForm):
    """Form for creating and editing journal entries"""

    class Meta:
        model = JournalEntry
        fields = ["entry_number", "entry_date", "description", "reference", "status"]
        widgets = {
            "entry_number": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "placeholder": "JE-0001",
                }
            ),
            "entry_date": forms.DateInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "type": "date",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "rows": 3,
                    "placeholder": "Describe this journal entry...",
                }
            ),
            "reference": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Reference number or document",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500"
                }
            ),
        }


class JournalEntryLineForm(forms.ModelForm):
    """Form for journal entry line items"""

    class Meta:
        model = JournalEntryLine
        fields = [
            "account",
            "description",
            "debit_amount",
            "credit_amount",
            "line_number",
        ]
        widgets = {
            "account": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded focus:ring-2 focus:ring-blue-500"
                }
            ),
            "description": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Line description",
                }
            ),
            "debit_amount": forms.NumberInput(
                attrs={
                    "class": "w-32 px-3 py-2 bg-gray-800 border border-gray-700 rounded focus:ring-2 focus:ring-blue-500",
                    "step": "0.01",
                    "min": "0.00",
                    "placeholder": "0.00",
                }
            ),
            "credit_amount": forms.NumberInput(
                attrs={
                    "class": "w-32 px-3 py-2 bg-gray-800 border border-gray-700 rounded focus:ring-2 focus:ring-blue-500",
                    "step": "0.01",
                    "min": "0.00",
                    "placeholder": "0.00",
                }
            ),
            "line_number": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)
        if company:
            self.fields["account"].queryset = Account.objects.filter(
                company=company, is_active=True
            ).order_by("code")


# ============================================================================
# EXPENSE FORMS
# ============================================================================


class ExpenseForm(forms.ModelForm):
    """Form for recording expenses"""

    class Meta:
        model = Expense
        fields = [
            "expense_number",
            "category",
            "vendor",
            "expense_date",
            "amount",
            "description",
            "receipt_number",
            "status",
            "notes",
        ]
        widgets = {
            "expense_number": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "placeholder": "EXP-0001",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500"
                }
            ),
            "vendor": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500"
                }
            ),
            "expense_date": forms.DateInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "type": "date",
                }
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "step": "0.01",
                    "min": "0.01",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "rows": 3,
                    "placeholder": "Expense description...",
                }
            ),
            "receipt_number": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Receipt or reference number",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500"
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "rows": 2,
                }
            ),
        }


# ============================================================================
# BUDGET FORMS
# ============================================================================


class BudgetForm(forms.ModelForm):
    """Form for creating and editing budgets"""

    class Meta:
        model = Budget
        fields = [
            "name",
            "fiscal_year",
            "period",
            "start_date",
            "end_date",
            "total_budget",
            "is_active",
            "notes",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Q1 2025 Budget",
                }
            ),
            "fiscal_year": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "placeholder": "2025",
                }
            ),
            "period": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500"
                }
            ),
            "start_date": forms.DateInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "type": "date",
                }
            ),
            "end_date": forms.DateInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "type": "date",
                }
            ),
            "total_budget": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "step": "0.01",
                    "min": "0.00",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "w-5 h-5 text-blue-600 bg-gray-800 border-gray-700 rounded focus:ring-blue-500"
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "rows": 3,
                }
            ),
        }


class BudgetLineForm(forms.ModelForm):
    """Form for budget line items"""

    class Meta:
        model = BudgetLine
        fields = ["account", "budgeted_amount", "notes"]
        widgets = {
            "account": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded focus:ring-2 focus:ring-blue-500"
                }
            ),
            "budgeted_amount": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded focus:ring-2 focus:ring-blue-500",
                    "step": "0.01",
                    "min": "0.00",
                }
            ),
            "notes": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Budget notes",
                }
            ),
        }


# ============================================================================
# FIXED ASSET FORMS
# ============================================================================


class FixedAssetForm(forms.ModelForm):
    """Form for creating and editing fixed assets"""

    class Meta:
        model = FixedAsset
        fields = [
            "asset_code",
            "name",
            "description",
            "category",
            "account",
            "acquisition_method",
            "purchase_date",
            "purchase_cost",
            "vendor",
            "serial_number",
            "manufacturer",
            "model",
            "barcode",
            "location",
            "department",
            "custodian",
            "salvage_value",
            "useful_life_years",
            "depreciation_method",
            "is_active",
            "is_depreciated",
            "notes",
        ]
        widgets = {
            "asset_code": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100",
                    "placeholder": "ASSET-0001",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100",
                    "placeholder": "Asset name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100",
                    "rows": 3,
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100"
                }
            ),
            "account": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100"
                }
            ),
            "acquisition_method": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100"
                }
            ),
            "purchase_date": forms.DateInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100",
                    "type": "date",
                }
            ),
            "purchase_cost": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100",
                    "step": "0.01",
                    "min": "0.00",
                }
            ),
            "vendor": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100"
                }
            ),
            "serial_number": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100"
                }
            ),
            "manufacturer": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100"
                }
            ),
            "model": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100"
                }
            ),
            "barcode": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100"
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100"
                }
            ),
            "department": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100"
                }
            ),
            "custodian": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100"
                }
            ),
            "salvage_value": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100",
                    "step": "0.01",
                    "min": "0.00",
                }
            ),
            "useful_life_years": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100",
                    "min": "1",
                }
            ),
            "depreciation_method": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100"
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "w-5 h-5 text-blue-600 bg-gray-800 border-gray-700 rounded focus:ring-blue-500"
                }
            ),
            "is_depreciated": forms.CheckboxInput(
                attrs={
                    "class": "w-5 h-5 text-blue-600 bg-gray-800 border-gray-700 rounded focus:ring-blue-500"
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100",
                    "rows": 3,
                }
            ),
        }

    def save(self, commit=True):
        """Calculate book value before saving"""
        instance = super().save(commit=False)
        instance.book_value = instance.purchase_cost - instance.accumulated_depreciation
        if commit:
            instance.save()
        return instance

    def __init__(self, *args, **kwargs):
        company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)
        if company:
            self.fields["account"].queryset = Account.objects.filter(
                company=company, is_active=True
            )
            self.fields["vendor"].queryset = Vendor.objects.filter(
                company=company, is_active=True
            )


# ============================================================================
# CUSTOMER FORMS
# ============================================================================


class CustomerForm(forms.ModelForm):
    """Form for creating and editing customers"""

    class Meta:
        model = Customer
        fields = [
            "customer_code",
            "company_name",
            "contact_name",
            "email",
            "phone",
            "address",
            "city",
            "country",
            "tax_id",
            "credit_limit",
            "payment_terms_days",
            "is_active",
        ]
        widgets = {
            "customer_code": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "placeholder": "CUST-0001",
                }
            ),
            "company_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Customer company name",
                }
            ),
            "contact_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Contact person name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "placeholder": "customer@example.com",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "placeholder": "+962-xxx-xxxx",
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "rows": 2,
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500"
                }
            ),
            "country": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500"
                }
            ),
            "tax_id": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500"
                }
            ),
            "credit_limit": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "step": "0.01",
                    "min": "0.00",
                }
            ),
            "payment_terms_days": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500",
                    "min": "0",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "w-5 h-5 text-blue-600 bg-gray-800 border-gray-700 rounded focus:ring-blue-500"
                }
            ),
        }
