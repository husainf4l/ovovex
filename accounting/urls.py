"""
URL Configuration for Accounting App
Routes for all CRUD operations
"""

from django.urls import path
from . import views

app_name = "accounting"

urlpatterns = [
    # Invoice URLs
    path("invoices/", views.invoice_list, name="invoice_list"),
    path("invoices/create/", views.invoice_create, name="invoice_create"),
    path("invoices/<int:pk>/", views.invoice_detail, name="invoice_detail"),
    path("invoices/<int:pk>/edit/", views.invoice_edit, name="invoice_edit"),
    path("invoices/<int:pk>/delete/", views.invoice_delete, name="invoice_delete"),
    path("invoices/<int:pk>/send/", views.invoice_send, name="invoice_send"),
    # Payment URLs
    path("payments/create/", views.payment_create, name="payment_create"),
    path(
        "payments/create/<int:invoice_id>/",
        views.payment_create,
        name="payment_create_for_invoice",
    ),
    # Journal Entry URLs
    path("journal-entries/", views.journal_entry_list, name="journal_entry_list"),
    path(
        "journal-entries/create/",
        views.journal_entry_create,
        name="journal_entry_create",
    ),
    path(
        "journal-entries/<int:pk>/",
        views.journal_entry_detail,
        name="journal_entry_detail",
    ),
    path(
        "journal-entries/<int:pk>/post/",
        views.journal_entry_post,
        name="journal_entry_post",
    ),
    path(
        "journal-entries/<int:pk>/delete/",
        views.journal_entry_delete,
        name="journal_entry_delete",
    ),
    # Expense URLs
    path("expenses/", views.expense_list, name="expense_list"),
    path("expenses/create/", views.expense_create, name="expense_create"),
    path("expenses/<int:pk>/", views.expense_detail, name="expense_detail"),
    path("expenses/<int:pk>/approve/", views.expense_approve, name="expense_approve"),
    path("expenses/<int:pk>/delete/", views.expense_delete, name="expense_delete"),
    # Budget URLs
    path("budgets/", views.budget_list, name="budget_list"),
    path("budgets/create/", views.budget_create, name="budget_create"),
    path("budgets/<int:pk>/", views.budget_detail, name="budget_detail"),
    path("budgets/<int:pk>/delete/", views.budget_delete, name="budget_delete"),
    # Fixed Asset URLs
    path("fixed-assets/", views.fixed_asset_list, name="fixed_asset_list"),
    path("fixed-assets/create/", views.fixed_asset_create, name="fixed_asset_create"),
    path("fixed-assets/<int:pk>/", views.fixed_asset_detail, name="fixed_asset_detail"),
    path(
        "fixed-assets/<int:pk>/edit/", views.fixed_asset_edit, name="fixed_asset_edit"
    ),
    path(
        "fixed-assets/<int:pk>/delete/",
        views.fixed_asset_delete,
        name="fixed_asset_delete",
    ),
    # Customer URLs
    path("customers/", views.customer_list, name="customer_list"),
    path("customers/create/", views.customer_create, name="customer_create"),
    path("customers/<int:pk>/", views.customer_detail, name="customer_detail"),
    # AI Insights URLs
    path("ai/run-analysis/", views.ai_run_analysis, name="ai_run_analysis"),
    path("ai/trend-analysis/", views.ai_trend_analysis, name="ai_trend_analysis"),
]
