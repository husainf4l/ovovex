from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_view(request):
    """
    Dashboard view for authenticated users
    """
    # Mock user for testing
    class MockUser:
        def __init__(self):
            self.username = "testuser"
            self.first_name = "Test"
            self.last_name = "User"
            self.email = "test@example.com"

        def get_full_name(self):
            return f"{self.first_name} {self.last_name}"

    context = {
        "title": "Dashboard",
        "description": "Your accounting dashboard and financial overview.",
        "user": MockUser(),
    }
    return render(request, "dashboard/dashboard.html", context)


@login_required
def general_ledger_view(request):
    """
    General Ledger view
    """
    from accounting.models import Account, JournalEntry, AccountType
    from django.db.models import Sum, Count
    from datetime import datetime, timedelta

    # Get filter parameters
    account_type_filter = request.GET.get("account_type", "all")

    # Get all accounts
    accounts = Account.objects.filter(is_active=True)
    if account_type_filter != "all":
        accounts = accounts.filter(account_type=account_type_filter)

    # Update balances for display
    for account in accounts:
        account.current_balance = account.get_balance()

    # Get statistics
    total_accounts = Account.objects.filter(is_active=True).count()

    # Journal entries this month
    current_month = datetime.now().replace(day=1).date()
    entries_this_month = JournalEntry.objects.filter(
        entry_date__gte=current_month, status="POSTED"
    ).count()

    # Unbalanced entries (draft or not balanced)
    unbalanced_entries = JournalEntry.objects.filter(status="DRAFT").count()

    # Recent journal entries
    recent_entries = JournalEntry.objects.filter(status="POSTED").order_by(
        "-entry_date", "-created_at"
    )[:5]

    # Calculate balance summary by account type
    from decimal import Decimal

    balance_summary = {
        "assets": Decimal("0.00"),
        "liabilities": Decimal("0.00"),
        "equity": Decimal("0.00"),
        "revenue": Decimal("0.00"),
        "expenses": Decimal("0.00"),
    }

    for account in Account.objects.filter(is_active=True):
        balance = account.get_balance()
        if account.account_type == AccountType.ASSET:
            balance_summary["assets"] += balance
        elif account.account_type == AccountType.LIABILITY:
            balance_summary["liabilities"] += balance
        elif account.account_type == AccountType.EQUITY:
            balance_summary["equity"] += balance
        elif account.account_type == AccountType.REVENUE:
            balance_summary["revenue"] += balance
        elif account.account_type == AccountType.EXPENSE:
            balance_summary["expenses"] += balance

    # Calculate net balance (Assets - Liabilities)
    net_balance = balance_summary["assets"] - balance_summary["liabilities"]

    # Total entries count
    total_entries = JournalEntry.objects.filter(status="POSTED").count()

    context = {
        "title": "General Ledger",
        "description": "Chart of accounts, journals, and ledger balances.",
        "user": request.user,
        "accounts": accounts,
        "recent_entries": recent_entries,
        "total_accounts": total_accounts,
        "entries_this_month": entries_this_month,
        "unbalanced_entries": unbalanced_entries,
        "total_entries": total_entries,
        "balance_summary": balance_summary,
        "net_balance": net_balance,
        "account_type_filter": account_type_filter,
        "account_types": AccountType.choices,
    }
    return render(request, "dashboard/modules/general_ledger.html", context)


@login_required
def invoices_view(request):
    """
    Invoices view
    """
    from accounting.models import Invoice, Customer
    from django.db.models import Sum, Count

    # Get all invoices
    invoices = Invoice.objects.all().select_related("customer")[:20]

    # Statistics
    total_invoices = Invoice.objects.count()
    total_revenue = Invoice.objects.aggregate(Sum("total_amount"))[
        "total_amount__sum"
    ] or Decimal("0.00")
    paid_invoices = Invoice.objects.filter(status="PAID").count()
    overdue_invoices = Invoice.objects.filter(status="OVERDUE").count()

    # Recent invoices
    recent_invoices = Invoice.objects.all().order_by("-invoice_date")[:5]

    context = {
        "title": "Invoices",
        "description": "Create, send, and track invoices.",
        "user": request.user,
        "invoices": invoices,
        "total_invoices": total_invoices,
        "total_revenue": total_revenue,
        "paid_invoices": paid_invoices,
        "overdue_invoices": overdue_invoices,
        "recent_invoices": recent_invoices,
    }
    return render(request, "dashboard/modules/invoices.html", context)


