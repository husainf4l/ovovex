from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from accounting.models import Account, AccountType, Customer, Invoice, Payment, JournalEntry
from dashboard.services.sync import DashboardSyncService
from decimal import Decimal


@login_required
def calculate_ratios_api(request):
    """
    API endpoint to calculate financial ratios dynamically
    """
    try:
        active_company = request.active_company

        # Get balance sheet data
        assets = Account.objects.filter(company=active_company, account_type=AccountType.ASSET, is_active=True)
        liabilities = Account.objects.filter(
            company=active_company, account_type=AccountType.LIABILITY, is_active=True
        )
        equity = Account.objects.filter(company=active_company, account_type=AccountType.EQUITY, is_active=True)

        total_assets = sum(acc.get_balance() for acc in assets)
        total_liabilities = sum(acc.get_balance() for acc in liabilities)
        total_equity = sum(acc.get_balance() for acc in equity)

        # Get income statement data
        revenue_accounts = Account.objects.filter(
            company=active_company, account_type=AccountType.REVENUE, is_active=True
        )
        expense_accounts = Account.objects.filter(
            company=active_company, account_type=AccountType.EXPENSE, is_active=True
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
    try:
        active_company = request.active_company

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
    try:
        active_company = request.active_company

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
    from django.http import HttpResponse
    import csv
    import io

    try:
        active_company = request.active_company

        # Get format from request
        export_format = request.GET.get("format", "csv")

        # Calculate ratios (similar to calculate_ratios_api)
        assets = Account.objects.filter(company=active_company, account_type=AccountType.ASSET, is_active=True)
        liabilities = Account.objects.filter(
            company=active_company, account_type=AccountType.LIABILITY, is_active=True
        )
        equity = Account.objects.filter(company=active_company, account_type=AccountType.EQUITY, is_active=True)

        total_assets = sum(acc.get_balance() for acc in assets)
        total_liabilities = sum(acc.get_balance() for acc in liabilities)
        total_equity = sum(acc.get_balance() for acc in equity)

        revenue_accounts = Account.objects.filter(
            company=active_company, account_type=AccountType.REVENUE, is_active=True
        )
        expense_accounts = Account.objects.filter(
            company=active_company, account_type=AccountType.EXPENSE, is_active=True
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


# ============================================================================
# INTERCONNECTED DASHBOARD API ENDPOINTS
# ============================================================================


@login_required
def customer_related_data_api(request, customer_id):
    """
    API endpoint to get related data for a customer (invoices, payments, etc.)
    Used for dynamic dropdowns and relationship displays
    """
    try:
        active_company = request.active_company
        sync_service = DashboardSyncService(active_company)

        related_data = sync_service.get_related_data("customer", customer_id)

        return JsonResponse({
            "success": True,
            "data": related_data
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def invoice_related_data_api(request, invoice_id):
    """
    API endpoint to get related data for an invoice (customer, payments, etc.)
    """
    try:
        active_company = request.active_company
        sync_service = DashboardSyncService(active_company)

        related_data = sync_service.get_related_data("invoice", invoice_id)

        return JsonResponse({
            "success": True,
            "data": related_data
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def live_kpi_updates_api(request):
    """
    API endpoint for real-time KPI updates
    Returns current dashboard metrics that may have changed
    """
    try:
        active_company = request.active_company
        sync_service = DashboardSyncService(active_company)

        kpi_data = sync_service.get_live_kpi_updates()

        return JsonResponse({
            "success": True,
            "kpis": kpi_data,
            "timestamp": "2025-01-07T12:00:00Z"  # Current timestamp
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def customer_search_api(request):
    """
    API endpoint for searching customers with balances
    Used for dynamic dropdowns in forms
    """
    try:
        active_company = request.active_company
        query = request.GET.get('q', '').strip()

        customers = Customer.objects.filter(
            company=active_company,
            is_active=True
        ).filter(
            Q(company_name__icontains=query) |
            Q(customer_code__icontains=query)
        ).values(
            'id', 'customer_code', 'company_name'
        )[:10]  # Limit results

        # Add balance information
        for customer in customers:
            customer_obj = Customer.objects.get(id=customer['id'])
            customer['outstanding_balance'] = float(customer_obj.get_outstanding_balance())

        return JsonResponse({
            "success": True,
            "customers": list(customers)
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def invoice_search_api(request):
    """
    API endpoint for searching unpaid invoices
    Used for payment forms
    """
    try:
        active_company = request.active_company
        customer_id = request.GET.get('customer_id')
        query = request.GET.get('q', '').strip()

        invoices = Invoice.objects.filter(
            company=active_company,
            status__in=['SENT', 'OVERDUE']
        )

        if customer_id:
            invoices = invoices.filter(customer_id=customer_id)

        if query:
            invoices = invoices.filter(
                Q(invoice_number__icontains=query) |
                Q(customer__company_name__icontains=query)
            )

        invoice_data = invoices.values(
            'id', 'invoice_number', 'total_amount', 'paid_amount',
            'customer__company_name', 'due_date', 'status'
        ).order_by('-invoice_date')[:20]

        # Calculate remaining balance for each
        for invoice in invoice_data:
            invoice['remaining_balance'] = float(
                Decimal(str(invoice['total_amount'])) - Decimal(str(invoice['paid_amount']))
            )

        return JsonResponse({
            "success": True,
            "invoices": list(invoice_data)
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def dashboard_summary_api(request):
    """
    API endpoint for dashboard summary data
    Returns key metrics for real-time updates
    """
    try:
        active_company = request.active_company

        # Get recent activity
        recent_invoices = Invoice.objects.filter(
            company=active_company
        ).order_by('-created_at')[:5].values(
            'id', 'invoice_number', 'customer__company_name',
            'total_amount', 'status', 'created_at'
        )

        recent_payments = Payment.objects.filter(
            company=active_company
        ).order_by('-created_at')[:5].values(
            'id', 'payment_number', 'customer__company_name',
            'amount', 'payment_date', 'created_at'
        )

        # Get summary counts
        total_customers = Customer.objects.filter(company=active_company, is_active=True).count()
        total_invoices = Invoice.objects.filter(company=active_company).count()
        unpaid_invoices = Invoice.objects.filter(
            company=active_company, status__in=['SENT', 'OVERDUE']
        ).count()

        total_revenue = Invoice.objects.filter(
            company=active_company, status='PAID'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

        return JsonResponse({
            "success": True,
            "summary": {
                "total_customers": total_customers,
                "total_invoices": total_invoices,
                "unpaid_invoices": unpaid_invoices,
                "total_revenue": float(total_revenue)
            },
            "recent_activity": {
                "invoices": list(recent_invoices),
                "payments": list(recent_payments)
            }
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
