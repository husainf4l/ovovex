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
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from . import views

# Non-translatable URLs (no language prefix needed)
# These URLs work the same regardless of language
urlpatterns = [
    path("admin/", admin.site.urls),  # Admin panel doesn't need translation prefix
    path("health/", views.health_check, name="health_check"),  # Health check endpoint
    path("i18n/", include("django.conf.urls.i18n")),  # Language switcher endpoint
    # Temporarily move dashboard outside i18n_patterns for testing
    path("dashboard/", include("dashboard.urls", namespace="dashboard")),
    # Companies management
    path("companies/", include("companies.urls")),
    # Accounting CRUD operations
    path("accounting/", include("accounting.urls", namespace="accounting")),
]

# Translatable URLs (will have language prefix like /en/ or /ar/)
# All user-facing URLs should be wrapped in i18n_patterns
urlpatterns += i18n_patterns(
    path("", views.home, name="home"),
    # Authentication URLs
    path("accounts/", include("accounts.urls", namespace="accounts")),
    # Dashboard - temporarily moved outside i18n_patterns for testing
    # path("dashboard/", views.dashboard_view, name="dashboard"),
    # Backward compatibility redirects for old module URLs
    path("ledger/", views.redirect_general_ledger, name="redirect_general_ledger"),
    path("invoices/", views.redirect_invoices, name="redirect_invoices"),
    path("balance-sheet/", views.redirect_balance_sheet, name="redirect_balance_sheet"),
    path(
        "journal-entries/",
        views.redirect_journal_entries,
        name="redirect_journal_entries",
    ),
    path("budgeting/", views.redirect_budgeting, name="redirect_budgeting"),
    path("fixed-assets/", views.redirect_fixed_assets, name="redirect_fixed_assets"),
    path("ai-insights/", views.redirect_ai_insights, name="redirect_ai_insights"),
    path("settings/", views.redirect_settings, name="redirect_settings"),
    # Public Pages
    path("", include("pages.urls", namespace="pages")),
    # This closes the i18n_patterns() function - all URLs above will have language prefix
)

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
