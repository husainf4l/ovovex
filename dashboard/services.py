"""
Optimized Financial Metrics & Analytics Service
- Efficient database queries
- Proper use of aggregations
- Minimal N+1 query issues
"""

from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q, F, Avg, Max, Min
from django.utils import timezone
from django.core.cache import cache

from accounting.models import (
    Account, AccountType, Invoice, Bill, JournalEntry,
    Customer, Vendor, Payment, Expense, JournalEntryLine
)


class FinancialMetricsService:
    """
    Optimized service for calculating financial metrics
    - Uses aggregations instead of loops
    - Caches expensive operations
    - Minimal database queries
    """

    def __init__(self, company):
        self.company = company
        self.today = timezone.now().date()
        self.current_month_start = self.today.replace(day=1)
        self.last_month_start = (self.current_month_start - timedelta(days=1)).replace(day=1)
        self.last_month_end = self.current_month_start - timedelta(days=1)
        self.year_start = self.today.replace(month=1, day=1)

    def get_all_metrics(self):
        """
        Get all metrics efficiently
        Uses a single database roundtrip where possible
        """
        # Get all metrics that can be calculated from account balances
        account_balances = self._get_account_balances_by_type()
        
        return {
            'cash_metrics': self._get_cash_metrics_optimized(account_balances),
            'revenue_metrics': self._get_revenue_metrics_optimized(account_balances),
            'expense_metrics': self._get_expense_metrics_optimized(account_balances),
            'profit_metrics': self._get_profit_metrics_optimized(account_balances),
            'invoice_metrics': self._get_invoice_metrics_optimized(),
            'bill_metrics': self._get_bill_metrics_optimized(),
            'customer_metrics': self._get_customer_metrics_optimized(),
            'financial_ratios': self._get_financial_ratios_optimized(account_balances),
            'health_score': self._calculate_health_score_optimized(),
            'alerts': self._get_alerts_optimized(),
        }

    def _get_account_balances_by_type(self):
        """
        Get aggregated account balances by type in a single query
        This replaces hundreds of individual acc.get_balance() calls
        """
        # Cache this for 5 minutes since it's expensive
        cache_key = f'account_balances_{self.company.id}'
        cached = cache.get(cache_key)
        
        if cached:
            return cached
        
        # Get all journal entry lines for the company in one query
        # This is still expensive but much better than N queries
        accounts = Account.objects.filter(
            company=self.company,
            is_active=True
        ).values('id', 'account_type', 'name', 'code')
        
        balances = {
            'ASSET': Decimal('0'),
            'LIABILITY': Decimal('0'),
            'EQUITY': Decimal('0'),
            'REVENUE': Decimal('0'),
            'EXPENSE': Decimal('0'),
            'accounts_by_type': {
                'ASSET': [],
                'LIABILITY': [],
                'EQUITY': [],
                'REVENUE': [],
                'EXPENSE': [],
            }
        }
        
        # Group accounts by type
        for account in accounts:
            acc_type = account['account_type']
            if acc_type in balances:
                balances['accounts_by_type'][acc_type].append(account)
        
        # For now, we'll use simplified balance calculation
        # In production, you'd want to optimize Account.get_balance() or cache it
        for acc_type in ['ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE']:
            acc_ids = [a['id'] for a in balances['accounts_by_type'][acc_type]]
            if acc_ids:
                # Get total debits and credits for these accounts
                lines = JournalEntryLine.objects.filter(
                    account_id__in=acc_ids,
                    journal_entry__status='POSTED',
                    journal_entry__company=self.company
                ).aggregate(
                    total_debit=Sum('debit_amount'),
                    total_credit=Sum('credit_amount')
                )
                
                debit = lines['total_debit'] or Decimal('0')
                credit = lines['total_credit'] or Decimal('0')
                
                # Balance depends on account type
                if acc_type in ['ASSET', 'EXPENSE']:
                    balances[acc_type] = debit - credit
                else:
                    balances[acc_type] = credit - debit
        
        # Cache for 5 minutes
        cache.set(cache_key, balances, 300)
        
        return balances

    def _get_cash_metrics_optimized(self, account_balances):
        """Optimized cash metrics using pre-calculated balances"""
        # Filter cash accounts from assets
        cash_account_ids = [
            a['id'] for a in account_balances['accounts_by_type']['ASSET']
            if 'cash' in a['name'].lower() or 'bank' in a['name'].lower()
        ]
        
        if not cash_account_ids:
            return {
                'total': Decimal('0'),
                'accounts_count': 0,
                'trend': 0,
            }
        
        # Get cash balance
        cash_lines = JournalEntryLine.objects.filter(
            account_id__in=cash_account_ids,
            journal_entry__status='POSTED',
            journal_entry__company=self.company
        ).aggregate(
            total_debit=Sum('debit_amount'),
            total_credit=Sum('credit_amount')
        )
        
        total_cash = (cash_lines['total_debit'] or Decimal('0')) - (cash_lines['total_credit'] or Decimal('0'))
        
        return {
            'total': total_cash,
            'accounts_count': len(cash_account_ids),
            'trend': 0,  # Would need historical data
        }

    def _get_revenue_metrics_optimized(self, account_balances):
        """Optimized revenue metrics"""
        current_revenue = account_balances['REVENUE']
        
        return {
            'current_month': current_revenue,
            'last_month': Decimal('0'),  # Would need period tracking
            'growth_percent': Decimal('0'),
            'ytd': current_revenue,
        }

    def _get_expense_metrics_optimized(self, account_balances):
        """Optimized expense metrics"""
        current_expenses = account_balances['EXPENSE']
        
        return {
            'current_month': current_expenses,
            'last_month': Decimal('0'),
            'growth_percent': Decimal('0'),
            'ytd': current_expenses,
            'by_category': {},
        }

    def _get_profit_metrics_optimized(self, account_balances):
        """Optimized profit metrics"""
        revenue = account_balances['REVENUE']
        expenses = account_balances['EXPENSE']
        profit = revenue - expenses
        margin = (profit / revenue * 100) if revenue > 0 else Decimal('0')
        
        return {
            'current_month': profit,
            'last_month': Decimal('0'),
            'margin_percent': margin,
            'growth_percent': Decimal('0'),
        }

    def _get_invoice_metrics_optimized(self):
        """Optimized invoice metrics - single aggregated query"""
        metrics = Invoice.objects.filter(
            company=self.company
        ).aggregate(
            unpaid_total=Sum('total_amount', filter=Q(status__in=['SENT', 'OVERDUE'])),
            unpaid_count=Count('id', filter=Q(status__in=['SENT', 'OVERDUE'])),
            overdue_total=Sum('total_amount', filter=Q(status='OVERDUE')),
            overdue_count=Count('id', filter=Q(status='OVERDUE')),
            paid_this_month=Count('id', filter=Q(
                status='PAID',
                invoice_date__gte=self.current_month_start
            ))
        )
        
        return {
            'unpaid_count': metrics['unpaid_count'] or 0,
            'unpaid_total': metrics['unpaid_total'] or Decimal('0'),
            'overdue_count': metrics['overdue_count'] or 0,
            'overdue_total': metrics['overdue_total'] or Decimal('0'),
            'paid_this_month': metrics['paid_this_month'] or 0,
        }

    def _get_bill_metrics_optimized(self):
        """Optimized bill metrics - single query"""
        upcoming_deadline = self.today + timedelta(days=7)
        
        metrics = Bill.objects.filter(
            company=self.company
        ).exclude(
            status='PAID'
        ).aggregate(
            due_soon_total=Sum('total_amount', filter=Q(
                due_date__gte=self.today,
                due_date__lte=upcoming_deadline
            )),
            due_soon_count=Count('id', filter=Q(
                due_date__gte=self.today,
                due_date__lte=upcoming_deadline
            )),
            overdue_total=Sum('total_amount', filter=Q(due_date__lt=self.today)),
            overdue_count=Count('id', filter=Q(due_date__lt=self.today))
        )
        
        return {
            'due_soon_count': metrics['due_soon_count'] or 0,
            'due_soon_total': metrics['due_soon_total'] or Decimal('0'),
            'overdue_count': metrics['overdue_count'] or 0,
            'overdue_total': metrics['overdue_total'] or Decimal('0'),
        }

    def _get_customer_metrics_optimized(self):
        """Optimized customer metrics - single query with annotation"""
        top_customers = Invoice.objects.filter(
            company=self.company,
            status='PAID'
        ).values(
            'customer__company_name'
        ).annotate(
            total_revenue=Sum('total_amount')
        ).order_by('-total_revenue')[:5]
        
        top_list = list(top_customers)
        top_customer = top_list[0] if top_list else None
        
        total_customers = Customer.objects.filter(
            company=self.company,
            is_active=True
        ).count()
        
        return {
            'top_customer_name': top_customer['customer__company_name'] if top_customer else 'N/A',
            'top_customer_revenue': top_customer['total_revenue'] if top_customer else Decimal('0'),
            'top_5': top_list,
            'total_customers': total_customers,
        }

    def _get_financial_ratios_optimized(self, account_balances):
        """Optimized financial ratios using pre-calculated balances"""
        assets = account_balances['ASSET']
        liabilities = account_balances['LIABILITY']
        equity = account_balances['EQUITY']
        
        # Simplified ratios (would need more detail for accurate calculation)
        current_assets = assets * Decimal('0.7')
        current_liabilities = liabilities * Decimal('0.7')
        
        current_ratio = (current_assets / current_liabilities) if current_liabilities > 0 else Decimal('0')
        debt_to_equity = (liabilities / equity) if equity > 0 else Decimal('0')
        working_capital = current_assets - current_liabilities
        
        return {
            'current_ratio': current_ratio,
            'quick_ratio': current_ratio * Decimal('0.8'),
            'debt_to_equity': debt_to_equity,
            'working_capital': working_capital,
            'assets': assets,
            'liabilities': liabilities,
            'equity': equity,
        }

    def _calculate_health_score_optimized(self):
        """Calculate health score efficiently"""
        # Simplified for now - would need more metrics
        return Decimal('75')  # Placeholder

    def _get_alerts_optimized(self):
        """Get system alerts efficiently"""
        alerts = []
        
        # Get invoice and bill metrics (already optimized)
        invoice_metrics = self._get_invoice_metrics_optimized()
        bill_metrics = self._get_bill_metrics_optimized()
        
        # Overdue invoices alert
        if invoice_metrics['overdue_count'] > 0:
            alerts.append({
                'type': 'warning',
                'icon': 'fa-exclamation-triangle',
                'message': f"{invoice_metrics['overdue_count']} overdue invoices totaling {invoice_metrics['overdue_total']}",
                'link': '/accounting/invoices/',
            })
        
        # Bills due soon alert
        if bill_metrics['due_soon_count'] > 0:
            alerts.append({
                'type': 'info',
                'icon': 'fa-bell',
                'message': f"{bill_metrics['due_soon_count']} bills due within 7 days",
                'link': '/accounting/bills/',
            })
        
        return alerts

    def get_financial_ratios(self):
        """Public method for getting financial ratios"""
        account_balances = self._get_account_balances_by_type()
        return self._get_financial_ratios_optimized(account_balances)

    def get_revenue_metrics(self):
        """Public method for revenue metrics"""
        account_balances = self._get_account_balances_by_type()
        return self._get_revenue_metrics_optimized(account_balances)

    def get_expense_metrics(self):
        """Public method for expense metrics"""
        account_balances = self._get_account_balances_by_type()
        return self._get_expense_metrics_optimized(account_balances)

    def get_profit_metrics(self):
        """Public method for profit metrics"""
        account_balances = self._get_account_balances_by_type()
        return self._get_profit_metrics_optimized(account_balances)
