from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView


def small_business_view(request):
    """
    Small Business page view
    """
    context = {
        "title": "Small Business Accounting Solutions",
        "description": "Accounting solutions for businesses with up to 50 employees.",
    }
    return render(request, "pages/small_business.html", context)


def enterprise_view(request):
    """
    Enterprise page view
    """
    context = {
        "title": "Enterprise Accounting Solutions",
        "description": "Accounting solutions for large organizations with 500+ employees.",
    }
    return render(request, "pages/enterprise.html", context)


def accounting_firms_view(request):
    """
    Accounting Firms page view
    """
    context = {
        "title": "Accounting Firms Solutions",
        "description": "Professional accounting firm management and multi-client solutions.",
    }
    return render(request, "pages/accounting_firms.html", context)


def retail_ecommerce_view(request):
    """
    Retail & E-commerce page view
    """
    context = {
        "title": "Retail & E-commerce Accounting",
        "description": "Specialized accounting solutions for retail and online businesses.",
    }
    return render(request, "pages/retail_ecommerce.html", context)


def manufacturing_view(request):
    """
    Manufacturing page view
    """
    context = {
        "title": "Manufacturing Accounting",
        "description": "Comprehensive accounting solutions for manufacturing operations.",
    }
    return render(request, "pages/manufacturing.html", context)


def smart_invoicing_view(request):
    """
    Smart Invoicing page view
    """
    context = {
        "title": "Smart Invoicing Solutions",
        "description": "Automated billing and payment processing tools.",
    }
    return render(request, "pages/smart_invoicing.html", context)


def ai_bookkeeping_view(request):
    """
    AI Bookkeeping page view
    """
    context = {
        "title": "AI-Powered Bookkeeping",
        "description": "Intelligent automation for financial record keeping.",
    }
    return render(request, "pages/ai_bookkeeping.html", context)


def real_time_analytics_view(request):
    """
    Real-time Analytics page view
    """
    context = {
        "title": "Real-Time Financial Insights",
        "description": "Live dashboards and analytics for instant business intelligence.",
    }
    return render(request, "pages/real_time_analytics.html", context)


def ifrs_compliance_view(request):
    """
    IFRS Compliance page view
    """
    context = {
        "title": "IFRS Compliance Solutions",
        "description": "International Financial Reporting Standards compliance tools.",
    }
    return render(request, "pages/ifrs_compliance.html", context)


def bank_grade_security_view(request):
    """
    Bank-Grade Security page view
    """
    context = {
        "title": "Bank-Grade Security",
        "description": "ISO 27001 certified data protection and security infrastructure.",
    }
    return render(request, "pages/bank_grade_security.html", context)


def pricing_view(request):
    """
    Pricing page view
    """
    context = {
        "title": "Pricing Plans - Ovovex",
        "description": "Choose the perfect plan for your business needs.",
    }
    return render(request, "pages/pricing.html", context)


def get_started_view(request):
    """
    Get Started page view
    """
    context = {
        "title": "Get Started with Ovovex",
        "description": "Begin your journey with Ovovex - guided onboarding and quick setup.",
    }
    return render(request, "pages/get_started.html", context)


def start_free_trial_view(request):
    """
    Start Free Trial page view
    """
    context = {
        "title": "Start Your Free Trial",
        "description": "Start a risk-free trial of Ovovex and explore core features.",
    }
    return render(request, "pages/start_free_trial.html", context)


def contact_sales_view(request):
    """
    Contact Sales page view
    """
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        company = request.POST.get("company")
        message = request.POST.get("message")

        # In a real app we'd create a SalesLead record or send an email
        messages.success(request, "Thanks! Our sales team will reach out shortly.")
        return redirect("contact_sales")

    context = {
        "title": "Contact Sales",
        "description": "Get a tailored quote and onboard support for your organization.",
    }
    return render(request, "pages/contact_sales.html", context)
