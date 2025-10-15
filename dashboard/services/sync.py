"""
Dashboard Synchronization Service
Handles cross-module updates and real-time data synchronization
"""

from decimal import Decimal
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum

from accounting.models import (
    Customer, Invoice, Payment, Vendor, Bill, JournalEntry, JournalEntryLine,
    Account, AccountType, Budget, BudgetLine, FixedAsset, Expense, ExpenseCategory
)


class DashboardSyncService:
    """
    Service for synchronizing data across dashboard modules
    Handles automatic updates when related models change
    """

    def __init__(self, company):
        self.company = company

    @transaction.atomic
    def sync_customer_creation(self, customer):
        """
        Sync actions when a new customer is created
        - Clear relevant caches
        - Update dashboard metrics
        """
        # Clear customer-related caches
        cache_keys = [
            f"dashboard_metrics_{self.company.id}",
            f"customer_metrics_{self.company.id}",
            f"top_customers_{self.company.id}",
        ]
        cache.delete_many(cache_keys)

        # Could add welcome email, default settings, etc.
        return {"status": "success", "message": f"Customer {customer.company_name} synced"}

    @transaction.atomic
    def sync_invoice_creation(self, invoice):
        """
        Sync actions when a new invoice is created
        - Update customer balance
        - Create automatic journal entries
        - Update dashboard metrics
        """
        # Update customer outstanding balance (this happens via signal)
        customer = invoice.customer
        customer.save()  # Triggers balance recalculation

        # Create automatic journal entries for invoice
        self._create_invoice_journal_entries(invoice)

        # Clear relevant caches
        cache_keys = [
            f"dashboard_metrics_{self.company.id}",
            f"invoice_metrics_{self.company.id}",
            f"customer_balance_{customer.id}",
            f"aging_report_{self.company.id}",
        ]
        cache.delete_many(cache_keys)

        return {"status": "success", "message": f"Invoice {invoice.invoice_number} synced"}

    @transaction.atomic
    def sync_payment_creation(self, payment):
        """
        Sync actions when a payment is recorded
        - Update invoice status
        - Update customer balance
        - Create journal entries
        - Update cash flow
        """
        # Update invoice (handled by signal)
        if payment.invoice:
            payment.invoice.save()

        # Update customer balance
        payment.customer.save()

        # Create automatic journal entries
        self._create_payment_journal_entries(payment)

        # Clear caches
        cache_keys = [
            f"dashboard_metrics_{self.company.id}",
            f"cash_metrics_{self.company.id}",
            f"invoice_metrics_{self.company.id}",
            f"customer_balance_{payment.customer.id}",
            f"cash_flow_{self.company.id}",
        ]
        cache.delete_many(cache_keys)

        return {"status": "success", "message": f"Payment {payment.payment_number} synced"}

    @transaction.atomic
    def sync_journal_entry_posting(self, journal_entry):
        """
        Sync actions when journal entry is posted
        - Update account balances
        - Update budget actuals
        - Update financial ratios
        - Refresh reports
        """
        # Update budget actuals (handled by signal)
        self._update_budget_actuals(journal_entry)

        # Clear all financial caches
        cache_keys = [
            f"dashboard_metrics_{self.company.id}",
            f"balance_sheet_{self.company.id}",
            f"pnl_statement_{self.company.id}",
            f"financial_ratios_{self.company.id}",
            f"account_balances_{self.company.id}",
        ]
        cache.delete_many(cache_keys)

        return {"status": "success", "message": f"Journal entry {journal_entry.entry_number} synced"}

    def _create_invoice_journal_entries(self, invoice):
        """
        Create automatic journal entries for invoice
        Debit: Accounts Receivable
        Credit: Revenue
        """
        # Find AR account
        ar_account = Account.objects.filter(
            company=self.company,
            account_type=AccountType.ASSET,
            name__icontains="receivable"
        ).first()

        # Find revenue account
        revenue_account = Account.objects.filter(
            company=self.company,
            account_type=AccountType.REVENUE
        ).first()

        if ar_account and revenue_account:
            # Create journal entry
            je = JournalEntry.objects.create(
                company=self.company,
                entry_number=f"INV-{invoice.invoice_number}",
                entry_date=invoice.invoice_date,
                description=f"Invoice {invoice.invoice_number} - {invoice.customer.company_name}",
                status="POSTED"
            )

            # Debit AR
            JournalEntryLine.objects.create(
                journal_entry=je,
                account=ar_account,
                description=f"Invoice {invoice.invoice_number}",
                debit_amount=invoice.total_amount,
                credit_amount=Decimal("0.00"),
                line_number=1
            )

            # Credit Revenue
            JournalEntryLine.objects.create(
                journal_entry=je,
                account=revenue_account,
                description=f"Revenue from {invoice.customer.company_name}",
                debit_amount=Decimal("0.00"),
                credit_amount=invoice.total_amount,
                line_number=2
            )

    def _create_payment_journal_entries(self, payment):
        """
        Create automatic journal entries for payment
        Debit: Cash/Bank
        Credit: Accounts Receivable
        """
        # Find cash/bank account
        cash_account = Account.objects.filter(
            company=self.company,
            account_type=AccountType.ASSET,
            name__icontains="cash"
        ).first() or Account.objects.filter(
            company=self.company,
            account_type=AccountType.ASSET,
            name__icontains="bank"
        ).first()

        # Find AR account
        ar_account = Account.objects.filter(
            company=self.company,
            account_type=AccountType.ASSET,
            name__icontains="receivable"
        ).first()

        if cash_account and ar_account:
            # Create journal entry
            je = JournalEntry.objects.create(
                company=self.company,
                entry_number=f"PAY-{payment.payment_number}",
                entry_date=payment.payment_date,
                description=f"Payment {payment.payment_number} - {payment.customer.company_name}",
                status="POSTED"
            )

            # Debit Cash
            JournalEntryLine.objects.create(
                journal_entry=je,
                account=cash_account,
                description=f"Payment received from {payment.customer.company_name}",
                debit_amount=payment.amount,
                credit_amount=Decimal("0.00"),
                line_number=1
            )

            # Credit AR
            JournalEntryLine.objects.create(
                journal_entry=je,
                account=ar_account,
                description=f"Payment for invoice {payment.invoice.invoice_number if payment.invoice else 'N/A'}",
                debit_amount=Decimal("0.00"),
                credit_amount=payment.amount,
                line_number=2
            )

    def _update_budget_actuals(self, journal_entry):
        """
        Update budget actual amounts based on posted journal entries
        """
        # Find active budgets covering this date
        budgets = Budget.objects.filter(
            company=self.company,
            is_active=True,
            start_date__lte=journal_entry.entry_date,
            end_date__gte=journal_entry.entry_date
        )

        for budget in budgets:
            # Update each budget line
            for line in budget.lines.all():
                # Calculate actual amount from journal entries
                actual = JournalEntryLine.objects.filter(
                    journal_entry__company=self.company,
                    journal_entry__status="POSTED",
                    journal_entry__entry_date__gte=budget.start_date,
                    journal_entry__entry_date__lte=budget.end_date,
                    account=line.account
                ).aggregate(
                    total_debit=Sum("debit_amount") or Decimal("0"),
                    total_credit=Sum("credit_amount") or Decimal("0")
                )

                # Calculate net based on account type
                if line.account.account_type in ["ASSET", "EXPENSE"]:
                    line.actual_amount = actual["total_debit"] - actual["total_credit"]
                else:
                    line.actual_amount = actual["total_credit"] - actual["total_debit"]

                line.save()

    def get_related_data(self, model_name, object_id):
        """
        Get related data for a specific object across modules
        Used for dynamic dropdowns and relationship displays
        """
        if model_name == "customer":
            customer = Customer.objects.get(id=object_id, company=self.company)
            return {
                "unpaid_invoices": Invoice.objects.filter(
                    company=self.company,
                    customer=customer,
                    status__in=["SENT", "OVERDUE"]
                ).values("id", "invoice_number", "total_amount", "paid_amount"),
                "total_outstanding": customer.get_outstanding_balance(),
                "payment_history": Payment.objects.filter(
                    company=self.company,
                    customer=customer
                ).order_by("-payment_date")[:5]
            }

        elif model_name == "invoice":
            invoice = Invoice.objects.get(id=object_id, company=self.company)
            return {
                "customer": {
                    "id": invoice.customer.id,
                    "name": invoice.customer.company_name,
                    "balance": invoice.customer.get_outstanding_balance()
                },
                "payments": Payment.objects.filter(
                    company=self.company,
                    invoice=invoice
                ).values("id", "payment_number", "amount", "payment_date"),
                "remaining_balance": invoice.get_balance_due()
            }

        return {}

    def refresh_dashboard_cache(self):
        """
        Clear all dashboard-related caches
        Call this when major data changes occur
        """
        cache_keys = [
            f"dashboard_metrics_{self.company.id}",
            f"balance_sheet_{self.company.id}",
            f"pnl_statement_{self.company.id}",
            f"financial_ratios_{self.company.id}",
            f"cash_flow_{self.company.id}",
            f"customer_metrics_{self.company.id}",
            f"invoice_metrics_{self.company.id}",
            f"account_balances_{self.company.id}",
        ]
        cache.delete_many(cache_keys)

    def get_live_kpi_updates(self):
        """
        Get real-time KPI updates for dashboard
        Returns data that changed since last check
        """
        # This would be used with WebSocket or polling
        # For now, return current metrics
        from dashboard.services import FinancialMetricsService
        service = FinancialMetricsService(self.company)
        return service.get_all_metrics()