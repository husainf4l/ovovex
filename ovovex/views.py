from django.shortcuts import render, redirect


from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from accounting.models import JournalEntryLine
from django.db import models

# Import all missing view stubs
# from .missing_views import *


def home(request):
    """
    Home page view
    """
    context = {
        "title": "Welcome to Ovovex",
        "description": "Your next-generation platform for innovative solutions.",
    }
    return render(request, "home.html", context)


def health_check(request):
    """
    Simple health check endpoint
    """
    return HttpResponse("OK", content_type="text/plain")


def login_redirect(request):
    """
    Redirect /login/ to the correct login URL with query parameters preserved
    """
    from django.urls import reverse
    login_url = reverse("accounts:login")
    query_string = request.META.get('QUERY_STRING', '')
    if query_string:
        login_url += '?' + query_string
    return redirect(login_url)


def login_view(request):
    """
    Login page view
    """
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(
                    request, f"Welcome back, {user.first_name or user.username}!"
                )
                next_url = request.GET.get("next", "home")
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please fill in all fields.")

    context = {
        "title": "Login to Ovovex",
        "description": "Access your accounting dashboard and manage your finances.",
    }
    return render(request, "auth/login.html", context)


def signup_view(request):
    """
    Signup page view
    """
    # Allow viewing signup pages even when authenticated (they might want to see the page)
    # Only redirect on POST (actual signup attempt)
    if request.user.is_authenticated and request.method == "POST":
        messages.info(request, "You are already logged in.")
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        # Validation
        if not all(
            [username, email, first_name, last_name, password, password_confirm]
        ):
            messages.error(request, "Please fill in all fields.")
        elif password != password_confirm:
            messages.error(request, "Passwords do not match.")
        elif len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        else:
            # Create user
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                )
                # Log the user in after account creation
                login(request, user)
                messages.success(
                    request,
                    f"Welcome to Ovovex, {user.first_name or user.username}! Your account has been created successfully.",
                )
                return redirect("dashboard")  # Redirect to dashboard instead of login
            except Exception as e:
                messages.error(
                    request, "An error occurred while creating your account."
                )

    context = {
        "title": "Join Ovovex",
        "description": "Create your account and start managing your finances today.",
    }
    return render(request, "auth/signup.html", context)


def logout_view(request):
    """
    Logout view
    """
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("home")


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


# Core Accounting Views


# ============================================================================
# MISSING VIEWS - STUBS FOR URL COMPATIBILITY
# ============================================================================


@login_required
def create_journal_entry_view(request):
    """
    Create journal entry view
    """
    from accounting.models import JournalEntry, JournalEntryLine, Account
    from django.http import JsonResponse
    from decimal import Decimal
    import json

    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Create journal entry
            journal_entry = JournalEntry.objects.create(
                entry_number=data["entry_number"],
                entry_date=data["entry_date"],
                description=data["description"],
                reference=data.get("reference", ""),
                created_by=request.user,
            )

            # Add line items
            total_debit = Decimal("0.00")
            total_credit = Decimal("0.00")

            for line_data in data["lines"]:
                debit_amount = Decimal(str(line_data.get("debit_amount", "0.00")))
                credit_amount = Decimal(str(line_data.get("credit_amount", "0.00")))

                account = Account.objects.get(id=line_data["account_id"])

                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=account,
                    description=line_data.get("description", ""),
                    debit_amount=debit_amount,
                    credit_amount=credit_amount,
                    line_number=line_data["line_number"],
                )

                total_debit += debit_amount
                total_credit += credit_amount

            # Update totals
            journal_entry.total_debit = total_debit
            journal_entry.total_credit = total_credit
            journal_entry.save()

            # Check if balanced
            if total_debit != total_credit:
                return JsonResponse(
                    {
                        "success": False,
                        "error": f"Journal entry is not balanced. Debit: ${total_debit}, Credit: ${total_credit}",
                    }
                )

            return JsonResponse(
                {
                    "success": True,
                    "message": "Journal entry created successfully",
                    "entry_id": journal_entry.id,
                    "entry_number": journal_entry.entry_number,
                }
            )

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    # GET request - return form data
    accounts = Account.objects.filter(is_active=True).order_by("code")
    context = {
        "title": "Create Journal Entry",
        "accounts": accounts,
    }
    return render(request, "modules/create_journal_entry.html", context)


@login_required
def post_journal_entries_view(request):
    """
    Post journal entries view
    """
    # Stub implementation
    return JsonResponse({"success": False, "message": "Not implemented yet"})


@login_required
def reverse_journal_entry_view(request):
    """
    Reverse journal entry view
    """
    # Stub implementation
    return JsonResponse({"success": False, "message": "Not implemented yet"})


@login_required
def export_journal_entries_view(request):
    """
    Export journal entries view
    """
    # Stub implementation
    return JsonResponse({"success": False, "message": "Not implemented yet"})


@login_required
def journal_report_view(request):
    """
    Journal report view
    """
    # Stub implementation
    context = {
        "title": "Journal Report",
    }
    return render(request, "modules/journal_report.html", context)


@login_required
def trial_balance_view(request):
    """
    Trial balance view
    """
    # Stub implementation
    context = {
        "title": "Trial Balance",
    }
    return render(request, "modules/trial_balance.html", context)


@login_required
def reconciliation_view(request):
    """
    Reconciliation view
    """
    # Stub implementation
    context = {
        "title": "Reconciliation",
    }
    return render(request, "modules/reconciliation.html", context)


@login_required
def cash_flow_view(request):
    """
    Cash flow view
    """
    # Stub implementation
    context = {
        "title": "Cash Flow",
    }
    return render(request, "modules/cash_flow.html", context)


@login_required
def create_budget_view(request):
    """
    Create budget view
    """
    # Stub implementation
    return JsonResponse({"success": False, "message": "Not implemented yet"})


@login_required
def copy_budget_view(request):
    """
    Copy budget view
    """
    # Stub implementation
    return JsonResponse({"success": False, "message": "Not implemented yet"})


@login_required
def export_budget_view(request):
    """
    Export budget view
    """
    # Stub implementation
    return JsonResponse({"success": False, "message": "Not implemented yet"})


