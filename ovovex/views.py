from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from accounting.models import JournalEntryLine

def home(request):
    """
    Home page view
    """
    context = {
        'title': 'Welcome to Ovovex',
        'description': 'Your next-generation platform for innovative solutions.',
    }
    return render(request, 'home.html', context)

def health_check(request):
    """
    Simple health check endpoint
    """
    return HttpResponse("OK", content_type="text/plain")

def login_view(request):
    """
    Login page view
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    context = {
        'title': 'Login to Ovovex',
        'description': 'Access your accounting dashboard and manage your finances.',
    }
    return render(request, 'auth/login.html', context)

def signup_view(request):
    """
    Signup page view
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validation
        if not all([username, email, first_name, last_name, password, password_confirm]):
            messages.error(request, 'Please fill in all fields.')
        elif password != password_confirm:
            messages.error(request, 'Passwords do not match.')
        elif len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            # Create user
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password
                )
                messages.success(request, 'Account created successfully! You can now login.')
                return redirect('login')
            except Exception as e:
                messages.error(request, 'An error occurred while creating your account.')
    
    context = {
        'title': 'Join Ovovex',
        'description': 'Create your account and start managing your finances today.',
    }
    return render(request, 'auth/signup.html', context)

def logout_view(request):
    """
    Logout view
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def dashboard_view(request):
    """
    Dashboard view for authenticated users
    """
    context = {
        'title': 'Dashboard',
        'description': 'Your accounting dashboard and financial overview.',
        'user': request.user,
    }
    return render(request, 'dashboard/dashboard.html', context)

# Core Accounting Views
@login_required
def general_ledger_view(request):
    """
    General Ledger view
    """
    from accounting.models import Account, JournalEntry, AccountType
    from django.db.models import Sum, Count
    from datetime import datetime, timedelta
    
    # Get filter parameters
    account_type_filter = request.GET.get('account_type', 'all')
    
    # Get all accounts
    accounts = Account.objects.filter(is_active=True)
    if account_type_filter != 'all':
        accounts = accounts.filter(account_type=account_type_filter)
    
    # Update balances for display
    for account in accounts:
        account.current_balance = account.get_balance()
    
    # Get statistics
    total_accounts = Account.objects.filter(is_active=True).count()
    
    # Journal entries this month
    current_month = datetime.now().replace(day=1).date()
    entries_this_month = JournalEntry.objects.filter(
        entry_date__gte=current_month,
        status='POSTED'
    ).count()
    
    # Unbalanced entries (draft or not balanced)
    unbalanced_entries = JournalEntry.objects.filter(
        status='DRAFT'
    ).count()
    
    # Recent journal entries
    recent_entries = JournalEntry.objects.filter(
        status='POSTED'
    ).order_by('-entry_date', '-created_at')[:5]
    
    # Calculate balance summary by account type
    from decimal import Decimal
    balance_summary = {
        'assets': Decimal('0.00'),
        'liabilities': Decimal('0.00'),
        'equity': Decimal('0.00'),
        'revenue': Decimal('0.00'),
        'expenses': Decimal('0.00'),
    }
    
    for account in Account.objects.filter(is_active=True):
        balance = account.get_balance()
        if account.account_type == AccountType.ASSET:
            balance_summary['assets'] += balance
        elif account.account_type == AccountType.LIABILITY:
            balance_summary['liabilities'] += balance
        elif account.account_type == AccountType.EQUITY:
            balance_summary['equity'] += balance
        elif account.account_type == AccountType.REVENUE:
            balance_summary['revenue'] += balance
        elif account.account_type == AccountType.EXPENSE:
            balance_summary['expenses'] += balance
    
    # Calculate net balance (Assets - Liabilities)
    net_balance = balance_summary['assets'] - balance_summary['liabilities']
    
    # Total entries count
    total_entries = JournalEntry.objects.filter(status='POSTED').count()
    
    context = {
        'title': 'General Ledger',
        'description': 'Chart of accounts, journals, and ledger balances.',
        'user': request.user,
        'accounts': accounts,
        'recent_entries': recent_entries,
        'total_accounts': total_accounts,
        'entries_this_month': entries_this_month,
        'unbalanced_entries': unbalanced_entries,
        'total_entries': total_entries,
        'balance_summary': balance_summary,
        'net_balance': net_balance,
        'account_type_filter': account_type_filter,
        'account_types': AccountType.choices,
    }
    return render(request, 'modules/general_ledger.html', context)

@login_required
def invoices_view(request):
    """
    Invoices view
    """
    from accounting.models import Invoice, Customer
    from django.db.models import Sum, Count
    
    # Get all invoices
    invoices = Invoice.objects.all().select_related('customer')[:20]
    
    # Statistics
    total_invoices = Invoice.objects.count()
    total_revenue = Invoice.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
    paid_invoices = Invoice.objects.filter(status='PAID').count()
    overdue_invoices = Invoice.objects.filter(status='OVERDUE').count()
    
    # Recent invoices
    recent_invoices = Invoice.objects.all().order_by('-invoice_date')[:5]
    
    context = {
        'title': 'Invoices',
        'description': 'Create, send, and track invoices.',
        'user': request.user,
        'invoices': invoices,
        'total_invoices': total_invoices,
        'total_revenue': total_revenue,
        'paid_invoices': paid_invoices,
        'overdue_invoices': overdue_invoices,
        'recent_invoices': recent_invoices,
    }
    return render(request, 'modules/invoices.html', context)

@login_required
def balance_sheet_view(request):
    """
    Balance Sheet view
    """
    from accounting.models import Account, AccountType
    from decimal import Decimal
    
    # Get accounts by type
    assets = Account.objects.filter(account_type=AccountType.ASSET, is_active=True)
    liabilities = Account.objects.filter(account_type=AccountType.LIABILITY, is_active=True)
    equity = Account.objects.filter(account_type=AccountType.EQUITY, is_active=True)
    
    # Calculate balances
    total_assets = sum(acc.get_balance() for acc in assets)
    total_liabilities = sum(acc.get_balance() for acc in liabilities)
    total_equity = sum(acc.get_balance() for acc in equity)
    
    # For balance sheet, calculate current vs non-current
    current_assets = sum(acc.get_balance() for acc in assets if acc.code < '1400')
    fixed_assets = sum(acc.get_balance() for acc in assets if acc.code >= '1400')
    current_liabilities = sum(acc.get_balance() for acc in liabilities if acc.code < '2300')
    long_term_liabilities = sum(acc.get_balance() for acc in liabilities if acc.code >= '2300')
    
    context = {
        'title': 'Balance Sheet',
        'description': 'Assets, liabilities, and equity overview.',
        'user': request.user,
        'assets': assets,
        'liabilities': liabilities,
        'equity': equity,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'current_assets': current_assets,
        'fixed_assets': fixed_assets,
        'current_liabilities': current_liabilities,
        'long_term_liabilities': long_term_liabilities,
    }
    return render(request, 'modules/balance_sheet.html', context)

@login_required
def pnl_statement_view(request):
    """
    P&L Statement view
    """
    from accounting.models import Account, AccountType
    from decimal import Decimal
    
    # Get revenue and expense accounts
    revenue_accounts = Account.objects.filter(account_type=AccountType.REVENUE, is_active=True)
    expense_accounts = Account.objects.filter(account_type=AccountType.EXPENSE, is_active=True)
    
    # Calculate totals
    total_revenue = sum(acc.get_balance() for acc in revenue_accounts)
    total_expenses = sum(acc.get_balance() for acc in expense_accounts)
    
    # Net profit/loss
    net_profit = total_revenue - total_expenses
    profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else Decimal('0.00')
    
    # Break down expenses by category
    cogs = sum(acc.get_balance() for acc in expense_accounts if acc.code.startswith('50'))
    operating_expenses = sum(acc.get_balance() for acc in expense_accounts if not acc.code.startswith('50'))
    
    gross_profit = total_revenue - cogs
    
    context = {
        'title': 'P&L Statement',
        'description': 'Profit and Loss statement analysis.',
        'user': request.user,
        'revenue_accounts': revenue_accounts,
        'expense_accounts': expense_accounts,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'cogs': cogs,
        'gross_profit': gross_profit,
        'operating_expenses': operating_expenses,
        'net_profit': net_profit,
        'profit_margin': profit_margin,
    }
    return render(request, 'modules/income_statement.html', context)

@login_required
def journal_entries_view(request):
    """
    Journal Entries view
    """
    from accounting.models import JournalEntry, JournalEntryLine, Account
    from django.db.models import Sum, Count, Q
    from datetime import datetime, timedelta
    
    # Get all journal entries
    journal_entries = JournalEntry.objects.all().order_by('-entry_date', '-id')
    
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
        entry_date__gte=first_day,
        entry_date__lte=today
    )
    
    # Get all lines for month entries
    month_lines = JournalEntryLine.objects.filter(
        journal_entry__in=month_entries
    )
    
    total_debits = month_lines.aggregate(Sum('debit_amount'))['debit_amount__sum'] or Decimal('0.00')
    total_credits = month_lines.aggregate(Sum('credit_amount'))['credit_amount__sum'] or Decimal('0.00')
    
    # Get status distribution (instead of entry_type which doesn't exist)
    status_distribution = journal_entries.values('status').annotate(count=Count('id'))
    
    # Get all active accounts for the dropdown
    accounts = Account.objects.filter(is_active=True).order_by('code')
    
    context = {
        'title': 'Journal Entries',
        'description': 'Manual journal entries and adjustments.',
        'user': request.user,
        'journal_entries': journal_entries,
        'total_entries': total_entries,
        'posted_entries': posted_entries,
        'draft_entries': draft_entries,
        'recent_entries': recent_entries,
        'total_debits': total_debits,
        'total_credits': total_credits,
        'status_distribution': status_distribution,
        'accounts': accounts,
    }
    return render(request, 'modules/journal_entries.html', context)

# ============================================================================
# MISSING VIEWS - STUBS FOR URL COMPATIBILITY
# ============================================================================

@login_required
def create_journal_entry_view(request):
    """
    Create journal entry view
    """
    # Stub implementation
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})

@login_required
def post_journal_entries_view(request):
    """
    Post journal entries view
    """
    # Stub implementation
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})

@login_required
def reverse_journal_entry_view(request):
    """
    Reverse journal entry view
    """
    # Stub implementation
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})

@login_required
def export_journal_entries_view(request):
    """
    Export journal entries view
    """
    # Stub implementation
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})

@login_required
def journal_report_view(request):
    """
    Journal report view
    """
    # Stub implementation
    context = {
        'title': 'Journal Report',
    }
    return render(request, 'modules/journal_report.html', context)

@login_required
def trial_balance_view(request):
    """
    Trial balance view
    """
    # Stub implementation
    context = {
        'title': 'Trial Balance',
    }
    return render(request, 'modules/trial_balance.html', context)

@login_required
def reconciliation_view(request):
    """
    Reconciliation view
    """
    # Stub implementation
    context = {
        'title': 'Reconciliation',
    }
    return render(request, 'modules/reconciliation.html', context)

@login_required
def cash_flow_view(request):
    """
    Cash flow view
    """
    # Stub implementation
    context = {
        'title': 'Cash Flow',
    }
    return render(request, 'modules/cash_flow.html', context)

@login_required
def create_budget_view(request):
    """
    Create budget view
    """
    # Stub implementation
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})

@login_required
def copy_budget_view(request):
    """
    Copy budget view
    """
    # Stub implementation
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})

@login_required
def export_budget_view(request):
    """
    Export budget view
    """
    # Stub implementation
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})

@login_required
def fixed_assets_view(request):
    """
    Fixed assets view
    """
    # Stub implementation
    context = {
        'title': 'Fixed Assets',
    }
    return render(request, 'modules/fixed_assets.html', context)

@login_required
def add_fixed_asset_view(request):
    """
    Add fixed asset view
    """
    # Stub implementation
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})

@login_required
def export_fixed_assets_view(request):
    """
    Export fixed assets view
    """
    # Stub implementation
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})

@login_required
def bank_reconciliation_view(request):
    """
    Bank reconciliation view
    """
    # Stub implementation
    context = {
        'title': 'Bank Reconciliation',
    }
    return render(request, 'modules/bank_reconciliation.html', context)

@login_required
def add_reconciliation_adjustment_view(request):
    """
    Add reconciliation adjustment view
    """
    # Stub implementation
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})

@login_required
def reconcile_statement_view(request, statement_id):
    """
    Reconcile statement view
    """
    # Stub implementation
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})

@login_required
def calculate_tax_depreciation_view(request):
    """
    Calculate tax depreciation view
    """
    # Stub implementation
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})

@login_required
def generate_tax_report_view(request):
    """
    Generate tax report view
    """
    # Stub implementation
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})

@login_required
def customer_profile_view(request):
    """
    Customer profile update view
    """
    if request.method == 'POST':
        # Handle profile update
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('customer_profile')
    
    context = {
        'title': 'Update Profile',
        'user': request.user,
    }
    return render(request, 'modules/customer_profile.html', context)

@login_required
def customer_support_view(request):
    """
    Customer support center view
    """
    if request.method == 'POST':
        # Handle support ticket submission
        subject = request.POST.get('subject')
        category = request.POST.get('category')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        
        # In a real system, you'd create a support ticket record
        # For now, just show success message
        messages.success(request, 'Support ticket submitted successfully! Our team will contact you within 24 hours.')
        return redirect('customer_support')
    
    context = {
        'title': 'Support Center',
    }
    return render(request, 'modules/customer_support.html', context)

@login_required
def customer_activity_view(request):
    """
    Customer activity history view
    """
    # Mock activity data - in a real system, this would come from a database
    activities = [
        {
            'id': 1,
            'type': 'asset_access',
            'title': 'Asset Portal Accessed',
            'description': 'You viewed your fixed assets',
            'timestamp': '2025-10-07 10:30:00',
            'icon': 'fas fa-cubes',
            'color': 'blue'
        },
        {
            'id': 2,
            'type': 'profile_update',
            'title': 'Profile Updated',
            'description': 'Contact information was updated successfully',
            'timestamp': '2025-10-06 14:20:00',
            'icon': 'fas fa-user',
            'color': 'green'
        },
        {
            'id': 3,
            'type': 'support_ticket',
            'title': 'Support Ticket Submitted',
            'description': 'Asset maintenance request submitted',
            'timestamp': '2025-10-04 09:15:00',
            'icon': 'fas fa-exclamation-triangle',
            'color': 'purple'
        },
        {
            'id': 4,
            'type': 'login',
            'title': 'Account Login',
            'description': 'Logged in from web browser',
            'timestamp': '2025-10-03 08:45:00',
            'icon': 'fas fa-sign-in-alt',
            'color': 'gray'
        },
        {
            'id': 5,
            'type': 'asset_report',
            'title': 'Asset Issue Reported',
            'description': 'Reported maintenance issue for asset COMP-001',
            'timestamp': '2025-10-02 16:30:00',
            'icon': 'fas fa-flag',
            'color': 'red'
        },
    ]
    
    context = {
        'title': 'Activity History',
        'activities': activities,
    }
    return render(request, 'modules/customer_activity.html', context)

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
        liabilities = Account.objects.filter(account_type=AccountType.LIABILITY, is_active=True)
        equity = Account.objects.filter(account_type=AccountType.EQUITY, is_active=True)
        
        total_assets = sum(acc.get_balance() for acc in assets)
        total_liabilities = sum(acc.get_balance() for acc in liabilities)
        total_equity = sum(acc.get_balance() for acc in equity)
        
        # Get income statement data
        revenue_accounts = Account.objects.filter(account_type=AccountType.REVENUE, is_active=True)
        expense_accounts = Account.objects.filter(account_type=AccountType.EXPENSE, is_active=True)
        
        total_revenue = sum(acc.get_balance() for acc in revenue_accounts)
        total_expenses = sum(acc.get_balance() for acc in expense_accounts)
        net_income = total_revenue - total_expenses
        
        # Calculate ratios
        ratios = {}
        
        # Liquidity ratios
        current_assets = sum(acc.get_balance() for acc in assets if acc.code < '1400')
        current_liabilities = sum(acc.get_balance() for acc in liabilities if acc.code < '2300')
        
        ratios['current_ratio'] = float((current_assets / current_liabilities) if current_liabilities > 0 else Decimal('0.00'))
        ratios['quick_ratio'] = float(ratios['current_ratio'])  # Simplified
        ratios['cash_ratio'] = float((current_assets * Decimal('0.5') / current_liabilities) if current_liabilities > 0 else Decimal('0.00'))  # Simplified
        ratios['working_capital'] = float(current_assets - current_liabilities)
        
        # Profitability ratios
        ratios['gross_margin'] = float(((total_revenue - total_expenses) / total_revenue * 100) if total_revenue > 0 else Decimal('0.00'))
        ratios['operating_margin'] = float((net_income / total_revenue * 100) if total_revenue > 0 else Decimal('0.00'))
        ratios['net_margin'] = float((net_income / total_revenue * 100) if total_revenue > 0 else Decimal('0.00'))
        ratios['return_on_assets'] = float((net_income / total_assets * 100) if total_assets > 0 else Decimal('0.00'))
        
        # Efficiency ratios
        ratios['asset_turnover'] = float((total_revenue / total_assets) if total_assets > 0 else Decimal('0.00'))
        ratios['inventory_turnover'] = 8.5  # Mock data
        ratios['receivables_turnover'] = 6.2  # Mock data
        ratios['payables_turnover'] = 12.8  # Mock data
        
        # Leverage ratios
        ratios['debt_to_equity'] = float((total_liabilities / total_equity) if total_equity > 0 else Decimal('0.00'))
        ratios['debt_ratio'] = float((total_liabilities / total_assets * 100) if total_assets > 0 else Decimal('0.00'))
        ratios['equity_ratio'] = float((total_equity / total_assets * 100) if total_assets > 0 else Decimal('0.00'))
        ratios['interest_coverage'] = 25.6  # Mock data
        
        return JsonResponse({
            'success': True,
            'ratios': ratios,
            'financial_data': {
                'total_assets': float(total_assets),
                'total_liabilities': float(total_liabilities),
                'total_equity': float(total_equity),
                'net_income': float(net_income),
                'total_revenue': float(total_revenue)
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def trend_analysis_api(request):
    """
    API endpoint for financial ratios trend analysis
    """
    from django.http import JsonResponse
    import json
    
    try:
        # Mock trend data - in a real system, this would be calculated from historical data
        months = ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
        
        trends = {
            'current_ratio': [2.1, 2.2, 2.3, 2.2, 2.3, 2.4],
            'profit_margin': [22.1, 24.2, 25.8, 26.3, 24.7, 25.3],
            'asset_turnover': [3.8, 4.1, 4.2, 4.0, 4.1, 4.2],
            'debt_to_equity': [0.25, 0.24, 0.23, 0.23, 0.22, 0.22],
            'net_margin': [20.1, 22.2, 23.8, 24.3, 22.7, 25.3],
            'return_on_assets': [10.2, 11.2, 11.8, 12.3, 11.7, 12.2]
        }
        
        return JsonResponse({
            'success': True,
            'trends': trends,
            'months': months
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def industry_compare_api(request):
    """
    API endpoint for industry comparison of financial ratios
    """
    from django.http import JsonResponse
    
    try:
        # Mock industry comparison data
        industry_data = {
            'retail': {
                'current_ratio': 1.8,
                'quick_ratio': 1.2,
                'gross_margin': 45.0,
                'net_margin': 8.5,
                'asset_turnover': 2.8,
                'debt_to_equity': 0.45,
                'return_on_assets': 6.2
            },
            'manufacturing': {
                'current_ratio': 2.2,
                'quick_ratio': 1.5,
                'gross_margin': 35.0,
                'net_margin': 12.0,
                'asset_turnover': 1.8,
                'debt_to_equity': 0.35,
                'return_on_assets': 8.5
            },
            'technology': {
                'current_ratio': 3.5,
                'quick_ratio': 2.8,
                'gross_margin': 65.0,
                'net_margin': 18.0,
                'asset_turnover': 1.2,
                'debt_to_equity': 0.15,
                'return_on_assets': 15.2
            },
            'finance': {
                'current_ratio': 1.2,
                'quick_ratio': 0.8,
                'gross_margin': 85.0,
                'net_margin': 25.0,
                'asset_turnover': 0.8,
                'debt_to_equity': 8.5,
                'return_on_assets': 1.8
            }
        }
        
        # Get current company ratios (simplified)
        company_ratios = {
            'current_ratio': 2.4,
            'quick_ratio': 1.8,
            'gross_margin': 63.8,
            'net_margin': 25.3,
            'asset_turnover': 4.2,
            'debt_to_equity': 0.22,
            'return_on_assets': 12.2
        }
        
        return JsonResponse({
            'success': True,
            'company_ratios': company_ratios,
            'industry_data': industry_data,
            'selected_industry': 'technology'  # Default selection
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


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
        export_format = request.GET.get('format', 'csv')
        
        # Calculate ratios (similar to calculate_ratios_api)
        assets = Account.objects.filter(account_type=AccountType.ASSET, is_active=True)
        liabilities = Account.objects.filter(account_type=AccountType.LIABILITY, is_active=True)
        equity = Account.objects.filter(account_type=AccountType.EQUITY, is_active=True)
        
        total_assets = sum(acc.get_balance() for acc in assets)
        total_liabilities = sum(acc.get_balance() for acc in liabilities)
        total_equity = sum(acc.get_balance() for acc in equity)
        
        revenue_accounts = Account.objects.filter(account_type=AccountType.REVENUE, is_active=True)
        expense_accounts = Account.objects.filter(account_type=AccountType.EXPENSE, is_active=True)
        
        total_revenue = sum(acc.get_balance() for acc in revenue_accounts)
        total_expenses = sum(acc.get_balance() for acc in expense_accounts)
        net_income = total_revenue - total_expenses
        
        # Prepare export data
        export_data = [
            ['Financial Ratios Report', ''],
            ['Generated on', '2025-01-07'],
            ['', ''],
            ['Liquidity Ratios', ''],
            ['Current Ratio', f"{(total_assets/total_liabilities if total_liabilities > 0 else 0):.2f}:1"],
            ['Quick Ratio', f"{(total_assets*Decimal('0.8')/total_liabilities if total_liabilities > 0 else 0):.2f}:1"],
            ['Cash Ratio', f"{(total_assets*Decimal('0.3')/total_liabilities if total_liabilities > 0 else 0):.2f}:1"],
            ['', ''],
            ['Profitability Ratios', ''],
            ['Gross Margin', f"{((total_revenue-total_expenses)/total_revenue*100 if total_revenue > 0 else 0):.1f}%"],
            ['Net Margin', f"{(net_income/total_revenue*100 if total_revenue > 0 else 0):.1f}%"],
            ['Return on Assets', f"{(net_income/total_assets*100 if total_assets > 0 else 0):.1f}%"],
            ['', ''],
            ['Efficiency Ratios', ''],
            ['Asset Turnover', f"{(total_revenue/total_assets if total_assets > 0 else 0):.1f}x"],
            ['', ''],
            ['Solvency Ratios', ''],
            ['Debt-to-Equity', f"{(total_liabilities/total_equity if total_equity > 0 else 0):.2f}:1"],
            ['Debt Ratio', f"{(total_liabilities/total_assets*100 if total_assets > 0 else 0):.1f}%"],
        ]
        
        if export_format == 'csv':
            # Create CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="financial_ratios_report.csv"'
            
            writer = csv.writer(response)
            for row in export_data:
                writer.writerow(row)
            
            return response
        else:
            return JsonResponse({'success': False, 'error': 'Unsupported export format'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def create_invoice_view(request):
    """
    Create invoice view
    """
    # Stub implementation
    context = {
        'title': 'Create Invoice',
    }
    return render(request, 'modules/create_invoice.html', context)

@login_required
def send_invoice_view(request):
    """
    Send invoice view
    """
    # Stub implementation
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})

@login_required
def record_payment_view(request):
    """
    Record payment view
    """
    # Stub implementation
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})

@login_required
def send_reminders_view(request):
    """
    Send reminders view
    """
    # Stub implementation
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})

@login_required
def collection_report_view(request):
    """
    Collection report view
    """
    # Stub implementation
    context = {
        'title': 'Collection Report',
    }
    return render(request, 'modules/collection_report.html', context)

@login_required
def send_statements_view(request):
    """
    Send statements view
    """
    # Stub implementation
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})

@login_required
def set_reminders_view(request):
    """
    Set reminders view
    """
    # Stub implementation
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})

@login_required
def invoice_report_view(request):
    """
    Invoice report view
    """
    # Stub implementation
    context = {
        'title': 'Invoice Report',
    }
    return render(request, 'modules/invoice_report.html', context)

@login_required
def budgeting_view(request):
    """
    Budgeting view
    """
    # Stub implementation
    context = {
        'title': 'Budgeting',
    }
    return render(request, 'modules/budgeting.html', context)

@login_required
def update_statement_balance_view(request):
    """
    Update bank statement balance view
    """
    # Stub implementation
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})

@login_required
def tax_center_view(request):
    """
    Tax center view
    """
    # Stub implementation
    context = {
        'title': 'Tax Center',
    }
    return render(request, 'modules/tax_center.html', context)

@login_required
def update_asset_tax_info_view(request, asset_id):
    """
    Update asset tax information view
    """
    # Stub implementation
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})

@login_required
def accounts_receivable_view(request):
    """
    Accounts receivable view
    """
    from accounting.models import Invoice, Customer
    from django.db.models import Sum
    from decimal import Decimal
    
    # Get all invoices
    invoices = Invoice.objects.filter(status__in=['SENT', 'OVERDUE']).select_related('customer')
    
    # Statistics
    total_receivable = invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
    total_paid = invoices.aggregate(Sum('paid_amount'))['paid_amount__sum'] or Decimal('0.00')
    outstanding = total_receivable - total_paid
    
    context = {
        'title': 'Accounts Receivable',
        'description': 'Manage customer invoices and payments.',
        'user': request.user,
        'invoices': invoices,
        'total_receivable': total_receivable,
        'total_paid': total_paid,
        'outstanding': outstanding,
    }
    return render(request, 'modules/accounts_receivable.html', context)


@login_required
def accounts_payable_view(request):
    """
    Accounts payable view
    """
    from accounting.models import Bill, Vendor
    from django.db.models import Sum
    from decimal import Decimal
    
    # Get all bills
    bills = Bill.objects.filter(status__in=['APPROVED', 'PAID']).select_related('vendor')
    
    # Get vendors for the template
    vendors = Vendor.objects.filter(is_active=True)
    
    # Statistics
    total_payable = bills.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
    total_paid = bills.aggregate(Sum('paid_amount'))['paid_amount__sum'] or Decimal('0.00')
    outstanding = total_payable - total_paid
    
    context = {
        'title': 'Accounts Payable',
        'description': 'Manage vendor bills and payments.',
        'user': request.user,
        'bills': bills,
        'vendors': vendors,
        'total_payable': total_payable,
        'total_paid': total_paid,
        'outstanding': outstanding,
    }
    return render(request, 'modules/accounts_payable.html', context)

@login_required
def create_bill_view(request):
    """
    Create new bill
    """
    from accounting.models import Vendor, Bill, BillLine
    from django.http import JsonResponse
    from decimal import Decimal
    import json

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create bill
            vendor = Vendor.objects.get(id=data['vendor_id'])
            bill = Bill.objects.create(
                bill_number=data['bill_number'],
                vendor=vendor,
                bill_date=data['bill_date'],
                due_date=data['due_date'],
                notes=data.get('notes', ''),
                created_by=request.user
            )
            
            # Add line items
            subtotal = Decimal('0.00')
            for line_data in data['lines']:
                line_total = Decimal(str(line_data['quantity'])) * Decimal(str(line_data['unit_price']))
                BillLine.objects.create(
                    bill=bill,
                    description=line_data['description'],
                    quantity=Decimal(str(line_data['quantity'])),
                    unit_price=Decimal(str(line_data['unit_price'])),
                    line_total=line_total
                )
                subtotal += line_total
            
            # Calculate totals
            tax_rate = Decimal('0.10')  # 10% tax rate
            tax_amount = subtotal * tax_rate
            total_amount = subtotal + tax_amount
            
            bill.subtotal = subtotal
            bill.tax_amount = tax_amount
            bill.total_amount = total_amount
            bill.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Bill created successfully',
                'bill_id': bill.id,
                'bill_number': bill.bill_number
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # GET request - return form data
    vendors = Vendor.objects.filter(is_active=True)
    return JsonResponse({
        'vendors': [{'id': v.id, 'name': v.company_name} for v in vendors]
    })


@login_required
def import_bills_view(request):
    """
    Import bills from CSV
    """
    from accounting.models import Vendor, Bill, BillLine
    from django.http import JsonResponse
    from decimal import Decimal
    import csv
    import io

    if request.method == 'POST':
        try:
            csv_file = request.FILES['file']
            file_data = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(file_data))
            
            imported_count = 0
            errors = []
            
            for row in csv_reader:
                try:
                    vendor = Vendor.objects.get(vendor_code=row['vendor_code'])
                    
                    bill = Bill.objects.create(
                        bill_number=row['bill_number'],
                        vendor=vendor,
                        bill_date=row['bill_date'],
                        due_date=row['due_date'],
                        subtotal=Decimal(row['subtotal']),
                        tax_amount=Decimal(row.get('tax_amount', '0.00')),
                        total_amount=Decimal(row['total_amount']),
                        notes=row.get('notes', ''),
                        created_by=request.user
                    )
                    
                    # Create a single line item from the bill data
                    BillLine.objects.create(
                        bill=bill,
                        description=row.get('description', 'Imported item'),
                        quantity=Decimal('1.00'),
                        unit_price=Decimal(row['subtotal']),
                        line_total=Decimal(row['subtotal'])
                    )
                    
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {csv_reader.line_num}: {str(e)}")
            
            return JsonResponse({
                'success': True,
                'message': f'Imported {imported_count} bills successfully',
                'imported_count': imported_count,
                'errors': errors
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def process_payments_view(request):
    """
    Process payments for multiple bills
    """
    from accounting.models import Bill, Payment
    from django.http import JsonResponse
    from decimal import Decimal
    import json

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            bill_ids = data['bill_ids']
            payment_amount = Decimal(str(data['payment_amount']))
            payment_method = data['payment_method']
            
            bills = Bill.objects.filter(id__in=bill_ids)
            total_outstanding = sum(bill.total_amount - bill.paid_amount for bill in bills)
            
            if payment_amount > total_outstanding:
                return JsonResponse({'success': False, 'error': 'Payment amount exceeds total outstanding'})
            
            # Distribute payment across bills
            remaining_payment = payment_amount
            processed_bills = []
            
            for bill in bills:
                if remaining_payment <= 0:
                    break
                
                outstanding = bill.total_amount - bill.paid_amount
                payment_for_bill = min(outstanding, remaining_payment)
                
                bill.paid_amount += payment_for_bill
                if bill.paid_amount >= bill.total_amount:
                    bill.status = Bill.Status.PAID
                bill.save()
                
                # Create payment record
                Payment.objects.create(
                    payment_number=f"PAY-{bill.bill_number}-{Payment.objects.count() + 1:04d}",
                    customer=None,  # This is a bill payment, not customer payment
                    invoice=None,
                    payment_date=data['payment_date'],
                    amount=payment_for_bill,
                    payment_method=payment_method,
                    reference=data.get('reference', ''),
                    notes=f'Payment for bill {bill.bill_number}',
                    created_by=request.user
                )
                
                processed_bills.append({
                    'bill_number': bill.bill_number,
                    'payment_amount': str(payment_for_bill)
                })
                
                remaining_payment -= payment_for_bill
            
            return JsonResponse({
                'success': True,
                'message': f'Processed payment of ${payment_amount} across {len(processed_bills)} bills',
                'processed_bills': processed_bills
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def send_payable_reminders_view(request):
    """
    Send payment reminders for overdue bills
    """
    from accounting.models import Bill
    from django.http import JsonResponse
    from django.utils import timezone
    import json

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            bill_ids = data.get('bill_ids', [])
            
            if not bill_ids:
                # Send reminders for all overdue bills
                overdue_bills = Bill.objects.filter(
                    status__in=['APPROVED', 'OVERDUE'],
                    due_date__lt=timezone.now().date()
                )
            else:
                overdue_bills = Bill.objects.filter(id__in=bill_ids)
            
            sent_count = 0
            for bill in overdue_bills:
                if bill.vendor.email:
                    # In production, send actual email reminder
                    # send_reminder_email(bill)
                    sent_count += 1
            
            return JsonResponse({
                'success': True,
                'message': f'Reminders sent to {sent_count} vendors'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def mark_as_paid_view(request):
    """
    Mark bills as paid
    """
    from accounting.models import Bill
    from django.http import JsonResponse
    import json

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            bill_ids = data['bill_ids']
            
            bills = Bill.objects.filter(id__in=bill_ids)
            updated_count = 0
            
            for bill in bills:
                if bill.paid_amount < bill.total_amount:
                    bill.paid_amount = bill.total_amount
                    bill.status = Bill.Status.PAID
                    bill.save()
                    updated_count += 1
            
            return JsonResponse({
                'success': True,
                'message': f'Marked {updated_count} bills as paid'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def three_way_match_view(request):
    """
    Three-way match for bill verification
    """
    from accounting.models import Bill
    from django.http import JsonResponse
    import json

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            bill_id = data['bill_id']
            
            bill = Bill.objects.get(id=bill_id)
            
            # Simplified three-way match logic
            # In production, this would compare:
            # 1. Purchase Order
            # 2. Goods Receipt/Inventory
            # 3. Vendor Invoice
            
            match_result = {
                'bill_number': bill.bill_number,
                'vendor': bill.vendor.company_name,
                'amount': str(bill.total_amount),
                'status': 'MATCHED',  # Simplified - assume it matches
                'discrepancies': []
            }
            
            # Update bill status if matched
            if match_result['status'] == 'MATCHED':
                bill.status = Bill.Status.APPROVED
                bill.save()
            
            return JsonResponse({
                'success': True,
                'match_result': match_result
            })
            
        except Bill.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Bill not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def payable_aging_report_view(request):
    """
    Generate payable aging report
    """
    from accounting.models import Bill, Vendor
    from django.http import JsonResponse
    from django.utils import timezone
    from decimal import Decimal

    bills = Bill.objects.filter(status__in=['APPROVED', 'OVERDUE']).select_related('vendor')
    
    # Calculate aging by vendor
    vendor_summary = {}
    today = timezone.now().date()
    
    for bill in bills:
        vendor_name = bill.vendor.company_name
        if vendor_name not in vendor_summary:
            vendor_summary[vendor_name] = {
                'current': Decimal('0.00'),
                '1_30_days': Decimal('0.00'),
                '31_60_days': Decimal('0.00'),
                '61_90_days': Decimal('0.00'),
                'over_90_days': Decimal('0.00'),
                'total': Decimal('0.00')
            }
        
        outstanding = bill.total_amount - bill.paid_amount
        days_overdue = (today - bill.due_date).days
        
        if days_overdue <= 0:
            vendor_summary[vendor_name]['current'] += outstanding
        elif days_overdue <= 30:
            vendor_summary[vendor_name]['1_30_days'] += outstanding
        elif days_overdue <= 60:
            vendor_summary[vendor_name]['31_60_days'] += outstanding
        elif days_overdue <= 90:
            vendor_summary[vendor_name]['61_90_days'] += outstanding
        else:
            vendor_summary[vendor_name]['over_90_days'] += outstanding
        
        vendor_summary[vendor_name]['total'] += outstanding
    
    # Convert to list format for JSON response
    report_data = []
    for vendor_name, amounts in vendor_summary.items():
        report_data.append({
            'vendor': vendor_name,
            'current': str(amounts['current']),
            '1_30_days': str(amounts['1_30_days']),
            '31_60_days': str(amounts['31_60_days']),
            '61_90_days': str(amounts['61_90_days']),
            'over_90_days': str(amounts['over_90_days']),
            'total': str(amounts['total'])
        })
    
    return JsonResponse({
        'success': True,
        'report_data': report_data
    })

@login_required
def customer_portal_view(request):
    """
    Customer portal main page view
    """
    # Get some basic stats for the portal
    from accounting.models import Customer
    
    total_customers = Customer.objects.count()
    
    context = {
        'title': 'Customer Portal',
        'total_customers': total_customers,
    }
    return render(request, 'modules/customer_portal.html', context)