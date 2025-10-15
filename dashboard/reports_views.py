"""
Financial Reports Views
Generate and display comprehensive financial reports
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from decimal import Decimal

from dashboard.reports import FinancialReports
from accounting.models import Invoice, Bill


@login_required
def profit_loss_report(request):
    """Generate Profit & Loss Statement"""
    active_company = request.active_company

    # Get date range from request or default to current month
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")

    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    else:
        today = datetime.now().date()
        start_date = today.replace(day=1)
        end_date = today

    # Generate report
    reports = FinancialReports(active_company, start_date, end_date)
    pnl_data = reports.profit_and_loss()

    context = {
        "title": "Profit & Loss Statement",
        "report": pnl_data,
        "start_date": start_date,
        "end_date": end_date,
    }

    # Handle export requests
    export_format = request.GET.get("export")
    if export_format == "pdf":
        return export_report_pdf(context, "pnl")
    elif export_format == "csv":
        return export_report_csv(pnl_data, "profit_loss")

    return render(request, "dashboard/reports/profit_loss.html", context)


@login_required
def balance_sheet_report(request):
    """Generate Balance Sheet"""
    active_company = request.active_company

    # Get date from request or default to today
    as_of_date_str = request.GET.get("as_of_date")

    if as_of_date_str:
        as_of_date = datetime.strptime(as_of_date_str, "%Y-%m-%d").date()
    else:
        as_of_date = datetime.now().date()

    # Generate report
    reports = FinancialReports(active_company, end_date=as_of_date)
    balance_sheet_data = reports.balance_sheet()

    context = {
        "title": "Balance Sheet",
        "report": balance_sheet_data,
        "as_of_date": as_of_date,
    }

    # Handle export requests
    export_format = request.GET.get("export")
    if export_format == "pdf":
        return export_report_pdf(context, "balance_sheet")
    elif export_format == "csv":
        return export_report_csv(balance_sheet_data, "balance_sheet")

    return render(request, "dashboard/reports/balance_sheet.html", context)


@login_required
def cash_flow_report(request):
    """Generate Cash Flow Statement"""
    active_company = request.active_company

    # Get date range from request or default to current month
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")

    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    else:
        today = datetime.now().date()
        start_date = today.replace(day=1)
        end_date = today

    # Generate report
    reports = FinancialReports(active_company, start_date, end_date)
    cash_flow_data = reports.cash_flow_statement()

    context = {
        "title": "Cash Flow Statement",
        "report": cash_flow_data,
        "start_date": start_date,
        "end_date": end_date,
    }

    # Handle export requests
    export_format = request.GET.get("export")
    if export_format == "pdf":
        return export_report_pdf(context, "cash_flow")
    elif export_format == "csv":
        return export_report_csv(cash_flow_data, "cash_flow")

    return render(request, "dashboard/reports/cash_flow.html", context)


@login_required
def aging_report(request):
    """Generate Accounts Receivable Aging Report"""
    active_company = request.active_company

    # Generate report
    reports = FinancialReports(active_company)
    aging_data = reports.aging_report_receivables()

    context = {
        "title": "Accounts Receivable Aging Report",
        "report": aging_data,
    }

    # Handle export requests
    export_format = request.GET.get("export")
    if export_format == "pdf":
        return export_report_pdf(context, "aging")
    elif export_format == "csv":
        return export_report_csv(aging_data, "aging_report")

    return render(request, "dashboard/reports/aging_report.html", context)


@login_required
def cash_flow_forecast_view(request):
    """Generate Cash Flow Forecast"""
    active_company = request.active_company

    # Get forecast period from request or default to 90 days
    days_ahead = int(request.GET.get("days", 90))

    # Generate forecast
    reports = FinancialReports(active_company)
    forecast_data = reports.cash_flow_forecast(days_ahead)

    context = {
        "title": f"{days_ahead}-Day Cash Flow Forecast",
        "report": forecast_data,
        "days_ahead": days_ahead,
    }

    # Handle export requests
    export_format = request.GET.get("export")
    if export_format == "json":
        return JsonResponse(forecast_data, safe=False)
    elif export_format == "csv":
        return export_report_csv(forecast_data, "cash_flow_forecast")

    return render(request, "dashboard/reports/cash_flow_forecast.html", context)


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================


def export_report_csv(report_data, report_name):
    """Export report to CSV"""
    import csv
    from io import StringIO

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="{report_name}_{datetime.now().strftime("%Y%m%d")}.csv"'
    )

    # Create CSV writer
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)

    # Write report data based on type
    if report_name == "profit_loss":
        writer.writerow(["Profit & Loss Statement"])
        writer.writerow(
            ["Period:", f"{report_data['start_date']} to {report_data['end_date']}"]
        )
        writer.writerow([])
        writer.writerow(["Revenue"])
        for item in report_data["revenue"]["items"]:
            writer.writerow([item["account"].name, f"${item['amount']:,.2f}"])
        writer.writerow(["Total Revenue", f"${report_data['revenue']['total']:,.2f}"])
        writer.writerow([])
        writer.writerow(["Expenses"])
        for item in report_data["expenses"]["items"]:
            writer.writerow([item["account"].name, f"${item['amount']:,.2f}"])
        writer.writerow(["Total Expenses", f"${report_data['expenses']['total']:,.2f}"])
        writer.writerow([])
        writer.writerow(["Net Income", f"${report_data['net_income']:,.2f}"])

    response.write(csv_buffer.getvalue())
    return response


def export_report_pdf(context, report_type):
    """Export report to PDF using ReportLab"""
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
        Spacer,
    )
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from io import BytesIO

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph(context["title"], styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Company name
    company_name = Paragraph(
        f"<b>{context['report'].get('company', 'Company')}</b>", styles["Normal"]
    )
    elements.append(company_name)
    elements.append(Spacer(1, 12))

    # Date range
    if "start_date" in context:
        date_range = Paragraph(
            f"Period: {context['start_date']} to {context['end_date']}",
            styles["Normal"],
        )
        elements.append(date_range)
        elements.append(Spacer(1, 20))

    # Build PDF
    doc.build(elements)

    # Get PDF data
    pdf = buffer.getvalue()
    buffer.close()

    # Create response
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="{report_type}_{datetime.now().strftime("%Y%m%d")}.pdf"'
    )
    response.write(pdf)

    return response


# ============================================================================
# API ENDPOINTS FOR CHARTS
# ============================================================================


@login_required
def revenue_expense_chart_data(request):
    """
    API endpoint for income vs expenses chart data
    Returns JSON for Chart.js
    """
    active_company = request.active_company

    # Get last 12 months data
    today = datetime.now().date()
    months_data = []

    for i in range(12):
        month_start = (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(
            days=1
        )

        reports = FinancialReports(active_company, month_start, month_end)
        pnl = reports.profit_and_loss()

        months_data.append(
            {
                "month": month_start.strftime("%b %Y"),
                "revenue": float(pnl["revenue"]["total"]),
                "expenses": float(pnl["expenses"]["total"]),
                "profit": float(pnl["net_income"]),
            }
        )

    # Reverse to show oldest first
    months_data.reverse()

    return JsonResponse(
        {
            "labels": [m["month"] for m in months_data],
            "revenue": [m["revenue"] for m in months_data],
            "expenses": [m["expenses"] for m in months_data],
            "profit": [m["profit"] for m in months_data],
        }
    )


@login_required
def expense_breakdown_chart_data(request):
    """
    API endpoint for expense breakdown by category
    Returns JSON for Chart.js pie chart
    """
    active_company = request.active_company

    from accounting.models import ExpenseCategory, Expense
    from django.db.models import Sum

    # Get expense totals by category
    categories = ExpenseCategory.objects.filter(
        account__company=active_company, is_active=True
    )

    category_data = []
    colors = [
        "#3B82F6",
        "#10B981",
        "#F59E0B",
        "#EF4444",
        "#8B5CF6",
        "#EC4899",
        "#14B8A6",
        "#F97316",
        "#6366F1",
        "#84CC16",
    ]

    for i, category in enumerate(categories):
        total = Expense.objects.filter(
            category=category, status__in=["APPROVED", "PAID"]
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        if total > 0:
            category_data.append(
                {
                    "category": category.name,
                    "total": float(total),
                    "color": colors[i % len(colors)],
                }
            )

    return JsonResponse(
        {
            "labels": [c["category"] for c in category_data],
            "data": [c["total"] for c in category_data],
            "colors": [c["color"] for c in category_data],
        }
    )


@login_required
def top_customers_chart_data(request):
    """
    API endpoint for top customers by invoice value
    """
    active_company = request.active_company

    from django.db.models import Sum
    from accounting.models import Customer

    # Get top 10 customers by total invoice value
    top_customers = (
        Customer.objects.filter(company=active_company, is_active=True)
        .annotate(total_invoiced=Sum("invoices__total_amount"))
        .order_by("-total_invoiced")[:10]
    )

    return JsonResponse(
        {
            "labels": [c.company_name for c in top_customers],
            "data": [float(c.total_invoiced or 0) for c in top_customers],
        }
    )
