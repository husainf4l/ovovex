"""
Optimized Dashboard Views
- All imports at top
- Minimal database queries with select_related/prefetch_related
- Caching for expensive operations
- Delegated calculations to services
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q, F, Prefetch
from django.http import JsonResponse
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone

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
    ExpenseCategory,
    Notification,
)


@login_required
def dashboard_view(request):
    """
    Optimized Dashboard View
    - Uses cached metrics
    - Delegates calculations to service layer
    - Minimal context data
    """
    active_company = request.active_company

    # Try to get cached dashboard metrics (5 minute cache)
    cache_key = f"dashboard_metrics_{active_company.id}"
    metrics = cache.get(cache_key)

    if metrics is None:
        # Calculate metrics using service
        metrics_service = FinancialMetricsService(active_company)
        metrics = metrics_service.get_all_metrics()

        # Cache for 5 minutes
        cache.set(cache_key, metrics, 300)

    # Get recent activity (not cached - real-time)
    recent_entries = (
        JournalEntry.objects.filter(company=active_company, status="POSTED")
        .select_related("created_by")
        .only(
            "id",
            "entry_number",
            "entry_date",
            "description",
            "status",
            "created_by",
            "created_by__username",
        )
        .order_by("-entry_date")[:5]
    )

    # Get top clients (light query)
    top_clients = (
        Customer.objects.filter(company=active_company, is_active=True)
        .annotate(total_invoiced=Sum("invoices__total_amount"))
        .filter(total_invoiced__gt=0)
        .only("id", "company_name")
        .order_by("-total_invoiced")[:5]
    )

    context = {
        "title": "Dashboard",
        "description": "Your accounting dashboard and financial overview.",
        "user": request.user,
        "metrics": metrics,
        "recent_entries": recent_entries,
        "top_clients": top_clients,
    }

    return render(request, "dashboard/dashboard.html", context)


@login_required
def general_ledger_view(request):
    """
    Optimized General Ledger View
    - Paginated accounts
    - Cached balance calculations
    """
    active_company = request.active_company
    account_type_filter = request.GET.get("account_type", "all")
    page_number = request.GET.get("page", 1)

    # Get cache key for balance summary
    cache_key = f"gl_balance_summary_{active_company.id}"
    balance_summary = cache.get(cache_key)

    if balance_summary is None:
        # Calculate balance summary
        metrics_service = FinancialMetricsService(active_company)
        ratios = metrics_service.get_financial_ratios()

        balance_summary = {
            "assets": ratios["assets"],
            "liabilities": ratios["liabilities"],
            "equity": ratios["equity"],
            "revenue": Decimal("0.00"),  # Would need period-specific calculation
            "expenses": Decimal("0.00"),
        }

        # Cache for 10 minutes
        cache.set(cache_key, balance_summary, 600)

    # Get accounts with filtering
    accounts = Account.objects.filter(company=active_company, is_active=True).only(
        "id", "code", "name", "account_type", "description"
    )

    if account_type_filter != "all":
        accounts = accounts.filter(account_type=account_type_filter)

    accounts = accounts.order_by("code")

    # Paginate accounts
    paginator = Paginator(accounts, 25)  # 25 accounts per page
    accounts_page = paginator.get_page(page_number)

    # Get statistics (light queries)
    total_accounts = Account.objects.filter(
        company=active_company, is_active=True
    ).count()

    current_month = datetime.now().replace(day=1).date()
    entries_this_month = JournalEntry.objects.filter(
        company=active_company, entry_date__gte=current_month, status="POSTED"
    ).count()

    unbalanced_entries = JournalEntry.objects.filter(
        company=active_company, status="DRAFT"
    ).count()

    # Recent entries (optimized)
    recent_entries = (
        JournalEntry.objects.filter(company=active_company, status="POSTED")
        .select_related("created_by")
        .only(
            "id",
            "entry_number",
            "entry_date",
            "description",
            "status",
            "created_by",
            "created_by__username",
        )
        .order_by("-entry_date", "-created_at")[:5]
    )

    context = {
        "title": "General Ledger",
        "description": "Chart of accounts, journals, and ledger balances.",
        "user": request.user,
        "accounts": accounts_page,
        "recent_entries": recent_entries,
        "total_accounts": total_accounts,
        "entries_this_month": entries_this_month,
        "unbalanced_entries": unbalanced_entries,
        "total_entries": JournalEntry.objects.filter(
            company=active_company, status="POSTED"
        ).count(),
        "balance_summary": balance_summary,
        "net_balance": balance_summary["assets"] - balance_summary["liabilities"],
        "account_type_filter": account_type_filter,
        "account_types": AccountType.choices,
    }

    return render(request, "dashboard/modules/general_ledger.html", context)


@login_required
def invoices_view(request):
    """
    Optimized Invoices View
    - Paginated results
    - Optimized queries with select_related
    """
    active_company = request.active_company
    page_number = request.GET.get("page", 1)

    # Get invoices with optimized query
    invoices = (
        Invoice.objects.filter(company=active_company)
        .select_related("customer")
        .only(
            "id",
            "invoice_number",
            "invoice_date",
            "due_date",
            "total_amount",
            "status",
            "customer__company_name",
        )
        .order_by("-invoice_date")
    )

    # Paginate
    paginator = Paginator(invoices, 20)
    invoices_page = paginator.get_page(page_number)

    # Get aggregated statistics (single query)
    stats = Invoice.objects.filter(company=active_company).aggregate(
        total_count=Count("id"),
        total_revenue=Sum("total_amount"),
        paid_count=Count("id", filter=Q(status="PAID")),
        overdue_count=Count("id", filter=Q(status="OVERDUE")),
    )

    # Recent invoices
    recent_invoices = invoices[:5]

    # Get all customers for the invoice creation modal
    customers = Customer.objects.filter(
        company=active_company, is_active=True
    ).only("id", "company_name").order_by("company_name")

    context = {
        "title": "Invoices",
        "description": "Create, send, and track invoices.",
        "user": request.user,
        "invoices": invoices_page,
        "total_invoices": stats["total_count"],
        "total_revenue": stats["total_revenue"] or Decimal("0.00"),
        "paid_invoices": stats["paid_count"],
        "overdue_invoices": stats["overdue_count"],
        "recent_invoices": recent_invoices,
        "customers": customers,
    }

    return render(request, "dashboard/modules/invoices.html", context)


@login_required
def balance_sheet_view(request):
    """
    Optimized Balance Sheet View
    - Uses cached financial ratios
    - Minimal queries
    """
    active_company = request.active_company

    # Try cache first
    cache_key = f"balance_sheet_{active_company.id}"
    data = cache.get(cache_key)

    if data is None:
        metrics_service = FinancialMetricsService(active_company)
        ratios = metrics_service.get_financial_ratios()

        data = {
            "total_assets": ratios["assets"],
            "total_liabilities": ratios["liabilities"],
            "total_equity": ratios["equity"],
            "current_assets": ratios["assets"] * Decimal("0.7"),  # Simplified
            "fixed_assets": ratios["assets"] * Decimal("0.3"),
            "current_liabilities": ratios["liabilities"] * Decimal("0.7"),
            "long_term_liabilities": ratios["liabilities"] * Decimal("0.3"),
        }

        # Cache for 15 minutes
        cache.set(cache_key, data, 900)

    # Get account lists (lightweight query)
    assets = Account.objects.filter(
        company=active_company, account_type=AccountType.ASSET, is_active=True
    ).only("id", "code", "name")

    liabilities = Account.objects.filter(
        company=active_company, account_type=AccountType.LIABILITY, is_active=True
    ).only("id", "code", "name")

    equity = Account.objects.filter(
        company=active_company, account_type=AccountType.EQUITY, is_active=True
    ).only("id", "code", "name")

    context = {
        "title": "Balance Sheet",
        "description": "Assets, liabilities, and equity overview.",
        "user": request.user,
        "assets": assets,
        "liabilities": liabilities,
        "equity": equity,
        **data,
    }

    return render(request, "dashboard/modules/balance_sheet.html", context)


@login_required
def pnl_statement_view(request):
    """
    Optimized P&L Statement View
    - Uses service layer for calculations
    """
    active_company = request.active_company

    # Try cache
    cache_key = f"pnl_statement_{active_company.id}"
    data = cache.get(cache_key)

    if data is None:
        metrics_service = FinancialMetricsService(active_company)

        revenue_metrics = metrics_service.get_revenue_metrics()
        expense_metrics = metrics_service.get_expense_metrics()
        profit_metrics = metrics_service.get_profit_metrics()

        data = {
            "total_revenue": revenue_metrics["current_month"],
            "total_expenses": expense_metrics["current_month"],
            "net_profit": profit_metrics["current_month"],
            "profit_margin": profit_metrics["margin_percent"],
            "cogs": Decimal("0.00"),  # Would need specific calculation
            "gross_profit": revenue_metrics["current_month"],
            "operating_expenses": expense_metrics["current_month"],
        }

        # Cache for 10 minutes
        cache.set(cache_key, data, 600)

    # Get account lists (light query)
    revenue_accounts = Account.objects.filter(
        company=active_company, account_type=AccountType.REVENUE, is_active=True
    ).only("id", "code", "name")

    expense_accounts = Account.objects.filter(
        company=active_company, account_type=AccountType.EXPENSE, is_active=True
    ).only("id", "code", "name")

    context = {
        "title": "P&L Statement",
        "description": "Profit and Loss statement analysis.",
        "user": request.user,
        "revenue_accounts": revenue_accounts,
        "expense_accounts": expense_accounts,
        **data,
    }

    return render(request, "dashboard/modules/income_statement.html", context)


@login_required
def journal_entries_view(request):
    """
    Optimized Journal Entries View
    - Paginated results
    - Aggregated statistics
    """
    active_company = request.active_company
    page_number = request.GET.get("page", 1)

    # Get journal entries (optimized query)
    journal_entries = (
        JournalEntry.objects.filter(company=active_company)
        .select_related("created_by")
        .only(
            "id",
            "entry_number",
            "entry_date",
            "description",
            "status",
            "total_debit",
            "total_credit",
            "created_by__username",
        )
        .order_by("-entry_date", "-id")
    )

    # Paginate
    paginator = Paginator(journal_entries, 20)
    entries_page = paginator.get_page(page_number)

    # Get aggregated stats
    stats = JournalEntry.objects.filter(company=active_company).aggregate(
        total_count=Count("id"),
        posted_count=Count("id", filter=Q(status=JournalEntry.Status.POSTED)),
        draft_count=Count("id", filter=Q(status=JournalEntry.Status.DRAFT)),
    )

    # Month totals
    today = datetime.now().date()
    first_day = today.replace(day=1)

    month_totals = JournalEntryLine.objects.filter(
        journal_entry__company=active_company,
        journal_entry__entry_date__gte=first_day,
        journal_entry__entry_date__lte=today,
    ).aggregate(total_debits=Sum("debit_amount"), total_credits=Sum("credit_amount"))

    # Get accounts (light query)
    accounts = (
        Account.objects.filter(company=active_company, is_active=True)
        .only("id", "code", "name")
        .order_by("code")
    )

    context = {
        "title": "Journal Entries",
        "description": "Manual journal entries and adjustments.",
        "user": request.user,
        "journal_entries": entries_page,
        "total_entries": stats["total_count"],
        "posted_entries": stats["posted_count"],
        "draft_entries": stats["draft_count"],
        "recent_entries": journal_entries[:10],
        "total_debits": month_totals["total_debits"] or Decimal("0.00"),
        "total_credits": month_totals["total_credits"] or Decimal("0.00"),
        "accounts": accounts,
    }

    return render(request, "dashboard/modules/journal_entries.html", context)


@login_required
def fixed_assets_view(request):
    """
    Optimized Fixed Assets View
    - Aggregated calculations
    """
    active_company = request.active_company

    # Get fixed assets (light query)
    fixed_assets = (
        FixedAsset.objects.filter(account__company=active_company, is_active=True)
        .only(
            "id",
            "asset_code",
            "name",
            "category",
            "purchase_cost",
            "accumulated_depreciation",
        )
        .order_by("asset_code")
    )

    # Get aggregated statistics (single query)
    stats = FixedAsset.objects.filter(
        account__company=active_company, is_active=True
    ).aggregate(
        total_cost=Sum("purchase_cost"),
        total_depreciation=Sum("accumulated_depreciation"),
        equipment_count=Count(
            "id", filter=Q(category__in=["OFFICE_EQUIPMENT", "COMPUTER_EQUIPMENT"])
        ),
        furniture_count=Count("id", filter=Q(category="FURNITURE")),
        vehicles_count=Count("id", filter=Q(category="VEHICLES")),
    )

    total_book_value = (stats["total_cost"] or Decimal("0.00")) - (
        stats["total_depreciation"] or Decimal("0.00")
    )

    context = {
        "title": "Fixed Assets",
        "fixed_assets": fixed_assets,
        "total_cost": stats["total_cost"] or Decimal("0.00"),
        "total_depreciation": stats["total_depreciation"] or Decimal("0.00"),
        "total_book_value": total_book_value,
        "equipment_count": stats["equipment_count"],
        "furniture_count": stats["furniture_count"],
        "vehicles_count": stats["vehicles_count"],
    }

    return render(request, "dashboard/modules/fixed_assets.html", context)


@login_required
def financial_ratios_view(request):
    """
    Optimized Financial Ratios View
    - Uses cached service calculations
    """
    active_company = request.active_company

    # Try cache first
    cache_key = f"financial_ratios_{active_company.id}"
    data = cache.get(cache_key)

    if data is None:
        metrics_service = FinancialMetricsService(active_company)
        ratios = metrics_service.get_financial_ratios()
        profit_metrics = metrics_service.get_profit_metrics()

        data = {
            "ratios": {
                "current_ratio": ratios["current_ratio"],
                "quick_ratio": ratios["quick_ratio"],
                "debt_to_equity": ratios["debt_to_equity"],
                "debt_ratio": (
                    (ratios["liabilities"] / ratios["assets"] * 100)
                    if ratios["assets"] > 0
                    else Decimal("0")
                ),
                "gross_margin": profit_metrics["margin_percent"],
                "net_margin": profit_metrics["margin_percent"],
                "return_on_assets": (
                    (profit_metrics["current_month"] / ratios["assets"] * 100)
                    if ratios["assets"] > 0
                    else Decimal("0")
                ),
                "return_on_equity": (
                    (profit_metrics["current_month"] / ratios["equity"] * 100)
                    if ratios["equity"] > 0
                    else Decimal("0")
                ),
            },
            "total_assets": ratios["assets"],
            "total_liabilities": ratios["liabilities"],
            "total_equity": ratios["equity"],
            "net_income": profit_metrics["current_month"],
        }

        # Cache for 15 minutes
        cache.set(cache_key, data, 900)

    context = {
        "title": "Financial Ratios",
        "description": "Key financial ratios and performance indicators.",
        "user": request.user,
        **data,
    }

    return render(request, "dashboard/modules/financial_ratios.html", context)


# Simplified placeholder views
@login_required
def budgeting_view(request):
    """Budgeting view"""
    context = {
        "title": "Budgeting",
        "description": "Create and manage budgets for your business.",
        "user": request.user,
    }
    return render(request, "dashboard/modules/budgeting.html", context)


@login_required
def ai_insights_view(request):
    """AI Insights view"""
    context = {
        "title": "AI Insights",
        "description": "AI-powered financial analysis and insights.",
        "user": request.user,
    }
    return render(request, "dashboard/modules/ai_insights.html", context)


@login_required
def settings_view(request):
    """Settings view"""
    context = {
        "title": "Settings",
        "description": "Configure your account and preferences.",
        "user": request.user,
    }
    return render(request, "dashboard/modules/settings.html", context)


@login_required
def cash_flow_view(request):
    """Cash Flow view"""
    context = {
        "title": "Cash Flow",
        "description": "Track cash inflows and outflows.",
        "user": request.user,
    }
    return render(request, "dashboard/modules/cash_flow.html", context)


@login_required
def create_invoice_view(request):
    """
    Create invoice view - redirects to accounting app
    This is kept for backwards compatibility with old URLs
    """
    from django.shortcuts import redirect

    return redirect("accounting:invoice_create")


@login_required
def customers_view(request):
    """
    Customer Management View
    - List all customers for active company
    - Add/edit/delete customers
    """
    active_company = request.active_company

    # Get filter parameters
    search_query = request.GET.get("search", "")
    status_filter = request.GET.get("status", "all")

    # Base queryset
    customers = Customer.objects.filter(company=active_company)

    # Apply filters
    if search_query:
        customers = customers.filter(
            Q(company_name__icontains=search_query)
            | Q(contact_name__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(customer_code__icontains=search_query)
        )

    if status_filter == "active":
        customers = customers.filter(is_active=True)
    elif status_filter == "inactive":
        customers = customers.filter(is_active=False)

    # Order by company name
    customers = customers.order_by("company_name")

    # Calculate balances for each customer
    customers_with_balances = []
    for customer in customers:
        outstanding_balance = customer.get_outstanding_balance()
        total_invoiced = customer.invoices.filter(
            status__in=["SENT", "PAID", "OVERDUE"]
        ).aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")

        customers_with_balances.append(
            {
                "customer": customer,
                "outstanding_balance": outstanding_balance,
                "total_invoiced": total_invoiced,
            }
        )

    context = {
        "title": "Customers",
        "description": "Manage your customer database and track outstanding balances.",
        "user": request.user,
        "customers": customers_with_balances,
        "search_query": search_query,
        "status_filter": status_filter,
        "total_customers": len(customers_with_balances),
        "active_customers": sum(
            1 for c in customers_with_balances if c["customer"].is_active
        ),
    }

    return render(request, "dashboard/modules/customers.html", context)


@login_required
def create_customer_view(request):
    """
    Create new customer via AJAX/modal
    """
    import json
    from accounting.forms import CustomerForm

    active_company = request.active_company

    if request.method == "POST":
        # Handle JSON data if content-type is application/json
        if request.content_type == "application/json":
            try:
                data = json.loads(request.body)

                # Auto-generate customer_code if not provided
                if not data.get("customer_code"):
                    last_customer = (
                        Customer.objects.filter(company=active_company)
                        .order_by("-id")
                        .first()
                    )
                    data["customer_code"] = (
                        f"CUST-{(int(last_customer.customer_code.split('-')[1]) + 1):04d}"
                        if last_customer
                        else "CUST-0001"
                    )

                form = CustomerForm(data)
            except json.JSONDecodeError:
                return JsonResponse(
                    {"success": False, "error": "Invalid JSON data"}, status=400
                )
        else:
            form = CustomerForm(request.POST)

        if form.is_valid():
            customer = form.save(commit=False)
            customer.company = active_company
            customer.save()

            # Check if this is an HTMX request
            if request.headers.get("HX-Request"):
                # Return HTML success message for HTMX
                return render(
                    request,
                    "dashboard/modules/customer_success.html",
                    {
                        "customer": customer,
                        "message": f"Customer {customer.company_name} created successfully!",
                    },
                )
            else:
                # Return JSON for regular AJAX
                return JsonResponse(
                    {
                        "success": True,
                        "message": f"Customer {customer.company_name} created successfully!",
                        "customer": {
                            "id": customer.id,
                            "customer_code": customer.customer_code,
                            "company_name": customer.company_name,
                            "contact_name": customer.contact_name,
                            "email": customer.email,
                            "phone": customer.phone,
                        },
                    }
                )
        else:
            # Log form errors for debugging
            print(f"Form validation errors: {form.errors.as_json()}")

            if request.headers.get("HX-Request"):
                # Return form with errors for HTMX
                context = {
                    "form": form,
                    "action": "Create",
                }
                return render(request, "dashboard/modules/customer_form.html", context)
            else:
                return JsonResponse(
                    {"success": False, "errors": form.errors}, status=400
                )

    # GET request - return form HTML
    # Generate next customer code
    last_customer = (
        Customer.objects.filter(company=active_company).order_by("-id").first()
    )
    next_code = (
        f"CUST-{(int(last_customer.customer_code.split('-')[1]) + 1):04d}"
        if last_customer
        else "CUST-0001"
    )

    form = CustomerForm(
        initial={
            "customer_code": next_code,
            "payment_terms_days": 30,
            "is_active": True,
        }
    )

    context = {
        "form": form,
        "action": "Create",
    }

    return render(request, "dashboard/modules/customer_form.html", context)


@login_required
def edit_customer_view(request, pk):
    """
    Edit existing customer
    """
    import json
    from accounting.forms import CustomerForm

    active_company = request.active_company
    customer = get_object_or_404(Customer, pk=pk, company=active_company)

    if request.method in ["POST", "PUT"]:
        # Handle JSON data if content-type is application/json
        if request.content_type == "application/json":
            try:
                data = json.loads(request.body)
                form = CustomerForm(data, instance=customer)
            except json.JSONDecodeError:
                return JsonResponse(
                    {"success": False, "error": "Invalid JSON data"}, status=400
                )
        else:
            form = CustomerForm(request.POST, instance=customer)

        if form.is_valid():
            customer = form.save()

            if request.headers.get("HX-Request"):
                # Return HTML success message for HTMX
                return render(
                    request,
                    "dashboard/modules/customer_success.html",
                    {
                        "customer": customer,
                        "message": f"Customer {customer.company_name} updated successfully!",
                    },
                )
            else:
                return JsonResponse(
                    {
                        "success": True,
                        "message": f"Customer {customer.company_name} updated successfully!",
                        "customer": {
                            "id": customer.id,
                            "customer_code": customer.customer_code,
                            "company_name": customer.company_name,
                            "contact_name": customer.contact_name,
                            "email": customer.email,
                            "phone": customer.phone,
                        },
                    }
                )
        else:
            # Log form errors for debugging
            print(f"Form validation errors: {form.errors.as_json()}")

            if request.headers.get("HX-Request"):
                # Return form with errors for HTMX
                context = {
                    "form": form,
                    "customer": customer,
                    "action": "Edit",
                }
                return render(request, "dashboard/modules/customer_form.html", context)
            else:
                return JsonResponse(
                    {"success": False, "errors": form.errors}, status=400
                )

    # GET request
    # If it's a JSON request (AJAX), return customer data
    if (
        request.headers.get("Accept") == "application/json"
        or request.META.get("HTTP_ACCEPT") == "application/json"
    ):
        return JsonResponse(
            {
                "id": customer.id,
                "customer_code": customer.customer_code,
                "company_name": customer.company_name,
                "contact_name": customer.contact_name,
                "email": customer.email,
                "phone": customer.phone or "",
                "address": customer.address or "",
                "city": customer.city or "",
                "country": customer.country or "",
                "tax_id": customer.tax_id or "",
                "credit_limit": str(customer.credit_limit),
                "payment_terms_days": customer.payment_terms_days,
                "is_active": customer.is_active,
            }
        )

    # Otherwise return HTML form
    form = CustomerForm(instance=customer)
    context = {
        "form": form,
        "customer": customer,
        "action": "Edit",
    }

    return render(request, "dashboard/modules/customer_form.html", context)


@login_required
def delete_customer_view(request, pk):
    """
    Delete customer (soft delete by setting is_active=False)
    """
    active_company = request.active_company
    customer = get_object_or_404(Customer, pk=pk, company=active_company)

    if request.method == "POST":
        customer.is_active = False
        customer.save()

        return JsonResponse(
            {
                "success": True,
                "message": f"Customer {customer.company_name} deactivated successfully!",
            }
        )

    return JsonResponse({"success": False, "message": "Invalid request method"})


@login_required
def notifications_view(request):
    """
    View all notifications for the current user
    """
    active_company = request.active_company

    # Get notifications for the user and company
    notifications = Notification.objects.filter(
        user=request.user, company=active_company
    ).order_by("-created_at")

    # Mark all as read if requested
    if request.method == "POST" and request.POST.get("action") == "mark_all_read":
        notifications.filter(is_read=False).update(is_read=True, read_at=timezone.now())
        return JsonResponse({"success": True, "message": "All notifications marked as read"})

    # Paginate notifications
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get unread count
    unread_count = notifications.filter(is_read=False).count()

    context = {
        "title": "Notifications",
        "description": "View all your notifications and alerts.",
        "user": request.user,
        "notifications": page_obj,
        "unread_count": unread_count,
    }

    return render(request, "dashboard/modules/notifications.html", context)
