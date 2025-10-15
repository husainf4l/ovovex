from django.urls import path
from . import views, reports_views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    # Financial Reports (NEW)
    path(
        "reports/profit-loss/",
        reports_views.profit_loss_report,
        name="profit_loss_report",
    ),
    path(
        "reports/balance-sheet/",
        reports_views.balance_sheet_report,
        name="balance_sheet_report",
    ),
    path("reports/cash-flow/", reports_views.cash_flow_report, name="cash_flow_report"),
    path("reports/aging/", reports_views.aging_report, name="aging_report"),
    path(
        "reports/cash-forecast/",
        reports_views.cash_flow_forecast_view,
        name="cash_flow_forecast",
    ),
    # Chart Data APIs (NEW)
    path(
        "api/charts/revenue-expense/",
        reports_views.revenue_expense_chart_data,
        name="revenue_expense_chart",
    ),
    path(
        "api/charts/expense-breakdown/",
        reports_views.expense_breakdown_chart_data,
        name="expense_breakdown_chart",
    ),
    path(
        "api/charts/top-customers/",
        reports_views.top_customers_chart_data,
        name="top_customers_chart",
    ),
    # Module views
    path("general-ledger/", views.general_ledger_view, name="general_ledger"),
    path("invoices/", views.invoices_view, name="invoices"),
    path("create-invoice/", views.create_invoice_view, name="create_invoice"),
    path("customers/", views.customers_view, name="customers"),
    path("customers/create/", views.create_customer_view, name="create_customer"),
    path("customers/edit/<int:pk>/", views.edit_customer_view, name="edit_customer"),
    path("customers/delete/<int:pk>/", views.delete_customer_view, name="delete_customer"),
    path("balance-sheet/", views.balance_sheet_view, name="balance_sheet"),
    path("pnl-statement/", views.pnl_statement_view, name="pnl_statement"),
    path("journal-entries/", views.journal_entries_view, name="journal_entries"),
    path("cash-flow/", views.cash_flow_view, name="cash_flow"),
    path("budgeting/", views.budgeting_view, name="budgeting"),
    path("fixed-assets/", views.fixed_assets_view, name="fixed_assets"),
    path("financial-ratios/", views.financial_ratios_view, name="financial_ratios"),
    path("ai-insights/", views.ai_insights_view, name="ai_insights"),
    path("settings/", views.settings_view, name="settings"),
]
