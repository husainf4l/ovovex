from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_view(request):
    """
    Dashboard view for authenticated users
    """
    # Mock user for testing
    class MockUser:
        def __init__(self):
            self.username = "testuser"
            self.first_name = "Test"
            self.last_name = "User"
            self.email = "test@example.com"

        def get_full_name(self):
            return f"{self.first_name} {self.last_name}"

    context = {
        "title": "Dashboard",
        "description": "Your accounting dashboard and financial overview.",
        "user": MockUser(),
    }
    return render(request, "dashboard/dashboard.html", context)
