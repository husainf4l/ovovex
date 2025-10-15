from companies.models import UserCompany
from django.shortcuts import redirect
from django.urls import reverse


class ActiveCompanyMiddleware:
    """
    Middleware that sets the active company for authenticated users.

    Features:
    - Sets request.active_company from UserCompany.is_active
    - Falls back to session-stored company_id
    - Provides user_companies list for easy access
    - Handles company access verification
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Initialize company attributes
        request.active_company = None
        request.user_companies = []

        if request.user.is_authenticated:
            # Get all companies this user has access to
            user_companies = UserCompany.objects.filter(
                user=request.user
            ).select_related('company')

            request.user_companies = user_companies

            # Try to get active company from database
            active_uc = user_companies.filter(is_active=True).first()

            if active_uc:
                request.active_company = active_uc.company
                # Sync session
                request.session['active_company_id'] = active_uc.company.id
            else:
                # Try to get from session
                session_company_id = request.session.get('active_company_id')
                if session_company_id:
                    try:
                        uc = user_companies.filter(company_id=session_company_id).first()
                        if uc:
                            # Restore active company
                            uc.is_active = True
                            uc.save()
                            # Deactivate others
                            user_companies.exclude(id=uc.id).update(is_active=False)
                            request.active_company = uc.company
                    except Exception:
                        pass

            # Store user's company IDs for quick access check
            request.user_company_ids = [uc.company_id for uc in user_companies]

        return self.get_response(request)