@login_required
def add_fixed_asset_view(request):
    """
    Add fixed asset view
    """
    # Stub implementation
    return JsonResponse({"success": False, "message": "Not implemented yet"})


@login_required
def export_fixed_assets_view(request):
    """
    Export fixed assets view
    """
    # Stub implementation
    return JsonResponse({"success": False, "message": "Not implemented yet"})


@login_required
def bank_reconciliation_view(request):
    """
    Bank reconciliation view
    """
    from accounting.models import BankReconciliation, BankStatement, Account
    from django.db.models import Sum
    from decimal import Decimal

    # Get bank accounts (assuming accounts with type ASSET and code starting with 1)
    bank_accounts = Account.objects.filter(
        account_type="ASSET", code__startswith="1", is_active=True
    )

    # Get latest reconciliation for each account
    latest_reconciliations = {}
    for account in bank_accounts:
        latest_rec = (
            BankReconciliation.objects.filter(account=account)
            .order_by("-reconciliation_date")
            .first()
        )
        if latest_rec:
            latest_reconciliations[account.id] = latest_rec

    # Get unreconciled statements
    unreconciled_statements = (
        BankStatement.objects.filter(is_reconciled=False)
        .select_related("account")
        .order_by("-statement_date")[:20]
    )

    # Calculate summary statistics
    total_unreconciled = unreconciled_statements.count()
    total_unreconciled_amount = sum(stmt.amount for stmt in unreconciled_statements)

    context = {
        "title": "Bank Reconciliation",
        "description": "Reconcile bank statements with accounting records.",
        "user": request.user,
        "bank_accounts": bank_accounts,
        "latest_reconciliations": latest_reconciliations,
        "unreconciled_statements": unreconciled_statements,
        "total_unreconciled": total_unreconciled,
        "total_unreconciled_amount": total_unreconciled_amount,
    }
    return render(request, "modules/bank_reconciliation.html", context)


@login_required
def add_reconciliation_adjustment_view(request):
    """
    Add reconciliation adjustment view
    """
    # Stub implementation
    return JsonResponse({"success": False, "message": "Not implemented yet"})


@login_required
def reconcile_statement_view(request, statement_id):
    """
    Reconcile statement view
    """
    # Stub implementation
    return JsonResponse({"success": False, "message": "Not implemented yet"})


@login_required
def calculate_tax_depreciation_view(request):
    """
    Calculate tax depreciation view
    """
    from accounting.models import FixedAsset
    from decimal import Decimal
    from django.http import JsonResponse

    if request.method == "POST":
        asset_id = request.POST.get("asset_id")
        year = int(request.POST.get("year", 2025))

        try:
            asset = FixedAsset.objects.get(id=asset_id, is_active=True)

            # Generate depreciation schedule
            schedule = []
            tax_basis = asset.purchase_cost
            remaining_basis = tax_basis
            accumulated_depreciation = Decimal("0.00")

            # Calculate depreciation for each year
            for i in range(asset.useful_life_years):
                current_year = year + i

                if asset.depreciation_method == "STRAIGHT_LINE":
                    annual_depreciation = (
                        tax_basis - asset.salvage_value
                    ) / asset.useful_life_years
                else:
                    # Simplified declining balance (20%)
                    annual_depreciation = remaining_basis * Decimal("0.2")
                    if annual_depreciation > remaining_basis:
                        annual_depreciation = remaining_basis

                accumulated_depreciation += annual_depreciation
                remaining_basis -= annual_depreciation

                schedule.append(
                    {
                        "year": current_year,
                        "rate": float(annual_depreciation / tax_basis),
                        "annual_depreciation": str(annual_depreciation),
                        "accumulated_depreciation": str(accumulated_depreciation),
                    }
                )

                # Stop if fully depreciated
                if remaining_basis <= 0:
                    break

            return JsonResponse(
                {
                    "success": True,
                    "schedule": schedule,
                    "asset_info": {
                        "asset_code": asset.asset_code,
                        "name": asset.name,
                        "tax_basis": str(tax_basis),
                        "depreciation_method": asset.depreciation_method,
                    },
                }
            )

        except FixedAsset.DoesNotExist:
            return JsonResponse({"success": False, "error": "Asset not found"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})


@login_required
def create_journal_entry_view(request):
    """
    Create journal entry view
    """
    from accounting.models import JournalEntry, JournalEntryLine, Account
    from django.http import JsonResponse
    from decimal import Decimal
    import json

    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Create journal entry
            journal_entry = JournalEntry.objects.create(
                entry_number=data["entry_number"],
                entry_date=data["entry_date"],
                description=data["description"],
                reference=data.get("reference", ""),
                created_by=request.user,
            )

            # Add line items
            total_debit = Decimal("0.00")
            total_credit = Decimal("0.00")

            for line_data in data["lines"]:
                debit_amount = Decimal(str(line_data.get("debit_amount", "0.00")))
                credit_amount = Decimal(str(line_data.get("credit_amount", "0.00")))

                account = Account.objects.get(id=line_data["account_id"])

                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=account,
                    description=line_data.get("description", ""),
                    debit_amount=debit_amount,
                    credit_amount=credit_amount,
                    line_number=line_data["line_number"],
                )

                total_debit += debit_amount
                total_credit += credit_amount

            # Update totals
            journal_entry.total_debit = total_debit
            journal_entry.total_credit = total_credit
            journal_entry.save()

            # Check if balanced
            if total_debit != total_credit:
                return JsonResponse(
                    {
                        "success": False,
                        "error": f"Journal entry is not balanced. Debit: ${total_debit}, Credit: ${total_credit}",
                    }
                )

            return JsonResponse(
                {
                    "success": True,
                    "message": "Journal entry created successfully",
                    "entry_id": journal_entry.id,
                    "entry_number": journal_entry.entry_number,
                }
            )

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    # GET request - return form data
    accounts = Account.objects.filter(is_active=True).order_by("code")
    context = {
        "title": "Create Journal Entry",
        "accounts": accounts,
    }
    return render(request, "dashboard/modules/create_journal_entry.html", context)


