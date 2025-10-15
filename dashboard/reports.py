"""
Financial Reports Generator
Generates Profit & Loss, Balance Sheet, and Cash Flow reports
"""

from django.db.models import Sum, Q
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from accounting.models import (
    Account,
    AccountType,
    JournalEntry,
    JournalEntryLine,
    Invoice,
    Payment,
    Expense,
    FixedAsset,
)


class FinancialReports:
    """Generate comprehensive financial reports"""

    def __init__(self, company, start_date=None, end_date=None):
        self.company = company
        self.start_date = start_date or datetime.now().date().replace(day=1)
        self.end_date = end_date or datetime.now().date()

    def profit_and_loss(self) -> Dict:
        """
        Generate Profit & Loss Statement (Income Statement)
        Revenue - Expenses = Net Income
        """
        # Get all revenue accounts
        revenue_accounts = Account.objects.filter(
            company=self.company, account_type=AccountType.REVENUE, is_active=True
        )

        # Get all expense accounts
        expense_accounts = Account.objects.filter(
            company=self.company, account_type=AccountType.EXPENSE, is_active=True
        )

        # Calculate revenue from posted journal entries in date range
        revenue_data = []
        total_revenue = Decimal("0.00")

        for account in revenue_accounts:
            # Get credit balance (revenue increases with credits)
            credits = JournalEntryLine.objects.filter(
                journal_entry__company=self.company,
                journal_entry__status="POSTED",
                journal_entry__entry_date__gte=self.start_date,
                journal_entry__entry_date__lte=self.end_date,
                account=account,
            ).aggregate(total=Sum("credit_amount"))["total"] or Decimal("0.00")

            debits = JournalEntryLine.objects.filter(
                journal_entry__company=self.company,
                journal_entry__status="POSTED",
                journal_entry__entry_date__gte=self.start_date,
                journal_entry__entry_date__lte=self.end_date,
                account=account,
            ).aggregate(total=Sum("debit_amount"))["total"] or Decimal("0.00")

            balance = credits - debits

            if balance != Decimal("0.00"):
                revenue_data.append({"account": account, "amount": balance})
                total_revenue += balance

        # Calculate expenses
        expense_data = []
        total_expenses = Decimal("0.00")

        for account in expense_accounts:
            # Get debit balance (expenses increase with debits)
            debits = JournalEntryLine.objects.filter(
                journal_entry__company=self.company,
                journal_entry__status="POSTED",
                journal_entry__entry_date__gte=self.start_date,
                journal_entry__entry_date__lte=self.end_date,
                account=account,
            ).aggregate(total=Sum("debit_amount"))["total"] or Decimal("0.00")

            credits = JournalEntryLine.objects.filter(
                journal_entry__company=self.company,
                journal_entry__status="POSTED",
                journal_entry__entry_date__gte=self.start_date,
                journal_entry__entry_date__lte=self.end_date,
                account=account,
            ).aggregate(total=Sum("credit_amount"))["total"] or Decimal("0.00")

            balance = debits - credits

            if balance != Decimal("0.00"):
                expense_data.append({"account": account, "amount": balance})
                total_expenses += balance

        # Calculate net income
        net_income = total_revenue - total_expenses

        return {
            "report_type": "Profit & Loss Statement",
            "company": self.company,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "revenue": {"items": revenue_data, "total": total_revenue},
            "expenses": {"items": expense_data, "total": total_expenses},
            "net_income": net_income,
            "net_margin": (
                (net_income / total_revenue * 100)
                if total_revenue > 0
                else Decimal("0.00")
            ),
        }

    def balance_sheet(self) -> Dict:
        """
        Generate Balance Sheet
        Assets = Liabilities + Equity
        """
        # Get all asset accounts
        asset_accounts = Account.objects.filter(
            company=self.company, account_type=AccountType.ASSET, is_active=True
        )

        # Get all liability accounts
        liability_accounts = Account.objects.filter(
            company=self.company, account_type=AccountType.LIABILITY, is_active=True
        )

        # Get all equity accounts
        equity_accounts = Account.objects.filter(
            company=self.company, account_type=AccountType.EQUITY, is_active=True
        )

        # Calculate assets (debit balance)
        assets_data = []
        total_assets = Decimal("0.00")

        for account in asset_accounts:
            debits = JournalEntryLine.objects.filter(
                journal_entry__company=self.company,
                journal_entry__status="POSTED",
                journal_entry__entry_date__lte=self.end_date,
                account=account,
            ).aggregate(total=Sum("debit_amount"))["total"] or Decimal("0.00")

            credits = JournalEntryLine.objects.filter(
                journal_entry__company=self.company,
                journal_entry__status="POSTED",
                journal_entry__entry_date__lte=self.end_date,
                account=account,
            ).aggregate(total=Sum("credit_amount"))["total"] or Decimal("0.00")

            balance = debits - credits

            if balance != Decimal("0.00"):
                assets_data.append({"account": account, "amount": balance})
                total_assets += balance

        # Calculate liabilities (credit balance)
        liabilities_data = []
        total_liabilities = Decimal("0.00")

        for account in liability_accounts:
            credits = JournalEntryLine.objects.filter(
                journal_entry__company=self.company,
                journal_entry__status="POSTED",
                journal_entry__entry_date__lte=self.end_date,
                account=account,
            ).aggregate(total=Sum("credit_amount"))["total"] or Decimal("0.00")

            debits = JournalEntryLine.objects.filter(
                journal_entry__company=self.company,
                journal_entry__status="POSTED",
                journal_entry__entry_date__lte=self.end_date,
                account=account,
            ).aggregate(total=Sum("debit_amount"))["total"] or Decimal("0.00")

            balance = credits - debits

            if balance != Decimal("0.00"):
                liabilities_data.append({"account": account, "amount": balance})
                total_liabilities += balance

        # Calculate equity (credit balance)
        equity_data = []
        total_equity = Decimal("0.00")

        for account in equity_accounts:
            credits = JournalEntryLine.objects.filter(
                journal_entry__company=self.company,
                journal_entry__status="POSTED",
                journal_entry__entry_date__lte=self.end_date,
                account=account,
            ).aggregate(total=Sum("credit_amount"))["total"] or Decimal("0.00")

            debits = JournalEntryLine.objects.filter(
                journal_entry__company=self.company,
                journal_entry__status="POSTED",
                journal_entry__entry_date__lte=self.end_date,
                account=account,
            ).aggregate(total=Sum("debit_amount"))["total"] or Decimal("0.00")

            balance = credits - debits

            if balance != Decimal("0.00"):
                equity_data.append({"account": account, "amount": balance})
                total_equity += balance

        # Add retained earnings (net income)
        pnl = self.profit_and_loss()
        retained_earnings = pnl["net_income"]
        total_equity += retained_earnings

        return {
            "report_type": "Balance Sheet",
            "company": self.company,
            "as_of_date": self.end_date,
            "assets": {"items": assets_data, "total": total_assets},
            "liabilities": {"items": liabilities_data, "total": total_liabilities},
            "equity": {
                "items": equity_data,
                "retained_earnings": retained_earnings,
                "total": total_equity,
            },
            "total_liabilities_and_equity": total_liabilities + total_equity,
            "balanced": abs(total_assets - (total_liabilities + total_equity))
            < Decimal("0.01"),
        }

    def cash_flow_statement(self) -> Dict:
        """
        Generate Cash Flow Statement
        Operating + Investing + Financing Activities = Net Cash Flow
        """
        # Simplified cash flow - tracks actual cash movements

        # Operating Activities: Revenue and Expenses
        cash_from_operations = Decimal("0.00")

        # Cash received from customers (invoice payments)
        cash_received = Payment.objects.filter(
            customer__company=self.company,
            payment_date__gte=self.start_date,
            payment_date__lte=self.end_date,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        # Cash paid for expenses
        cash_paid_expenses = Expense.objects.filter(
            status="PAID",
            expense_date__gte=self.start_date,
            expense_date__lte=self.end_date,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        cash_from_operations = cash_received - cash_paid_expenses

        # Investing Activities: Fixed asset purchases
        asset_purchases = FixedAsset.objects.filter(
            company=self.company,
            purchase_date__gte=self.start_date,
            purchase_date__lte=self.end_date,
        ).aggregate(total=Sum("purchase_cost"))["total"] or Decimal("0.00")

        cash_from_investing = -asset_purchases  # Negative because it's cash outflow

        # Financing Activities: Would include loans, equity, dividends
        # For now, we'll leave this as 0 until those features are added
        cash_from_financing = Decimal("0.00")

        # Net change in cash
        net_cash_change = (
            cash_from_operations + cash_from_investing + cash_from_financing
        )

        # Beginning and ending cash balance
        cash_accounts = Account.objects.filter(
            company=self.company, account_type=AccountType.ASSET, is_active=True
        ).filter(Q(name__icontains="cash") | Q(name__icontains="bank"))

        ending_cash_balance = sum(acc.get_balance() for acc in cash_accounts)
        beginning_cash_balance = ending_cash_balance - net_cash_change

        return {
            "report_type": "Cash Flow Statement",
            "company": self.company,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "operating_activities": {
                "cash_received": cash_received,
                "cash_paid": cash_paid_expenses,
                "net": cash_from_operations,
            },
            "investing_activities": {
                "asset_purchases": -asset_purchases,
                "net": cash_from_investing,
            },
            "financing_activities": {"net": cash_from_financing},
            "net_cash_change": net_cash_change,
            "beginning_cash": beginning_cash_balance,
            "ending_cash": ending_cash_balance,
        }

    def aging_report_receivables(self) -> Dict:
        """
        Accounts Receivable Aging Report
        Groups outstanding invoices by age
        """
        today = datetime.now().date()

        # Get all unpaid invoices
        unpaid_invoices = Invoice.objects.filter(
            company=self.company, status__in=["SENT", "OVERDUE"]
        )

        # Categorize by age
        current = []  # 0-30 days
        days_31_60 = []
        days_61_90 = []
        over_90 = []

        for invoice in unpaid_invoices:
            days_overdue = (today - invoice.due_date).days
            balance_due = invoice.get_balance_due()

            invoice_data = {
                "invoice": invoice,
                "days_overdue": days_overdue,
                "balance_due": balance_due,
            }

            if days_overdue <= 30:
                current.append(invoice_data)
            elif days_overdue <= 60:
                days_31_60.append(invoice_data)
            elif days_overdue <= 90:
                days_61_90.append(invoice_data)
            else:
                over_90.append(invoice_data)

        return {
            "report_type": "Accounts Receivable Aging",
            "company": self.company,
            "as_of_date": today,
            "current": {
                "items": current,
                "total": sum(item["balance_due"] for item in current),
            },
            "31_60_days": {
                "items": days_31_60,
                "total": sum(item["balance_due"] for item in days_31_60),
            },
            "61_90_days": {
                "items": days_61_90,
                "total": sum(item["balance_due"] for item in days_61_90),
            },
            "over_90_days": {
                "items": over_90,
                "total": sum(item["balance_due"] for item in over_90),
            },
            "grand_total": sum(
                item["balance_due"]
                for item in current + days_31_60 + days_61_90 + over_90
            ),
        }

    def cash_flow_forecast(self, days_ahead=90) -> Dict:
        """
        Cash Flow Forecast for next 30/60/90 days
        Estimates future cash position based on outstanding invoices and bills
        """
        today = datetime.now().date()
        forecast_date = today + timedelta(days=days_ahead)

        # Current cash position
        cash_accounts = Account.objects.filter(
            company=self.company, account_type=AccountType.ASSET, is_active=True
        ).filter(Q(name__icontains="cash") | Q(name__icontains="bank"))

        current_cash = sum(acc.get_balance() for acc in cash_accounts)

        # Expected cash inflows (outstanding invoices due within forecast period)
        expected_inflows = Invoice.objects.filter(
            company=self.company,
            status__in=["SENT", "OVERDUE"],
            due_date__lte=forecast_date,
        ).aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")

        # Expected cash outflows (bills due within forecast period)
        from accounting.models import Bill

        expected_outflows = Bill.objects.filter(
            status__in=["APPROVED"], due_date__lte=forecast_date
        ).aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")

        # Projected cash position
        projected_cash = current_cash + expected_inflows - expected_outflows

        # Monthly breakdown
        monthly_forecast = []
        for month in range(1, (days_ahead // 30) + 2):
            month_end = today + timedelta(days=30 * month)

            inflows = Invoice.objects.filter(
                company=self.company,
                status__in=["SENT", "OVERDUE"],
                due_date__gte=today,
                due_date__lte=month_end,
            ).aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")

            outflows = Bill.objects.filter(
                status__in=["APPROVED"], due_date__gte=today, due_date__lte=month_end
            ).aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")

            monthly_forecast.append(
                {
                    "month": month,
                    "end_date": month_end,
                    "inflows": inflows,
                    "outflows": outflows,
                    "net": inflows - outflows,
                }
            )

        return {
            "report_type": "Cash Flow Forecast",
            "company": self.company,
            "forecast_date": forecast_date,
            "days_ahead": days_ahead,
            "current_cash": current_cash,
            "expected_inflows": expected_inflows,
            "expected_outflows": expected_outflows,
            "projected_cash": projected_cash,
            "monthly_breakdown": monthly_forecast,
        }