@login_required
def balance_sheet_view(request):
    """
    Balance Sheet view
    """
    from accounting.models import Account, AccountType
    from decimal import Decimal

    # Get accounts by type
    assets = Account.objects.filter(account_type=AccountType.ASSET, is_active=True)
    liabilities = Account.objects.filter(
        account_type=AccountType.LIABILITY, is_active=True
    )
    equity = Account.objects.filter(account_type=AccountType.EQUITY, is_active=True)

    # Calculate balances
    total_assets = sum(acc.get_balance() for acc in assets)
    total_liabilities = sum(acc.get_balance() for acc in liabilities)
    total_equity = sum(acc.get_balance() for acc in equity)

    # For balance sheet, calculate current vs non-current
    current_assets = sum(acc.get_balance() for acc in assets if acc.code < "1400")
    fixed_assets = sum(acc.get_balance() for acc in assets if acc.code >= "1400")
    current_liabilities = sum(
        acc.get_balance() for acc in liabilities if acc.code < "2300"
    )
    long_term_liabilities = sum(
        acc.get_balance() for acc in liabilities if acc.code >= "2300"
    )

    context = {
        "title": "Balance Sheet",
        "description": "Assets, liabilities, and equity overview.",
        "user": request.user,
        "assets": assets,
        "liabilities": liabilities,
        "equity": equity,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "total_equity": total_equity,
        "current_assets": current_assets,
        "fixed_assets": fixed_assets,
        "current_liabilities": current_liabilities,
        "long_term_liabilities": long_term_liabilities,
    }
    return render(request, "dashboard/modules/balance_sheet.html", context)


@login_required
def pnl_statement_view(request):
    """
    P&L Statement view
    """
    from accounting.models import Account, AccountType
    from decimal import Decimal

    # Get revenue and expense accounts
    revenue_accounts = Account.objects.filter(
        account_type=AccountType.REVENUE, is_active=True
    )
    expense_accounts = Account.objects.filter(
        account_type=AccountType.EXPENSE, is_active=True
    )

    # Calculate totals
    total_revenue = sum(acc.get_balance() for acc in revenue_accounts)
    total_expenses = sum(acc.get_balance() for acc in expense_accounts)

    # Net profit/loss
    net_profit = total_revenue - total_expenses
    profit_margin = (
        (net_profit / total_revenue * 100) if total_revenue > 0 else Decimal("0.00")
    )

    # Break down expenses by category
    cogs = sum(
        acc.get_balance() for acc in expense_accounts if acc.code.startswith("50")
    )
    operating_expenses = sum(
        acc.get_balance() for acc in expense_accounts if not acc.code.startswith("50")
    )

    gross_profit = total_revenue - cogs

    context = {
        "title": "P&L Statement",
        "description": "Profit and Loss statement analysis.",
        "user": request.user,
        "revenue_accounts": revenue_accounts,
        "expense_accounts": expense_accounts,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "cogs": cogs,
        "gross_profit": gross_profit,
        "operating_expenses": operating_expenses,
        "net_profit": net_profit,
        "profit_margin": profit_margin,
    }
    return render(request, "dashboard/modules/income_statement.html", context)