@login_required
def invoices_view(request):
    """
    Invoices view
    """
    from accounting.models import Invoice, Customer
    from django.db.models import Sum

    # Get filter parameters
    status_filter = request.GET.get("status", "all")
    customer_filter = request.GET.get("customer", "all")

    # Get invoices
    invoices = Invoice.objects.select_related("customer").order_by("-invoice_date")

    if status_filter != "all":
        invoices = invoices.filter(status=status_filter)
    if customer_filter != "all":
        invoices = invoices.filter(customer_id=customer_filter)

    # Calculate summary statistics
    total_invoices = invoices.count()
    total_amount = invoices.aggregate(Sum("total_amount"))["total_amount__sum"] or 0
    paid_invoices = invoices.filter(status="PAID").count()
    overdue_invoices = invoices.filter(status="OVERDUE").count()

    # Get customers for filter dropdown
    customers = Customer.objects.filter(is_active=True).order_by("name")

    context = {
        "title": "Invoices",
        "description": "Manage your customer invoices and billing.",
        "user": request.user,
        "invoices": invoices[:50],  # Limit for performance
        "total_invoices": total_invoices,
        "total_amount": total_amount,
        "paid_invoices": paid_invoices,
        "overdue_invoices": overdue_invoices,
        "customers": customers,
    }
    return render(request, "dashboard/modules/invoices.html", context)


@login_required
def balance_sheet_view(request):
    """
    Balance Sheet view
    """
    from accounting.models import Account, AccountType
    from decimal import Decimal

    # Get all accounts
    assets = Account.objects.filter(account_type=AccountType.ASSET, is_active=True)
    liabilities = Account.objects.filter(
        account_type=AccountType.LIABILITY, is_active=True
    )
    equity = Account.objects.filter(account_type=AccountType.EQUITY, is_active=True)

    # Calculate totals
    total_assets = sum(acc.get_balance() for acc in assets)
    total_liabilities = sum(acc.get_balance() for acc in liabilities)
    total_equity = sum(acc.get_balance() for acc in equity)

    context = {
        "title": "Balance Sheet",
        "description": "Financial position statement showing assets, liabilities, and equity.",
        "user": request.user,
        "assets": assets,
        "liabilities": liabilities,
        "equity": equity,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "total_equity": total_equity,
    }
    return render(request, "dashboard/modules/balance_sheet.html", context)


