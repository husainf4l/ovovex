"""
URL configuration for ovovex project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf.urls.i18n import i18n_patterns
from . import views

# Non-translatable URLs (no language prefix needed)
# These URLs work the same regardless of language
urlpatterns = [
    path("admin/", admin.site.urls),  # Admin panel doesn't need translation prefix
    path("health/", views.health_check, name="health_check"),  # Health check endpoint
    path('i18n/', include('django.conf.urls.i18n')),  # Language switcher endpoint
]

# Translatable URLs (will have language prefix like /en/ or /ar/)
# All user-facing URLs should be wrapped in i18n_patterns
urlpatterns += i18n_patterns(
    path("", views.home, name="home"),
    # Authentication URLs
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    # Dashboard
    path("dashboard/", views.dashboard_view, name="dashboard"),
    # Core Accounting
    path("ledger/", views.general_ledger_view, name="general_ledger"),
    path("invoices/", views.invoices_view, name="invoices"),
    path("invoices/create/", views.create_invoice_view, name="create_invoice"),
    path(
        "invoices/send/<int:invoice_id>/", views.send_invoice_view, name="send_invoice"
    ),
    path("invoices/record-payment/", views.record_payment_view, name="record_payment"),
    path("invoices/send-reminders/", views.send_reminders_view, name="send_reminders"),
    path(
        "invoices/collection-report/",
        views.collection_report_view,
        name="collection_report",
    ),
    path(
        "invoices/send-statements/", views.send_statements_view, name="send_statements"
    ),
    path("invoices/set-reminders/", views.set_reminders_view, name="set_reminders"),
    path("invoices/report/", views.invoice_report_view, name="invoice_report"),
    path("balance-sheet/", views.balance_sheet_view, name="balance_sheet"),
    path("pnl-statement/", views.pnl_statement_view, name="pnl_statement"),
    path("journal-entries/", views.journal_entries_view, name="journal_entries"),
    path(
        "journal-entries/create/",
        views.create_journal_entry_view,
        name="create_journal_entry",
    ),
    path(
        "journal-entries/post/",
        views.post_journal_entries_view,
        name="post_journal_entries",
    ),
    path(
        "journal-entries/reverse/",
        views.reverse_journal_entry_view,
        name="reverse_journal_entry",
    ),
    path(
        "journal-entries/export/",
        views.export_journal_entries_view,
        name="export_journal_entries",
    ),
    path("journal-report/", views.journal_report_view, name="journal_report"),
    path("trial-balance/", views.trial_balance_view, name="trial_balance"),
    path("reconciliation/", views.reconciliation_view, name="reconciliation"),
    # Financial Management
    path("cash-flow/", views.cash_flow_view, name="cash_flow"),
    path("budgeting/", views.budgeting_view, name="budgeting"),
    path("budgeting/create/", views.create_budget_view, name="create_budget"),
    path("budgeting/copy/", views.copy_budget_view, name="copy_budget"),
    path("budgeting/export/", views.export_budget_view, name="export_budget"),
    path("fixed-assets/", views.fixed_assets_view, name="fixed_assets"),
    path("fixed-assets/add/", views.add_fixed_asset_view, name="add_fixed_asset"),
    path(
        "fixed-assets/export/",
        views.export_fixed_assets_view,
        name="export_fixed_assets",
    ),
    path(
        "bank-reconciliation/",
        views.bank_reconciliation_view,
        name="bank_reconciliation",
    ),
    path(
        "bank-reconciliation/update-statement-balance/",
        views.update_statement_balance_view,
        name="update_statement_balance",
    ),
    path(
        "bank-reconciliation/add-adjustment/",
        views.add_reconciliation_adjustment_view,
        name="add_reconciliation_adjustment",
    ),
    path(
        "bank-reconciliation/reconcile-statement/<int:statement_id>/",
        views.reconcile_statement_view,
        name="reconcile_statement",
    ),
    path("tax-center/", views.tax_center_view, name="tax_center"),
    path(
        "tax-center/update-asset-tax-info/<int:asset_id>/",
        views.update_asset_tax_info_view,
        name="update_asset_tax_info",
    ),
    path(
        "tax-center/calculate-depreciation/",
        views.calculate_tax_depreciation_view,
        name="calculate_tax_depreciation",
    ),
    path(
        "tax-center/generate-report/",
        views.generate_tax_report_view,
        name="generate_tax_report",
    ),
    # Receivables & Payables
    path(
        "accounts-receivable/",
        views.accounts_receivable_view,
        name="accounts_receivable",
    ),
    path("accounts-payable/", views.accounts_payable_view, name="accounts_payable"),
    path("accounts-payable/create-bill/", views.create_bill_view, name="create_bill"),
    path(
        "accounts-payable/import-bills/", views.import_bills_view, name="import_bills"
    ),
    path(
        "accounts-payable/process-payments/",
        views.process_payments_view,
        name="process_payments",
    ),
    path(
        "accounts-payable/send-reminders/",
        views.send_payable_reminders_view,
        name="send_payable_reminders",
    ),
    path(
        "accounts-payable/mark-as-paid/", views.mark_as_paid_view, name="mark_as_paid"
    ),
    path(
        "accounts-payable/three-way-match/",
        views.three_way_match_view,
        name="three_way_match",
    ),
    path(
        "accounts-payable/aging-report/",
        views.payable_aging_report_view,
        name="payable_aging_report",
    ),
    path("customer-portal/", views.customer_portal_view, name="customer_portal"),
    path(
        "customer-portal/fixed-assets/",
        views.customer_fixed_assets_view,
        name="customer_fixed_assets",
    ),
    path(
        "customer-portal/profile/", views.customer_profile_view, name="customer_profile"
    ),
    path(
        "customer-portal/support/", views.customer_support_view, name="customer_support"
    ),
    path(
        "customer-portal/activity/",
        views.customer_activity_view,
        name="customer_activity",
    ),
    # Analytics & Insights
    path("financial-ratios/", views.financial_ratios_view, name="financial_ratios"),
    path(
        "api/financial-ratios/calculate/",
        views.calculate_ratios_api,
        name="calculate_ratios_api",
    ),
    path(
        "api/financial-ratios/trends/",
        views.trend_analysis_api,
        name="trend_analysis_api",
    ),
    path(
        "api/financial-ratios/industry/",
        views.industry_compare_api,
        name="industry_compare_api",
    ),
    path(
        "api/financial-ratios/export/",
        views.export_ratios_api,
        name="export_ratios_api",
    ),
    path("ai-insights/", views.ai_insights_view, name="ai_insights"),
    path("anomaly-detection/", views.anomaly_detection_view, name="anomaly_detection"),
    # Operations
    path(
        "expense-management/", views.expense_management_view, name="expense_management"
    ),
    path(
        "expense-management/create/", views.create_expense_view, name="create_expense"
    ),
    path(
        "expense-management/scan-receipt/", views.scan_receipt_view, name="scan_receipt"
    ),
    path(
        "expense-management/bulk-approve/",
        views.bulk_approve_expenses_view,
        name="bulk_approve_expenses",
    ),
    path(
        "expense-management/export/", views.export_expenses_view, name="export_expenses"
    ),
    path("purchase-orders/", views.purchase_orders_view, name="purchase_orders"),
    path("inventory/", views.inventory_view, name="inventory"),
    path("inventory/add-product/", views.add_product_view, name="add_product"),
    path("inventory/import-items/", views.import_items_view, name="import_items"),
    path("inventory/receive-stock/", views.receive_stock_view, name="receive_stock"),
    path("inventory/stock-report/", views.stock_report_view, name="stock_report"),
    path("inventory/adjust-stock/", views.adjust_stock_view, name="adjust_stock"),
    path("inventory/create-po/", views.create_po_view, name="create_po"),
    path("inventory/set-reorder-point/", views.set_reorder_point_view, name="set_reorder_point"),
    path("inventory/export/", views.export_inventory_view, name="export_inventory"),
    path("documents/", views.documents_view, name="documents"),
    # Reports & Compliance
    path("financial-statements/", views.financial_ratios_view, name="financial_statements"),
    path("tax-reports/", views.tax_reports_view, name="tax_reports"),
    path("audit-compliance/", views.audit_compliance_view, name="audit_compliance"),
    # Export API endpoints
    path(
        "api/financial-statements/export/",
        views.export_financial_statements_api,
        name="export_financial_statements_api",
    ),
    path(
        "api/tax-reports/export/",
        views.export_tax_reports_api,
        name="export_tax_reports_api",
    ),
    path(
        "api/audit-compliance/export/",
        views.export_audit_compliance_api,
        name="export_audit_compliance_api",
    ),
    path(
        "api/purchase-orders/export/",
        views.export_purchase_orders_api,
        name="export_purchase_orders_api",
    ),
    # Settings
    path("settings/", views.settings_view, name="settings"),
    # Settings API endpoints
    path("api/settings/export-users/", views.export_users_api, name="export_users_api"),
    path("api/settings/add-user/", views.add_user_api, name="add_user_api"),
    path("api/settings/edit-user/", views.edit_user_api, name="edit_user_api"),
    path("api/settings/disable-user/", views.disable_user_api, name="disable_user_api"),
    path("api/settings/save/", views.save_settings_api, name="save_settings_api"),
    path(
        "api/settings/security-audit/",
        views.security_audit_api,
        name="security_audit_api",
    ),
    path(
        "api/settings/add-integration/",
        views.add_integration_api,
        name="add_integration_api",
    ),
    path(
        "api/settings/connect-integration/",
        views.connect_integration_api,
        name="connect_integration_api",
    ),
    path(
        "api/settings/regenerate-key/",
        views.regenerate_key_api,
        name="regenerate_key_api",
    ),
    path(
        "api/settings/delete-all-data/",
        views.delete_all_data_api,
        name="delete_all_data_api",
    ),
    path(
        "api/settings/delete-account/",
        views.delete_account_api,
        name="delete_account_api",
    ),
    # Notification API endpoints
    path("api/notifications/", views.notifications_api, name="notifications_api"),
    path(
        "api/notifications/mark-read/",
        views.mark_notification_read_api,
        name="mark_notification_read_api",
    ),
    path(
        "api/notifications/mark-all-read/",
        views.mark_all_notifications_read_api,
        name="mark_all_notifications_read_api",
    ),
    path(
        "api/notifications/create/",
        views.create_notification_api,
        name="create_notification_api",
    ),
    path(
        "api/notifications/delete/<int:notification_id>/",
        views.delete_notification_api,
        name="delete_notification_api",
    ),
    path(
        "api/notifications/stats/",
        views.notification_stats_api,
        name="notification_stats_api",
    ),
    # Public Pages
    path("small-business/", views.small_business_view, name="small_business"),
    path("enterprise/", views.enterprise_view, name="enterprise"),
    path("accounting-firms/", views.accounting_firms_view, name="accounting_firms"),
    path("retail-ecommerce/", views.retail_ecommerce_view, name="retail_ecommerce"),
    path("manufacturing/", views.manufacturing_view, name="manufacturing"),
    path("smart-invoicing/", views.smart_invoicing_view, name="smart_invoicing"),
    path("ai-bookkeeping/", views.ai_bookkeeping_view, name="ai_bookkeeping"),
    path(
        "real-time-analytics/",
        views.real_time_analytics_view,
        name="real_time_analytics",
    ),
    path("ifrs-compliance/", views.ifrs_compliance_view, name="ifrs_compliance"),
    path(
        "bank-grade-security/",
        views.bank_grade_security_view,
        name="bank_grade_security",
    ),
    path("pricing/", views.pricing_view, name="pricing"),
    path("get-started/", views.get_started_view, name="get_started"),
    path("start-free-trial/", views.start_free_trial_view, name="start_free_trial"),
    # Signup Pages
    path("professional-signup/", TemplateView.as_view(template_name='pages/professional_signup.html'), name='professional_signup'),
    path("starter-signup/", TemplateView.as_view(template_name='pages/starter_signup.html'), name='starter_signup'),
    path("enterprise-signup/", TemplateView.as_view(template_name='pages/enterprise_signup.html'), name='enterprise_signup'),
    path("free-signup/", TemplateView.as_view(template_name='pages/free_signup.html'), name='free_signup'),
    path("contact-sales/", views.contact_sales_view, name="contact_sales"),
    # Pricing Pages
    path('pages/starter-plan/', TemplateView.as_view(template_name='pages/starter_plan.html'), name='starter_plan'),
    path('pages/professional-plan/', TemplateView.as_view(template_name='pages/professional_plan.html'), name='professional_plan'),
    path('pages/enterprise-plan/', TemplateView.as_view(template_name='pages/enterprise_plan.html'), name='enterprise_plan'),
    # Billing Pages
    path('pages/payment-setup/', TemplateView.as_view(template_name='pages/payment_setup.html'), name='payment_setup'),
    path('pages/subscription-management/', TemplateView.as_view(template_name='pages/subscription_management.html'), name='subscription_management'),
    path('pages/billing-history/', TemplateView.as_view(template_name='pages/billing_history.html'), name='billing_history'),
    # Feature Pages
    path('features/smart-invoicing/', TemplateView.as_view(template_name='features/smart-invoicing.html'), name='feature_smart_invoicing'),
    path('features/financial-analytics/', TemplateView.as_view(template_name='features/financial-analytics.html'), name='feature_financial_analytics'),
    path('features/expense-management/', TemplateView.as_view(template_name='features/expense-management.html'), name='feature_expense_management'),
    path('features/team-collaboration/', TemplateView.as_view(template_name='features/team-collaboration.html'), name='feature_team_collaboration'),
    path('features/security-compliance/', TemplateView.as_view(template_name='features/security-compliance.html'), name='feature_security_compliance'),
    path('features/integrations/', TemplateView.as_view(template_name='features/integrations.html'), name='feature_integrations'),
    # This closes the i18n_patterns() function - all URLs above will have language prefix
)
