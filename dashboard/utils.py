"""
Dashboard Utility Functions
Helper functions for caching, calculations, and common operations
"""

from django.core.cache import cache
from decimal import Decimal
from datetime import datetime, timedelta


def get_cached_dashboard_metrics(company, metrics_service):
    """
    Get dashboard metrics with caching
    Cache key includes company ID and current hour for automatic refresh
    """
    current_hour = datetime.now().strftime("%Y%m%d%H")
    cache_key = f"dashboard_metrics_{company.id}_{current_hour}"

    metrics = cache.get(cache_key)

    if metrics is None:
        metrics = metrics_service.get_all_metrics()
        # Cache for 1 hour (3600 seconds)
        cache.set(cache_key, metrics, 3600)

    return metrics


def invalidate_dashboard_cache(company):
    """
    Invalidate dashboard cache when data changes
    Call this from signals when invoices, journal entries, etc. are saved
    """
    current_hour = datetime.now().strftime("%Y%m%d%H")
    cache_keys = [
        f"dashboard_metrics_{company.id}_{current_hour}",
        f"dashboard_metrics_{company.id}",
        f"balance_sheet_{company.id}",
        f"pnl_statement_{company.id}",
        f"financial_ratios_{company.id}",
        f"gl_balance_summary_{company.id}",
    ]

    for key in cache_keys:
        cache.delete(key)


def format_currency(amount, currency_symbol="$"):
    """Format decimal amount as currency"""
    if amount is None:
        return f"{currency_symbol}0.00"
    return f"{currency_symbol}{amount:,.2f}"


def calculate_percentage_change(current, previous):
    """Calculate percentage change between two values"""
    if previous == 0 or previous is None:
        return Decimal("0")
    if current is None:
        current = Decimal("0")
    return ((current - previous) / previous * 100).quantize(Decimal("0.1"))


def get_date_range_for_period(period="current_month"):
    """
    Get start and end dates for common periods

    Args:
        period: 'current_month', 'last_month', 'current_year', 'last_year', 'ytd'

    Returns:
        tuple: (start_date, end_date)
    """
    today = datetime.now().date()

    if period == "current_month":
        start_date = today.replace(day=1)
        end_date = today

    elif period == "last_month":
        first_day_this_month = today.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        start_date = last_day_last_month.replace(day=1)
        end_date = last_day_last_month

    elif period == "current_year":
        start_date = today.replace(month=1, day=1)
        end_date = today

    elif period == "last_year":
        start_date = today.replace(year=today.year - 1, month=1, day=1)
        end_date = today.replace(year=today.year - 1, month=12, day=31)

    elif period == "ytd":
        start_date = today.replace(month=1, day=1)
        end_date = today

    elif period == "last_30_days":
        end_date = today
        start_date = today - timedelta(days=30)

    elif period == "last_90_days":
        end_date = today
        start_date = today - timedelta(days=90)

    else:
        # Default to current month
        start_date = today.replace(day=1)
        end_date = today

    return start_date, end_date


def chunk_queryset(queryset, chunk_size=100):
    """
    Iterate over queryset in chunks to avoid memory issues
    Useful for processing large datasets
    """
    count = queryset.count()
    for i in range(0, count, chunk_size):
        yield queryset[i : i + chunk_size]


def sanitize_amount(value):
    """Convert any numeric value to Decimal safely"""
    if value is None:
        return Decimal("0.00")
    try:
        return Decimal(str(value)).quantize(Decimal("0.01"))
    except:
        return Decimal("0.00")


def get_financial_health_indicator(score):
    """
    Get health indicator based on score

    Returns:
        dict: {'status': str, 'color': str, 'icon': str}
    """
    if score >= 80:
        return {"status": "Excellent", "color": "green", "icon": "fa-check-circle"}
    elif score >= 60:
        return {"status": "Good", "color": "blue", "icon": "fa-thumbs-up"}
    elif score >= 40:
        return {"status": "Fair", "color": "yellow", "icon": "fa-exclamation-triangle"}
    else:
        return {
            "status": "Needs Attention",
            "color": "red",
            "icon": "fa-exclamation-circle",
        }


def batch_update_account_balances(accounts):
    """
    Batch update account balances for efficiency
    This would be called periodically or via signals
    """
    # This is a placeholder for a more efficient implementation
    # In production, you might store balances in a separate table
    # and update them via triggers or scheduled tasks
    pass
