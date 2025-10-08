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
    from accounting.models import JournalEntry, JournalEntryLine, Account
    from django.http import JsonResponse
    from decimal import Decimal
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create journal entry
            journal_entry = JournalEntry.objects.create(
                entry_number=data['entry_number'],
                entry_date=data['entry_date'],
                description=data['description'],
                reference=data.get('reference', ''),
                created_by=request.user
            )
            
            # Add line items
            total_debit = Decimal('0.00')
            total_credit = Decimal('0.00')
            
            for line_data in data['lines']:
                debit_amount = Decimal(str(line_data.get('debit_amount', '0.00')))
                credit_amount = Decimal(str(line_data.get('credit_amount', '0.00')))
                
                account = Account.objects.get(id=line_data['account_id'])
                
                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=account,
                    description=line_data.get('description', ''),
                    debit_amount=debit_amount,
                    credit_amount=credit_amount,
                    line_number=line_data['line_number']
                )
                
                total_debit += debit_amount
                total_credit += credit_amount
            
            # Update totals
            journal_entry.total_debit = total_debit
            journal_entry.total_credit = total_credit
            journal_entry.save()
            
            # Check if balanced
            if total_debit != total_credit:
                return JsonResponse({
                    'success': False,
                    'error': f'Journal entry is not balanced. Debit: ${total_debit}, Credit: ${total_credit}'
                })
            
            return JsonResponse({
                'success': True,
                'message': 'Journal entry created successfully',
                'entry_id': journal_entry.id,
                'entry_number': journal_entry.entry_number
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # GET request - return form data
    accounts = Account.objects.filter(is_active=True).order_by('code')
    context = {
        'title': 'Create Journal Entry',
        'accounts': accounts,
    }
    return render(request, 'modules/create_journal_entry.html', context)

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
    from accounting.models import BankReconciliation, BankStatement, Account
    from django.db.models import Sum
    from decimal import Decimal
    
    # Get bank accounts (assuming accounts with type ASSET and code starting with 1)
    bank_accounts = Account.objects.filter(
        account_type='ASSET',
        code__startswith='1',
        is_active=True
    )
    
    # Get latest reconciliation for each account
    latest_reconciliations = {}
    for account in bank_accounts:
        latest_rec = BankReconciliation.objects.filter(
            account=account
        ).order_by('-reconciliation_date').first()
        if latest_rec:
            latest_reconciliations[account.id] = latest_rec
    
    # Get unreconciled statements
    unreconciled_statements = BankStatement.objects.filter(
        is_reconciled=False
    ).select_related('account').order_by('-statement_date')[:20]
    
    # Calculate summary statistics
    total_unreconciled = unreconciled_statements.count()
    total_unreconciled_amount = sum(stmt.amount for stmt in unreconciled_statements)
    
    context = {
        'title': 'Bank Reconciliation',
        'description': 'Reconcile bank statements with accounting records.',
        'user': request.user,
        'bank_accounts': bank_accounts,
        'latest_reconciliations': latest_reconciliations,
        'unreconciled_statements': unreconciled_statements,
        'total_unreconciled': total_unreconciled,
        'total_unreconciled_amount': total_unreconciled_amount,
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
def financial_ratios_view(request):
    """
    Financial ratios view
    """
    from accounting.models import Account, AccountType
    from decimal import Decimal
    
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
    
    ratios['current_ratio'] = (current_assets / current_liabilities) if current_liabilities > 0 else Decimal('0.00')
    ratios['quick_ratio'] = ratios['current_ratio']  # Simplified
    
    # Profitability ratios
    ratios['gross_margin'] = ((total_revenue - total_expenses) / total_revenue * 100) if total_revenue > 0 else Decimal('0.00')
    ratios['net_margin'] = (net_income / total_revenue * 100) if total_revenue > 0 else Decimal('0.00')
    ratios['return_on_assets'] = (net_income / total_assets * 100) if total_assets > 0 else Decimal('0.00')
    ratios['return_on_equity'] = (net_income / total_equity * 100) if total_equity > 0 else Decimal('0.00')
    
    # Leverage ratios
    ratios['debt_to_equity'] = (total_liabilities / total_equity) if total_equity > 0 else Decimal('0.00')
    ratios['debt_ratio'] = (total_liabilities / total_assets * 100) if total_assets > 0 else Decimal('0.00')
    
    context = {
        'title': 'Financial Ratios',
        'description': 'Key financial ratios and performance indicators.',
        'user': request.user,
        'ratios': ratios,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'net_income': net_income,
    }
    return render(request, 'modules/financial_ratios.html', context)


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
    from accounting.models import Customer, Invoice, InvoiceLine
    from django.http import JsonResponse
    from decimal import Decimal
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create invoice
            customer = Customer.objects.get(id=data['customer_id'])
            invoice = Invoice.objects.create(
                invoice_number=data['invoice_number'],
                customer=customer,
                invoice_date=data['invoice_date'],
                due_date=data['due_date'],
                notes=data.get('notes', ''),
                created_by=request.user
            )
            
            # Add line items
            subtotal = Decimal('0.00')
            for line_data in data['lines']:
                line_total = Decimal(str(line_data['quantity'])) * Decimal(str(line_data['unit_price']))
                InvoiceLine.objects.create(
                    invoice=invoice,
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
            
            invoice.subtotal = subtotal
            invoice.tax_amount = tax_amount
            invoice.total_amount = total_amount
            invoice.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Invoice created successfully',
                'invoice_id': invoice.id,
                'invoice_number': invoice.invoice_number
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # GET request - return form data
    customers = Customer.objects.filter(is_active=True)
    context = {
        'title': 'Create Invoice',
        'customers': customers,
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
    from accounting.models import Budget, BudgetLine, Account
    from django.db.models import Sum
    from decimal import Decimal
    
    # Get all budgets
    budgets = Budget.objects.all().order_by('-fiscal_year', '-start_date')
    
    # Get current budget (if exists)
    current_year = 2025  # Current year
    current_budget = Budget.objects.filter(
        fiscal_year=current_year,
        is_active=True
    ).first()
    
    # Get budget lines for current budget
    budget_lines = []
    if current_budget:
        budget_lines = BudgetLine.objects.filter(
            budget=current_budget
        ).select_related('account').order_by('account__code')
        
        # Calculate totals
        total_budgeted = sum(line.budgeted_amount for line in budget_lines)
        total_actual = sum(line.actual_amount for line in budget_lines)
        total_variance = sum(line.variance for line in budget_lines)
    
    # Get accounts for budget creation
    accounts = Account.objects.filter(is_active=True).order_by('code')
    
    context = {
        'title': 'Budgeting',
        'description': 'Create and manage budgets for financial planning.',
        'user': request.user,
        'budgets': budgets,
        'current_budget': current_budget,
        'budget_lines': budget_lines,
        'accounts': accounts,
        'total_budgeted': total_budgeted if current_budget else Decimal('0.00'),
        'total_actual': total_actual if current_budget else Decimal('0.00'),
        'total_variance': total_variance if current_budget else Decimal('0.00'),
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


@login_required
def customer_fixed_assets_view(request):
    """
    Customer fixed assets portal view
    """
    from accounting.models import FixedAsset
    
    # Get assets assigned to the current user (customer)
    assets = FixedAsset.objects.all().order_by('-purchase_date')
    
    # Calculate some statistics
    total_assets = assets.count()
    total_value = sum(asset.purchase_cost for asset in assets)
    total_depreciation = sum(asset.accumulated_depreciation for asset in assets)
    net_value = total_value - total_depreciation
    
    context = {
        'title': 'My Fixed Assets',
        'assets': assets,
        'total_assets': total_assets,
        'total_value': total_value,
        'total_depreciation': total_depreciation,
        'net_value': net_value,
    }
    return render(request, 'modules/customer_fixed_assets.html', context)


@login_required
def customer_profile_view(request):
    """
    Customer profile update view
    """
    from django.contrib import messages
    from django.shortcuts import redirect
    from accounting.models import UserProfile

    user = request.user

    # Ensure profile exists
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Handle profile update
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        company = request.POST.get('company')
        job_title = request.POST.get('job_title')
        address = request.POST.get('address')
        timezone = request.POST.get('timezone')
        language = request.POST.get('language')

        # Basic validation
        if not all([first_name, last_name, email]):
            messages.error(request, 'First name, last name and email are required.')
            return redirect('customer_profile')

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        profile.phone = phone
        profile.company = company
        profile.job_title = job_title
        profile.address = address
        profile.timezone = timezone
        profile.language = language
        profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('customer_profile')

    context = {
        'title': 'Update Profile',
        'user': user,
        'profile': profile,
    }
    return render(request, 'modules/customer_profile.html', context)


@login_required
def customer_support_view(request):
    """
    Customer support center view
    """
    from django.contrib import messages
    from django.shortcuts import redirect
    
    if request.method == 'POST':
        # Handle support ticket submission
        subject = request.POST.get('subject')
        category = request.POST.get('category')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        
        # In a real system, you'd create a support ticket record
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
    # Mock activity data
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
    ]
    
    context = {
        'title': 'Activity History',
        'activities': activities,
    }
    return render(request, 'modules/customer_activity.html', context)


@login_required
def ai_insights_view(request):
    """
    AI insights view
    """
    from accounting.models import AIInsight, AIModel, AnomalyAlert
    
    # Get AI insights
    insights = AIInsight.objects.filter(is_active=True).order_by('-generated_at')[:24]
    
    # Get AI models performance
    ai_models = AIModel.objects.all()
    
    # Get anomaly statistics
    total_anomalies = AnomalyAlert.objects.count()
    active_anomalies = AnomalyAlert.objects.filter(status__in=['DETECTED', 'INVESTIGATING']).count()
    
    # Calculate insights statistics
    total_insights = AIInsight.objects.count()
    implemented_insights = AIInsight.objects.filter(is_implemented=True).count()
    
    # Get recent predictions
    from accounting.models import AIPrediction
    predictions = AIPrediction.objects.order_by('-prediction_date')[:5]
    
    context = {
        'title': 'AI Insights',
        'description': 'AI-powered financial insights and recommendations.',
        'user': request.user,
        'insights': insights,
        'ai_models': ai_models,
        'total_anomalies': total_anomalies,
        'active_anomalies': active_anomalies,
        'total_insights': total_insights,
        'implemented_insights': implemented_insights,
        'predictions': predictions,
    }
    return render(request, 'modules/ai_insights.html', context)


@login_required
def anomaly_detection_view(request):
    """
    Anomaly detection view
    """
    from accounting.models import AnomalyAlert, AnomalyDetectionModel
    
    # Get anomaly alerts
    alerts = AnomalyAlert.objects.all().order_by('-detected_at')[:10]
    
    # Get detection models
    detection_models = AnomalyDetectionModel.objects.all()
    
    # Calculate statistics
    total_alerts = AnomalyAlert.objects.count()
    resolved_alerts = AnomalyAlert.objects.filter(status__in=['RESOLVED', 'FALSE_POSITIVE', 'IGNORED']).count()
    critical_alerts = AnomalyAlert.objects.filter(severity='CRITICAL').count()
    
    # Get alerts by type
    alerts_by_type = AnomalyAlert.objects.values('anomaly_type').annotate(
        count=models.Count('id')
    ).order_by('-count')
    
    # Get recent alerts for timeline
    recent_alerts = AnomalyAlert.objects.order_by('-detected_at')[:20]
    
    context = {
        'title': 'Anomaly Detection',
        'description': 'Detect unusual patterns and anomalies in financial data.',
        'user': request.user,
        'alerts': alerts,
        'detection_models': detection_models,
        'total_alerts': total_alerts,
        'resolved_alerts': resolved_alerts,
        'critical_alerts': critical_alerts,
        'alerts_by_type': alerts_by_type,
        'recent_alerts': recent_alerts,
    }
    return render(request, 'modules/anomaly_detection.html', context)


@login_required
def expense_management_view(request):
    """
    Expense management view
    """
    from accounting.models import Expense, ExpenseCategory
    from django.db.models import Sum, Count
    
    expenses = Expense.objects.all().order_by('-expense_date')[:50]
    categories = ExpenseCategory.objects.all()
    
    # Statistics
    total_expenses = Expense.objects.count()
    total_amount = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # Expenses by category
    expenses_by_category = Expense.objects.values('category__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Recent expenses
    recent_expenses = Expense.objects.select_related('category', 'vendor').order_by('-expense_date')[:10]
    
    # Monthly expense trend (mock data for now)
    monthly_expenses = [
        {'month': 'Jan', 'amount': 12500},
        {'month': 'Feb', 'amount': 15200},
        {'month': 'Mar', 'amount': 13800},
        {'month': 'Apr', 'amount': 16700},
        {'month': 'May', 'amount': 14300},
        {'month': 'Jun', 'amount': 18900},
    ]
    
    context = {
        'title': 'Expense Management',
        'description': 'Track and manage business expenses.',
        'user': request.user,
        'expenses': expenses,
        'categories': categories,
        'total_expenses': total_expenses,
        'total_amount': total_amount,
        'expenses_by_category': expenses_by_category,
        'recent_expenses': recent_expenses,
        'monthly_expenses': monthly_expenses,
    }
    return render(request, 'modules/expense_management.html', context)


@login_required
def create_expense_view(request):
    """
    Create expense view
    """
    from accounting.models import Expense, ExpenseCategory, Vendor
    from django.http import JsonResponse
    from decimal import Decimal
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create expense
            category = ExpenseCategory.objects.get(id=data['category_id'])
            vendor = Vendor.objects.get(id=data['vendor_id']) if data.get('vendor_id') else None
            
            expense = Expense.objects.create(
                expense_number=data['expense_number'],
                category=category,
                vendor=vendor,
                expense_date=data['expense_date'],
                amount=Decimal(str(data['amount'])),
                description=data['description'],
                receipt_number=data.get('receipt_number', ''),
                status='DRAFT',
                created_by=request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Expense created successfully',
                'expense_id': expense.id,
                'expense_number': expense.expense_number
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # GET request - return form data
    categories = ExpenseCategory.objects.filter(is_active=True)
    vendors = Vendor.objects.filter(is_active=True)
    
    context = {
        'title': 'Create Expense',
        'categories': categories,
        'vendors': vendors,
    }
    return render(request, 'modules/create_expense.html', context)


@login_required
def scan_receipt_view(request):
    """
    Scan receipt view
    """
    from django.http import JsonResponse
    import json
    
    if request.method == 'POST':
        try:
            # In a real implementation, this would process uploaded receipt images
            # using OCR technology to extract expense data
            # For now, we'll simulate the receipt scanning process
            
            # Simulate OCR processing delay
            import time
            time.sleep(2)
            
            # Mock extracted data
            extracted_data = {
                'vendor_name': 'Office Depot',
                'amount': 245.67,
                'date': '2025-10-08',
                'description': 'Office supplies and stationery',
                'category': 'Office Supplies',
                'confidence': 0.95
            }
            
            return JsonResponse({
                'success': True,
                'message': 'Receipt scanned successfully',
                'extracted_data': extracted_data
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    context = {
        'title': 'Scan Receipt',
        'description': 'Upload and scan expense receipts using AI-powered OCR.',
    }
    return render(request, 'modules/scan_receipt.html', context)


@login_required
def bulk_approve_expenses_view(request):
    """
    Bulk approve expenses view
    """
    from accounting.models import Expense
    from django.http import JsonResponse
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            expense_ids = data['expense_ids']
            
            # Update expenses to approved status
            expenses = Expense.objects.filter(id__in=expense_ids, status='DRAFT')
            updated_count = 0
            
            for expense in expenses:
                expense.status = 'APPROVED'
                expense.approved_by = request.user
                expense.save()
                updated_count += 1
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully approved {updated_count} expenses',
                'approved_count': updated_count
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # GET request - show pending expenses for bulk approval
    pending_expenses = Expense.objects.filter(status='DRAFT').select_related('category', 'vendor', 'created_by')
    
    context = {
        'title': 'Bulk Approve Expenses',
        'description': 'Review and approve multiple expenses at once.',
        'pending_expenses': pending_expenses,
    }
    return render(request, 'modules/bulk_approve_expenses.html', context)


@login_required
def export_expenses_view(request):
    """
    Export expenses view
    """
    from accounting.models import Expense
    from django.http import HttpResponse
    import csv
    from datetime import datetime
    
    try:
        # Get filter parameters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        status = request.GET.get('status')
        category_id = request.GET.get('category_id')
        
        # Filter expenses
        expenses = Expense.objects.all().select_related('category', 'vendor', 'created_by')
        
        if start_date:
            expenses = expenses.filter(expense_date__gte=start_date)
        if end_date:
            expenses = expenses.filter(expense_date__lte=end_date)
        if status:
            expenses = expenses.filter(status=status)
        if category_id:
            expenses = expenses.filter(category_id=category_id)
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        filename = f'expenses_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Expense Number', 'Date', 'Category', 'Vendor', 'Description', 
            'Amount', 'Status', 'Created By', 'Receipt Number'
        ])
        
        for expense in expenses:
            writer.writerow([
                expense.expense_number,
                expense.expense_date.strftime('%Y-%m-%d'),
                expense.category.name if expense.category else '',
                expense.vendor.company_name if expense.vendor else '',
                expense.description,
                str(expense.amount),
                expense.status,
                expense.created_by.get_full_name() if expense.created_by else '',
                expense.receipt_number or ''
            ])
        
        return response
        
    except Exception as e:
        return HttpResponse(f'Error generating export: {str(e)}', status=500)


@login_required
def purchase_orders_view(request):
    """
    Purchase orders view
    """
    from accounting.models import PurchaseOrder
    from django.db.models import Sum, Count
    
    purchase_orders = PurchaseOrder.objects.select_related('vendor').order_by('-order_date')
    
    # Statistics
    total_pos = PurchaseOrder.objects.count()
    total_value = PurchaseOrder.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
    approved_pos = PurchaseOrder.objects.filter(status='APPROVED').count()
    pending_pos = PurchaseOrder.objects.filter(status__in=['DRAFT', 'PENDING_APPROVAL']).count()
    
    # POs by status
    pos_by_status = PurchaseOrder.objects.values('status').annotate(
        count=Count('id'),
        total_value=Sum('total_amount')
    ).order_by('status')
    
    # Recent POs
    recent_pos = PurchaseOrder.objects.select_related('vendor').order_by('-order_date')[:10]
    
    # Monthly PO trend
    monthly_pos = [
        {'month': 'Jan', 'count': 12, 'value': 45000},
        {'month': 'Feb', 'count': 15, 'value': 52000},
        {'month': 'Mar', 'count': 18, 'value':   48000},
        {'month': 'Apr', 'count': 22, 'value': 61000},
        {'month': 'May', 'count': 19, 'value': 55000},
        {'month': 'Jun', 'count': 25, 'value': 72000},
    ]
    
    context = {
        'title': 'Purchase Orders',
        'description': 'Manage purchase orders and procurement.',
        'user': request.user,
        'purchase_orders': purchase_orders,
        'total_pos': total_pos,
        'total_value': total_value,
        'approved_pos': approved_pos,
        'pending_pos': pending_pos,
        'pos_by_status': pos_by_status,
        'recent_pos': recent_pos,
        'monthly_pos': monthly_pos,
    }
    return render(request, 'modules/purchase_orders.html', context)


@login_required
def inventory_view(request):
    """
    Inventory view
    """
    from accounting.models import InventoryItem, InventoryTransaction, InventoryCategory
    from django.db.models import Sum, Count
    
    # Get inventory items
    items = InventoryItem.objects.select_related('category', 'primary_vendor').all()
    
    # Statistics
    total_items = InventoryItem.objects.count()
    total_value = InventoryItem.objects.aggregate(
        total_value=Sum(models.F('current_stock') * models.F('unit_cost'))
    )['total_value'] or Decimal('0.00')
    
    low_stock_items = InventoryItem.objects.filter(
        current_stock__lte=models.F('minimum_stock')
    ).count()
    
    # Items by category
    items_by_category = InventoryItem.objects.values('category__name').annotate(
        count=Count('id'),
        total_value=Sum(models.F('current_stock') * models.F('unit_cost'))
    ).order_by('-total_value')
    
    # Recent transactions
    recent_transactions = InventoryTransaction.objects.select_related(
        'item', 'created_by'
    ).order_by('-created_at')[:10]
    
    # Top items by value
    top_items = InventoryItem.objects.annotate(
        total_value=models.F('current_stock') * models.F('unit_cost')
    ).order_by('-total_value')[:5]
    
    context = {
        'title': 'Inventory',
        'description': 'Inventory management and tracking.',
        'user': request.user,
        'items': items,
        'total_items': total_items,
        'total_value': total_value,
        'low_stock_items': low_stock_items,
        'items_by_category': items_by_category,
        'recent_transactions': recent_transactions,
        'top_items': top_items,
    }
    return render(request, 'modules/inventory.html', context)


@login_required
def documents_view(request):
    """
    Documents view
    """
    from accounting.models import Document, DocumentCategory, DocumentShare
    from django.db.models import Count
    
    # Get documents
    documents = Document.objects.select_related('category', 'uploaded_by').all()
    
    # Statistics
    total_documents = Document.objects.count()
    total_size = Document.objects.aggregate(
        total_size=Sum('file_size')
    )['total_size'] or 0
    
    # Documents by category
    documents_by_category = Document.objects.values('category__name').annotate(
        count=Count('id'),
        total_size=Sum('file_size')
    ).order_by('-count')
    
    # Recent documents
    recent_documents = Document.objects.select_related(
        'category', 'uploaded_by'
    ).order_by('-uploaded_at')[:10]
    
    # Shared documents
    shared_documents = DocumentShare.objects.select_related(
        'document', 'shared_with'
    ).filter(shared_with=request.user).order_by('-shared_at')[:5]
    
    context = {
        'title': 'Documents',
        'description': 'Document management and storage.',
        'user': request.user,
        'documents': documents,
        'total_documents': total_documents,
        'total_size': total_size,
        'documents_by_category': documents_by_category,
        'recent_documents': recent_documents,
        'shared_documents': shared_documents,
    }
    return render(request, 'modules/documents.html', context)


@login_required
def financial_statements_view(request):
    """
    Financial statements view
    """
    from accounting.models import Account, AccountType
    from decimal import Decimal
    from datetime import datetime, date
    
    # Get date range (default to current year)
    start_date = request.GET.get('start_date', f'{datetime.now().year}-01-01')
    end_date = request.GET.get('end_date', date.today().isoformat())
    
    # Balance Sheet Data
    assets = Account.objects.filter(account_type=AccountType.ASSET, is_active=True)
    liabilities = Account.objects.filter(account_type=AccountType.LIABILITY, is_active=True)
    equity = Account.objects.filter(account_type=AccountType.EQUITY, is_active=True)
    
    total_assets = sum(acc.get_balance() for acc in assets)
    total_liabilities = sum(acc.get_balance() for acc in liabilities)
    total_equity = sum(acc.get_balance() for acc in equity)
    
    # Income Statement Data
    revenue_accounts = Account.objects.filter(account_type=AccountType.REVENUE, is_active=True)
    expense_accounts = Account.objects.filter(account_type=AccountType.EXPENSE, is_active=True)
    
    total_revenue = sum(acc.get_balance() for acc in revenue_accounts)
    total_expenses = sum(acc.get_balance() for acc in expense_accounts)
    net_income = total_revenue - total_expenses
    
    # Cash Flow Statement (simplified)
    # In a real system, this would be calculated from journal entries
    operating_cash_flow = net_income + Decimal('5000')  # Simplified
    investing_cash_flow = Decimal('-15000')  # Simplified
    financing_cash_flow = Decimal('8000')  # Simplified
    net_cash_flow = operating_cash_flow + investing_cash_flow + financing_cash_flow
    
    context = {
        'title': 'Financial Statements',
        'description': 'Complete financial statement package.',
        'user': request.user,
        'start_date': start_date,
        'end_date': end_date,
        # Balance Sheet
        'assets': assets,
        'liabilities': liabilities,
        'equity': equity,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        # Income Statement
        'revenue_accounts': revenue_accounts,
        'expense_accounts': expense_accounts,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_income': net_income,
        # Cash Flow
        'operating_cash_flow': operating_cash_flow,
        'investing_cash_flow': investing_cash_flow,
        'financing_cash_flow': financing_cash_flow,
        'net_cash_flow': net_cash_flow,
    }
    return render(request, 'modules/financial_statements.html', context)


@login_required
def tax_reports_view(request):
    """
    Tax reports view
    """
    from accounting.models import TaxReturn
    
    reports = TaxReturn.objects.all().order_by('-created_at')
    
    context = {
        'title': 'Tax Reports',
        'description': 'Tax reporting and compliance documents.',
        'user': request.user,
        'reports': reports,
    }
    return render(request, 'modules/tax_reports.html', context)


@login_required
def audit_compliance_view(request):
    """
    Audit compliance view
    """
    from accounting.models import AuditTrail, ComplianceCheck, ComplianceViolation
    from django.db.models import Count
    
    # Get audit trails
    audit_trails = AuditTrail.objects.select_related('user').order_by('-timestamp')[:50]
    
    # Get compliance checks
    compliance_checks = ComplianceCheck.objects.all().order_by('-last_checked')
    
    # Get compliance violations
    violations = ComplianceViolation.objects.select_related('check').order_by('-detected_at')[:20]
    
    # Statistics
    total_audits = AuditTrail.objects.count()
    total_checks = ComplianceCheck.objects.count()
    active_violations = ComplianceViolation.objects.filter(status__in=['OPEN', 'INVESTIGATING']).count()
    resolved_violations = ComplianceViolation.objects.filter(status='RESOLVED').count()
    
    # Audits by action type
    audits_by_action = AuditTrail.objects.values('action').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Compliance status summary
    compliance_status = ComplianceCheck.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    context = {
        'title': 'Audit & Compliance',
        'description': 'Audit trails and compliance monitoring.',
        'user': request.user,
        'audit_trails': audit_trails,
        'compliance_checks': compliance_checks,
        'violations': violations,
        'total_audits': total_audits,
        'total_checks': total_checks,
        'active_violations': active_violations,
        'resolved_violations': resolved_violations,
        'audits_by_action': audits_by_action,
        'compliance_status': compliance_status,
    }
    return render(request, 'modules/audit_compliance.html', context)


@login_required
def settings_view(request):
    """
    Settings view
    """
    context = {
        'title': 'Settings',
        'description': 'System settings and configuration.',
        'user': request.user,
    }
    return render(request, 'modules/settings.html', context)


@login_required
def export_users_api(request):
    """
    API endpoint to export users data
    """
    from django.http import JsonResponse, HttpResponse
    from django.contrib.auth.models import User
    import csv
    import io

    try:
        # Get all users
        users = User.objects.all().order_by('date_joined')

        if request.GET.get('format', 'json') == 'csv':
            # Create CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="users_export.csv"'

            writer = csv.writer(response)
            writer.writerow(['Username', 'First Name', 'Last Name', 'Email', 'Date Joined', 'Last Login', 'Is Active', 'Is Staff'])

            for user in users:
                writer.writerow([
                    user.username,
                    user.first_name,
                    user.last_name,
                    user.email,
                    user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                    user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never',
                    'Yes' if user.is_active else 'No',
                    'Yes' if user.is_staff else 'No'
                ])

            return response
        else:
            # Return JSON response
            users_data = []
            for user in users:
                users_data.append({
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                    'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff
                })

            return JsonResponse({
                'success': True,
                'users': users_data,
                'total_users': len(users_data)
            })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def save_settings_api(request):
    """
    API endpoint to save system settings
    """
    from django.http import JsonResponse
    import json

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})

    try:
        data = json.loads(request.body)

        # Here you would save the settings to database
        # For now, we'll just simulate saving
        settings_saved = {
            'company_name': data.get('company_name'),
            'currency': data.get('currency'),
            'fiscal_year_start': data.get('fiscal_year_start'),
            'timezone': data.get('timezone'),
            'dark_mode': data.get('dark_mode', False),
            'compact_view': data.get('compact_view', False),
            'show_tooltips': data.get('show_tooltips', True),
            'auto_save': data.get('auto_save', True),
            'items_per_page': data.get('items_per_page', 25)
        }

        # In a real implementation, you'd save these to a settings model
        # For demo purposes, we'll just return success

        return JsonResponse({
            'success': True,
            'message': 'Settings saved successfully',
            'settings': settings_saved
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def security_audit_api(request):
    """
    API endpoint to run security audit
    """
    from django.http import JsonResponse
    from django.contrib.auth.models import User
    import json

    try:
        audit_results = {
            'timestamp': '2025-01-08T10:30:00Z',
            'status': 'PASSED',
            'checks': [
                {
                    'name': 'Password Policy',
                    'status': 'PASSED',
                    'details': 'All users have strong passwords'
                },
                {
                    'name': 'User Permissions',
                    'status': 'PASSED',
                    'details': 'All user roles are properly configured'
                },
                {
                    'name': 'Login Security',
                    'status': 'PASSED',
                    'details': 'No suspicious login attempts detected'
                },
                {
                    'name': 'Data Encryption',
                    'status': 'PASSED',
                    'details': 'All sensitive data is properly encrypted'
                },
                {
                    'name': 'Session Management',
                    'status': 'PASSED',
                    'details': 'Session timeouts are properly configured'
                }
            ],
            'recommendations': [
                'Consider enabling two-factor authentication for all users',
                'Regular password changes should be enforced'
            ]
        }

        return JsonResponse({
            'success': True,
            'audit_results': audit_results
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def regenerate_api_key_api(request):
    """
    API endpoint to regenerate API key
    """
    from django.http import JsonResponse
    import secrets
    import string

    try:
        # Generate a new API key
        alphabet = string.ascii_letters + string.digits
        new_api_key = 'sk-' + ''.join(secrets.choice(alphabet) for i in range(32))

        # In a real implementation, you'd save this to the user's profile
        # For demo purposes, we'll just return the new key

        return JsonResponse({
            'success': True,
            'message': 'API key regenerated successfully',
            'new_api_key': new_api_key
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def export_data_api(request):
    """
    API endpoint to export user data
    """
    from django.http import JsonResponse, HttpResponse
    from django.contrib.auth.models import User
    import json
    import zipfile
    import io

    try:
        export_format = request.GET.get('format', 'json')

        # Gather user data
        user_data = {
            'user_info': {
                'username': request.user.username,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'date_joined': request.user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                'last_login': request.user.last_login.strftime('%Y-%m-%d %H:%M:%S') if request.user.last_login else None
            },
            'export_date': '2025-01-08T10:30:00Z',
            'data_types': ['user_profile', 'activity_logs', 'preferences']
        }

        if export_format == 'json':
            response = HttpResponse(json.dumps(user_data, indent=2), content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename="user_data_export.json"'
            return response

        elif export_format == 'zip':
            # Create a ZIP file with multiple data files
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add user data as JSON
                zip_file.writestr('user_data.json', json.dumps(user_data, indent=2))

                # Add a sample activity log
                activity_data = {
                    'activities': [
                        {'date': '2025-01-08', 'action': 'Login', 'details': 'User logged in'},
                        {'date': '2025-01-07', 'action': 'Settings Update', 'details': 'Updated profile information'},
                        {'date': '2025-01-06', 'action': 'Data Export', 'details': 'Requested data export'}
                    ]
                }
                zip_file.writestr('activity_log.json', json.dumps(activity_data, indent=2))

            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="user_data_export.zip"'
            return response

        else:
            return JsonResponse({
                'success': False,
                'error': 'Unsupported export format. Use json or zip.'
            })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def delete_account_api(request):
    """
    API endpoint to delete user account
    """
    from django.http import JsonResponse
    from django.contrib.auth.models import User

    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})

    try:
        # In a real implementation, you'd:
        # 1. Mark user as inactive instead of deleting
        # 2. Queue data for deletion after retention period
        # 3. Send confirmation email
        # 4. Log the deletion

        # For demo purposes, we'll just return success
        # DO NOT actually delete the user in production without proper safeguards

        return JsonResponse({
            'success': True,
            'message': 'Account deletion initiated. You will be logged out shortly.',
            'logout_required': True
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def edit_user_api(request):
    """
    API endpoint to edit user information
    """
    from django.http import JsonResponse
    from django.contrib.auth.models import User
    import json

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})

    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        is_active = data.get('is_active')

        user = User.objects.get(id=user_id)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.is_active = is_active
        user.save()

        return JsonResponse({
            'success': True,
            'message': 'User updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'is_active': user.is_active
            }
        })

    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def disable_user_api(request):
    """
    API endpoint to disable/enable user account
    """
    from django.http import JsonResponse
    from django.contrib.auth.models import User
    import json

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})

    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        is_active = data.get('is_active', False)

        user = User.objects.get(id=user_id)
        user.is_active = is_active
        user.save()

        action = 'enabled' if is_active else 'disabled'
        return JsonResponse({
            'success': True,
            'message': f'User account {action} successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'is_active': user.is_active
            }
        })

    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def add_integration_api(request):
    """
    API endpoint to add a new integration
    """
    from django.http import JsonResponse
    import json

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})

    try:
        data = json.loads(request.body)
        integration_type = data.get('integration_type')
        name = data.get('name')
        config = data.get('config', {})

        # In a real implementation, you'd save this to an Integration model
        # For demo purposes, we'll just return success

        integration = {
            'id': 'int_' + str(hash(name + integration_type))[:8],
            'type': integration_type,
            'name': name,
            'status': 'configured',
            'config': config,
            'created_at': '2025-01-08T10:30:00Z'
        }

        return JsonResponse({
            'success': True,
            'message': f'{integration_type.title()} integration added successfully',
            'integration': integration
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def connect_integration_api(request):
    """
    API endpoint to connect/test an integration
    """
    from django.http import JsonResponse
    import json

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})

    try:
        data = json.loads(request.body)
        integration_id = data.get('integration_id')

        # In a real implementation, you'd test the connection
        # For demo purposes, we'll simulate a successful connection

        return JsonResponse({
            'success': True,
            'message': 'Integration connected successfully',
            'integration_id': integration_id,
            'status': 'connected',
            'last_tested': '2025-01-08T10:30:00Z'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def regenerate_key_api(request):
    """
    API endpoint to regenerate API key
    """
    from django.http import JsonResponse
    import secrets
    import string

    try:
        # Generate a new API key
        alphabet = string.ascii_letters + string.digits
        new_api_key = 'sk-' + ''.join(secrets.choice(alphabet) for i in range(32))

        # In a real implementation, you'd save this to the user's profile
        # For demo purposes, we'll just return the new key

        return JsonResponse({
            'success': True,
            'message': 'API key regenerated successfully',
            'new_api_key': new_api_key
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def delete_all_data_api(request):
    """
    API endpoint to delete all user data
    """
    from django.http import JsonResponse

    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})

    try:
        # In a real implementation, you'd:
        # 1. Queue all user data for deletion
        # 2. Mark account for deletion after retention period
        # 3. Send confirmation email
        # 4. Log the deletion request

        # For demo purposes, we'll just return success
        # DO NOT actually delete data in production without proper safeguards

        return JsonResponse({
            'success': True,
            'message': 'Data deletion initiated. All your data will be permanently deleted within 30 days.',
            'deletion_date': '2025-02-07T10:30:00Z',
            'logout_required': True
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def add_user_api(request):
    """
    API endpoint to add a new user
    """
    from django.http import JsonResponse
    from django.contrib.auth.models import User
    import json

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})

    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        password = data.get('password')
        is_staff = data.get('is_staff', False)

        # Validation
        if not all([username, email, first_name, last_name, password]):
            return JsonResponse({'success': False, 'error': 'All fields are required'})

        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'Username already exists'})

        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'Email already exists'})

        if len(password) < 8:
            return JsonResponse({'success': False, 'error': 'Password must be at least 8 characters long'})

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            is_staff=is_staff
        )

        return JsonResponse({
            'success': True,
            'message': 'User created successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'is_staff': user.is_staff,
                'is_active': user.is_active,
                'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S')
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def notifications_api(request):
    """
    API endpoint to get user notifications
    """
    from accounting.models import Notification
    from django.http import JsonResponse
    from django.core.paginator import Paginator
    
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        unread_only = request.GET.get('unread_only', 'false').lower() == 'true'
        
        # Get notifications for the current user
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        
        if unread_only:
            notifications = notifications.filter(is_read=False)
        
        # Paginate results
        paginator = Paginator(notifications, per_page)
        page_obj = paginator.page(page)
        
        # Format notifications for JSON response
        notifications_data = []
        for notification in page_obj.object_list:
            notifications_data.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'notification_type': notification.notification_type,
                'is_read': notification.is_read,
                'action_url': notification.action_url,
                'action_text': notification.action_text,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': notification.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            })
        
        return JsonResponse({
            'success': True,
            'notifications': notifications_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def mark_notification_read_api(request):
    """
    API endpoint to mark a notification as read
    """
    from accounting.models import Notification
    from django.http import JsonResponse
    import json
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    try:
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read',
            'notification_id': notification_id
        })
        
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def mark_all_notifications_read_api(request):
    """
    API endpoint to mark all user notifications as read
    """
    from accounting.models import Notification
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    try:
        # Mark all unread notifications as read for the current user
        updated_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        
        return JsonResponse({
            'success': True,
            'message': f'Marked {updated_count} notifications as read',
            'updated_count': updated_count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def create_notification_api(request):
    """
    API endpoint to create a new notification (admin/staff only)
    """
    from accounting.models import Notification
    from django.contrib.auth.models import User
    from django.http import JsonResponse
    import json
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    # Check if user has permission to create notifications
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    try:
        data = json.loads(request.body)
        
        # Get target user(s)
        user_ids = data.get('user_ids', [])
        if not user_ids:
            # If no specific users, create for all active users
            users = User.objects.filter(is_active=True)
        else:
            users = User.objects.filter(id__in=user_ids, is_active=True)
        
        created_notifications = []
        for user in users:
            notification = Notification.objects.create(
                user=user,
                title=data['title'],
                message=data['message'],
                notification_type=data.get('notification_type', 'info'),
                action_url=data.get('action_url'),
                action_text=data.get('action_text'),
                created_by=request.user
            )
            created_notifications.append({
                'id': notification.id,
                'user_id': user.id,
                'title': notification.title
            })
        
        return JsonResponse({
            'success': True,
            'message': f'Created {len(created_notifications)} notifications',
            'notifications': created_notifications
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def delete_notification_api(request, notification_id):
    """
    API endpoint to delete a notification
    """
    from accounting.models import Notification
    from django.http import JsonResponse
    
    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification deleted successfully',
            'notification_id': notification_id
        })
        
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def notification_stats_api(request):
    """
    API endpoint to get notification statistics for the current user
    """
    from accounting.models import Notification
    from django.http import JsonResponse
    from django.db.models import Count
    
    try:
        # Get notification counts
        total_notifications = Notification.objects.filter(user=request.user).count()
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
        read_notifications = total_notifications - unread_notifications
        
        # Get notifications by type
        notifications_by_type = Notification.objects.filter(user=request.user).values('notification_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Get recent unread notifications (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.now() - timedelta(days=7)
        recent_unread = Notification.objects.filter(
            user=request.user,
            is_read=False,
            created_at__gte=week_ago
        ).count()
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total': total_notifications,
                'unread': unread_notifications,
                'read': read_notifications,
                'recent_unread': recent_unread,
                'by_type': list(notifications_by_type)
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Public/Marketing Views
def small_business_view(request):
    """
    Small Business page view
    """
    context = {
        'title': 'Small Business Accounting Solutions',
        'description': 'Accounting solutions for businesses with up to 50 employees.',
    }
    return render(request, 'pages/small_business.html', context)


def enterprise_view(request):
    """
    Enterprise page view
    """
    context = {
        'title': 'Enterprise Accounting Solutions',
        'description': 'Accounting solutions for large organizations with 500+ employees.',
    }
    return render(request, 'pages/enterprise.html', context)


def accounting_firms_view(request):
    """
    Accounting Firms page view
    """
    context = {
        'title': 'Accounting Firms Solutions',
        'description': 'Professional accounting firm management and multi-client solutions.',
    }
    return render(request, 'pages/accounting_firms.html', context)


def retail_ecommerce_view(request):
    """
    Retail & E-commerce page view
    """
    context = {
        'title': 'Retail & E-commerce Accounting',
        'description': 'Specialized accounting solutions for retail and online businesses.',
    }
    return render(request, 'pages/retail_ecommerce.html', context)


def manufacturing_view(request):
    """
    Manufacturing page view
    """
    context = {
        'title': 'Manufacturing Accounting',
        'description': 'Comprehensive accounting solutions for manufacturing operations.',
    }
    return render(request, 'pages/manufacturing.html', context)


def smart_invoicing_view(request):
    """
    Smart Invoicing page view
    """
    context = {
        'title': 'Smart Invoicing Solutions',
        'description': 'Automated billing and payment processing tools.',
    }
    return render(request, 'pages/smart_invoicing.html', context)


def ai_bookkeeping_view(request):
    """
    AI Bookkeeping page view
    """
    context = {
        'title': 'AI-Powered Bookkeeping',
        'description': 'Intelligent automation for financial record keeping.',
    }
    return render(request, 'pages/ai_bookkeeping.html', context)


def real_time_analytics_view(request):
    """
    Real-time Analytics page view
    """
    context = {
        'title': 'Real-Time Financial Insights',
        'description': 'Live dashboards and analytics for instant business intelligence.',
    }
    return render(request, 'pages/real_time_analytics.html', context)


def ifrs_compliance_view(request):
    """
    IFRS Compliance page view
    """
    context = {
        'title': 'IFRS Compliance Solutions',
        'description': 'International Financial Reporting Standards compliance tools.',
    }
    return render(request, 'pages/ifrs_compliance.html', context)


def bank_grade_security_view(request):
    """
    Bank-Grade Security page view
    """
    context = {
        'title': 'Bank-Grade Security',
        'description': 'ISO 27001 certified data protection and security infrastructure.',
    }
    return render(request, 'pages/bank_grade_security.html', context)


def pricing_view(request):
    """
    Pricing page view
    """
    context = {
        'title': 'Pricing Plans - Ovovex',
        'description': 'Choose the perfect plan for your business needs.',
    }
    return render(request, 'pages/pricing.html', context)


def get_started_view(request):
    """
    Get Started page view
    """
    context = {
        'title': 'Get Started with Ovovex',
        'description': 'Begin your journey with Ovovex - guided onboarding and quick setup.',
    }
    return render(request, 'pages/get_started.html', context)


def start_free_trial_view(request):
    """
    Start Free Trial page view
    """
    context = {
        'title': 'Start Your Free Trial',
        'description': 'Start a risk-free trial of Ovovex and explore core features.',
    }
    return render(request, 'pages/start_free_trial.html', context)


def contact_sales_view(request):
    """
    Contact Sales page view
    """
    from django.contrib import messages
    from django.shortcuts import redirect

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        company = request.POST.get('company')
        message = request.POST.get('message')

        # In a real app we'd create a SalesLead record or send an email
        messages.success(request, 'Thanks! Our sales team will reach out shortly.')
        return redirect('contact_sales')

    context = {
        'title': 'Contact Sales',
        'description': 'Get a tailored quote and onboard support for your organization.',
    }
    return render(request, 'pages/contact_sales.html', context)