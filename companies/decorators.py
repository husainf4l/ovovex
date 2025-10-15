from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden


def company_required(view_func):
    """
    Decorator to ensure user has an active company selected.
    Redirects to company selection page if no active company.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if not request.active_company:
            messages.warning(request, "Please select a company to continue.")
            return redirect('select_company')

        return view_func(request, *args, **kwargs)
    return wrapper


def company_access_required(view_func):
    """
    Decorator to verify user has access to the active company.
    Returns 403 if user doesn't have access.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if not request.active_company:
            messages.warning(request, "Please select a company to continue.")
            return redirect('select_company')

        # Verify user has access to this company
        if request.active_company.id not in request.user_company_ids:
            return HttpResponseForbidden(
                "<h1>Access Denied</h1>"
                "<p>You don't have permission to access this company's data.</p>"
                "<p><a href='/companies/select/'>Select Company</a></p>"
            )

        return view_func(request, *args, **kwargs)
    return wrapper


def company_owner_required(view_func):
    """
    Decorator to ensure user is owner/admin of the company.
    Can be extended with role-based permissions later.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if not request.active_company:
            messages.warning(request, "Please select a company to continue.")
            return redirect('select_company')

        # Verify user has access
        if request.active_company.id not in request.user_company_ids:
            return HttpResponseForbidden("Access Denied: You don't have access to this company.")

        # TODO: Add role-based permission check here
        # For now, all users with access are considered owners
        # Future: Check UserCompany.role field

        return view_func(request, *args, **kwargs)
    return wrapper