@login_required
def journal_entries_view(request):
    """
    Journal Entries view
    """
    from accounting.models import JournalEntry, JournalEntryLine, Account
    from django.db.models import Sum, Count, Q
    from datetime import datetime, timedelta

    # Get all journal entries
    journal_entries = JournalEntry.objects.all().order_by("-entry_date", "-id")

    # Get statistics
    total_entries = journal_entries.count()

    # Get entries by status
    posted_entries = journal_entries.filter(status=JournalEntry.Status.POSTED).count()
    draft_entries = journal_entries.filter(status=JournalEntry.Status.DRAFT).count()

    # Get recent entries
    recent_entries = journal_entries[:10]

    # Calculate total debits and credits for this month
    today = datetime.now().date()
    first_day = today.replace(day=1)

    month_entries = JournalEntry.objects.filter(
        entry_date__gte=first_day, entry_date__lte=today
    )

    # Get all lines for month entries
    month_lines = JournalEntryLine.objects.filter(journal_entry__in=month_entries)

    total_debits = month_lines.aggregate(Sum("debit_amount"))[
        "debit_amount__sum"
    ] or Decimal("0.00")
    total_credits = month_lines.aggregate(Sum("credit_amount"))[
        "credit_amount__sum"
    ] or Decimal("0.00")

    # Get status distribution (instead of entry_type which doesn't exist)
    status_distribution = journal_entries.values("status").annotate(count=Count("id"))

    # Get all active accounts for the dropdown
    accounts = Account.objects.filter(is_active=True).order_by("code")

    context = {
        "title": "Journal Entries",
        "description": "Manual journal entries and adjustments.",
        "user": request.user,
        "journal_entries": journal_entries,
        "total_entries": total_entries,
        "posted_entries": posted_entries,
        "draft_entries": draft_entries,
        "recent_entries": recent_entries,
        "total_debits": total_debits,
        "total_credits": total_credits,
        "status_distribution": status_distribution,
        "accounts": accounts,
    }
    return render(request, "dashboard/modules/journal_entries.html", context)


@login_required
def budgeting_view(request):
    """
    Budgeting view
    """
    context = {
        "title": "Budgeting",
        "description": "Create and manage budgets for your business.",
        "user": request.user,
    }
    return render(request, "dashboard/modules/budgeting.html", context)


@login_required
def fixed_assets_view(request):
    """
    Fixed assets view
    """
    from accounting.models import FixedAsset
    from decimal import Decimal
    from django.db.models import Sum, Count
    
    # Get all active fixed assets
    fixed_assets = FixedAsset.objects.filter(is_active=True).order_by('asset_code')
    
    # Calculate summary statistics
    total_cost = fixed_assets.aggregate(total=Sum('purchase_cost'))['total'] or Decimal('0.00')
    total_depreciation = fixed_assets.aggregate(total=Sum('accumulated_depreciation'))['total'] or Decimal('0.00')
    total_book_value = total_cost - total_depreciation
    
    # Count assets by category
    category_counts = fixed_assets.values('category').annotate(count=Count('id'))
    
    equipment_count = 0
    furniture_count = 0
    vehicles_count = 0
    
    for count_data in category_counts:
        if count_data['category'] == 'OFFICE_EQUIPMENT':
            equipment_count = count_data['count']
        elif count_data['category'] == 'COMPUTER_EQUIPMENT':
            equipment_count += count_data['count']  # Add computer equipment to equipment
        elif count_data['category'] == 'FURNITURE':
            furniture_count = count_data['count']
        elif count_data['category'] == 'VEHICLES':
            vehicles_count = count_data['count']
    
    context = {
        "title": "Fixed Assets",
        "fixed_assets": fixed_assets,
        "total_cost": total_cost,
        "total_depreciation": total_depreciation,
        "total_book_value": total_book_value,
        "equipment_count": equipment_count,
        "furniture_count": furniture_count,
        "vehicles_count": vehicles_count,
    }
    return render(request, "dashboard/modules/fixed_assets.html", context)


@login_required
def ai_insights_view(request):
    """
    AI Insights view
    """
    context = {
        "title": "AI Insights",
        "description": "AI-powered financial analysis and insights.",
        "user": request.user,
    }
    return render(request, "dashboard/modules/ai_insights.html", context)


@login_required
def settings_view(request):
    """
    Settings view
    """
    context = {
        "title": "Settings",
        "description": "Configure your account and preferences.",
        "user": request.user,
    }
    return render(request, "dashboard/modules/settings.html", context)


@login_required
def cash_flow_view(request):
    """
    Cash Flow view
    """
    context = {
        "title": "Cash Flow",
        "description": "Track cash inflows and outflows.",
        "user": request.user,
    }
    return render(request, "dashboard/modules/cash_flow.html", context)


@login_required
def financial_ratios_view(request):
    """
    Financial Ratios view
    """
    context = {
        "title": "Financial Ratios",
        "description": "Key financial ratios and metrics.",
        "user": request.user,
    }
    return render(request, "dashboard/modules/financial_ratios.html", context)
