from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Financial Ratios API
    path('financial-ratios/calculate/', views.calculate_ratios_api, name='calculate_ratios_api'),
    path('financial-ratios/trends/', views.trend_analysis_api, name='trend_analysis_api'),
    path('financial-ratios/industry/', views.industry_compare_api, name='industry_compare_api'),
    path('financial-ratios/export/', views.export_ratios_api, name='export_ratios_api'),
]