@login_required
def income_statement_view(request):
    """
    Income Statement view
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
    net_income = total_revenue - total_expenses

    context = {
        "title": "Income Statement",
        "description": "Profit and loss statement showing revenue, expenses, and net income.",
        "user": request.user,
        "revenue_accounts": revenue_accounts,
        "expense_accounts": expense_accounts,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "net_income": net_income,
    }
    return render(request, "dashboard/modules/income_statement.html", context)


@login_required
def journal_entries_view(request):
    """
    Journal Entries view
    """
    from accounting.models import JournalEntry
    from django.db.models import Q

    # Get filter parameters
    status_filter = request.GET.get("status", "all")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    # Get journal entries
    journal_entries = JournalEntry.objects.select_related().order_by("-entry_date")

    if status_filter != "all":
        journal_entries = journal_entries.filter(status=status_filter)
    if date_from:
        journal_entries = journal_entries.filter(entry_date__gte=date_from)
    if date_to:
        journal_entries = journal_entries.filter(entry_date__lte=date_to)

    # Calculate summary statistics
    total_entries = journal_entries.count()
    posted_entries = journal_entries.filter(status="POSTED").count()
    draft_entries = journal_entries.filter(status="DRAFT").count()

    context = {
        "title": "Journal Entries",
        "description": "View and manage all journal entries in your accounting system.",
        "user": request.user,
        "journal_entries": journal_entries[:50],  # Limit for performance
        "total_entries": total_entries,
        "posted_entries": posted_entries,
        "draft_entries": draft_entries,
    }
    return render(request, "dashboard/modules/journal_entries.html", context)


@login_required
def budgeting_view(request):
    """
    Budgeting view
    """
    context = {
        "title": "Budgeting",
        "description": "Create and manage budgets for financial planning.",
        "user": request.user,
    }
    return render(request, "dashboard/modules/budgeting.html", context)


@login_required
def fixed_assets_view(request):
    """
    Fixed Assets view
    """
    from accounting.models import FixedAsset

    # Get all fixed assets
    fixed_assets = FixedAsset.objects.filter(is_active=True).order_by("asset_code")

    # Calculate summary statistics
    total_assets = fixed_assets.count()
    total_value = sum(asset.purchase_cost for asset in fixed_assets)
    depreciated_value = sum(asset.accumulated_depreciation for asset in fixed_assets)
    net_value = total_value - depreciated_value

    context = {
        "title": "Fixed Assets",
        "description": "Manage your company's fixed assets and depreciation.",
        "user": request.user,
        "fixed_assets": fixed_assets,
        "total_assets": total_assets,
        "total_value": total_value,
        "depreciated_value": depreciated_value,
        "net_value": net_value,
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
        "description": "Configure your accounting system settings.",
        "user": request.user,
    }
    return render(request, "dashboard/modules/settings.html", context)


@login_required
def post_journal_entries_view(request):
    """
    Post journal entries view
    """
    # Stub implementation
    return JsonResponse({"success": False, "message": "Not implemented yet"})


@login_required
def reverse_journal_entry_view(request):
    """
    Reverse journal entry view
    """
    # Stub implementation
    return JsonResponse({"success": False, "message": "Not implemented yet"})


@login_required
def export_journal_entries_view(request):
    """
    Export journal entries view
    """
    # Stub implementation
    return JsonResponse({"success": False, "message": "Not implemented yet"})


@login_required
def journal_report_view(request):
    """
    Journal report view
    """
    # Stub implementation
    context = {
        "title": "Journal Report",
    }
    return render(request, "dashboard/modules/journal_report.html", context)


@login_required
def trial_balance_view(request):
    """
    Trial balance view
    """
    # Stub implementation
    context = {
        "title": "Trial Balance",
    }
    return render(request, "dashboard/modules/trial_balance.html", context)


@login_required
def reconciliation_view(request):
    """
    Reconciliation view
    """
    # Stub implementation
    context = {
        "title": "Reconciliation",
    }
    return render(request, "dashboard/modules/reconciliation.html", context)


@login_required
def cash_flow_view(request):
    """
    Cash flow view
    """
    # Stub implementation
    context = {
        "title": "Cash Flow",
    }
    return render(request, "dashboard/modules/cash_flow.html", context)


@login_required
def create_budget_view(request):
    """
    Create budget view
    """
    # Stub implementation
    return JsonResponse({"success": False, "message": "Not implemented yet"})


@login_required
def copy_budget_view(request):
    """
    Copy budget view
    """
    # Stub implementation
    return JsonResponse({"success": False, "message": "Not implemented yet"})


@login_required
def export_budget_view(request):
    """
    Export budget view
    """
    # Stub implementation
    return JsonResponse({"success": False, "message": "Not implemented yet"})


@login_required
def add_fixed_asset_view(request):
    """
    Add fixed asset view
    """
    # Stub implementation
    return JsonResponse({"success": False, "message": "Not implemented yet"})


@login_required
def export_fixed_assets_view(request):
    """
    Export fixed assets view
    """
    # Stub implementation
    return JsonResponse({"success": False, "message": "Not implemented yet"})


@login_required
def bank_reconciliation_view(request):
    """
    Bank reconciliation view
    """
    from accounting.models import BankReconciliation, BankStatement, Account
    from django.db.models import Sum
    from decimal import Decimal

    # Get bank accounts (assuming accounts with type ASSET and code starting with 1)
    bank_accounts = Account.objects.filter(
        account_type="ASSET", code__startswith="1", is_active=True
    )

    # Get latest reconciliation for each account
    latest_reconciliations = {}
    for account in bank_accounts:
        latest_rec = (
            BankReconciliation.objects.filter(account=account)
            .order_by("-reconciliation_date")
            .first()
        )
        if latest_rec:
            latest_reconciliations[account.id] = latest_rec

    # Get unreconciled statements
    unreconciled_statements = (
        BankStatement.objects.filter(is_reconciled=False)
        .select_related("account")
        .order_by("-statement_date")[:20]
    )

    # Calculate summary statistics
    total_unreconciled = unreconciled_statements.count()
    total_unreconciled_amount = sum(stmt.amount for stmt in unreconciled_statements)

    context = {
        "title": "Bank Reconciliation",
        "description": "Reconcile bank statements with accounting records.",
        "user": request.user,
        "bank_accounts": bank_accounts,
        "latest_reconciliations": latest_reconciliations,
        "unreconciled_statements": unreconciled_statements,
        "total_unreconciled": total_unreconciled,
        "total_unreconciled_amount": total_unreconciled_amount,
    }
    return render(request, "dashboard/modules/bank_reconciliation.html", context)


@login_required
def add_reconciliation_adjustment_view(request):
    """
    Add reconciliation adjustment view
    """
    # Stub implementation
    return JsonResponse({"success": False, "message": "Not implemented yet"})


@login_required
def reconcile_statement_view(request, statement_id):
    """
    Reconcile statement view
    """
    # Stub implementation
    return JsonResponse({"success": False, "message": "Not implemented yet"})


@login_required
def calculate_tax_depreciation_view(request):
    """
    Calculate tax depreciation view
    """
    from accounting.models import FixedAsset
    from decimal import Decimal
    from django.http import JsonResponse

    if request.method == "POST":
        asset_id = request.POST.get("asset_id")
        year = int(request.POST.get("year", 2025))

        try:
            asset = FixedAsset.objects.get(id=asset_id, is_active=True)

            # Generate depreciation schedule
            schedule = []
            tax_basis = asset.purchase_cost
            remaining_basis = tax_basis
            accumulated_depreciation = Decimal("0.00")

            # Calculate depreciation for each year
            for i in range(asset.useful_life_years):
                current_year = year + i

                if asset.depreciation_method == "STRAIGHT_LINE":
                    annual_depreciation = (
                        tax_basis - asset.salvage_value
                    ) / asset.useful_life_years
                else:
                    # Simplified declining balance (20%)
                    annual_depreciation = remaining_basis * Decimal("0.2")
                    if annual_depreciation > remaining_basis:
                        annual_depreciation = remaining_basis

                accumulated_depreciation += annual_depreciation
                remaining_basis -= annual_depreciation

                schedule.append(
                    {
                        "year": current_year,
                        "rate": float(annual_depreciation / tax_basis),
                        "annual_depreciation": str(annual_depreciation),
                        "accumulated_depreciation": str(accumulated_depreciation),
                    }
                )

                # Stop if fully depreciated
                if remaining_basis <= 0:
                    break

            return JsonResponse(
                {
                    "success": True,
                    "schedule": schedule,
                    "asset_info": {
                        "asset_code": asset.asset_code,
                        "name": asset.name,
                        "tax_basis": str(tax_basis),
                        "depreciation_method": asset.depreciation_method,
                    },
                }
            )

        except FixedAsset.DoesNotExist:
            return JsonResponse({"success": False, "error": "Asset not found"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})


@login_required
def generate_tax_report_view(request):
    """
    Generate tax report view
    """
    from accounting.models import FixedAsset
    from decimal import Decimal
    from django.http import JsonResponse

    if request.method == "POST":
        report_type = request.POST.get("report_type")
        year = int(request.POST.get("year", 2025))

        try:
            fixed_assets = FixedAsset.objects.filter(is_active=True)

            if report_type == "form_4562":
                # Form 4562 - Depreciation and Amortization
                total_basis = Decimal("0.00")
                total_depreciation = Decimal("0.00")
                section_179_total = Decimal("0.00")

                for asset in fixed_assets:
                    total_basis += asset.purchase_cost

                    # Calculate current year depreciation
                    if asset.depreciation_method == "STRAIGHT_LINE":
                        annual_depreciation = (
                            asset.purchase_cost - asset.salvage_value
                        ) / asset.useful_life_years
                    else:
                        annual_depreciation = asset.purchase_cost * Decimal("0.2")

                    total_depreciation += annual_depreciation

                    # Section 179 deduction (simplified - assume eligible assets get deduction)
                    if asset.purchase_cost <= Decimal("1000000"):  # Section 179 limit
                        section_179_total += min(
                            asset.purchase_cost, Decimal("1000000")
                        )

                return JsonResponse(
                    {
                        "success": True,
                        "report_data": {
                            "form_4562": {
                                "total_basis": str(total_basis),
                                "total_depreciation": str(total_depreciation),
                                "section_179_deduction": str(section_179_total),
                                "year": year,
                            }
                        },
                    }
                )

            elif report_type == "depreciation":
                # Depreciation Report
                assets_data = []
                total_basis = Decimal("0.00")
                total_depreciation = Decimal("0.00")
                total_book_value = Decimal("0.00")
                section_179_total = Decimal("0.00")

                for asset in fixed_assets:
                    # Calculate tax basis and current year depreciation
                    tax_basis = asset.purchase_cost
                    tax_book_value = tax_basis - asset.accumulated_depreciation

                    if asset.depreciation_method == "STRAIGHT_LINE":
                        current_year_depreciation = (
                            tax_basis - asset.salvage_value
                        ) / asset.useful_life_years
                    else:
                        current_year_depreciation = tax_basis * Decimal("0.2")

                    # Section 179 (simplified)
                    section_179 = (
                        min(tax_basis, Decimal("1000000"))
                        if tax_basis <= Decimal("1000000")
                        else Decimal("0.00")
                    )

                    assets_data.append(
                        {
                            "asset_code": asset.asset_code,
                            "name": asset.name,
                            "tax_basis": str(tax_basis),
                            "current_year_depreciation": str(current_year_depreciation),
                            "tax_book_value": str(tax_book_value),
                            "section_179": str(section_179),
                        }
                    )

                    total_basis += tax_basis
                    total_depreciation += current_year_depreciation
                    total_book_value += tax_book_value
                    section_179_total += section_179

                return JsonResponse(
                    {
                        "success": True,
                        "report_data": {
                            "assets": assets_data,
                            "totals": {
                                "total_basis": str(total_basis),
                                "total_depreciation": str(total_depreciation),
                                "total_book_value": str(total_book_value),
                                "section_179_total": str(section_179_total),
                            },
                            "year": year,
                        },
                    }
                )

            elif report_type == "property_tax":
                # Property Tax Report
                total_assessed_value = Decimal("0.00")
                total_property_tax = Decimal("0.00")

                for asset in fixed_assets:
                    assessed_value = asset.purchase_cost  # Simplified
                    property_tax_rate = Decimal("0.01")  # 1%
                    property_tax = assessed_value * property_tax_rate

                    total_assessed_value += assessed_value
                    total_property_tax += property_tax

                return JsonResponse(
                    {
                        "success": True,
                        "report_data": {
                            "total_assessed_value": str(total_assessed_value),
                            "total_property_tax": str(total_property_tax),
                            "tax_rate": "1.0%",
                            "year": year,
                        },
                    }
                )

            else:
                return JsonResponse({"success": False, "error": "Invalid report type"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})


@login_required
def customer_profile_view(request):
    """
    Customer profile update view
    """
    if request.method == "POST":
        # Handle profile update
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")

        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("customer_profile")

    context = {
        "title": "Update Profile",
        "user": request.user,
    }
    return render(request, "modules/customer_profile.html", context)


@login_required
def customer_support_view(request):
    """
    Customer support center view
    """
    if request.method == "POST":
        # Handle support ticket submission
        subject = request.POST.get("subject")
        category = request.POST.get("category")
        description = request.POST.get("description")
        priority = request.POST.get("priority")

        # In a real system, you'd create a support ticket record
        # For now, just show success message
        messages.success(
            request,
            "Support ticket submitted successfully! Our team will contact you within 24 hours.",
        )
        return redirect("customer_support")

    context = {
        "title": "Support Center",
    }
    return render(request, "modules/customer_support.html", context)


@login_required
def customer_activity_view(request):
    """
    Customer activity history view
    """
    # Mock activity data - in a real system, this would come from a database
    activities = [
        {
            "id": 1,
            "type": "asset_access",
            "title": "Asset Portal Accessed",
            "description": "You viewed your fixed assets",
            "timestamp": "2025-10-07 10:30:00",
            "icon": "fas fa-cubes",
            "color": "blue",
        },
        {
            "id": 2,
            "type": "profile_update",
            "title": "Profile Updated",
            "description": "Contact information was updated successfully",
            "timestamp": "2025-10-06 14:20:00",
            "icon": "fas fa-user",
            "color": "green",
        },
        {
            "id": 3,
            "type": "support_ticket",
            "title": "Support Ticket Submitted",
            "description": "Asset maintenance request submitted",
            "timestamp": "2025-10-04 09:15:00",
            "icon": "fas fa-exclamation-triangle",
            "color": "purple",
        },
        {
            "id": 4,
            "type": "login",
            "title": "Account Login",
            "description": "Logged in from web browser",
            "timestamp": "2025-10-03 08:45:00",
            "icon": "fas fa-sign-in-alt",
            "color": "gray",
        },
        {
            "id": 5,
            "type": "asset_report",
            "title": "Asset Issue Reported",
            "description": "Reported maintenance issue for asset COMP-001",
            "timestamp": "2025-10-02 16:30:00",
            "icon": "fas fa-flag",
            "color": "red",
        },
    ]

    context = {
        "title": "Activity History",
        "activities": activities,
    }
    return render(request, "modules/customer_activity.html", context)


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
    return render(request, "modules/financial_ratios.html", context)


@login_required
def calculate_ratios_api(request):
    """
    API endpoint to calculate financial ratios dynamically
    """
    from accounting.models import Account, AccountType
    from decimal import Decimal
    from django.http import JsonResponse

    try:
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

        ratios["current_ratio"] = float(
            (current_assets / current_liabilities)
            if current_liabilities > 0
            else Decimal("0.00")
        )
        ratios["quick_ratio"] = float(ratios["current_ratio"])  # Simplified
        ratios["cash_ratio"] = float(
            (current_assets * Decimal("0.5") / current_liabilities)
            if current_liabilities > 0
            else Decimal("0.00")
        )  # Simplified
        ratios["working_capital"] = float(current_assets - current_liabilities)

        # Profitability ratios
        ratios["gross_margin"] = float(
            ((total_revenue - total_expenses) / total_revenue * 100)
            if total_revenue > 0
            else Decimal("0.00")
        )
        ratios["operating_margin"] = float(
            (net_income / total_revenue * 100) if total_revenue > 0 else Decimal("0.00")
        )
        ratios["net_margin"] = float(
            (net_income / total_revenue * 100) if total_revenue > 0 else Decimal("0.00")
        )
        ratios["return_on_assets"] = float(
            (net_income / total_assets * 100) if total_assets > 0 else Decimal("0.00")
        )

        # Efficiency ratios
        ratios["asset_turnover"] = float(
            (total_revenue / total_assets) if total_assets > 0 else Decimal("0.00")
        )
        ratios["inventory_turnover"] = 8.5  # Mock data
        ratios["receivables_turnover"] = 6.2  # Mock data
        ratios["payables_turnover"] = 12.8  # Mock data

        # Leverage ratios
        ratios["debt_to_equity"] = float(
            (total_liabilities / total_equity) if total_equity > 0 else Decimal("0.00")
        )
        ratios["debt_ratio"] = float(
            (total_liabilities / total_assets * 100)
            if total_assets > 0
            else Decimal("0.00")
        )
        ratios["equity_ratio"] = float(
            (total_equity / total_assets * 100) if total_assets > 0 else Decimal("0.00")
        )
        ratios["interest_coverage"] = 25.6  # Mock data

        return JsonResponse(
            {
                "success": True,
                "ratios": ratios,
                "financial_data": {
                    "total_assets": float(total_assets),
                    "total_liabilities": float(total_liabilities),
                    "total_equity": float(total_equity),
                    "net_income": float(net_income),
                    "total_revenue": float(total_revenue),
                },
            }
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def trend_analysis_api(request):
    """
    API endpoint for financial ratios trend analysis
    """
    from django.http import JsonResponse
    import json

    try:
        # Mock trend data - in a real system, this would be calculated from historical data
        months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep"]

        trends = {
            "current_ratio": [2.1, 2.2, 2.3, 2.2, 2.3, 2.4],
            "profit_margin": [22.1, 24.2, 25.8, 26.3, 24.7, 25.3],
            "asset_turnover": [3.8, 4.1, 4.2, 4.0, 4.1, 4.2],
            "debt_to_equity": [0.25, 0.24, 0.23, 0.23, 0.22, 0.22],
            "net_margin": [20.1, 22.2, 23.8, 24.3, 22.7, 25.3],
            "return_on_assets": [10.2, 11.2, 11.8, 12.3, 11.7, 12.2],
        }

        return JsonResponse({"success": True, "trends": trends, "months": months})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def industry_compare_api(request):
    """
    API endpoint for industry comparison of financial ratios
    """
    from django.http import JsonResponse

    try:
        # Mock industry comparison data
        industry_data = {
            "retail": {
                "current_ratio": 1.8,
                "quick_ratio": 1.2,
                "gross_margin": 45.0,
                "net_margin": 8.5,
                "asset_turnover": 2.8,
                "debt_to_equity": 0.45,
                "return_on_assets": 6.2,
            },
            "manufacturing": {
                "current_ratio": 2.2,
                "quick_ratio": 1.5,
                "gross_margin": 35.0,
                "net_margin": 12.0,
                "asset_turnover": 1.8,
                "debt_to_equity": 0.35,
                "return_on_assets": 8.5,
            },
            "technology": {
                "current_ratio": 3.5,
                "quick_ratio": 2.8,
                "gross_margin": 65.0,
                "net_margin": 18.0,
                "asset_turnover": 1.2,
                "debt_to_equity": 0.15,
                "return_on_assets": 15.2,
            },
            "finance": {
                "current_ratio": 1.2,
                "quick_ratio": 0.8,
                "gross_margin": 85.0,
                "net_margin": 25.0,
                "asset_turnover": 0.8,
                "debt_to_equity": 8.5,
                "return_on_assets": 1.8,
            },
        }

        # Get current company ratios (simplified)
        company_ratios = {
            "current_ratio": 2.4,
            "quick_ratio": 1.8,
            "gross_margin": 63.8,
            "net_margin": 25.3,
            "asset_turnover": 4.2,
            "debt_to_equity": 0.22,
            "return_on_assets": 12.2,
        }

        return JsonResponse(
            {
                "success": True,
                "company_ratios": company_ratios,
                "industry_data": industry_data,
                "selected_industry": "technology",  # Default selection
            }
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def export_ratios_api(request):
    """
    API endpoint to export financial ratios report
    """
    from django.http import JsonResponse, HttpResponse
    from accounting.models import Account, AccountType
    from decimal import Decimal
    import csv
    import io

    try:
        # Get format from request
        export_format = request.GET.get("format", "csv")

        # Calculate ratios (similar to calculate_ratios_api)
        assets = Account.objects.filter(account_type=AccountType.ASSET, is_active=True)
        liabilities = Account.objects.filter(
            account_type=AccountType.LIABILITY, is_active=True
        )
        equity = Account.objects.filter(account_type=AccountType.EQUITY, is_active=True)

        total_assets = sum(acc.get_balance() for acc in assets)
        total_liabilities = sum(acc.get_balance() for acc in liabilities)
        total_equity = sum(acc.get_balance() for acc in equity)

        revenue_accounts = Account.objects.filter(
            account_type=AccountType.REVENUE, is_active=True
        )
        expense_accounts = Account.objects.filter(
            account_type=AccountType.EXPENSE, is_active=True
        )

        total_revenue = sum(acc.get_balance() for acc in revenue_accounts)
        total_expenses = sum(acc.get_balance() for acc in expense_accounts)
        net_income = total_revenue - total_expenses

        # Prepare export data
        export_data = [
            ["Financial Ratios Report", ""],
            ["Generated on", "2025-01-07"],
            ["", ""],
            ["Liquidity Ratios", ""],
            [
                "Current Ratio",
                f"{(total_assets/total_liabilities if total_liabilities > 0 else 0):.2f}:1",
            ],
            [
                "Quick Ratio",
                f"{(total_assets*Decimal('0.8')/total_liabilities if total_liabilities > 0 else 0):.2f}:1",
            ],
            [
                "Cash Ratio",
                f"{(total_assets*Decimal('0.3')/total_liabilities if total_liabilities > 0 else 0):.2f}:1",
            ],
            ["", ""],
            ["Profitability Ratios", ""],
            [
                "Gross Margin",
                f"{((total_revenue-total_expenses)/total_revenue*100 if total_revenue > 0 else 0):.1f}%",
            ],
            [
                "Net Margin",
                f"{(net_income/total_revenue*100 if total_revenue > 0 else 0):.1f}%",
            ],
            [
                "Return on Assets",
                f"{(net_income/total_assets*100 if total_assets > 0 else 0):.1f}%",
            ],
            ["", ""],
            ["Efficiency Ratios", ""],
            [
                "Asset Turnover",
                f"{(total_revenue/total_assets if total_assets > 0 else 0):.1f}x",
            ],
            ["", ""],
            ["Solvency Ratios", ""],
            [
                "Debt-to-Equity",
                f"{(total_liabilities/total_equity if total_equity > 0 else 0):.2f}:1",
            ],
            [
                "Debt Ratio",
                f"{(total_liabilities/total_assets*100 if total_assets > 0 else 0):.1f}%",
            ],
        ]

        if export_format == "csv":
            # Create CSV response
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = (
                'attachment; filename="financial_ratios_report.csv"'
            )

            writer = csv.writer(response)
            for row in export_data:
                writer.writerow(row)

            return response
        else:
            return JsonResponse(
                {"success": False, "error": "Unsupported export format"}
            )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def export_financial_statements_api(request):
    """
    API endpoint to export financial statements
    """
    from django.http import HttpResponse, JsonResponse
    from accounting.models import Account, AccountType
    from decimal import Decimal
    import csv
    import io

    try:
        statement_type = request.GET.get("type", "balance-sheet")
        export_format = request.GET.get("format", "csv")

        # Get financial data based on statement type
        if statement_type == "balance-sheet":
            # Balance Sheet data
            assets = Account.objects.filter(
                account_type=AccountType.ASSET, is_active=True
            )
            liabilities = Account.objects.filter(
                account_type=AccountType.LIABILITY, is_active=True
            )
            equity = Account.objects.filter(
                account_type=AccountType.EQUITY, is_active=True
            )

            total_assets = sum(acc.get_balance() for acc in assets)
            total_liabilities = sum(acc.get_balance() for acc in liabilities)
            total_equity = sum(acc.get_balance() for acc in equity)

            export_data = [
                ["Balance Sheet", ""],
                ["Generated on", "2025-10-11"],
                ["", ""],
                ["Assets", ""],
            ]

            for asset in assets:
                export_data.append([asset.name, str(asset.get_balance())])

            export_data.extend(
                [
                    ["", ""],
                    ["Total Assets", str(total_assets)],
                    ["", ""],
                    ["Liabilities", ""],
                ]
            )

            for liability in liabilities:
                export_data.append([liability.name, str(liability.get_balance())])

            export_data.extend(
                [
                    ["", ""],
                    ["Total Liabilities", str(total_liabilities)],
                    ["", ""],
                    ["Equity", ""],
                ]
            )

            for eq in equity:
                export_data.append([eq.name, str(eq.get_balance())])

            export_data.extend(
                [
                    ["", ""],
                    ["Total Equity", str(total_equity)],
                    ["", ""],
                    [
                        "Total Liabilities & Equity",
                        str(total_liabilities + total_equity),
                    ],
                ]
            )

        elif statement_type == "income-statement":
            # Income Statement data
            revenue_accounts = Account.objects.filter(
                account_type=AccountType.REVENUE, is_active=True
            )
            expense_accounts = Account.objects.filter(
                account_type=AccountType.EXPENSE, is_active=True
            )

            total_revenue = sum(acc.get_balance() for acc in revenue_accounts)
            total_expenses = sum(acc.get_balance() for acc in expense_accounts)
            net_income = total_revenue - total_expenses

            export_data = [
                ["Income Statement", ""],
                ["Generated on", "2025-10-11"],
                ["", ""],
                ["Revenue", ""],
            ]

            for revenue in revenue_accounts:
                export_data.append([revenue.name, str(revenue.get_balance())])

            export_data.extend(
                [
                    ["", ""],
                    ["Total Revenue", str(total_revenue)],
                    ["", ""],
                    ["Expenses", ""],
                ]
            )

            for expense in expense_accounts:
                export_data.append([expense.name, str(expense.get_balance())])

            export_data.extend(
                [
                    ["", ""],
                    ["Total Expenses", str(total_expenses)],
                    ["", ""],
                    ["Net Income", str(net_income)],
                ]
            )

        else:
            return JsonResponse({"success": False, "error": "Invalid statement type"})

        if export_format == "csv":
            # Create CSV response
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = (
                f'attachment; filename="{statement_type}_report.csv"'
            )

            writer = csv.writer(response)
            for row in export_data:
                writer.writerow(row)

            return response
        else:
            return JsonResponse(
                {"success": False, "error": "Unsupported export format"}
            )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def export_tax_reports_api(request):
    """
    API endpoint to export tax reports
    """
    from django.http import HttpResponse, JsonResponse
    from accounting.models import TaxReturn, TaxPayment
    from decimal import Decimal
    import csv
    import io

    try:
        report_type = request.GET.get("type", "summary")
        export_format = request.GET.get("format", "csv")
        tax_year = request.GET.get("year", "2025")

        # Mock tax data - in a real system, this would come from tax models
        if report_type == "summary":
            export_data = [
                ["Tax Report Summary", ""],
                ["Tax Year", tax_year],
                ["Generated on", "2025-10-11"],
                ["", ""],
                ["Income Tax", ""],
                ["Gross Income", "250000.00"],
                ["Deductions", "45000.00"],
                ["Taxable Income", "205000.00"],
                ["Tax Rate", "25%"],
                ["Tax Owed", "51250.00"],
                ["Tax Paid", "50000.00"],
                ["Balance Due", "1250.00"],
                ["", ""],
                ["Sales Tax", ""],
                ["Total Sales", "750000.00"],
                ["Tax Collected", "56250.00"],
                ["Tax Paid to Government", "55000.00"],
                ["Balance Due", "1250.00"],
            ]
        elif report_type == "transactions":
            export_data = [
                ["Tax Transactions Report", ""],
                ["Tax Year", tax_year],
                ["Generated on", "2025-10-11"],
                ["", ""],
                ["Date", "Type", "Amount", "Tax Rate", "Tax Amount"],
                ["2025-01-15", "Income", "25000.00", "25%", "6250.00"],
                ["2025-02-15", "Income", "25000.00", "25%", "6250.00"],
                ["2025-03-15", "Income", "25000.00", "25%", "6250.00"],
                ["2025-04-15", "Income", "25000.00", "25%", "6250.00"],
                ["2025-05-15", "Income", "25000.00", "25%", "6250.00"],
                ["2025-06-15", "Income", "25000.00", "25%", "6250.00"],
                ["2025-07-15", "Income", "25000.00", "25%", "6250.00"],
                ["2025-08-15", "Income", "25000.00", "25%", "6250.00"],
                ["2025-09-15", "Income", "25000.00", "25%", "6250.00"],
                ["2025-10-15", "Income", "25000.00", "25%", "6250.00"],
                ["2025-11-15", "Income", "25000.00", "25%", "6250.00"],
                ["2025-12-15", "Income", "25000.00", "25%", "6250.00"],
            ]
        else:
            return JsonResponse({"success": False, "error": "Invalid report type"})

        if export_format == "csv":
            # Create CSV response
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = (
                f'attachment; filename="tax_report_{report_type}_{tax_year}.csv"'
            )

            writer = csv.writer(response)
            for row in export_data:
                writer.writerow(row)

            return response
        else:
            return JsonResponse(
                {"success": False, "error": "Unsupported export format"}
            )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# Public/Marketing Views
def small_business_view(request):
    """
    Small Business page view
    """
    context = {
        "title": "Small Business Accounting Solutions",
        "description": "Accounting solutions for businesses with up to 50 employees.",
    }
    return render(request, "pages/small_business.html", context)


def enterprise_view(request):
    """
    Enterprise page view
    """
    context = {
        "title": "Enterprise Accounting Solutions",
        "description": "Accounting solutions for large organizations with 500+ employees.",
    }
    return render(request, "pages/enterprise.html", context)


def accounting_firms_view(request):
    """
    Accounting Firms page view
    """
    context = {
        "title": "Accounting Firms Solutions",
        "description": "Professional accounting firm management and multi-client solutions.",
    }
    return render(request, "pages/accounting_firms.html", context)


def retail_ecommerce_view(request):
    """
    Retail & E-commerce page view
    """
    context = {
        "title": "Retail & E-commerce Accounting",
        "description": "Specialized accounting solutions for retail and online businesses.",
    }
    return render(request, "pages/retail_ecommerce.html", context)


def manufacturing_view(request):
    """
    Manufacturing page view
    """
    context = {
        "title": "Manufacturing Accounting",
        "description": "Comprehensive accounting solutions for manufacturing operations.",
    }
    return render(request, "pages/manufacturing.html", context)


def smart_invoicing_view(request):
    """
    Smart Invoicing page view
    """
    context = {
        "title": "Smart Invoicing Solutions",
        "description": "Automated billing and payment processing tools.",
    }
    return render(request, "pages/smart_invoicing.html", context)


def ai_bookkeeping_view(request):
    """
    AI Bookkeeping page view
    """
    context = {
        "title": "AI-Powered Bookkeeping",
        "description": "Intelligent automation for financial record keeping.",
    }
    return render(request, "pages/ai_bookkeeping.html", context)


def real_time_analytics_view(request):
    """
    Real-time Analytics page view
    """
    context = {
        "title": "Real-Time Financial Insights",
        "description": "Live dashboards and analytics for instant business intelligence.",
    }
    return render(request, "pages/real_time_analytics.html", context)


def ifrs_compliance_view(request):
    """
    IFRS Compliance page view
    """
    context = {
        "title": "IFRS Compliance Solutions",
        "description": "International Financial Reporting Standards compliance tools.",
    }
    return render(request, "pages/ifrs_compliance.html", context)


def bank_grade_security_view(request):
    """
    Bank-Grade Security page view
    """
    context = {
        "title": "Bank-Grade Security",
        "description": "ISO 27001 certified data protection and security infrastructure.",
    }
    return render(request, "pages/bank_grade_security.html", context)


def pricing_view(request):
    """
    Pricing page view
    """
    context = {
        "title": "Pricing Plans - Ovovex",
        "description": "Choose the perfect plan for your business needs.",
    }
    return render(request, "pages/pricing.html", context)


def get_started_view(request):
    """
    Get Started page view
    """
    context = {
        "title": "Get Started with Ovovex",
        "description": "Begin your journey with Ovovex - guided onboarding and quick setup.",
    }
    return render(request, "pages/get_started.html", context)


def start_free_trial_view(request):
    """
    Start Free Trial page view
    """
    context = {
        "title": "Start Your Free Trial",
        "description": "Start a risk-free trial of Ovovex and explore core features.",
    }
    return render(request, "pages/start_free_trial.html", context)


def contact_sales_view(request):
    """
    Contact Sales page view
    """
    from django.contrib import messages
    from django.shortcuts import redirect

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        company = request.POST.get("company")
        message = request.POST.get("message")

        # In a real app we'd create a SalesLead record or send an email
        messages.success(request, "Thanks! Our sales team will reach out shortly.")
        return redirect("contact_sales")

    context = {
        "title": "Contact Sales",
        "description": "Get a tailored quote and onboard support for your organization.",
    }
    return render(request, "pages/contact_sales.html", context)


# Redirect views for backward compatibility
def redirect_general_ledger(request):
    """Redirect old general ledger URL to dashboard"""
    return redirect("dashboard:general_ledger")


def redirect_invoices(request):
    """Redirect old invoices URL to dashboard"""
    return redirect("dashboard:invoices")


def redirect_balance_sheet(request):
    """Redirect old balance sheet URL to dashboard"""
    return redirect("dashboard:balance_sheet")


def redirect_journal_entries(request):
    """Redirect old journal entries URL to dashboard"""
    return redirect("dashboard:journal_entries")


def redirect_budgeting(request):
    """Redirect old budgeting URL to dashboard"""
    return redirect("dashboard:budgeting")


def redirect_fixed_assets(request):
    """Redirect old fixed assets URL to dashboard"""
    return redirect("dashboard:fixed_assets")


def redirect_ai_insights(request):
    """Redirect old AI insights URL to dashboard"""
    return redirect("dashboard:ai_insights")


def redirect_settings(request):
    """Redirect old settings URL to dashboard"""
    return redirect("dashboard:settings")
