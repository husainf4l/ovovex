# DJANGO URL STRUCTURE IMPLEMENTATION GUIDE
# ==========================================

"""
This file outlines the complete URL routing structure for the Ovovex Accounting Platform.
Organize by app modules for clean separation of concerns.
"""

# ============================================================================
# PROJECT URLS (ovovex/urls.py) - Main URL Configuration
# ============================================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # API
    path("api/", include("api.urls")),
    # Authentication
    path("auth/", include("accounts.urls")),
    # Public Site (Marketing)
    path("", include("website.urls")),
    # Dashboard (Authenticated)
    path("dashboard/", include("dashboard.urls")),
    # Core Accounting
    path("accounting/", include("accounting.urls")),
    # Invoicing & Billing
    path("invoicing/", include("invoicing.urls")),
    # Receivables & Payables
    path("receivables/", include("receivables.urls")),
    path("payables/", include("payables.urls")),
    # Banking & Treasury
    path("banking/", include("banking.urls")),
    # Financial Management
    path("financials/", include("financials.urls")),
    # Assets
    path("assets/", include("assets.urls")),
    # Operations
    path("operations/", include("operations.urls")),
    # Tax & Compliance
    path("tax/", include("tax.urls")),
    path("compliance/", include("compliance.urls")),
    # Analytics & Insights
    path("analytics/", include("analytics.urls")),
    # AI Features
    path("ai/", include("ai_engine.urls")),
    # Workflows & Automation
    path("workflows/", include("workflows.urls")),
    # Integrations
    path("integrations/", include("integrations.urls")),
    # Documents
    path("documents/", include("documents.urls")),
    # Notifications
    path("notifications/", include("notifications.urls")),
    # Customer Portal
    path("portal/", include("portal.urls")),
    # Multi-Company
    path("companies/", include("multicompany.urls")),
    # Settings
    path("settings/", include("settings.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# ============================================================================
# WEBSITE URLS (website/urls.py) - Public Marketing Site
# ============================================================================

from django.urls import path
from . import views

app_name = "website"

urlpatterns = [
    # Homepage
    path("", views.home, name="home"),
    # Solutions
    path("small-business/", views.small_business, name="small_business"),
    path("mid-market/", views.mid_market, name="mid_market"),
    path("enterprise/", views.enterprise, name="enterprise"),
    path("accounting-firms/", views.accounting_firms, name="accounting_firms"),
    path("startups/", views.startups, name="startups"),
    # Industries
    path("retail-ecommerce/", views.retail_ecommerce, name="retail_ecommerce"),
    path("manufacturing/", views.manufacturing, name="manufacturing"),
    path(
        "professional-services/",
        views.professional_services,
        name="professional_services",
    ),
    path("healthcare/", views.healthcare, name="healthcare"),
    path("real-estate/", views.real_estate, name="real_estate"),
    path("technology-saas/", views.technology_saas, name="technology_saas"),
    path("non-profit/", views.non_profit, name="non_profit"),
    # Features
    path("smart-invoicing/", views.smart_invoicing, name="smart_invoicing"),
    path("ai-bookkeeping/", views.ai_bookkeeping, name="ai_bookkeeping"),
    path(
        "expense-management-feature/",
        views.expense_management_feature,
        name="expense_management_feature",
    ),
    path("real-time-analytics/", views.real_time_analytics, name="real_time_analytics"),
    path("multi-currency/", views.multi_currency, name="multi_currency"),
    path("bank-integrations/", views.bank_integrations, name="bank_integrations"),
    path("ifrs-compliance/", views.ifrs_compliance, name="ifrs_compliance"),
    path("bank-grade-security/", views.bank_grade_security, name="bank_grade_security"),
    path("api-integrations/", views.api_integrations, name="api_integrations"),
    # Resources
    path("documentation/", views.documentation, name="documentation"),
    path("api-reference/", views.api_reference, name="api_reference"),
    path("blog/", views.blog_list, name="blog"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("case-studies/", views.case_studies, name="case_studies"),
    path(
        "case-studies/<slug:slug>/", views.case_study_detail, name="case_study_detail"
    ),
    path("training/", views.training, name="training"),
    path("community/", views.community, name="community"),
    path("help-center/", views.help_center, name="help_center"),
    # Pricing & CTA
    path("pricing/", views.pricing, name="pricing"),
    path("start-free-trial/", views.start_free_trial, name="start_free_trial"),
    path("request-demo/", views.request_demo, name="request_demo"),
    # Legal
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("terms-of-service/", views.terms_of_service, name="terms_of_service"),
    path("security/", views.security_page, name="security_page"),
]


# ============================================================================
# DASHBOARD URLS (dashboard/urls.py) - Main Dashboard
# ============================================================================

from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    # Overview
    path("", views.dashboard_home, name="home"),
    path("quick-actions/", views.quick_actions, name="quick_actions"),
    path("recent-activity/", views.recent_activity, name="recent_activity"),
    # Help & Support
    path("help-center/", views.help_center, name="help_center"),
    path("video-tutorials/", views.video_tutorials, name="video_tutorials"),
    path("contact-support/", views.contact_support, name="contact_support"),
    path("submit-feedback/", views.submit_feedback, name="submit_feedback"),
    path("whats-new/", views.whats_new, name="whats_new"),
]


# ============================================================================
# ACCOUNTING URLS (accounting/urls.py)
# ============================================================================

from django.urls import path
from . import views

app_name = "accounting"

urlpatterns = [
    # General Ledger
    path("ledger/", views.general_ledger, name="general_ledger"),
    path("chart-of-accounts/", views.chart_of_accounts, name="chart_of_accounts"),
    path("accounts/create/", views.account_create, name="account_create"),
    path("accounts/<int:pk>/edit/", views.account_edit, name="account_edit"),
    # Journal Entries
    path("journal-entries/", views.journal_entries, name="journal_entries"),
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
        "journal-entries/<int:pk>/edit/",
        views.journal_entry_edit,
        name="journal_entry_edit",
    ),
    path(
        "journal-entries/<int:pk>/post/",
        views.journal_entry_post,
        name="journal_entry_post",
    ),
    path(
        "journal-entries/<int:pk>/reverse/",
        views.journal_entry_reverse,
        name="journal_entry_reverse",
    ),
    # Trial Balance
    path("trial-balance/", views.trial_balance, name="trial_balance"),
    # Reconciliation
    path("reconciliation/", views.reconciliation, name="reconciliation"),
]


# ============================================================================
# INVOICING URLS (invoicing/urls.py)
# ============================================================================

from django.urls import path
from . import views

app_name = "invoicing"

urlpatterns = [
    # Invoices
    path("invoices/", views.invoice_list, name="invoice_list"),
    path("invoices/create/", views.invoice_create, name="invoice_create"),
    path("invoices/<int:pk>/", views.invoice_detail, name="invoice_detail"),
    path("invoices/<int:pk>/edit/", views.invoice_edit, name="invoice_edit"),
    path("invoices/<int:pk>/send/", views.invoice_send, name="invoice_send"),
    path("invoices/<int:pk>/pdf/", views.invoice_pdf, name="invoice_pdf"),
    path("invoices/<int:pk>/void/", views.invoice_void, name="invoice_void"),
    path(
        "invoices/<int:pk>/duplicate/",
        views.invoice_duplicate,
        name="invoice_duplicate",
    ),
    # Recurring Invoices
    path(
        "recurring-invoices/",
        views.recurring_invoice_list,
        name="recurring_invoice_list",
    ),
    path(
        "recurring-invoices/create/",
        views.recurring_invoice_create,
        name="recurring_invoice_create",
    ),
    path(
        "recurring-invoices/<int:pk>/",
        views.recurring_invoice_detail,
        name="recurring_invoice_detail",
    ),
    # Quotes & Estimates
    path("quotes/", views.quote_list, name="quote_list"),
    path("quotes/create/", views.quote_create, name="quote_create"),
    path("quotes/<int:pk>/", views.quote_detail, name="quote_detail"),
    path(
        "quotes/<int:pk>/convert/", views.quote_convert_to_invoice, name="quote_convert"
    ),
    # Credit Notes
    path("credit-notes/", views.credit_note_list, name="credit_note_list"),
    path("credit-notes/create/", views.credit_note_create, name="credit_note_create"),
    path("credit-notes/<int:pk>/", views.credit_note_detail, name="credit_note_detail"),
    # Payment Links
    path("payment-links/", views.payment_link_list, name="payment_link_list"),
    path(
        "payment-links/create/", views.payment_link_create, name="payment_link_create"
    ),
    path(
        "payment-links/<uuid:uuid>/",
        views.payment_link_public,
        name="payment_link_public",
    ),
]


# ============================================================================
# RECEIVABLES URLS (receivables/urls.py)
# ============================================================================

from django.urls import path
from . import views

app_name = "receivables"

urlpatterns = [
    # Accounts Receivable
    path("", views.accounts_receivable_dashboard, name="dashboard"),
    path("aging-report/", views.aging_report, name="aging_report"),
    # Customers
    path("customers/", views.customer_list, name="customer_list"),
    path("customers/create/", views.customer_create, name="customer_create"),
    path("customers/<int:pk>/", views.customer_detail, name="customer_detail"),
    path("customers/<int:pk>/edit/", views.customer_edit, name="customer_edit"),
    path(
        "customers/<int:pk>/statement/",
        views.customer_statement,
        name="customer_statement",
    ),
    # Payments
    path("payments/", views.payment_list, name="payment_list"),
    path("payments/record/", views.payment_record, name="payment_record"),
    path("payments/<int:pk>/", views.payment_detail, name="payment_detail"),
    # Collections
    path("collections/", views.collections_dashboard, name="collections"),
    path(
        "collections/send-reminders/",
        views.send_collection_reminders,
        name="send_reminders",
    ),
]


# ============================================================================
# PAYABLES URLS (payables/urls.py)
# ============================================================================

from django.urls import path
from . import views

app_name = "payables"

urlpatterns = [
    # Accounts Payable
    path("", views.accounts_payable_dashboard, name="dashboard"),
    path("aging-report/", views.ap_aging_report, name="aging_report"),
    # Vendors
    path("vendors/", views.vendor_list, name="vendor_list"),
    path("vendors/create/", views.vendor_create, name="vendor_create"),
    path("vendors/<int:pk>/", views.vendor_detail, name="vendor_detail"),
    path("vendors/<int:pk>/edit/", views.vendor_edit, name="vendor_edit"),
    # Bills
    path("bills/", views.bill_list, name="bill_list"),
    path("bills/create/", views.bill_create, name="bill_create"),
    path("bills/<int:pk>/", views.bill_detail, name="bill_detail"),
    path("bills/<int:pk>/approve/", views.bill_approve, name="bill_approve"),
    path("bills/import/", views.bill_import, name="bill_import"),
    # Payments
    path("payments/", views.vendor_payment_list, name="payment_list"),
    path("payments/process/", views.payment_process, name="payment_process"),
    path("payments/<int:pk>/", views.vendor_payment_detail, name="payment_detail"),
    # Three-way Match
    path("three-way-match/", views.three_way_match, name="three_way_match"),
]


# ============================================================================
# BANKING URLS (banking/urls.py)
# ============================================================================

from django.urls import path
from . import views

app_name = "banking"

urlpatterns = [
    # Bank Accounts
    path("accounts/", views.bank_account_list, name="account_list"),
    path("accounts/create/", views.bank_account_create, name="account_create"),
    path("accounts/<int:pk>/", views.bank_account_detail, name="account_detail"),
    # Bank Reconciliation
    path("reconciliation/", views.bank_reconciliation, name="reconciliation"),
    path(
        "reconciliation/<int:pk>/",
        views.reconciliation_detail,
        name="reconciliation_detail",
    ),
    path(
        "reconciliation/<int:pk>/match/",
        views.reconciliation_match,
        name="reconciliation_match",
    ),
    # Bank Feeds
    path("feeds/", views.bank_feeds, name="feeds"),
    path("feeds/connect/", views.bank_feed_connect, name="feed_connect"),
    path("feeds/<int:pk>/sync/", views.bank_feed_sync, name="feed_sync"),
    # Treasury
    path("treasury/", views.treasury_management, name="treasury"),
    # Multi-Currency
    path("multi-currency/", views.multi_currency, name="multi_currency"),
    path("exchange-rates/", views.exchange_rates, name="exchange_rates"),
]


# ============================================================================
# FINANCIALS URLS (financials/urls.py)
# ============================================================================

from django.urls import path
from . import views

app_name = "financials"

urlpatterns = [
    # Financial Statements
    path("balance-sheet/", views.balance_sheet, name="balance_sheet"),
    path("income-statement/", views.income_statement, name="income_statement"),
    path("cash-flow-statement/", views.cash_flow_statement, name="cash_flow_statement"),
    path("statements/export/", views.statements_export, name="statements_export"),
    # Budgeting
    path("budgeting/", views.budgeting_dashboard, name="budgeting"),
    path("budgets/create/", views.budget_create, name="budget_create"),
    path("budgets/<int:pk>/", views.budget_detail, name="budget_detail"),
    path("budgets/<int:pk>/edit/", views.budget_edit, name="budget_edit"),
    path("budget-vs-actual/", views.budget_vs_actual, name="budget_vs_actual"),
    # Cash Flow Forecasting
    path("cash-flow-forecast/", views.cash_flow_forecast, name="cash_flow_forecast"),
    path("cash-flow-forecast/create/", views.forecast_create, name="forecast_create"),
    # Scenario Planning
    path("scenario-planning/", views.scenario_planning, name="scenario_planning"),
    path("scenarios/create/", views.scenario_create, name="scenario_create"),
    path("scenarios/<int:pk>/", views.scenario_detail, name="scenario_detail"),
]


# ============================================================================
# ASSETS URLS (assets/urls.py)
# ============================================================================

from django.urls import path
from . import views

app_name = "assets"

urlpatterns = [
    # Fixed Assets
    path("", views.fixed_asset_list, name="list"),
    path("create/", views.fixed_asset_create, name="create"),
    path("<int:pk>/", views.fixed_asset_detail, name="detail"),
    path("<int:pk>/edit/", views.fixed_asset_edit, name="edit"),
    path("<int:pk>/dispose/", views.fixed_asset_dispose, name="dispose"),
    # Depreciation
    path("depreciation/", views.depreciation_dashboard, name="depreciation"),
    path(
        "depreciation/calculate/",
        views.depreciation_calculate,
        name="depreciation_calculate",
    ),
    path("depreciation/report/", views.depreciation_report, name="depreciation_report"),
]


# ============================================================================
# OPERATIONS URLS (operations/urls.py)
# ============================================================================

from django.urls import path
from . import views

app_name = "operations"

urlpatterns = [
    # Expense Management
    path("expenses/", views.expense_list, name="expense_list"),
    path("expenses/create/", views.expense_create, name="expense_create"),
    path("expenses/<int:pk>/", views.expense_detail, name="expense_detail"),
    path("expenses/<int:pk>/approve/", views.expense_approve, name="expense_approve"),
    path(
        "expenses/bulk-approve/",
        views.expense_bulk_approve,
        name="expense_bulk_approve",
    ),
    # Receipt Scanner
    path("receipt-scanner/", views.receipt_scanner, name="receipt_scanner"),
    path("receipt-scanner/upload/", views.receipt_upload, name="receipt_upload"),
    # Purchase Orders
    path("purchase-orders/", views.purchase_order_list, name="purchase_order_list"),
    path(
        "purchase-orders/create/",
        views.purchase_order_create,
        name="purchase_order_create",
    ),
    path(
        "purchase-orders/<int:pk>/",
        views.purchase_order_detail,
        name="purchase_order_detail",
    ),
    path(
        "purchase-orders/<int:pk>/approve/",
        views.purchase_order_approve,
        name="purchase_order_approve",
    ),
    # Inventory
    path("inventory/", views.inventory_list, name="inventory_list"),
    path("inventory/create/", views.inventory_create, name="inventory_create"),
    path("inventory/<int:pk>/", views.inventory_detail, name="inventory_detail"),
    path("inventory/adjust/", views.inventory_adjust, name="inventory_adjust"),
    # Projects
    path("projects/", views.project_list, name="project_list"),
    path("projects/create/", views.project_create, name="project_create"),
    path("projects/<int:pk>/", views.project_detail, name="project_detail"),
    # Time Tracking
    path("time-tracking/", views.time_tracking, name="time_tracking"),
    path("time-entries/create/", views.time_entry_create, name="time_entry_create"),
]


# ============================================================================
# TAX URLS (tax/urls.py)
# ============================================================================

from django.urls import path
from . import views

app_name = "tax"

urlpatterns = [
    # Tax Center
    path("", views.tax_center, name="center"),
    # Tax Reports
    path("reports/", views.tax_reports, name="reports"),
    path("reports/<str:report_type>/", views.tax_report_detail, name="report_detail"),
    # VAT/GST
    path("vat-returns/", views.vat_returns, name="vat_returns"),
    path("vat-returns/create/", views.vat_return_create, name="vat_return_create"),
    path("vat-returns/<int:pk>/", views.vat_return_detail, name="vat_return_detail"),
    path("vat-returns/<int:pk>/file/", views.vat_return_file, name="vat_return_file"),
    # Tax Compliance
    path("compliance/", views.tax_compliance, name="compliance"),
    path("compliance/calendar/", views.compliance_calendar, name="compliance_calendar"),
]


# ============================================================================
# COMPLIANCE URLS (compliance/urls.py)
# ============================================================================

from django.urls import path
from . import views

app_name = "compliance"

urlpatterns = [
    # Compliance Dashboard
    path("", views.compliance_dashboard, name="dashboard"),
    # Audit Trail
    path("audit-trail/", views.audit_trail, name="audit_trail"),
    path("audit-logs/", views.audit_logs, name="audit_logs"),
    # Regulatory Filing
    path("regulatory-filing/", views.regulatory_filing, name="regulatory_filing"),
    path("filings/create/", views.filing_create, name="filing_create"),
    # Compliance Reports
    path("reports/", views.compliance_reports, name="reports"),
    path(
        "reports/<str:report_type>/export/", views.report_export, name="report_export"
    ),
]


# ============================================================================
# ANALYTICS URLS (analytics/urls.py)
# ============================================================================

from django.urls import path
from . import views

app_name = "analytics"

urlpatterns = [
    # Financial Dashboard
    path("dashboard/", views.financial_dashboard, name="dashboard"),
    # Financial Ratios
    path("ratios/", views.financial_ratios, name="ratios"),
    path("ratios/calculate/", views.ratios_calculate, name="ratios_calculate"),
    # KPI Tracking
    path("kpi/", views.kpi_tracking, name="kpi_tracking"),
    path("kpi/create/", views.kpi_create, name="kpi_create"),
    path("kpi/<int:pk>/", views.kpi_detail, name="kpi_detail"),
    # Custom Reports
    path("reports/", views.custom_reports, name="custom_reports"),
    path("reports/create/", views.report_create, name="report_create"),
    path("reports/<int:pk>/", views.report_detail, name="report_detail"),
    path("reports/<int:pk>/run/", views.report_run, name="report_run"),
    # Benchmarking
    path("benchmarking/", views.benchmarking, name="benchmarking"),
]


# ============================================================================
# AI ENGINE URLS (ai_engine/urls.py)
# ============================================================================

from django.urls import path
from . import views

app_name = "ai"

urlpatterns = [
    # AI Chat Assistant
    path("chat/", views.ai_chat, name="chat"),
    path("chat/message/", views.ai_chat_message, name="chat_message"),
    # AI Insights
    path("insights/", views.ai_insights, name="insights"),
    path("insights/<int:pk>/", views.insight_detail, name="insight_detail"),
    # Anomaly Detection
    path("anomaly-detection/", views.anomaly_detection, name="anomaly_detection"),
    path("anomalies/<int:pk>/", views.anomaly_detail, name="anomaly_detail"),
    # Predictive Analytics
    path(
        "predictive-analytics/", views.predictive_analytics, name="predictive_analytics"
    ),
    path("predictions/<str:model_type>/", views.prediction_run, name="prediction_run"),
    # Smart Recommendations
    path("recommendations/", views.smart_recommendations, name="recommendations"),
    path(
        "recommendations/<int:pk>/apply/",
        views.recommendation_apply,
        name="recommendation_apply",
    ),
    # AI Report Generator
    path("report-generator/", views.ai_report_generator, name="report_generator"),
    path("report-generator/generate/", views.generate_report, name="generate_report"),
    # Forecasting Models
    path("forecasting/", views.forecasting_models, name="forecasting"),
    path("forecasting/<str:model_type>/train/", views.model_train, name="model_train"),
]


# ============================================================================
# WORKFLOWS URLS (workflows/urls.py)
# ============================================================================

from django.urls import path
from . import views

app_name = "workflows"

urlpatterns = [
    # Approval Workflows
    path("approvals/", views.approval_workflows, name="approvals"),
    path("approvals/pending/", views.pending_approvals, name="pending_approvals"),
    path(
        "approvals/<int:pk>/approve/", views.approval_approve, name="approval_approve"
    ),
    path("approvals/<int:pk>/reject/", views.approval_reject, name="approval_reject"),
    # Workflow Configuration
    path("workflows/", views.workflow_list, name="workflow_list"),
    path("workflows/create/", views.workflow_create, name="workflow_create"),
    path("workflows/<int:pk>/", views.workflow_detail, name="workflow_detail"),
    # Automation Rules
    path("automation/", views.automation_rules, name="automation"),
    path("automation/create/", views.rule_create, name="rule_create"),
    path("automation/<int:pk>/", views.rule_detail, name="rule_detail"),
    # Email Templates
    path("email-templates/", views.email_templates, name="email_templates"),
    path(
        "email-templates/create/",
        views.email_template_create,
        name="email_template_create",
    ),
    # Scheduled Reports
    path("scheduled-reports/", views.scheduled_reports, name="scheduled_reports"),
    path(
        "scheduled-reports/create/",
        views.scheduled_report_create,
        name="scheduled_report_create",
    ),
]


# ============================================================================
# INTEGRATIONS URLS (integrations/urls.py)
# ============================================================================

from django.urls import path
from . import views

app_name = "integrations"

urlpatterns = [
    # Integration Hub
    path("", views.integration_hub, name="hub"),
    # Bank Connections
    path("banks/", views.bank_connections, name="banks"),
    path("banks/connect/", views.bank_connect, name="bank_connect"),
    path("banks/<int:pk>/disconnect/", views.bank_disconnect, name="bank_disconnect"),
    # Payment Processors
    path("payment-processors/", views.payment_processors, name="payment_processors"),
    path(
        "payment-processors/<str:provider>/connect/",
        views.payment_processor_connect,
        name="payment_processor_connect",
    ),
    # E-commerce
    path("ecommerce/", views.ecommerce_integrations, name="ecommerce"),
    path(
        "ecommerce/<str:platform>/connect/",
        views.ecommerce_connect,
        name="ecommerce_connect",
    ),
    # Payroll
    path("payroll/", views.payroll_integrations, name="payroll"),
    # CRM
    path("crm/", views.crm_integrations, name="crm"),
    # ERP
    path("erp/", views.erp_integrations, name="erp"),
    # API & Webhooks
    path("api-webhooks/", views.api_webhooks, name="api_webhooks"),
    path("api-keys/", views.api_keys, name="api_keys"),
    path("api-keys/create/", views.api_key_create, name="api_key_create"),
    path("webhooks/", views.webhooks, name="webhooks"),
    path("webhooks/create/", views.webhook_create, name="webhook_create"),
]


# ============================================================================
# DOCUMENTS URLS (documents/urls.py)
# ============================================================================

from django.urls import path
from . import views

app_name = "documents"

urlpatterns = [
    # Document Management
    path("", views.document_list, name="list"),
    path("upload/", views.document_upload, name="upload"),
    path("<int:pk>/", views.document_detail, name="detail"),
    path("<int:pk>/download/", views.document_download, name="download"),
    path("<int:pk>/delete/", views.document_delete, name="delete"),
    path("<int:pk>/share/", views.document_share, name="share"),
    # Categories
    path("categories/", views.category_list, name="category_list"),
]


# ============================================================================
# NOTIFICATIONS URLS (notifications/urls.py)
# ============================================================================

from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    # Notifications
    path("", views.notification_list, name="list"),
    path("<int:pk>/mark-read/", views.notification_mark_read, name="mark_read"),
    path("mark-all-read/", views.notifications_mark_all_read, name="mark_all_read"),
    # Settings
    path("settings/", views.notification_settings, name="settings"),
]


