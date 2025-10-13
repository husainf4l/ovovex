from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'pages'

urlpatterns = [
    path('small-business/', views.small_business_view, name='small_business'),
    path('enterprise/', views.enterprise_view, name='enterprise'),
    path('accounting-firms/', views.accounting_firms_view, name='accounting_firms'),
    path('retail-ecommerce/', views.retail_ecommerce_view, name='retail_ecommerce'),
    path('manufacturing/', views.manufacturing_view, name='manufacturing'),
    path('smart-invoicing/', views.smart_invoicing_view, name='smart_invoicing'),
    path('ai-bookkeeping/', views.ai_bookkeeping_view, name='ai_bookkeeping'),
    path('real-time-analytics/', views.real_time_analytics_view, name='real_time_analytics'),
    path('ifrs-compliance/', views.ifrs_compliance_view, name='ifrs_compliance'),
    path('bank-grade-security/', views.bank_grade_security_view, name='bank_grade_security'),
    path('pricing/', views.pricing_view, name='pricing'),
    path('get-started/', views.get_started_view, name='get_started'),
    path('start-free-trial/', views.start_free_trial_view, name='start_free_trial'),
    path('contact-sales/', views.contact_sales_view, name='contact_sales'),
    # Signup Pages
    path('professional-signup/', TemplateView.as_view(template_name='pages/professional_signup.html'), name='professional_signup'),
    path('starter-signup/', TemplateView.as_view(template_name='pages/starter_plan.html'), name='starter_signup'),
    path('enterprise-signup/', TemplateView.as_view(template_name='pages/enterprise_signup.html'), name='enterprise_signup'),
    path('free-signup/', TemplateView.as_view(template_name='pages/free_signup.html'), name='free_signup'),
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
]
