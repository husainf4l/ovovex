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
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('health/', views.health_check, name='health_check'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Core Accounting
    path('ledger/', views.general_ledger_view, name='general_ledger'),
    path('invoices/', views.invoices_view, name='invoices'),
    path('invoices/create/', views.create_invoice_view, name='create_invoice'),
    path('invoices/send/<int:invoice_id>/', views.send_invoice_view, name='send_invoice'),
    path('invoices/record-payment/', views.record_payment_view, name='record_payment'),
    path('invoices/send-reminders/', views.send_reminders_view, name='send_reminders'),
    path('invoices/collection-report/', views.collection_report_view, name='collection_report'),
    path('invoices/send-statements/', views.send_statements_view, name='send_statements'),
    path('invoices/set-reminders/', views.set_reminders_view, name='set_reminders'),
    path('invoices/report/', views.invoice_report_view, name='invoice_report'),
    path('balance-sheet/', views.balance_sheet_view, name='balance_sheet'),
    path('pnl-statement/', views.pnl_statement_view, name='pnl_statement'),
    path('journal-entries/', views.journal_entries_view, name='journal_entries'),
    path('journal-entries/create/', views.create_journal_entry_view, name='create_journal_entry'),
    path('journal-entries/post/', views.post_journal_entries_view, name='post_journal_entries'),
    path('journal-entries/reverse/', views.reverse_journal_entry_view, name='reverse_journal_entry'),
    path('journal-entries/export/', views.export_journal_entries_view, name='export_journal_entries'),
    path('journal-report/', views.journal_report_view, name='journal_report'),
    path('trial-balance/', views.trial_balance_view, name='trial_balance'),
    path('reconciliation/', views.reconciliation_view, name='reconciliation'),
    
    # Financial Management
    path('cash-flow/', views.cash_flow_view, name='cash_flow'),
    path('budgeting/', views.budgeting_view, name='budgeting'),
    path('budgeting/create/', views.create_budget_view, name='create_budget'),
    path('budgeting/copy/', views.copy_budget_view, name='copy_budget'),
    path('budgeting/export/', views.export_budget_view, name='export_budget'),
    path('fixed-assets/', views.fixed_assets_view, name='fixed_assets'),
    path('fixed-assets/add/', views.add_fixed_asset_view, name='add_fixed_asset'),
    path('fixed-assets/export/', views.export_fixed_assets_view, name='export_fixed_assets'),
    path('bank-reconciliation/', views.bank_reconciliation_view, name='bank_reconciliation'),
    path('bank-reconciliation/update-statement-balance/', views.update_statement_balance_view, name='update_statement_balance'),
    path('bank-reconciliation/add-adjustment/', views.add_reconciliation_adjustment_view, name='add_reconciliation_adjustment'),
    path('bank-reconciliation/reconcile-statement/<int:statement_id>/', views.reconcile_statement_view, name='reconcile_statement'),
    path('tax-center/', views.tax_center_view, name='tax_center'),
    path('tax-center/update-asset-tax-info/<int:asset_id>/', views.update_asset_tax_info_view, name='update_asset_tax_info'),
    path('tax-center/calculate-depreciation/', views.calculate_tax_depreciation_view, name='calculate_tax_depreciation'),
    path('tax-center/generate-report/', views.generate_tax_report_view, name='generate_tax_report'),
    
    # Receivables & Payables
    path('accounts-receivable/', views.accounts_receivable_view, name='accounts_receivable'),
    path('accounts-payable/', views.accounts_payable_view, name='accounts_payable'),
    path('accounts-payable/create-bill/', views.create_bill_view, name='create_bill'),
    path('accounts-payable/import-bills/', views.import_bills_view, name='import_bills'),
    path('accounts-payable/process-payments/', views.process_payments_view, name='process_payments'),
    path('accounts-payable/send-reminders/', views.send_payable_reminders_view, name='send_payable_reminders'),
    path('accounts-payable/mark-as-paid/', views.mark_as_paid_view, name='mark_as_paid'),
    path('accounts-payable/three-way-match/', views.three_way_match_view, name='three_way_match'),
    path('accounts-payable/aging-report/', views.payable_aging_report_view, name='payable_aging_report'),
    path('customer-portal/', views.customer_portal_view, name='customer_portal'),
    path('customer-portal/fixed-assets/', views.customer_fixed_assets_view, name='customer_fixed_assets'),
    path('customer-portal/profile/', views.customer_profile_view, name='customer_profile'),
    path('customer-portal/support/', views.customer_support_view, name='customer_support'),
    path('customer-portal/activity/', views.customer_activity_view, name='customer_activity'),
    
    # Analytics & Insights
    path('financial-ratios/', views.financial_ratios_view, name='financial_ratios'),
    path('api/financial-ratios/calculate/', views.calculate_ratios_api, name='calculate_ratios_api'),
    path('api/financial-ratios/trends/', views.trend_analysis_api, name='trend_analysis_api'),
    path('api/financial-ratios/industry/', views.industry_compare_api, name='industry_compare_api'),
    path('api/financial-ratios/export/', views.export_ratios_api, name='export_ratios_api'),
    path('ai-insights/', views.ai_insights_view, name='ai_insights'),
    path('anomaly-detection/', views.anomaly_detection_view, name='anomaly_detection'),
    
    # Operations
    path('expense-management/', views.expense_management_view, name='expense_management'),
    path('purchase-orders/', views.purchase_orders_view, name='purchase_orders'),
    path('inventory/', views.inventory_view, name='inventory'),
    path('documents/', views.documents_view, name='documents'),
    
    # Reports & Compliance
    path('financial-statements/', views.financial_statements_view, name='financial_statements'),
    path('tax-reports/', views.tax_reports_view, name='tax_reports'),
    path('audit-compliance/', views.audit_compliance_view, name='audit_compliance'),
    
    # Settings
    path('settings/', views.settings_view, name='settings'),
]
