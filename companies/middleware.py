from companies.models import UserCompany


class ActiveCompanyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            active = UserCompany.objects.filter(user=request.user, is_active=True).first()
            request.active_company = active.company if active else None
        else:
            request.active_company = None
        return self.get_response(request)
