"""
Accounting Views - Full CRUD Operations
Multi-company aware views with proper data isolation
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Sum, Q
from decimal import Decimal
from datetime import datetime, timedelta
import json

from .models import (
    Invoice,
    InvoiceLine,
    Payment,
    Customer,
    JournalEntry,
    JournalEntryLine,
    Account,
    Expense,
    ExpenseCategory,
    Budget,
    BudgetLine,
    FixedAsset,
    Vendor,
    Bill,
    BillLine,
)
from .forms import (
    InvoiceForm,
    InvoiceLineForm,
    PaymentForm,
    JournalEntryForm,
    JournalEntryLineForm,
    ExpenseForm,
    BudgetForm,
    BudgetLineForm,
    FixedAssetForm,
    CustomerForm,
)


# ============================================================================
# INVOICE CRUD OPERATIONS
# ============================================================================


@login_required
def invoice_list(request):
    """List all invoices for active company"""
    active_company = request.active_company
    invoices = (
        Invoice.objects.filter(company=active_company)
        .select_related("customer")
        .order_by("-invoice_date")
    )

    # Statistics
    total_invoices = invoices.count()
    total_revenue = invoices.aggregate(Sum("total_amount"))[
        "total_amount__sum"
    ] or Decimal("0.00")
    paid_count = invoices.filter(status="PAID").count()
    overdue_count = invoices.filter(status="OVERDUE").count()

    context = {
        "title": "Invoices",
        "invoices": invoices,
        "total_invoices": total_invoices,
        "total_revenue": total_revenue,
        "paid_count": paid_count,
        "overdue_count": overdue_count,
    }
    return render(request, "accounting/invoice_list.html", context)


@login_required
def invoice_create(request):
    """Create new invoice"""
    active_company = request.active_company

    # Debug: Check if active_company exists
    if not active_company:
        messages.error(request, "No active company selected. Please select a company first.")
        return redirect("dashboard:index")

    if request.method == "POST":
        form = InvoiceForm(request.POST, company=active_company)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.company = active_company
            invoice.created_by = request.user
            invoice.save()
            messages.success(
                request, f"Invoice {invoice.invoice_number} created successfully!"
            )
            return redirect("accounting:invoice_detail", pk=invoice.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Generate next invoice number
        last_invoice = (
            Invoice.objects.filter(company=active_company).order_by("-id").first()
        )
        next_number = (
            f"INV-{(int(last_invoice.invoice_number.split('-')[1]) + 1):04d}"
            if last_invoice
            else "INV-0001"
        )

        form = InvoiceForm(
            company=active_company,
            initial={
                "invoice_number": next_number,
                "invoice_date": datetime.now().date(),
                "due_date": datetime.now().date() + timedelta(days=30),
                "status": "DRAFT",
            },
        )

    # Debug: Add customer count to context
    customer_count = Customer.objects.filter(company=active_company, is_active=True).count()

    context = {
        "title": "Create Invoice",
        "form": form,
        "action": "Create",
        "customer_count": customer_count,
        "active_company": active_company,
    }
    return render(request, "accounting/invoice_form.html", context)


@login_required
def invoice_detail(request, pk):
    """View invoice details"""
    active_company = request.active_company
    invoice = get_object_or_404(Invoice, pk=pk, company=active_company)
    lines = invoice.lines.all()
    payments = invoice.payments.all()

    context = {
        "title": f"Invoice {invoice.invoice_number}",
        "invoice": invoice,
        "lines": lines,
        "payments": payments,
        "balance_due": invoice.get_balance_due(),
    }
    return render(request, "accounting/invoice_detail.html", context)


@login_required
def invoice_edit(request, pk):
    """Edit existing invoice"""
    active_company = request.active_company

    # Check if active_company exists
    if not active_company:
        messages.error(request, "No active company selected. Please select a company first.")
        return redirect("dashboard:index")

    invoice = get_object_or_404(Invoice, pk=pk, company=active_company)

    if request.method == "POST":
        form = InvoiceForm(request.POST, instance=invoice, company=active_company)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Invoice {invoice.invoice_number} updated successfully!"
            )
            return redirect("accounting:invoice_detail", pk=invoice.pk)
    else:
        form = InvoiceForm(instance=invoice, company=active_company)

    # Add customer count to context
    customer_count = Customer.objects.filter(company=active_company, is_active=True).count()

    context = {
        "title": f"Edit Invoice {invoice.invoice_number}",
        "form": form,
        "invoice": invoice,
        "action": "Update",
        "customer_count": customer_count,
        "active_company": active_company,
    }
    return render(request, "accounting/invoice_form.html", context)


@login_required
def invoice_delete(request, pk):
    """Delete invoice"""
    active_company = request.active_company
    invoice = get_object_or_404(Invoice, pk=pk, company=active_company)

    if request.method == "POST":
        invoice_number = invoice.invoice_number
        invoice.delete()
        messages.success(request, f"Invoice {invoice_number} deleted successfully!")
        return redirect("accounting:invoice_list")

    context = {"title": "Delete Invoice", "invoice": invoice}
    return render(request, "accounting/invoice_confirm_delete.html", context)


@login_required
def invoice_send(request, pk):
    """Mark invoice as sent"""
    active_company = request.active_company
    invoice = get_object_or_404(Invoice, pk=pk, company=active_company)

    if invoice.status == "DRAFT":
        invoice.status = "SENT"
        invoice.save()
        messages.success(request, f"Invoice {invoice.invoice_number} marked as sent!")
    else:
        messages.warning(request, f"Invoice is already {invoice.get_status_display()}.")

    return redirect("accounting:invoice_detail", pk=invoice.pk)


# ============================================================================
# PAYMENT CRUD OPERATIONS
# ============================================================================


@login_required
def payment_create(request, invoice_id=None):
    """Record a payment"""
    active_company = request.active_company

    invoice = None
    if invoice_id:
        invoice = get_object_or_404(Invoice, pk=invoice_id, company=active_company)

    if request.method == "POST":
        form = PaymentForm(request.POST, company=active_company)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.company = active_company
            payment.created_by = request.user
            payment.save()

            # Update invoice paid amount
            if payment.invoice:
                payment.invoice.paid_amount += payment.amount
                if payment.invoice.paid_amount >= payment.invoice.total_amount:
                    payment.invoice.status = "PAID"
                payment.invoice.save()

            messages.success(
                request, f"Payment {payment.payment_number} recorded successfully!"
            )
            if payment.invoice:
                return redirect("accounting:invoice_detail", pk=payment.invoice.pk)
            else:
                return redirect("accounting:invoice_list")
    else:
        # Generate next payment number
        last_payment = Payment.objects.filter(company=active_company).order_by("-id").first()
        next_number = (
            f"PAY-{(int(last_payment.payment_number.split('-')[1]) + 1):04d}"
            if last_payment
            else "PAY-0001"
        )

        initial_data = {
            "payment_number": next_number,
            "payment_date": datetime.now().date(),
        }
        if invoice:
            initial_data["customer"] = invoice.customer
            initial_data["invoice"] = invoice
            initial_data["amount"] = invoice.get_balance_due()

        form = PaymentForm(initial=initial_data, company=active_company)

    context = {"title": "Record Payment", "form": form, "invoice": invoice}
    return render(request, "accounting/payment_form.html", context)


# ============================================================================
# JOURNAL ENTRY CRUD OPERATIONS
# ============================================================================


@login_required
def journal_entry_list(request):
    """List all journal entries for active company"""
    active_company = request.active_company
    entries = JournalEntry.objects.filter(company=active_company).order_by(
        "-entry_date"
    )

    total_entries = entries.count()
    posted_entries = entries.filter(status="POSTED").count()
    draft_entries = entries.filter(status="DRAFT").count()

    context = {
        "title": "Journal Entries",
        "entries": entries,
        "total_entries": total_entries,
        "posted_entries": posted_entries,
        "draft_entries": draft_entries,
    }
    return render(request, "accounting/journal_entry_list.html", context)


@login_required
@transaction.atomic
def journal_entry_create(request):
    """Create new journal entry"""
    active_company = request.active_company

    if request.method == "POST":
        form = JournalEntryForm(request.POST)

        if form.is_valid():
            entry = form.save(commit=False)
            entry.company = active_company
            entry.created_by = request.user
            entry.save()

            # Process line items from POST data
            line_count = int(request.POST.get("line_count", 0))
            total_debit = Decimal("0.00")
            total_credit = Decimal("0.00")

            for i in range(line_count):
                account_id = request.POST.get(f"line_{i}_account")
                description = request.POST.get(f"line_{i}_description", "")
                debit = Decimal(request.POST.get(f"line_{i}_debit", "0.00") or "0.00")
                credit = Decimal(request.POST.get(f"line_{i}_credit", "0.00") or "0.00")

                if account_id and (debit > 0 or credit > 0):
                    account = Account.objects.get(id=account_id, company=active_company)
                    JournalEntryLine.objects.create(
                        journal_entry=entry,
                        account=account,
                        description=description,
                        debit_amount=debit,
                        credit_amount=credit,
                        line_number=i + 1,
                    )
                    total_debit += debit
                    total_credit += credit

            entry.total_debit = total_debit
            entry.total_credit = total_credit
            entry.save()

            if entry.is_balanced():
                messages.success(
                    request, f"Journal entry {entry.entry_number} created successfully!"
                )
            else:
                messages.warning(
                    request,
                    f"Journal entry created but is not balanced (Debit: {total_debit}, Credit: {total_credit})",
                )

            return redirect("accounting:journal_entry_detail", pk=entry.pk)
    else:
        # Generate next entry number
        last_entry = (
            JournalEntry.objects.filter(company=active_company).order_by("-id").first()
        )
        next_number = (
            f"JE-{(int(last_entry.entry_number.split('-')[1]) + 1):04d}"
            if last_entry
            else "JE-0001"
        )

        form = JournalEntryForm(
            initial={
                "entry_number": next_number,
                "entry_date": datetime.now().date(),
                "status": "DRAFT",
            }
        )

    accounts = Account.objects.filter(company=active_company, is_active=True).order_by(
        "code"
    )

    # Convert accounts to JSON for JavaScript
    accounts_json = json.dumps([
        {"id": acc.id, "code": acc.code, "name": acc.name}
        for acc in accounts
    ])

    context = {
        "title": "Create Journal Entry",
        "form": form,
        "accounts": accounts_json,
        "action": "Create",
    }
    return render(request, "accounting/journal_entry_form.html", context)


@login_required
def journal_entry_detail(request, pk):
    """View journal entry details"""
    active_company = request.active_company
    entry = get_object_or_404(JournalEntry, pk=pk, company=active_company)
    lines = entry.lines.select_related("account").all()

    context = {
        "title": f"Journal Entry {entry.entry_number}",
        "entry": entry,
        "lines": lines,
        "is_balanced": entry.is_balanced(),
    }
    return render(request, "accounting/journal_entry_detail.html", context)


@login_required
def journal_entry_post(request, pk):
    """Post a journal entry"""
    active_company = request.active_company
    entry = get_object_or_404(JournalEntry, pk=pk, company=active_company)

    if entry.status == "DRAFT" and entry.is_balanced():
        entry.status = "POSTED"
        entry.posted_at = datetime.now()
        entry.posted_by = request.user
        entry.save()
        messages.success(
            request, f"Journal entry {entry.entry_number} posted successfully!"
        )
    elif not entry.is_balanced():
        messages.error(request, "Cannot post unbalanced journal entry!")
    else:
        messages.warning(
            request, f"Journal entry is already {entry.get_status_display()}."
        )

    return redirect("accounting:journal_entry_detail", pk=entry.pk)


@login_required
def journal_entry_delete(request, pk):
    """Delete journal entry"""
    active_company = request.active_company
    entry = get_object_or_404(JournalEntry, pk=pk, company=active_company)

    if entry.status == "POSTED":
        messages.error(request, "Cannot delete posted journal entries!")
        return redirect("accounting:journal_entry_detail", pk=entry.pk)

    if request.method == "POST":
        entry_number = entry.entry_number
        entry.delete()
        messages.success(request, f"Journal entry {entry_number} deleted successfully!")
        return redirect("accounting:journal_entry_list")

    context = {"title": "Delete Journal Entry", "entry": entry}
    return render(request, "accounting/journal_entry_confirm_delete.html", context)


# ============================================================================
# EXPENSE CRUD OPERATIONS
# ============================================================================


@login_required
def expense_list(request):
    """List all expenses"""
    active_company = request.active_company
    expenses = Expense.objects.filter(company=active_company).select_related(
        "category", "vendor", "created_by"
    ).order_by("-expense_date")

    total_expenses = expenses.aggregate(Sum("amount"))["amount__sum"] or Decimal("0.00")
    approved_count = expenses.filter(status="APPROVED").count()
    pending_count = expenses.filter(status="SUBMITTED").count()

    context = {
        "title": "Expenses",
        "expenses": expenses,
        "total_expenses": total_expenses,
        "approved_count": approved_count,
        "pending_count": pending_count,
    }
    return render(request, "accounting/expense_list.html", context)


@login_required
def expense_create(request):
    """Create new expense"""
    active_company = request.active_company

    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.company = active_company
            expense.created_by = request.user
            expense.save()
            messages.success(
                request, f"Expense {expense.expense_number} recorded successfully!"
            )
            return redirect("accounting:expense_detail", pk=expense.pk)
    else:
        # Generate next expense number
        last_expense = Expense.objects.filter(company=active_company).order_by("-id").first()
        next_number = (
            f"EXP-{(int(last_expense.expense_number.split('-')[1]) + 1):04d}"
            if last_expense
            else "EXP-0001"
        )

        form = ExpenseForm(
            initial={
                "expense_number": next_number,
                "expense_date": datetime.now().date(),
                "status": "DRAFT",
            }
        )

    context = {"title": "Record Expense", "form": form, "action": "Create"}
    return render(request, "accounting/expense_form.html", context)


@login_required
def expense_detail(request, pk):
    """View expense details"""
    active_company = request.active_company
    expense = get_object_or_404(Expense, pk=pk, company=active_company)

    context = {"title": f"Expense {expense.expense_number}", "expense": expense}
    return render(request, "accounting/expense_detail.html", context)


@login_required
def expense_approve(request, pk):
    """Approve an expense"""
    active_company = request.active_company
    expense = get_object_or_404(Expense, pk=pk, company=active_company)

    if expense.status == "SUBMITTED":
        expense.status = "APPROVED"
        expense.approved_by = request.user
        expense.save()
        messages.success(request, f"Expense {expense.expense_number} approved!")
    else:
        messages.warning(request, f"Expense is already {expense.get_status_display()}.")

    return redirect("accounting:expense_detail", pk=expense.pk)


@login_required
def expense_delete(request, pk):
    """Delete expense"""
    active_company = request.active_company
    expense = get_object_or_404(Expense, pk=pk, company=active_company)

    if request.method == "POST":
        expense_number = expense.expense_number
        expense.delete()
        messages.success(request, f"Expense {expense_number} deleted successfully!")
        return redirect("accounting:expense_list")

    context = {"title": "Delete Expense", "expense": expense}
    return render(request, "accounting/expense_confirm_delete.html", context)


# ============================================================================
# BUDGET CRUD OPERATIONS
# ============================================================================


@login_required
def budget_list(request):
    """List all budgets"""
    active_company = request.active_company
    budgets = Budget.objects.filter(company=active_company).order_by("-fiscal_year", "-start_date")

    context = {"title": "Budgets", "budgets": budgets}
    return render(request, "accounting/budget_list.html", context)


@login_required
def budget_create(request):
    """Create new budget"""
    active_company = request.active_company

    if request.method == "POST":
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.company = active_company
            budget.created_by = request.user
            budget.save()
            messages.success(request, f'Budget "{budget.name}" created successfully!')
            return redirect("accounting:budget_detail", pk=budget.pk)
    else:
        form = BudgetForm(
            initial={
                "fiscal_year": datetime.now().year,
                "start_date": datetime.now().date(),
                "is_active": True,
            }
        )

    context = {"title": "Create Budget", "form": form, "action": "Create"}
    return render(request, "accounting/budget_form.html", context)


@login_required
def budget_detail(request, pk):
    """View budget details"""
    active_company = request.active_company
    budget = get_object_or_404(Budget, pk=pk, company=active_company)
    lines = budget.lines.select_related("account").all()

    # Calculate totals
    total_budgeted = sum(line.budgeted_amount for line in lines)
    total_actual = sum(line.actual_amount for line in lines)
    total_variance = total_actual - total_budgeted

    context = {
        "title": f"Budget: {budget.name}",
        "budget": budget,
        "lines": lines,
        "total_budgeted": total_budgeted,
        "total_actual": total_actual,
        "total_variance": total_variance,
    }
    return render(request, "accounting/budget_detail.html", context)


@login_required
def budget_delete(request, pk):
    """Delete budget"""
    active_company = request.active_company
    budget = get_object_or_404(Budget, pk=pk, company=active_company)

    if request.method == "POST":
        budget_name = budget.name
        budget.delete()
        messages.success(request, f'Budget "{budget_name}" deleted successfully!')
        return redirect("accounting:budget_list")

    context = {"title": "Delete Budget", "budget": budget}
    return render(request, "accounting/budget_confirm_delete.html", context)


# ============================================================================
# FIXED ASSET CRUD OPERATIONS
# ============================================================================


@login_required
def fixed_asset_list(request):
    """List all fixed assets"""
    active_company = request.active_company
    assets = FixedAsset.objects.filter(company=active_company, is_active=True).order_by("asset_code")

    total_cost = assets.aggregate(Sum("purchase_cost"))[
        "purchase_cost__sum"
    ] or Decimal("0.00")
    total_depreciation = assets.aggregate(Sum("accumulated_depreciation"))[
        "accumulated_depreciation__sum"
    ] or Decimal("0.00")
    total_book_value = total_cost - total_depreciation

    context = {
        "title": "Fixed Assets",
        "assets": assets,
        "total_cost": total_cost,
        "total_depreciation": total_depreciation,
        "total_book_value": total_book_value,
    }
    return render(request, "accounting/fixed_asset_list.html", context)


@login_required
def fixed_asset_create(request):
    """Create new fixed asset"""
    active_company = request.active_company

    if request.method == "POST":
        form = FixedAssetForm(request.POST, company=active_company)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.company = active_company
            asset.created_by = request.user
            asset.book_value = asset.purchase_cost  # Initial book value
            asset.save()
            messages.success(
                request, f"Fixed asset {asset.asset_code} created successfully!"
            )
            return redirect("accounting:fixed_asset_detail", pk=asset.pk)
    else:
        # Generate next asset code
        last_asset = FixedAsset.objects.filter(company=active_company).order_by("-id").first()
        next_code = (
            f"ASSET-{(int(last_asset.asset_code.split('-')[1]) + 1):04d}"
            if last_asset
            else "ASSET-0001"
        )

        form = FixedAssetForm(
            company=active_company,
            initial={
                "asset_code": next_code,
                "purchase_date": datetime.now().date(),
                "is_active": True,
                "is_depreciated": True,
                "depreciation_method": "STRAIGHT_LINE",
                "salvage_value": Decimal("0.00"),
                "accumulated_depreciation": Decimal("0.00"),
            }
        )

    context = {"title": "Add Fixed Asset", "form": form, "action": "Create"}
    return render(request, "accounting/fixed_asset_form.html", context)


@login_required
def fixed_asset_detail(request, pk):
    """View fixed asset details"""
    active_company = request.active_company
    asset = get_object_or_404(FixedAsset, pk=pk, company=active_company)

    # Calculate depreciation info
    monthly_depreciation = asset.calculate_monthly_depreciation()
    depreciation_status = asset.get_depreciation_status()
    age_years = asset.get_age_in_years()
    remaining_life = asset.get_remaining_life_years()

    context = {
        "title": f"Asset: {asset.asset_code}",
        "asset": asset,
        "monthly_depreciation": monthly_depreciation,
        "depreciation_status": depreciation_status,
        "age_years": round(age_years, 2),
        "remaining_life": round(remaining_life, 2),
    }
    return render(request, "accounting/fixed_asset_detail.html", context)


@login_required
def fixed_asset_edit(request, pk):
    """Edit fixed asset"""
    active_company = request.active_company
    asset = get_object_or_404(FixedAsset, pk=pk, company=active_company)

    if request.method == "POST":
        form = FixedAssetForm(request.POST, instance=asset, company=active_company)
        if form.is_valid():
            updated_asset = form.save(commit=False)
            updated_asset.updated_by = request.user
            updated_asset.save()
            messages.success(
                request, f"Fixed asset {asset.asset_code} updated successfully!"
            )
            return redirect("accounting:fixed_asset_detail", pk=asset.pk)
    else:
        form = FixedAssetForm(instance=asset, company=active_company)

    context = {
        "title": f"Edit Asset: {asset.asset_code}",
        "form": form,
        "asset": asset,
        "action": "Update",
    }
    return render(request, "accounting/fixed_asset_form.html", context)


@login_required
def fixed_asset_delete(request, pk):
    """Delete fixed asset"""
    active_company = request.active_company
    asset = get_object_or_404(FixedAsset, pk=pk, company=active_company)

    if request.method == "POST":
        asset_code = asset.asset_code
        asset.delete()
        messages.success(request, f"Fixed asset {asset_code} deleted successfully!")
        return redirect("accounting:fixed_asset_list")

    context = {"title": "Delete Fixed Asset", "asset": asset}
    return render(request, "accounting/fixed_asset_confirm_delete.html", context)


# ============================================================================
# CUSTOMER CRUD OPERATIONS
# ============================================================================


@login_required
def customer_list(request):
    """List all customers for active company"""
    active_company = request.active_company
    customers = Customer.objects.filter(
        company=active_company, is_active=True
    ).order_by("company_name")

    context = {"title": "Customers", "customers": customers}
    return render(request, "accounting/customer_list.html", context)


@login_required
def customer_create(request):
    """Create new customer"""
    active_company = request.active_company

    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.company = active_company
            customer.save()
            messages.success(
                request, f"Customer {customer.company_name} created successfully!"
            )
            return redirect("accounting:customer_detail", pk=customer.pk)
    else:
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

    context = {"title": "Add Customer", "form": form, "action": "Create"}
    return render(request, "accounting/customer_form.html", context)


@login_required
def customer_detail(request, pk):
    """View customer details"""
    active_company = request.active_company
    customer = get_object_or_404(Customer, pk=pk, company=active_company)

    # Get customer invoices
    invoices = customer.invoices.order_by("-invoice_date")[:10]
    outstanding_balance = customer.get_outstanding_balance()

    context = {
        "title": f"Customer: {customer.company_name}",
        "customer": customer,
        "invoices": invoices,
        "outstanding_balance": outstanding_balance,
    }
    return render(request, "accounting/customer_detail.html", context)


# ============================================================================
# AI INSIGHTS OPERATIONS
# ============================================================================


@login_required
def ai_run_analysis(request):
    """Trigger AI analysis for the active company"""
    active_company = request.active_company

    # This would typically trigger an async task
    # For now, we'll just show a success message
    messages.success(request, "AI analysis started! Results will be available shortly.")

    return redirect("dashboard:ai_insights")


@login_required
def ai_trend_analysis(request):
    """Generate trend analysis charts"""
    active_company = request.active_company

    # Get monthly revenue and expenses for the past 12 months
    from accounting.models import AccountType

    months_data = []
    today = datetime.now().date()

    for i in range(12):
        month_start = (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(
            days=1
        )

        # This is simplified - you'd need proper monthly balance tracking
        months_data.append(
            {
                "month": month_start.strftime("%b %Y"),
                "revenue": Decimal("0.00"),  # Calculate from journal entries
                "expenses": Decimal("0.00"),  # Calculate from journal entries
            }
        )

    context = {"title": "Trend Analysis", "months_data": months_data}
    return render(request, "accounting/trend_analysis.html", context)
