"""
Accounting Signals - Auto-update logic and validations
Automatically trigger when models are saved/updated
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date

from .models import (
    Invoice,
    Payment,
    JournalEntry,
    JournalEntryLine,
    BudgetLine,
    Expense,
    FixedAsset,
)


# ============================================================================
# INVOICE & PAYMENT SIGNALS
# ============================================================================


@receiver(post_save, sender=Payment)
def update_invoice_on_payment(sender, instance, created, **kwargs):
    """
    Auto-update invoice paid_amount and status when payment is recorded
    """
    if instance.invoice:
        invoice = instance.invoice

        # Recalculate total paid amount from all payments
        total_paid = Payment.objects.filter(invoice=invoice).aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0.00")

        invoice.paid_amount = total_paid

        # Auto-update status based on payment
        if total_paid >= invoice.total_amount:
            invoice.status = "PAID"
        elif total_paid > Decimal("0.00"):
            invoice.status = "PARTIALLY_PAID"  # You may need to add this status

        invoice.save(update_fields=["paid_amount", "status"])


@receiver(post_delete, sender=Payment)
def update_invoice_on_payment_delete(sender, instance, **kwargs):
    """
    Update invoice when payment is deleted
    """
    if instance.invoice:
        invoice = instance.invoice

        # Recalculate total paid
        total_paid = Payment.objects.filter(invoice=invoice).aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0.00")

        invoice.paid_amount = total_paid

        # Revert status if needed
        if total_paid < invoice.total_amount:
            if invoice.status == "PAID":
                invoice.status = "SENT"

        invoice.save(update_fields=["paid_amount", "status"])


@receiver(pre_save, sender=Invoice)
def validate_invoice(sender, instance, **kwargs):
    """
    Validate invoice before saving
    """
    # Ensure due date is not before invoice date
    if instance.due_date < instance.invoice_date:
        raise ValidationError("Due date cannot be before invoice date")

    # Ensure amounts are non-negative
    if instance.total_amount < Decimal("0.00"):
        raise ValidationError("Invoice total cannot be negative")

    # Auto-calculate total if subtotal, tax, and discount are set
    if instance.subtotal is not None:
        calculated_total = (
            instance.subtotal + instance.tax_amount - instance.discount_amount
        )
        if abs(calculated_total - instance.total_amount) > Decimal("0.01"):
            instance.total_amount = calculated_total


# ============================================================================
# JOURNAL ENTRY SIGNALS
# ============================================================================


@receiver(pre_save, sender=JournalEntry)
def validate_journal_entry(sender, instance, **kwargs):
    """
    Ensure journal entry is balanced before posting
    """
    if instance.status == "POSTED":
        if not instance.is_balanced():
            raise ValidationError(
                f"Cannot post unbalanced journal entry. "
                f"Debit: {instance.total_debit}, Credit: {instance.total_credit}"
            )


@receiver(post_save, sender=JournalEntryLine)
def update_journal_entry_totals(sender, instance, **kwargs):
    """
    Auto-recalculate journal entry totals when line is added/updated
    """
    instance.journal_entry.calculate_totals()


@receiver(post_delete, sender=JournalEntryLine)
def update_journal_entry_totals_on_delete(sender, instance, **kwargs):
    """
    Recalculate totals when line is deleted
    """
    instance.journal_entry.calculate_totals()


# ============================================================================
# BUDGET SIGNALS
# ============================================================================


@receiver(post_save, sender=JournalEntry)
def update_budget_actual_amounts(sender, instance, **kwargs):
    """
    Update budget actual amounts when journal entries are posted
    """
    if instance.status == "POSTED":
        # Get active budgets for this company covering the entry date
        from .models import Budget, BudgetLine

        budgets = Budget.objects.filter(
            company=instance.company,
            is_active=True,
            start_date__lte=instance.entry_date,
            end_date__gte=instance.entry_date,
        )

        for budget in budgets:
            # Update actual amounts for each budget line
            for budget_line in budget.lines.all():
                # Sum actual transactions for this account in budget period
                actual = JournalEntryLine.objects.filter(
                    journal_entry__company=budget.company,
                    journal_entry__status="POSTED",
                    journal_entry__entry_date__gte=budget.start_date,
                    journal_entry__entry_date__lte=budget.end_date,
                    account=budget_line.account,
                ).aggregate(
                    total_debit=models.Sum("debit_amount"),
                    total_credit=models.Sum("credit_amount"),
                )

                # Calculate net amount based on account type
                total_debit = actual["total_debit"] or Decimal("0.00")
                total_credit = actual["total_credit"] or Decimal("0.00")

                if budget_line.account.account_type in ["EXPENSE", "ASSET"]:
                    budget_line.actual_amount = total_debit - total_credit
                else:
                    budget_line.actual_amount = total_credit - total_debit

                # Calculate variance
                budget_line.calculate_variance()


@receiver(pre_save, sender=BudgetLine)
def auto_calculate_variance(sender, instance, **kwargs):
    """
    Auto-calculate variance before saving budget line
    """
    instance.variance = instance.actual_amount - instance.budgeted_amount


# ============================================================================
# EXPENSE SIGNALS
# ============================================================================


@receiver(pre_save, sender=Expense)
def validate_expense(sender, instance, **kwargs):
    """
    Validate expense before saving
    """
    if instance.amount < Decimal("0.00"):
        raise ValidationError("Expense amount cannot be negative")

    if instance.expense_date > date.today():
        raise ValidationError("Expense date cannot be in the future")


# ============================================================================
# FIXED ASSET SIGNALS
# ============================================================================


@receiver(post_save, sender=FixedAsset)
def calculate_asset_book_value(sender, instance, created, **kwargs):
    """
    Auto-calculate book value after saving fixed asset
    """
    if created or instance.accumulated_depreciation:
        instance.calculate_book_value()
        if not created:  # Avoid recursion on creation
            FixedAsset.objects.filter(pk=instance.pk).update(
                book_value=instance.book_value
            )


# ============================================================================
# OVERDUE INVOICE DETECTION
# ============================================================================

from django.utils import timezone


@receiver(post_save, sender=Invoice)
def check_overdue_status(sender, instance, **kwargs):
    """
    Auto-mark invoices as OVERDUE when due date passes
    """
    today = timezone.now().date()

    if instance.status in ["SENT"] and instance.due_date < today:
        Invoice.objects.filter(pk=instance.pk).update(status="OVERDUE")


# Import models module for aggregate functions
from django.db import models
