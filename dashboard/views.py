from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_view(request):
    """
    Dashboard view for authenticated users
    """
    from accounting.models import (
        Account,
        AccountType,
        Invoice,
        JournalEntry,
        JournalEntryLine,
        Customer,
        Vendor,
        Bill,
        Expense,
        FixedAsset,
        Budget,
        BudgetLine,
    )
    from django.db.models import Sum, Count, Q
    from decimal import Decimal
    from datetime import datetime, timedelta

    # Get current date info
    today = datetime.now().date()
    current_month = today.replace(day=1)
    last_month = (current_month - timedelta(days=1)).replace(day=1)

    # Get active company from middleware
    active_company = request.active_company

    # === FINANCIAL OVERVIEW KPIs ===

    # 1. Total Revenue (from posted journal entries to revenue accounts)
    revenue_accounts = Account.objects.filter(
        company=active_company,
        account_type=AccountType.REVENUE,
        is_active=True
    )
    total_revenue = sum(acc.get_balance() for acc in revenue_accounts)

    # 2. Total Expenses (from posted journal entries to expense accounts)
    expense_accounts = Account.objects.filter(
        company=active_company,
        account_type=AccountType.EXPENSE,
        is_active=True
    )
    total_expenses = sum(acc.get_balance() for acc in expense_accounts)

    # 3. Net Profit (Revenue - Expenses)
    net_profit = total_revenue - total_expenses

    # 4. Cash on Hand (balance of cash/bank accounts)
    cash_accounts = Account.objects.filter(
        company=active_company,
        account_type=AccountType.ASSET,
        is_active=True
    ).filter(Q(name__icontains="cash") | Q(name__icontains="bank"))
    cash_on_hand = sum(acc.get_balance() for acc in cash_accounts)

    # 5. Outstanding Invoices (unpaid invoices)
    outstanding_invoices = Invoice.objects.filter(
        company=active_company,
        status__in=["SENT", "OVERDUE"]
    ).aggregate(total=Sum("total_amount"), count=Count("id"))
    outstanding_amount = outstanding_invoices["total"] or Decimal("0.00")
    outstanding_count = outstanding_invoices["count"] or 0

    # 6. Payables Due (unpaid bills due within 7 days)
    payables_due = (
        Bill.objects.filter(
            status__in=["APPROVED", "PAID"], due_date__lte=today + timedelta(days=7)
        )
        .exclude(status="PAID")
        .aggregate(total=Sum("total_amount"), count=Count("id"))
    )
    payables_amount = payables_due["total"] or Decimal("0.00")
    payables_count = payables_due["count"] or 0

    # === MONTHLY COMPARISON (vs last month) ===

    # Revenue this month vs last month
    current_month_revenue = Decimal("0.00")
    last_month_revenue = Decimal("0.00")

    # Get journal entries for revenue accounts this month
    for acc in revenue_accounts:
        # This is simplified - in reality you'd need to track monthly balances
        # For now, we'll use total balances (this is a limitation of the current model)
        pass

    # Calculate percentage changes (would need historical data for accurate calculation)
    revenue_change_pct = Decimal("0.0")
    expenses_change_pct = Decimal("0.0")
    profit_change_pct = Decimal("0.0")
    cash_change_pct = Decimal("0.0")

    # === ADDITIONAL KPIs ===

    # Gross Margin
    cogs_accounts = expense_accounts.filter(name__icontains="cost of goods")
    cogs = sum(acc.get_balance() for acc in cogs_accounts)
    gross_profit = total_revenue - cogs
    gross_margin = (
        (gross_profit / total_revenue * 100) if total_revenue > 0 else Decimal("0.00")
    )

    # Customer Acquisition Cost (would need detailed tracking)
    cac = Decimal("0.00")

    # Monthly Recurring Revenue
    mrr = Decimal("0.00")

    # Employee Productivity
    productivity = Decimal("0.0")

    # === BALANCE SHEET SUMMARY ===
    assets = Account.objects.filter(account_type=AccountType.ASSET, is_active=True)
    liabilities = Account.objects.filter(
        account_type=AccountType.LIABILITY, is_active=True
    )
    equity = Account.objects.filter(account_type=AccountType.EQUITY, is_active=True)

    total_assets = sum(acc.get_balance() for acc in assets)
    total_liabilities = sum(acc.get_balance() for acc in liabilities)
    total_equity = sum(acc.get_balance() for acc in equity)

    # === RECENT ACTIVITY ===
    recent_entries = (
        JournalEntry.objects.filter(status="POSTED")
        .select_related("created_by")
        .order_by("-entry_date")[:5]
    )

    # === TOP CLIENTS ===
    top_clients = (
        Customer.objects.annotate(total_invoiced=Sum("invoices__total_amount"))
        .filter(total_invoiced__gt=0)
        .order_by("-total_invoiced")[:5]
    )

    # === FINANCIAL RATIOS ===
    # Calculate current assets/liabilities for ratio calculation
    current_assets = sum(acc.get_balance() for acc in assets if acc.code < "1400")
    current_liabilities = sum(acc.get_balance() for acc in liabilities if acc.code < "2300")

    current_ratio = (current_assets / current_liabilities) if current_liabilities > 0 else Decimal("0.00")
    quick_ratio = current_ratio  # Simplified - would need inventory data
    debt_to_equity = (
        (total_liabilities / total_equity) if total_equity > 0 else Decimal("0.00")
    )
    roe = (net_profit / total_equity * 100) if total_equity > 0 else Decimal("0.00")
    roa = (net_profit / total_assets * 100) if total_assets > 0 else Decimal("0.00")

    # === EXPENSE BREAKDOWN ===
    # Calculate from actual expenses
    expense_breakdown = []
    if total_expenses > 0:
        from accounting.models import ExpenseCategory
        for category in ExpenseCategory.objects.all():
            category_expenses = Expense.objects.filter(category=category)
            category_total = sum(exp.amount for exp in category_expenses)
            if category_total > 0:
                percentage = (category_total / total_expenses * 100)
                expense_breakdown.append({
                    "category": category.name,
                    "amount": category_total,
                    "percentage": percentage,
                })

    # Sort by amount descending
    expense_breakdown.sort(key=lambda x: x['amount'], reverse=True)

    # === BUDGET INFORMATION ===
    current_budget = Budget.objects.filter(
        is_active=True, start_date__lte=today, end_date__gte=today
    ).first()

    if current_budget:
        budget_lines = BudgetLine.objects.filter(budget=current_budget)
        total_budget = current_budget.total_budget
        budget_used = sum(line.actual_amount for line in budget_lines)
        budget_remaining = total_budget - budget_used
        budget_utilization = (
            (budget_used / total_budget * 100)
            if total_budget > 0
            else Decimal("0.00")
        )
    else:
        total_budget = Decimal("0.00")
        budget_used = Decimal("0.00")
        budget_remaining = Decimal("0.00")
        budget_utilization = Decimal("0.0")

    # === GOALS & TARGETS ===
    # These would typically come from a Goals/Targets model
    monthly_revenue_goal = Decimal("0.00")
    monthly_revenue_actual = total_revenue
    revenue_goal_completion = (
        (monthly_revenue_actual / monthly_revenue_goal * 100)
        if monthly_revenue_goal > 0
        else Decimal("0.00")
    )

    new_clients_goal = 0
    new_clients_actual = Customer.objects.filter(
        created_at__gte=current_month
    ).count() if hasattr(Customer, 'created_at') else 0
    clients_goal_completion = (
        (new_clients_actual / new_clients_goal * 100)
        if new_clients_goal > 0
        else Decimal("0.00")
    )

    expense_budget_goal = Decimal("0.00")
    expense_budget_actual = total_expenses
    expense_budget_completion = (
        (expense_budget_actual / expense_budget_goal * 100)
        if expense_budget_goal > 0
        else Decimal("0.00")
    )

    profit_margin_goal = Decimal("0.0")
    profit_margin_actual = (
        (net_profit / total_revenue * 100) if total_revenue > 0 else Decimal("0.00")
    )
    profit_margin_completion = (
        (profit_margin_actual / profit_margin_goal * 100)
        if profit_margin_goal > 0
        else Decimal("0.00")
    )

    context = {
        "title": "Dashboard",
        "description": "Your accounting dashboard and financial overview.",
        "user": request.user,
        # Main KPIs
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "net_profit": net_profit,
        "cash_on_hand": cash_on_hand,
        "outstanding_invoices": outstanding_amount,
        "outstanding_count": outstanding_count,
        "payables_due": payables_amount,
        "payables_count": payables_count,
        # Percentage changes
        "revenue_change_pct": revenue_change_pct,
        "expenses_change_pct": expenses_change_pct,
        "profit_change_pct": profit_change_pct,
        "cash_change_pct": cash_change_pct,
        # Additional KPIs
        "gross_margin": gross_margin,
        "cac": cac,
        "mrr": mrr,
        "productivity": productivity,
        # Balance Sheet
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "total_equity": total_equity,
        # Recent Activity
        "recent_entries": recent_entries,
        # Top Clients
        "top_clients": top_clients,
        # Financial Ratios
        "current_ratio": current_ratio,
        "quick_ratio": quick_ratio,
        "debt_to_equity": debt_to_equity,
        "roe": roe,
        "roa": roa,
        # Expense Breakdown
        "expense_breakdown": expense_breakdown,
        # Budget
        "total_budget": total_budget,
        "budget_used": budget_used,
        "budget_remaining": budget_remaining,
        "budget_utilization": budget_utilization,
        # Goals
        "monthly_revenue_goal": monthly_revenue_goal,
        "monthly_revenue_actual": monthly_revenue_actual,
        "revenue_goal_completion": revenue_goal_completion,
        "new_clients_goal": new_clients_goal,
        "new_clients_actual": new_clients_actual,
        "clients_goal_completion": clients_goal_completion,
        "expense_budget_goal": expense_budget_goal,
        "expense_budget_actual": expense_budget_actual,
        "expense_budget_completion": expense_budget_completion,
        "profit_margin_goal": profit_margin_goal,
        "profit_margin_actual": profit_margin_actual,
        "profit_margin_completion": profit_margin_completion,
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
    from decimal import Decimal

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
    from decimal import Decimal

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
    fixed_assets = FixedAsset.objects.filter(is_active=True).order_by("asset_code")

    # Calculate summary statistics
    total_cost = fixed_assets.aggregate(total=Sum("purchase_cost"))["total"] or Decimal(
        "0.00"
    )
    total_depreciation = fixed_assets.aggregate(total=Sum("accumulated_depreciation"))[
        "total"
    ] or Decimal("0.00")
    total_book_value = total_cost - total_depreciation

    # Count assets by category
    category_counts = fixed_assets.values("category").annotate(count=Count("id"))

    equipment_count = 0
    furniture_count = 0
    vehicles_count = 0

    for count_data in category_counts:
        if count_data["category"] == "OFFICE_EQUIPMENT":
            equipment_count = count_data["count"]
        elif count_data["category"] == "COMPUTER_EQUIPMENT":
            equipment_count += count_data[
                "count"
            ]  # Add computer equipment to equipment
        elif count_data["category"] == "FURNITURE":
            furniture_count = count_data["count"]
        elif count_data["category"] == "VEHICLES":
            vehicles_count = count_data["count"]

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
def create_invoice_view(request):
    """
    Create invoice view
    """
    from accounting.models import Customer, Invoice, InvoiceLine
    from django.http import JsonResponse
    from decimal import Decimal
    import json

    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Create invoice
            customer = Customer.objects.get(id=data["customer_id"])
            invoice = Invoice.objects.create(
                invoice_number=data["invoice_number"],
                customer=customer,
                invoice_date=data["invoice_date"],
                due_date=data["due_date"],
                notes=data.get("notes", ""),
                created_by=request.user,
            )

            # Add line items
            subtotal = Decimal("0.00")
            for line_data in data["lines"]:
                line_total = Decimal(str(line_data["quantity"])) * Decimal(
                    str(line_data["unit_price"])
                )
                InvoiceLine.objects.create(
                    invoice=invoice,
                    description=line_data["description"],
                    quantity=Decimal(str(line_data["quantity"])),
                    unit_price=Decimal(str(line_data["unit_price"])),
                    line_total=line_total,
                )
                subtotal += line_total

            # Calculate totals
            tax_rate = Decimal("0.10")  # 10% tax rate
            tax_amount = subtotal * tax_rate
            total_amount = subtotal + tax_amount

            invoice.subtotal = subtotal
            invoice.tax_amount = tax_amount
            invoice.total_amount = total_amount
            invoice.save()

            return JsonResponse(
                {
                    "success": True,
                    "message": "Invoice created successfully",
                    "invoice_id": invoice.id,
                    "invoice_number": invoice.invoice_number,
                }
            )

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    # GET request - return form data
    customers = Customer.objects.filter(is_active=True)
    context = {
        "title": "Create Invoice",
        "customers": customers,
    }
    return render(request, "modules/create_invoice.html", context)


@login_required
def financial_ratios_view(request):
    """
    Financial ratios view
    """
    from accounting.models import Account, AccountType
    from decimal import Decimal

    # Get balance sheet data
    assets = Account.objects.filter(account_type=AccountType.ASSET, is_active=True)
    liabilities = Account.objects.filter(
        account_type=AccountType.LIABILITY, is_active=True
    )
    equity = Account.objects.filter(account_type=AccountType.EQUITY, is_active=True)

    total_assets = sum(acc.get_balance() for acc in assets)
    total_liabilities = sum(acc.get_balance() for acc in liabilities)
    total_equity = sum(acc.get_balance() for acc in equity)

    # Get income statement data
    revenue_accounts = Account.objects.filter(
        account_type=AccountType.REVENUE, is_active=True
    )
    expense_accounts = Account.objects.filter(
        account_type=AccountType.EXPENSE, is_active=True
    )

    total_revenue = sum(acc.get_balance() for acc in revenue_accounts)
    total_expenses = sum(acc.get_balance() for acc in expense_accounts)
    net_income = total_revenue - total_expenses

    # Calculate ratios
    ratios = {}

    # Liquidity ratios
    current_assets = sum(acc.get_balance() for acc in assets if acc.code < "1400")
    current_liabilities = sum(
        acc.get_balance() for acc in liabilities if acc.code < "2300"
    )

    ratios["current_ratio"] = (
        (current_assets / current_liabilities)
        if current_liabilities > 0
        else Decimal("0.00")
    )
    ratios["quick_ratio"] = ratios["current_ratio"]  # Simplified

    # Profitability ratios
    ratios["gross_margin"] = (
        ((total_revenue - total_expenses) / total_revenue * 100)
        if total_revenue > 0
        else Decimal("0.00")
    )
    ratios["net_margin"] = (
        (net_income / total_revenue * 100) if total_revenue > 0 else Decimal("0.00")
    )
    ratios["return_on_assets"] = (
        (net_income / total_assets * 100) if total_assets > 0 else Decimal("0.00")
    )
    ratios["return_on_equity"] = (
        (net_income / total_equity * 100) if total_equity > 0 else Decimal("0.00")
    )

    # Leverage ratios
    ratios["debt_to_equity"] = (
        (total_liabilities / total_equity) if total_equity > 0 else Decimal("0.00")
    )
    ratios["debt_ratio"] = (
        (total_liabilities / total_assets * 100)
        if total_assets > 0
        else Decimal("0.00")
    )

    context = {
        "title": "Financial Ratios",
        "description": "Key financial ratios and performance indicators.",
        "user": request.user,
        "ratios": ratios,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "total_equity": total_equity,
        "net_income": net_income,
    }
    return render(request, "dashboard/modules/financial_ratios.html", context)
