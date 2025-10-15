"""
Financial Metrics & Analytics Service
Calculates advanced KPIs, ratios, and insights for dashboard
"""

from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q, F, Avg
from django.utils import timezone
from accounting.models import (
    Account, AccountType, Invoice, Bill, JournalEntry,
    Customer, Vendor, Payment, Expense
)


class FinancialMetricsService:
    """Calculate comprehensive financial metrics for a company"""

    def __init__(self, company):
        self.company = company
        self.today = timezone.now().date()
        self.current_month_start = self.today.replace(day=1)
        self.last_month_start = (self.current_month_start - timedelta(days=1)).replace(day=1)
        self.last_month_end = self.current_month_start - timedelta(days=1)

    def get_all_metrics(self):
        """Get all metrics in one call for dashboard"""
        return {
            'cash_metrics': self.get_cash_metrics(),
            'revenue_metrics': self.get_revenue_metrics(),
            'expense_metrics': self.get_expense_metrics(),
            'profit_metrics': self.get_profit_metrics(),
            'invoice_metrics': self.get_invoice_metrics(),
            'bill_metrics': self.get_bill_metrics(),
            'customer_metrics': self.get_customer_metrics(),
            'health_score': self.calculate_health_score(),
            'financial_ratios': self.get_financial_ratios(),
            'trends': self.get_monthly_trends(),
            'alerts': self.get_alerts(),
            'recent_activity': self.get_recent_activity(),
        }

    def get_cash_metrics(self):
        """Calculate cash in bank and related metrics"""
        cash_accounts = Account.objects.filter(
            company=self.company,
            account_type=AccountType.ASSET,
            is_active=True
        ).filter(
            Q(name__icontains='cash') | Q(name__icontains='bank')
        )

        total_cash = sum(acc.get_balance() for acc in cash_accounts)

        # Last month cash for comparison
        # Simplified - in production, you'd track historical balances
        return {
            'total': total_cash,
            'accounts_count': cash_accounts.count(),
            'trend': 0,  # Calculate from historical data
        }

    def get_revenue_metrics(self):
        """Calculate revenue and growth"""
        current_revenue = self._get_revenue_for_period(
            self.current_month_start,
            self.today
        )

        last_month_revenue = self._get_revenue_for_period(
            self.last_month_start,
            self.last_month_end
        )

        growth = self._calculate_growth(current_revenue, last_month_revenue)

        return {
            'current_month': current_revenue,
            'last_month': last_month_revenue,
            'growth_percent': growth,
            'ytd': self._get_revenue_for_period(
                self.today.replace(month=1, day=1),
                self.today
            )
        }

    def get_expense_metrics(self):
        """Calculate expenses and growth"""
        current_expenses = self._get_expenses_for_period(
            self.current_month_start,
            self.today
        )

        last_month_expenses = self._get_expenses_for_period(
            self.last_month_start,
            self.last_month_end
        )

        growth = self._calculate_growth(current_expenses, last_month_expenses)

        # Get expense breakdown by category
        expense_accounts = Account.objects.filter(
            company=self.company,
            account_type=AccountType.EXPENSE,
            is_active=True
        )

        categories = {}
        for account in expense_accounts:
            balance = account.get_balance()
            if balance > 0:
                # Try to categorize by account name
                category = self._categorize_expense(account.name)
                categories[category] = categories.get(category, Decimal('0')) + balance

        return {
            'current_month': current_expenses,
            'last_month': last_month_expenses,
            'growth_percent': growth,
            'ytd': self._get_expenses_for_period(
                self.today.replace(month=1, day=1),
                self.today
            ),
            'by_category': categories
        }

    def get_profit_metrics(self):
        """Calculate profit and margins"""
        revenue = self._get_revenue_for_period(
            self.current_month_start,
            self.today
        )
        expenses = self._get_expenses_for_period(
            self.current_month_start,
            self.today
        )

        profit = revenue - expenses

        # Last month for comparison
        last_revenue = self._get_revenue_for_period(
            self.last_month_start,
            self.last_month_end
        )
        last_expenses = self._get_expenses_for_period(
            self.last_month_start,
            self.last_month_end
        )
        last_profit = last_revenue - last_expenses

        # Profit margin
        margin = (profit / revenue * 100) if revenue > 0 else Decimal('0')

        growth = self._calculate_growth(profit, last_profit)

        return {
            'current_month': profit,
            'last_month': last_profit,
            'margin_percent': margin,
            'growth_percent': growth,
        }

    def get_invoice_metrics(self):
        """Calculate invoice statistics"""
        invoices = Invoice.objects.filter(company=self.company)

        unpaid = invoices.filter(status__in=['SENT', 'OVERDUE'])
        overdue = invoices.filter(status='OVERDUE')

        unpaid_total = unpaid.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
        overdue_total = overdue.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')

        return {
            'unpaid_count': unpaid.count(),
            'unpaid_total': unpaid_total,
            'overdue_count': overdue.count(),
            'overdue_total': overdue_total,
            'paid_this_month': invoices.filter(
                status='PAID',
                invoice_date__gte=self.current_month_start
            ).count(),
        }

    def get_bill_metrics(self):
        """Calculate bill/payable statistics"""
        bills = Bill.objects.filter(company=self.company)

        # Bills due within 7 days
        upcoming_deadline = self.today + timedelta(days=7)
        due_soon = bills.filter(
            due_date__lte=upcoming_deadline,
            due_date__gte=self.today
        ).exclude(status='PAID')

        due_soon_total = due_soon.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')

        # Overdue bills
        overdue = bills.filter(
            due_date__lt=self.today
        ).exclude(status='PAID')

        overdue_total = overdue.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')

        return {
            'due_soon_count': due_soon.count(),
            'due_soon_total': due_soon_total,
            'overdue_count': overdue.count(),
            'overdue_total': overdue_total,
        }

    def get_customer_metrics(self):
        """Get top customers and metrics"""
        invoices = Invoice.objects.filter(company=self.company, status='PAID')

        # Top customers by revenue
        top_customers = invoices.values('customer__company_name').annotate(
            total_revenue=Sum('total_amount')
        ).order_by('-total_revenue')[:5]

        top_customer = top_customers.first() if top_customers else None

        return {
            'top_customer_name': top_customer['customer__company_name'] if top_customer else 'N/A',
            'top_customer_revenue': top_customer['total_revenue'] if top_customer else Decimal('0'),
            'top_5': list(top_customers),
            'total_customers': Customer.objects.filter(company=self.company, is_active=True).count(),
        }

    def get_financial_ratios(self):
        """Calculate key financial ratios"""
        # Get account balances by type
        assets = self._get_total_by_account_type(AccountType.ASSET)
        liabilities = self._get_total_by_account_type(AccountType.LIABILITY)
        equity = self._get_total_by_account_type(AccountType.EQUITY)

        # Current assets (simplified - should filter by liquidity)
        current_assets = assets * Decimal('0.7')  # Rough estimate
        current_liabilities = liabilities * Decimal('0.7')

        # Calculate ratios
        current_ratio = (current_assets / current_liabilities) if current_liabilities > 0 else Decimal('0')
        debt_to_equity = (liabilities / equity) if equity > 0 else Decimal('0')
        working_capital = current_assets - current_liabilities

        return {
            'current_ratio': current_ratio,
            'quick_ratio': current_ratio * Decimal('0.8'),  # Simplified
            'debt_to_equity': debt_to_equity,
            'working_capital': working_capital,
            'assets': assets,
            'liabilities': liabilities,
            'equity': equity,
        }

    def calculate_health_score(self):
        """Calculate business health score (0-100)"""
        score = Decimal('50')  # Base score

        # Factor 1: Profitability (30 points)
        profit_metrics = self.get_profit_metrics()
        if profit_metrics['current_month'] > 0:
            score += Decimal('15')
        if profit_metrics['margin_percent'] > 10:
            score += Decimal('15')

        # Factor 2: Cash position (20 points)
        cash = self.get_cash_metrics()['total']
        if cash > 0:
            score += Decimal('10')
        if cash > 10000:  # Threshold
            score += Decimal('10')

        # Factor 3: Receivables (20 points)
        invoice_metrics = self.get_invoice_metrics()
        if invoice_metrics['overdue_count'] == 0:
            score += Decimal('20')
        elif invoice_metrics['overdue_count'] < 5:
            score += Decimal('10')

        # Factor 4: Payables (15 points)
        bill_metrics = self.get_bill_metrics()
        if bill_metrics['overdue_count'] == 0:
            score += Decimal('15')

        # Factor 5: Growth (15 points)
        revenue_metrics = self.get_revenue_metrics()
        if revenue_metrics['growth_percent'] > 0:
            score += min(Decimal('15'), revenue_metrics['growth_percent'] / 2)

        return min(Decimal('100'), max(Decimal('0'), score))

    def get_monthly_trends(self, months=12):
        """Get monthly trends for charts"""
        trends = []

        for i in range(months):
            month_start = (self.today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            revenue = self._get_revenue_for_period(month_start, month_end)
            expenses = self._get_expenses_for_period(month_start, month_end)

            trends.insert(0, {
                'month': month_start.strftime('%b %Y'),
                'revenue': float(revenue),
                'expenses': float(expenses),
                'profit': float(revenue - expenses),
            })

        return trends

    def get_alerts(self):
        """Get system alerts and warnings"""
        alerts = []

        # Overdue invoices
        invoice_metrics = self.get_invoice_metrics()
        if invoice_metrics['overdue_count'] > 0:
            alerts.append({
                'type': 'warning',
                'icon': 'fa-exclamation-triangle',
                'message': f"{invoice_metrics['overdue_count']} overdue invoices totaling {invoice_metrics['overdue_total']} {self.company.currency}",
                'link': '/dashboard/invoices/',
            })

        # Bills due soon
        bill_metrics = self.get_bill_metrics()
        if bill_metrics['due_soon_count'] > 0:
            alerts.append({
                'type': 'info',
                'icon': 'fa-bell',
                'message': f"{bill_metrics['due_soon_count']} bills due within 7 days ({bill_metrics['due_soon_total']} {self.company.currency})",
                'link': '/dashboard/bills/',
            })

        # Low cash warning
        cash = self.get_cash_metrics()['total']
        if cash < 5000:  # Threshold
            alerts.append({
                'type': 'danger',
                'icon': 'fa-money-bill-wave',
                'message': f"Low cash balance: {cash} {self.company.currency}",
                'link': '/dashboard/cash-flow/',
            })

        # Health score warning
        health = self.calculate_health_score()
        if health < 50:
            alerts.append({
                'type': 'warning',
                'icon': 'fa-heartbeat',
                'message': f"Business health score is {health}/100 - needs attention",
                'link': '/dashboard/reports/',
            })

        return alerts

    # Helper methods
    def _get_revenue_for_period(self, start_date, end_date):
        """Get total revenue for period"""
        revenue_accounts = Account.objects.filter(
            company=self.company,
            account_type=AccountType.REVENUE,
            is_active=True
        )
        return sum(acc.get_balance() for acc in revenue_accounts)

    def _get_expenses_for_period(self, start_date, end_date):
        """Get total expenses for period"""
        expense_accounts = Account.objects.filter(
            company=self.company,
            account_type=AccountType.EXPENSE,
            is_active=True
        )
        return sum(acc.get_balance() for acc in expense_accounts)

    def _get_total_by_account_type(self, account_type):
        """Get total balance for account type"""
        accounts = Account.objects.filter(
            company=self.company,
            account_type=account_type,
            is_active=True
        )
        return sum(acc.get_balance() for acc in accounts)

    def _calculate_growth(self, current, previous):
        """Calculate percentage growth"""
        if previous == 0:
            return Decimal('0')
        return ((current - previous) / previous * 100)

    def _categorize_expense(self, account_name):
        """Categorize expense by account name"""
        name_lower = account_name.lower()

        categories = {
            'Salaries': ['salary', 'wage', 'payroll', 'compensation'],
            'Rent': ['rent', 'lease'],
            'Marketing': ['marketing', 'advertising', 'promotion'],
            'Utilities': ['utility', 'electricity', 'water', 'internet'],
            'Office': ['office', 'supplies', 'equipment'],
            'Travel': ['travel', 'transportation', 'fuel'],
            'Professional': ['legal', 'accounting', 'consulting'],
        }

        for category, keywords in categories.items():
            if any(keyword in name_lower for keyword in keywords):
                return category

        return 'Other'

    def get_recent_activity(self, limit=10):
        """Get recent business activity feed"""
        activities = []

        # Recent invoices
        recent_invoices = Invoice.objects.filter(
            company=self.company
        ).order_by('-created_at')[:5]

        for invoice in recent_invoices:
            activities.append({
                'type': 'invoice',
                'icon': 'fa-file-invoice',
                'color': 'blue',
                'title': f'Invoice {invoice.invoice_number} created',
                'description': f'{invoice.customer.company_name if hasattr(invoice, "customer") else "Customer"}',
                'amount': invoice.total_amount,
                'timestamp': invoice.created_at,
                'status': invoice.status,
            })

        # Recent journal entries
        recent_journals = JournalEntry.objects.filter(
            company=self.company
        ).order_by('-created_at')[:5]

        for journal in recent_journals:
            activities.append({
                'type': 'journal',
                'icon': 'fa-book',
                'color': 'purple',
                'title': f'Journal Entry {journal.entry_number}',
                'description': journal.description[:50],
                'amount': journal.total_debit,
                'timestamp': journal.created_at,
                'status': journal.status,
            })

        # Sort by timestamp and limit
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return activities[:limit]
