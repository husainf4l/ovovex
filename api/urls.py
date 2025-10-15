from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Financial Ratios API
    path('financial-ratios/calculate/', views.calculate_ratios_api, name='calculate_ratios_api'),
    path('financial-ratios/trends/', views.trend_analysis_api, name='trend_analysis_api'),
    path('financial-ratios/industry/', views.industry_compare_api, name='industry_compare_api'),
    path('financial-ratios/export/', views.export_ratios_api, name='export_ratios_api'),

    # Interconnected Dashboard API
    path('customers/<int:customer_id>/related/', views.customer_related_data_api, name='customer_related_data_api'),
    path('invoices/<int:invoice_id>/related/', views.invoice_related_data_api, name='invoice_related_data_api'),
    path('kpi/live-updates/', views.live_kpi_updates_api, name='live_kpi_updates_api'),
    path('customers/search/', views.customer_search_api, name='customer_search_api'),
    path('invoices/search/', views.invoice_search_api, name='invoice_search_api'),
    path('dashboard/summary/', views.dashboard_summary_api, name='dashboard_summary_api'),
]
