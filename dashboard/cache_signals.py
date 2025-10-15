"""
Dashboard Cache Signals
Automatically invalidate cached metrics when financial data changes
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from accounting.models import (
    Invoice,
    Bill,
    JournalEntry,
    JournalEntryLine,
    Payment,
    Expense,
    Account,
)


def invalidate_company_cache(company):
    """Invalidate all dashboard caches for a company"""
    if not company:
        return

    cache_keys = [
        f"dashboard_metrics_{company.id}",
        f"account_balances_{company.id}",
        f"balance_sheet_{company.id}",
        f"pnl_statement_{company.id}",
        f"financial_ratios_{company.id}",
        f"gl_balance_summary_{company.id}",
    ]

    # Also delete hourly cached versions
    from datetime import datetime

    current_hour = datetime.now().strftime("%Y%m%d%H")
    cache_keys.append(f"dashboard_metrics_{company.id}_{current_hour}")

    for key in cache_keys:
        cache.delete(key)


@receiver(post_save, sender=Invoice)
@receiver(post_delete, sender=Invoice)
def invoice_changed(sender, instance, **kwargs):
    """Invalidate cache when invoice changes"""
    invalidate_company_cache(instance.company)


@receiver(post_save, sender=Bill)
@receiver(post_delete, sender=Bill)
def bill_changed(sender, instance, **kwargs):
    """Invalidate cache when bill changes"""
    invalidate_company_cache(instance.company)


@receiver(post_save, sender=JournalEntry)
@receiver(post_delete, sender=JournalEntry)
def journal_entry_changed(sender, instance, **kwargs):
    """Invalidate cache when journal entry changes"""
    invalidate_company_cache(instance.company)


@receiver(post_save, sender=JournalEntryLine)
@receiver(post_delete, sender=JournalEntryLine)
def journal_line_changed(sender, instance, **kwargs):
    """Invalidate cache when journal entry line changes"""
    if hasattr(instance.journal_entry, "company"):
        invalidate_company_cache(instance.journal_entry.company)


@receiver(post_save, sender=Payment)
@receiver(post_delete, sender=Payment)
def payment_changed(sender, instance, **kwargs):
    """Invalidate cache when payment changes"""
    if hasattr(instance, "invoice") and instance.invoice:
        invalidate_company_cache(instance.invoice.company)


@receiver(post_save, sender=Expense)
@receiver(post_delete, sender=Expense)
def expense_changed(sender, instance, **kwargs):
    """Invalidate cache when expense changes"""
    invalidate_company_cache(instance.company)


@receiver(post_save, sender=Account)
def account_changed(sender, instance, **kwargs):
    """Invalidate cache when account changes"""
    invalidate_company_cache(instance.company)