# ============================================================================
# PORTAL URLS (portal/urls.py) - Customer Portal
# ============================================================================

from django.urls import path
from . import views

app_name = "portal"

urlpatterns = [
    # Portal Dashboard
    path("", views.portal_dashboard, name="dashboard"),
    # Invoices
    path("invoices/", views.portal_invoices, name="invoices"),
    path("invoices/<int:pk>/", views.portal_invoice_detail, name="invoice_detail"),
    path("invoices/<int:pk>/pay/", views.portal_invoice_pay, name="invoice_pay"),
    # Payments
    path("payments/", views.portal_payments, name="payments"),
    # Documents
    path("documents/", views.portal_documents, name="documents"),
    # Support
    path("support/", views.portal_support, name="support"),
    path("support/tickets/create/", views.portal_ticket_create, name="ticket_create"),
]


# ============================================================================
# MULTICOMPANY URLS (multicompany/urls.py)
# ============================================================================

from django.urls import path
from . import views

app_name = "multicompany"

urlpatterns = [
    # Company Selector
    path("selector/", views.company_selector, name="selector"),
    path("switch/<int:company_id>/", views.company_switch, name="switch"),
    # Consolidation
    path("consolidation/", views.consolidation_dashboard, name="consolidation"),
    path("consolidation/run/", views.consolidation_run, name="consolidation_run"),
    # Inter-Company
    path("inter-company/", views.inter_company_transactions, name="inter_company"),
    # Group Reporting
    path("group-reporting/", views.group_reporting, name="group_reporting"),
]


