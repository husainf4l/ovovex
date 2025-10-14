from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from decimal import Decimal
import json

# Public Views
def home(request):
    """
    Home page view
    """
    context = {
        "title": "Ovovex - Modern Accounting Software",
        "description": "Streamline your accounting with AI-powered automation and real-time insights.",
    }
    return render(request, "home.html", context)


def health_check(request):
    """
    Health check endpoint for monitoring
    """
    return JsonResponse({"status": "healthy", "timestamp": datetime.now().isoformat()})


def login_view(request):
    """
    Login view
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get("next", "dashboard")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")

    context = {
        "title": "Login - Ovovex",
    }
    return render(request, "accounts/login.html", context)


def signup_view(request):
    """
    Signup view
    """
    from django.contrib.auth.models import User

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("signup")

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, "Account created successfully!")
        return redirect("dashboard")

    context = {
        "title": "Sign Up - Ovovex",
    }
    return render(request, "accounts/signup.html", context)


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
    Dashboard view
    """
    from accounting.models import Account, JournalEntry

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

    context = {
        "title": "Dashboard",
        "description": "Your accounting dashboard and financial overview.",
        "user": request.user,
        "accounts": accounts,
        "total_accounts": total_accounts,
        "entries_this_month": entries_this_month,
        "unbalanced_entries": unbalanced_entries,
        "recent_entries": recent_entries,
    }
    return render(request, "dashboard/dashboard.html", context)


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

def redirect_fixed_assets(request):
    """Redirect old fixed assets URL to dashboard"""
    return redirect('dashboard:fixed_assets')

def redirect_ai_insights(request):
    """Redirect old AI insights URL to dashboard"""
    return redirect('dashboard:ai_insights')

def redirect_settings(request):
    """Redirect old settings URL to dashboard"""
    return redirect('dashboard:settings')

# Redirect views for backward compatibility
def redirect_general_ledger(request):
    """Redirect old general ledger URL to dashboard"""
    return redirect('dashboard:general_ledger')

def redirect_invoices(request):
    """Redirect old invoices URL to dashboard"""
    return redirect('dashboard:invoices')

def redirect_balance_sheet(request):
    """Redirect old balance sheet URL to dashboard"""
    return redirect('dashboard:balance_sheet')

def redirect_journal_entries(request):
    """Redirect old journal entries URL to dashboard"""
    return redirect('dashboard:journal_entries')

def redirect_budgeting(request):
    """Redirect old budgeting URL to dashboard"""
    return redirect('dashboard:budgeting')

def redirect_fixed_assets(request):
    """Redirect old fixed assets URL to dashboard"""
    return redirect('dashboard:fixed_assets')

def redirect_ai_insights(request):
    """Redirect old AI insights URL to dashboard"""
    return redirect('dashboard:ai_insights')

def redirect_settings(request):
    """Redirect old settings URL to dashboard"""
    return redirect('dashboard:settings')
