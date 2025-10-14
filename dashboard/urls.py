from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    
    # Module views
    path('general-ledger/', views.general_ledger_view, name='general_ledger'),
    path('invoices/', views.invoices_view, name='invoices'),
    path('balance-sheet/', views.balance_sheet_view, name='balance_sheet'),
    path('pnl-statement/', views.pnl_statement_view, name='pnl_statement'),
    path('journal-entries/', views.journal_entries_view, name='journal_entries'),
    path('cash-flow/', views.cash_flow_view, name='cash_flow'),
    path('budgeting/', views.budgeting_view, name='budgeting'),
    path('fixed-assets/', views.fixed_assets_view, name='fixed_assets'),
    path('financial-ratios/', views.financial_ratios_view, name='financial_ratios'),
    path('ai-insights/', views.ai_insights_view, name='ai_insights'),
    path('settings/', views.settings_view, name='settings'),
]