# ============================================================================
# SETTINGS URLS (settings/urls.py)
# ============================================================================

from django.urls import path
from . import views

app_name = "settings"

urlpatterns = [
    # Company Settings
    path("company/", views.company_settings, name="company"),
    # User Management
    path("users/", views.user_management, name="users"),
    path("users/invite/", views.user_invite, name="user_invite"),
    path("users/<int:pk>/", views.user_detail, name="user_detail"),
    # Roles & Permissions
    path("roles/", views.roles_permissions, name="roles"),
    path("roles/create/", views.role_create, name="role_create"),
    # Security
    path("security/", views.security_settings, name="security"),
    path("two-factor-auth/", views.two_factor_auth, name="two_factor_auth"),
    # Audit Logs
    path("audit-logs/", views.audit_logs, name="audit_logs"),
    # Backup & Recovery
    path("backup/", views.backup_recovery, name="backup"),
    path("backup/create/", views.backup_create, name="backup_create"),
    path("backup/<int:pk>/restore/", views.backup_restore, name="backup_restore"),
    # Data Export
    path("data-export/", views.data_export, name="data_export"),
    # Billing
    path("billing/", views.billing_subscription, name="billing"),
    path("billing/upgrade/", views.subscription_upgrade, name="upgrade"),
    # Preferences
    path("preferences/", views.user_preferences, name="preferences"),
]


# ============================================================================
# API URLS (api/urls.py) - REST API Endpoints
# ============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# Register ViewSets here
# router.register(r'accounts', AccountViewSet)
# router.register(r'invoices', InvoiceViewSet)
# etc.

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("rest_framework.urls")),
]
